# unbound-public-service
A self contained Ansible playbook with tests, to build an Unbound DoT server for
general public consumption.

The playbook is structured such that discrete functionality is separated into
separate files so they can be skipped accordingly if not required.

This playbook is fairly specifically tied to Suse but could be easily adapted to
use another OS.

This has been used exclusively on the Linode SuSELeap 13.3 image.  YMMV on other providers / images.

# Features
The playbook will:
 * Set up basic sys. admin such as creating a sudo user ```admin_user```, set ssh key, disable  root login etc.
 * Disable IPv6
 * Enable and configure nftables add enable some basic rate limiting to aid in thwarting DoS attacks. see [files/nftables.conf](files/nftables.conf)
 * Install and valid TLS cert using let's encrypt and enable auto renewal
 * Install and configure DataDog agent along with Unbound integration
 * Install and configure Unbound configured only to server requests over DoH see [files/unbound-dot.conf.j2](files/unbound-dot.conf.j2)

# Vars
* ```admin_user``` in [unbound_dot.yml](unbound_dot.yml) - User created for sudo and SSH key access - defaults to ```operator```
* ```ssh_key``` in [unbound_dot.yml](unbound_dot.yml) - SSH key to use for admin_user - deafults to a ~/.ssh/id_your_key.pub on the local file system
* ```hostname``` in [unbound_dot.yml](unbound_dot.yml) - Hostname to use for the TLS cert - defaults to Ansible's ```inventory_hostname``` this should be a FQDN
* ```datadog_api_key``` [tasks/datadog_tasks.yml](tasks/datadog_tasks.yml) - The Datadog API key for the agent

# Tests
A number of Pytest / Testinfra tests can be found in [tests/test_unbound_public_dot.py](tests/test_unbound_public_dot.py) these have be
written to not only validate a build, but with the intention that they would be run regularly against a running service, e.g. checking the TLS cert validity
period.

# Ancillary
* [linode.yml](linode.yml) is an example of a dynamic Ansible inventory for Linode - expects hosts to have a tag of ```unbound```
* [tests/dns_testing.py](tests/dns_testing.py)  - Helper functions for the Testinfra tests.  Includes TLS cert testing (validity and expiry) and querying CN TXT records

# Standards
All Python files are [Blackened](https://en.wikipedia.org/wiki/...And_Justice_for_All_(album)) with [black](https://github.com/psf/black)


# Example Usage (with Linode dynamic iventory)
## Ansible
```ansible-galaxy install -r require```

(First run)

```ansible-playbook -i linode.yml -u root unbound_dot.yml -e datadog_api_key=AAAAAAAAAAAAAAAAAAAAAAAAAAAA ```

(Subsequent runs)

```ansible-playbook -i linode.yml -u operator -b unbound_dot.yml -e datadog_api_key=AAAAAAAAAAAAAAAAAAAAAAAA```

## Test
This requires pytest, pytest-testinfra, dnspython


```ANSIBLE_REMOTE_USER=operator pytest -vv --hosts='ansible://unbound' --ansible-inventory=linode.yml```
