from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

ALLOWED_SCHEMES = frozenset({"http", "https"})

# Cloud metadata endpoints — common SSRF pivot targets. Resolving any of these
# to a private address already blocks them, but link-local 169.254.169.254 is
# the canonical metadata IP across AWS/GCP/Azure, caught by the link-local check.


class UnsafeURLError(ValueError):
    """Raised when a URL is rejected as unsafe to fetch (SSRF guard)."""


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """A resolved address is blocked if it is not a routable public address."""
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or (isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None
            and _is_blocked_ip(ip.ipv4_mapped))
    )


def _resolve_addresses(host: str) -> list[ipaddress._BaseAddress]:
    """Resolve a hostname to all of its IPv4/IPv6 addresses.

    A literal IP returns itself; a name is resolved via getaddrinfo so that DNS
    rebinding to a private range is caught at validation time.
    """
    try:
        return [ipaddress.ip_address(host)]
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise UnsafeURLError(f"Could not resolve host: {host}") from exc
    addresses: list[ipaddress._BaseAddress] = []
    for info in infos:
        sockaddr = info[4]
        try:
            addresses.append(ipaddress.ip_address(sockaddr[0]))
        except ValueError:
            continue
    if not addresses:
        raise UnsafeURLError(f"Could not resolve host: {host}")
    return addresses


def validate_public_url(url: str) -> str:
    """Validate that ``url`` is safe to fetch, guarding against SSRF.

    Rejects non-http(s) schemes and any URL whose host resolves to a private,
    loopback, link-local (incl. cloud metadata 169.254.169.254), multicast,
    reserved, or unspecified address. Returns the URL unchanged when safe.
    """
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise UnsafeURLError("URL scheme must be http or https")
    host = parts.hostname
    if not host:
        raise UnsafeURLError("URL has no host")

    for address in _resolve_addresses(host):
        if _is_blocked_ip(address):
            raise UnsafeURLError("URL resolves to a non-public address")
    return url
