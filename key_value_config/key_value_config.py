import datetime
import sys
import socket

HAS_CONSUL = False
try:
    import consul
    HAS_CONSUL = True
except ImportError:
    pass


def main():
    
    module = AnsibleModule(
        argument_spec = dict(
            provider=dict(default='consul', choices=['consul', 'etcd']),
            host=dict(default='127.0.0.1'),
            port=dict(default=None),
            timeout=dict(default=300),
            delay=dict(default=0),
            state=dict(default='present', choices=['present', 'absent'),
            key=dict(default=None),
            value=dict(default=None)
        ),
    )
    
# import module snippets
from ansible.module_utils.basic import *
main()    