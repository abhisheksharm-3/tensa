import ipaddress
from unittest.mock import patch

import pytest

from src.core.url_safety import UnsafeURLError, validate_public_url


def _fake_resolver(ip: str):
    addr = ipaddress.ip_address(ip)

    def _resolve(host: str):
        return [addr]

    return _resolve


def test_public_url_passes():
    with patch("src.core.url_safety._resolve_addresses", _fake_resolver("93.184.216.34")):
        assert validate_public_url("https://example.com/video") == "https://example.com/video"


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/x",
        "file:///etc/passwd",
        "gopher://example.com",
    ],
)
def test_rejects_non_http_schemes(url):
    with pytest.raises(UnsafeURLError):
        validate_public_url(url)


def test_rejects_missing_host():
    with pytest.raises(UnsafeURLError):
        validate_public_url("https://")


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",       # loopback
        "10.0.0.5",        # private
        "192.168.1.10",    # private
        "172.16.5.4",      # private
        "169.254.169.254", # link-local / cloud metadata
        "0.0.0.0",         # unspecified
        "::1",             # ipv6 loopback
        "fd00::1",         # ipv6 ULA (private)
    ],
)
def test_rejects_internal_addresses(ip):
    with patch("src.core.url_safety._resolve_addresses", _fake_resolver(ip)):
        with pytest.raises(UnsafeURLError):
            validate_public_url("https://evil.internal/")


def test_rejects_ipv4_mapped_ipv6_loopback():
    with patch("src.core.url_safety._resolve_addresses", _fake_resolver("::ffff:127.0.0.1")):
        with pytest.raises(UnsafeURLError):
            validate_public_url("https://evil.internal/")
