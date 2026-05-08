"""Проверка подписи уведомлений ЮMoney (параметр sign, HMAC-SHA256 по документации ЮMoney)."""

from __future__ import annotations

import hashlib
import hmac
from urllib.parse import quote

from config import settings


def _secret_key_bytes() -> bytes:
    raw = settings.yoomoney_notification_secret.strip()
    if not raw:
        return b""
    if settings.yoomoney_secret_is_hex:
        return bytes.fromhex(raw)
    return raw.encode("utf-8")


def canonical_string(params: dict[str, str]) -> str:
    """Все параметры кроме sign, значения закодировать по RFC 3986, отсортировать ключи алфавитно."""
    without_sign = {k: str(v) for k, v in params.items() if k != "sign"}
    pairs: list[str] = []
    for key in sorted(without_sign.keys()):
        encoded_value = quote(str(without_sign[key]), safe="", encoding="utf-8")
        pairs.append(f"{key}={encoded_value}")
    return "&".join(pairs)


def compute_sign_hmac(params_with_sign_field: dict[str, str]) -> str:
    key = _secret_key_bytes()
    msg = canonical_string(params_with_sign_field).encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def notification_sign_ok(params_with_sign_field: dict[str, str]) -> bool:
    received = params_with_sign_field.get("sign")
    if not received or not settings.yoomoney_notification_secret:
        return False
    expected = compute_sign_hmac(params_with_sign_field)
    return hmac.compare_digest(expected.casefold(), str(received).casefold())
