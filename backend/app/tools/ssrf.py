import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple


ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {80, 443, None}


class SSRFValidationError(Exception):
    pass


def is_ip_private_or_restricted(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        return False


def validate_url_safe(url: str) -> Tuple[bool, str]:
    """Validate a URL against SSRF vulnerabilities and protocol constraints.
    Returns (is_safe, error_message_or_normalized_url).
    """
    if not url or len(url) > 2048:
        return False, "URL is empty or exceeds 2048 characters"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Malformed URL: {e}"

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"Unsupported URL scheme: '{parsed.scheme}'. Only HTTP/HTTPS allowed."

    if parsed.username or parsed.password:
        return False, "Userinfo in URL credentials is forbidden"

    port = parsed.port
    if port is not None and port not in (80, 443):
        return False, f"Non-standard port '{port}' is forbidden"

    hostname = parsed.hostname
    if not hostname:
        return False, "URL must contain a valid hostname"

    # Check literal IP
    if is_ip_private_or_restricted(hostname):
        return False, f"Target IP address '{hostname}' is a restricted/private network target"

    # Resolve hostname to verify destination IP
    try:
        addr_info = socket.getaddrinfo(hostname, port or (443 if parsed.scheme == "https" else 80))
        for item in addr_info:
            ip = item[4][0]
            if is_ip_private_or_restricted(ip):
                return False, f"Hostname '{hostname}' resolves to private/restricted IP: {ip}"
    except socket.gaierror as e:
        return False, f"DNS resolution failed for hostname '{hostname}': {e}"

    # Return safe normalized URL
    clean_url = parsed._replace(fragment="").geturl()
    return True, clean_url
