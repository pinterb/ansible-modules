## Key/Value Config
Maybe your configuration data isn't in files on disk, but in a new fancy distributed configuration store. But you still want to manage that configuration in code. Enter the key_value_config type for Ansible.  

Inspired by Gareth Rushgrove's Puppet [module](https://github.com/garethr/garethr-key_value_config).   

### Usage  
Currently this type has two providers for Etcd and Consul but writing other providers for Zookeeper or similar services should be trivial.   


### Configuration  


### A note on error handling   
