from __future__ import annotations

import minidesk
from helpers import call


def _refund(amount, key, confirm=False):
    refund = getattr(minidesk, "refund", None)
    assert refund, "还缺 refund。把 prompts/04 贴给助手。"
    return call(refund, amount, key, confirm=confirm)


def test_refund_always_confirm_required():
    out = _refund(16, "huideng:refund:M-3105:1600", confirm=False)
    assert out["status"] == "confirm_required"
    assert out["executed"] is False


def test_refund_confirm_true_still_does_not_pay():
    out = _refund(360, "huideng:refund:M-3103:36000", confirm=True)
    assert out["executed"] is False
    assert out["status"] == "confirm_required"
    assert out.get("ok") is not True


def test_same_idempotency_key_does_not_pay_twice():
    key = "huideng:refund:M-dup:1600"
    first = _refund(16, key, confirm=True)
    second = _refund(16, key, confirm=True)
    assert first["idempotency_key"] == second["idempotency_key"] == key
    assert first["executed"] is False
    assert second["executed"] is False
    assert second.get("replayed") is True
    assert first["status"] == second["status"] == "confirm_required"
