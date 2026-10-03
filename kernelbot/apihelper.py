"""Low-level HTTP layer for the KernelGram Bot API.

Mirrors the public surface of `telebot.apihelper`.
"""

import json
import socket
import requests
import logging

from .version import __version__

logger = logging.getLogger("kernelbot")

# --- KernelGram endpoints (hardcoded) ---
API_HOST = "https://api.kernelgram.club"
API_URL = API_HOST + "/bot{0}/{1}"
FILE_URL = API_HOST + "/file/bot{0}/{1}"

# --- Behaviour flags ---
CONNECT_TIMEOUT = 3.5
READ_TIMEOUT = 999
SESSION_TIME_TO_LIVE = None
RETRY_ON_ERROR = False
MAX_RETRIES = 3

FORCE_IPV4 = True
CUSTOM_REQUEST_SENDER = None
proxy = None

# Поля, которые при multipart-запросе KernelGram ожидает как JSON-строку.
_JSON_FIELDS = ("reply_markup",)


def _build_session():
    session = requests.Session()
    if FORCE_IPV4:
        from requests.adapters import HTTPAdapter
        from urllib3.util import connection

        def _ipv4_only(address, *args, **kwargs):
            host, port = address
            infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
            family, socktype, proto, _canon, sockaddr = infos[0]
            sock = socket.socket(family, socktype, proto)
            try:
                sock.connect(sockaddr)
            except Exception:
                sock.close()
                raise
            return sock

        connection.create_connection = _ipv4_only

    adapter = HTTPAdapter(max_retries=MAX_RETRIES)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_session = None


def _get_session():
    global _session
    if _session is None:
        _session = _build_session()
    return _session


def _serialize_for_multipart(params):
    """Привести dict-параметры к JSON-строкам для multipart-запроса."""
    out = dict(params)
    for key in _JSON_FIELDS:
        if key in out and not isinstance(out[key], str):
            out[key] = json.dumps(out[key], ensure_ascii=False)
    return out


def _make_request(token, method_name, method="get", params=None, files=None, **kwargs):
    url = API_URL.format(token, method_name)
    params = params or {}
    timeout = kwargs.pop("timeout", READ_TIMEOUT + CONNECT_TIMEOUT)

    if CUSTOM_REQUEST_SENDER is not None:
        return CUSTOM_REQUEST_SENDER(method=method, url=url, params=params, files=files, timeout=timeout)

    session = _get_session()
    proxies = proxy

    try:
        if method == "get":
            resp = session.get(url, params=params, timeout=timeout, proxies=proxies, **kwargs)
        elif method == "post":
            if files:
                data = _serialize_for_multipart(params)
                resp = session.post(url, data=data, files=files, timeout=timeout, proxies=proxies, **kwargs)
            else:
                resp = session.post(url, json=params, timeout=timeout, proxies=proxies, **kwargs)
        else:
            raise ValueError("Unsupported HTTP method: %r" % method)
    except requests.exceptions.RequestException as e:
        logger.error("Request to %s failed: %s", url, e)
        raise

    try:
        result = resp.json()
    except ValueError:
        resp.raise_for_status()
        raise

    if not result.get("ok"):
        description = result.get("description", "Unknown error")
        logger.error("KernelGram API error in %s: %s", method_name, description)
        raise ApiTelegramException(method_name, result, result)

    return result


class ApiTelegramException(Exception):
    """Raised when the KernelGram Bot API returns ok=false."""

    def __init__(self, function_name, result, payload):
        super().__init__(
            "KernelGram API error in %s: %s" % (function_name, result.get("description"))
        )
        self.function_name = function_name
        self.result = result
        self.error_code = result.get("error_code")
        self.description = result.get("description")
        self.payload = payload
