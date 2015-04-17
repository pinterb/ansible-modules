#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import sys
import socket
import json

HAS_CONSUL = False
try:
    import consul
    HAS_CONSUL = True
except ImportError:
    pass

class KeyValueStore(object):
    """
    This is a generic key-value storage class.
    
    A subclass may wish to override some or all of the following methods:
        - feh1
        - feh2
    """
    
    def __init__(self, module):
        self.module = module
        self.params = self.module.params
        
    def valid_params(self):
        return True
    
    def check_if_system_state_would_be_changed(self):
        return False
    
    def get(self):
        return (False, False)

    def put(self):
        return (False, False)

    def delete(self):
        return (False, False)


class ConsulKeyValueStore(KeyValueStore):
    """
    This is the Consul key-value storage class.
    Go to http://consul.io to learn more about Consul.
    
    """
    
    def __init__(self, module):
        self.module = module
        self.params = self.module.params
        
        self.host = self.params['host']
        self.port = self.params['port']
        if self.port is None:
            self.port = 8500
            
        self.consul_kvs = consul.Consul(host=self.host, port=self.port)
        
    def _valid_key(self):
        """
        Validate the key.
        Any non-zero-length value is currently a valid key.
        """
        self.key = self.params['key']
       
        if self.key is None:
            return False
        elif len(self.key) == 0:
            return False
        
        return True
        
    def _valid_value(self):
        """
        Validate the value.
        Any non-zero-length value is currently valid.
        """
        self.value = self.params['value']
       
        if self.value is None:
            return False
        elif len(self.value) == 0:
            return False
        
        return True
        
    def valid_params(self):
        return True
    
    def check_if_system_state_would_be_changed(self):
        return False
    
    def get(self):
        if not self._valid_key():
            raise MissingKeyException()
        
        return self.consul_kvs.kv.get(self.key)
    
    def put(self):
        """
        Store a key/value into Consul's Key Value endpoint.
        
        Existing key/value should result in a no-op.
        Returns a tuple of booleans: (Success/Failure of Consul put operation, Data changed)
        """
        self.value = self.params['value']
        if not self._valid_value():
            raise MissingValueException()
        
        current_data = self.get()
        if len(current_data):
            current_index = current_data[0]
            current_value_body = current_data[1]
            if current_value_body is None:
                self.index = 0

            elif self.value == current_value_body['Value']:
                # Nothing to update; no reason to fail -- so return True
                return (True, False)
            else:
                # Updates require the Consul ModifyIndex value
                self.index = current_index

        op_status = self.consul_kvs.kv.put(self.key, self.value, cas=self.index)
        return (op_status, True)
    
    def delete(self):
        """
        Remove a key/value from Consul's Key Value endpoint.
        
        Non-existent key should result in a no-op.
        Returns a tuple of booleans: (Success/Failure of Consul delete operation, Data changed)
        """
        current_data = self.get()
        if len(current_data):
            current_index = current_data[0]
            current_value_body = current_data[1]
            if current_value_body is None:
                return (True, False)

        else:
            return (True, False)
        
        op_status = self.consul_kvs.kv.delete(self.key)
        return (op_status, True)

        
class MissingKeyException(Exception):
    pass

class MissingValueException(Exception):
    pass

def main():
    
    module = AnsibleModule(
        argument_spec = dict(
            provider=dict(default='consul', choices=['consul', 'etcd']),
            host=dict(default='127.0.0.1'),
            port=dict(default=None),
            delay=dict(default=0),
            state=dict(default='present', choices=['present', 'absent']),
            key=dict(default=None),
            value=dict(default=None)
        ),
        supports_check_mode=False
    )

    params = module.params

    provider = params['provider']
    host = params['host']
    if params['port']:
        port = int(params['port'])
    else:
        port = None
    delay = int(params['delay'])
    state = params['state']
    key = params['key']
    value = params['value']
   
    # The backend system that's doing all the work 
    backend = None

    # Create the backend key-value storage provider    
    if provider == 'consul':
        if HAS_CONSUL:
            backend = ConsulKeyValueStore(module)
        else:
            module.fail_json(msg="python-consul library was not found. consider running 'pip install python-consul'")
    
    elif provider == 'etcd':
        module.fail_json(msg="support for the etcd provider is planned, but currently not implemented")
        
    if backend is None:
        module.fail_json(msg="invalid provider")

    # Start our timer        
    start = datetime.datetime.now()
    if delay:
        time.sleep(delay)

    # Perform actual backend storage operation        
    op_status = False
    kvs_changed = False
    
    if state == 'present':
        try:
            op_status, kvs_changed  = backend.put()
        except MissingKeyException:
            module.fail_json(msg="invalid or missing key was provided")
        except MissingValueException:
            module.fail_json(msg="invalid or missing value was provided")
        except:
            module.fail_json(msg="unknown error occurred")
    elif state == 'absent':
        try:
            op_status, kvs_changed  = backend.delete()
        except MissingKeyException:
            module.fail_json(msg="invalid or missing key was provided")
        except:
            module.fail_json(msg="unknown error occurred")
    else:
        module.fail_json(msg="invalid state was provided")

        
    # Wrap-up        
    elapsed = datetime.datetime.now() - start
    module.exit_json(changed=kvs_changed, kvs_status=op_status, state=state, provider=provider, key=key, value=value, host=host, port=port, delay=delay, elapsed=elapsed.seconds)
    
# import module snippets
from ansible.module_utils.basic import *
main()    
