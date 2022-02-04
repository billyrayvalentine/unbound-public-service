# Helper functions for DNS / DoT testing
import socket
import ssl
from datetime import datetime, timedelta
import dns.resolver
import dns.message
import dns.name


def host_has_valid_tls_cert(fqdn, port):
    """Return boolean if host has valid tls cert"""
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_socket = ssl_context.wrap_socket(
        socket.socket(socket.AF_INET), server_hostname=fqdn
    )

    try:
        ssl_socket.connect((fqdn, port))
    except ssl.SSLError as e:
        return False
    except:
        raise e
    finally:
        ssl_socket.close()

    return True


def host_tls_cert_length_days(fqdn, port):
    """Return the length of days the cert is valid for"""
    # WARN Zero error handling
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_socket = ssl_context.wrap_socket(
        socket.socket(socket.AF_INET), server_hostname=fqdn
    )

    ssl_socket.connect((fqdn, port))
    cert = ssl_socket.getpeercert()

    cert_expiry = ssl.cert_time_to_seconds(cert["notAfter"])
    delta = datetime.fromtimestamp(cert_expiry) - datetime.now()
    ssl_socket.close()

    return delta.days


def get_a_record(query):
    """Return a single A record for a query (do a DNS lookup) using this host resolver"""
    answer = dns.resolver.resolve(query)
    return answer[0].address


def host_choasnet_record(query, fqdn, port):
    """Return a the value of a chaos net TXT record as a string or None"""
    qname = dns.name.from_text(query)
    query = dns.message.make_query(
        qname, dns.rdatatype.TXT, rdclass=dns.rdataclass.CHAOS
    )
    response = dns.query.tls(query, get_a_record(fqdn))
    answer = response.get_rrset(
        dns.message.ANSWER, qname, dns.rdataclass.CHAOS, dns.rdatatype.TXT
    )
    if answer != None:
        return answer.to_text()
    else:
        return None
