import socket
import ssl
import requests
import smtplib
from datetime import datetime

ENDPOINTS = [
    "https://google.com",
    "https://github.com",
    "https://akamai.com",
    "https://example.com"
]

def check_dns(host):
    try:
        socket.gethostbyname(host)
        return True, "DNS OK"
    except Exception as e:
        return False, f"DNS Fail: {e}"

def check_http(url):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200, f"HTTP {r.status_code}"
    except Exception as e:
        return False, f"HTTP Fail: {e}"

def check_tls_expiry(host):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_context(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, 443))
            cert = s.getpeercert()
            expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (expiry - datetime.now()).days
            return days_left > 30, f"TLS expires in {days_left} days"
    except Exception as e:
        return False, f"TLS Check Fail: {e}"

if __name__ == "__main__":
    for url in ENDPOINTS:
        host = url.replace("https://","").replace("http://","").split("/")[0]
        dns_ok, dns_msg = check_dns(host)
        http_ok, http_msg = check_http(url)
        tls_ok, tls_msg = check_tls_expiry(host)
        status = "PASS" if all([dns_ok, http_ok, tls_ok]) else "FAIL"
        print(f"[{status}] {host} | {dns_msg} | {http_msg} | {tls_msg}")
