"""Генерация ссылки ЮMoney QuickPay (форма shop)."""

from __future__ import annotations

from decimal import Decimal
from urllib.parse import urlencode


def quickpay_confirm_url(
    *,
    receiver: str,
    label: str,
    sum_rub: Decimal | float,
    targets: str,
    quickpay_form: str = "shop",
) -> str:
    amt = Decimal(str(sum_rub))
    q = {
        "receiver": receiver.strip(),
        "quickpay-form": quickpay_form,
        "targets": targets,
        "sum": f"{amt:.2f}",
        "label": label,
        "need-fio": "false",
        "need-email": "false",
        "need-phone": "false",
        "need-address": "false",
    }
    return "https://yoomoney.ru/quickpay/confirm.xml?" + urlencode(q, encoding="utf-8")
