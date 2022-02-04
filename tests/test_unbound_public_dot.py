import testinfra
import dns_testing

# Tests for working Unbound server

# Let's encrypt / Certbot
def test_certbot_installed(host):
    assert True == host.package("python3-certbot").is_installed


# The Certbot renew system timer will fail without this file and thus break
# the service as the cert will not renew
def test_certbot_sysconfig_present(host):
    assert True == host.file("/etc/sysconfig/certbot").exists


def test_certbot_renew_timer_enabled(host):
    # systemctl will still exit 0 even if the pattern does not match
    # so catch an empty JSON list to match failure
    assert "[]" != host.check_output(
        "systemctl list-timers certbot-renew.timer -o json --no-pager"
    )


# Unbound
def test_unbound_service_running(host):
    assert True == host.service("unbound").is_running


def test_unbound_service_enabled(host):
    assert True == host.service("unbound").is_enabled


def test_unbound_control_keys_secure(host):
    assert host.file("/etc/unbound/unbound_control.key").size > 0
    assert 0o640 == host.file("/etc/unbound/unbound_control.key").mode
    assert "root" == host.file("/etc/unbound/unbound_control.key").user
    assert "unbound-control" == host.file("/etc/unbound/unbound_control.key").group

    assert host.file("/etc/unbound/unbound_control.pem").size > 0
    assert 0o640 == host.file("/etc/unbound/unbound_control.pem").mode
    assert "root" == host.file("/etc/unbound/unbound_control.pem").user
    assert "unbound-control" == host.file("/etc/unbound/unbound_control.key").group

    assert host.file("/etc/unbound/unbound_server.pem").size > 0
    assert 0o640 == host.file("/etc/unbound/unbound_server.pem").mode
    assert "root" == host.file("/etc/unbound/unbound_server.pem").user
    assert "unbound-control" == host.file("/etc/unbound/unbound_server.pem").group

    assert host.file("/etc/unbound/unbound_server.key").size > 0
    assert 0o600 == host.file("/etc/unbound/unbound_server.key").mode
    assert "root" == host.file("/etc/unbound/unbound_server.key").user
    assert "unbound" == host.file("/etc/unbound/unbound_server.key").group


def test_hide_identity(host):
    """Test if the hide-identify setting is yes (returns no answer)"""
    this_host = host.backend.host
    assert None == dns_testing.host_choasnet_record("id.server", this_host, 843)
    assert None == dns_testing.host_choasnet_record("hostname.bind", this_host, 843)


def test_hide_version(host):
    """Test if the hide-version setting is yes (returns no answer)"""
    this_host = host.backend.host
    assert None == dns_testing.host_choasnet_record("version.server", this_host, 843)
    assert None == dns_testing.host_choasnet_record("version.bind", this_host, 843)


def test_hide_trust_anchor(host):
    """Test if the hide-trustanchor setting is yes (returns an answer)"""
    this_host = host.backend.host
    assert None != dns_testing.host_choasnet_record(
        "trustanchor.unbound", this_host, 843
    )


# TLS
def test_valid_tls_cert(host):
    # Get the name of the current host
    this_host = host.backend.host
    assert True == dns_testing.host_has_valid_tls_cert(this_host, 853)


def test_tls_cert_older_than_days(host):
    this_host = host.backend.host
    assert dns_testing.host_tls_cert_length_days(this_host, 853) > 20, "Cert too old"
