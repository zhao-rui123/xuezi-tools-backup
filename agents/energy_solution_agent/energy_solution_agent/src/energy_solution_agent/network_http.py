from __future__ import annotations

import json
import os
import ssl
from typing import Any
from urllib.request import (
    ProxyHandler,
    Request,
    build_opener,
    urlopen,
)


DEFAULT_USER_AGENT = "energy-solution-agent/0.1"

# Allow disabling SSL verification for corporate networks with MITM inspection.
# Set ENERGY_AGENT_SSL_NO_VERIFY=1 to skip certificate validation (insecure, use with caution).
_SSL_NO_VERIFY = os.environ.get("ENERGY_AGENT_SSL_NO_VERIFY", "").strip() in {"1", "true", "yes"}


def get_proxy_url(network: dict[str, Any] | None = None) -> str | None:
    network = network or {}
    explicit = network.get("proxy_url") or network.get("https_proxy") or network.get("http_proxy")
    if explicit:
        return str(explicit)
    return os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")


def http_get_json(url: str, user_agent: str = DEFAULT_USER_AGENT, timeout: float = 30.0, proxy_url: str | None = None) -> Any:
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    raw = _http_get_bytes(request, timeout=timeout, proxy_url=proxy_url)
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid JSON response from {url}: {exc}") from exc


def http_get_text(url: str, user_agent: str = DEFAULT_USER_AGENT, timeout: float = 30.0, proxy_url: str | None = None) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": user_agent})
    response = _open_request(request, timeout=timeout, proxy_url=proxy_url)
    with response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        content_type = response.headers.get("Content-Type", "")
    return raw.decode(charset, errors="ignore"), content_type


def _http_get_bytes(request: Request, timeout: float, proxy_url: str | None) -> bytes:
    response = _open_request(request, timeout=timeout, proxy_url=proxy_url)
    with response:
        return response.read()


def _open_request(request: Request, timeout: float, proxy_url: str | None):
    context = None
    if _SSL_NO_VERIFY:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    if proxy_url:
        opener = build_opener(ProxyHandler({"http": proxy_url, "https": proxy_url}))
        return opener.open(request, timeout=timeout, context=context)
    return urlopen(request, timeout=timeout, context=context)
