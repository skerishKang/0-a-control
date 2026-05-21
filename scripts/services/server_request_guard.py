from __future__ import annotations

import ipaddress
import os
from urllib.parse import urlparse

ALLOW_NONLOCAL_MUTATIONS_ENV = "CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS"
ALLOW_NONLOCAL_READS_ENV = "CONTROL_TOWER_ALLOW_NONLOCAL_READS"
TRUTHY_VALUES = {"1", "true", "yes", "on"}

PUBLIC_GET_PATHS = frozenset({"/api/health"})


def env_allows_nonlocal_mutations() -> bool:
    return os.getenv(ALLOW_NONLOCAL_MUTATIONS_ENV, "").strip().lower() in TRUTHY_VALUES


def env_allows_nonlocal_reads() -> bool:
    return os.getenv(ALLOW_NONLOCAL_READS_ENV, "").strip().lower() in TRUTHY_VALUES


def extract_host(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return ""

    if "://" in raw:
        return (urlparse(raw).hostname or "").strip("[]").rstrip(".")

    if raw.startswith("[") and "]" in raw:
        return raw[1:raw.index("]")].rstrip(".")

    if raw.count(":") == 1:
        raw = raw.split(":", 1)[0]

    return raw.strip("[]").rstrip(".")


def is_loopback_host(value: str | None) -> bool:
    host = extract_host(value)
    if not host:
        return False
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def local_header_allowed(value: str | None) -> bool:
    if not value:
        return True
    return is_loopback_host(value)


def mutation_request_allowed(handler) -> bool:
    """Return whether a POST/PATCH request is allowed to mutate local state.

    The dashboard is a local operations tool. By default, mutation routes accept
    only loopback clients with local Host/Origin headers. Non-local operation
    requires an explicit environment override.
    """
    if env_allows_nonlocal_mutations():
        return True

    client_address = getattr(handler, "client_address", None) or ("",)
    client_host = client_address[0] if client_address else ""
    if not is_loopback_host(client_host):
        return False

    headers = getattr(handler, "headers", None)
    host = headers.get("Host", "") if headers is not None else ""
    origin = headers.get("Origin", "") if headers is not None else ""

    return local_header_allowed(host) and local_header_allowed(origin)


def mutation_rejection_payload() -> dict[str, str]:
    return {"error": "mutation requests are restricted to local clients"}


def read_request_allowed(handler, path: str) -> bool:
    """Return whether a GET request is allowed to read local operations data.

    /api/health is intentionally public-safe for smoke tests. Other API GET
    endpoints require loopback client, local Host/Origin headers, or an explicit
    environment override.
    """
    if path in PUBLIC_GET_PATHS:
        return True

    if env_allows_nonlocal_reads():
        return True

    client_address = getattr(handler, "client_address", None) or ("",)
    client_host = client_address[0] if client_address else ""
    if not is_loopback_host(client_host):
        return False

    headers = getattr(handler, "headers", None)
    host = headers.get("Host", "") if headers is not None else ""
    origin = headers.get("Origin", "") if headers is not None else ""

    return local_header_allowed(host) and local_header_allowed(origin)


def read_rejection_payload() -> dict[str, str]:
    return {"error": "read requests are restricted to local clients"}
