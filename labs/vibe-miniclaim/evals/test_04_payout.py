from __future__ import annotations

import miniclaim
from helpers import call


def _payout(amount, key, confirm=False):
    payout = getattr(miniclaim, "payout", None)
    assert payout, "还缺 payout。把 prompts/04 贴给助手。"
    return call(payout, amount, key, confirm=confirm)


def test_payout_always_confirm_required():
    out = _payout(22, "wujin:payout:K-4202:2200", confirm=False)
    assert out["status"] == "confirm_required"
    assert out["executed"] is False


def test_payout_confirm_true_still_does_not_pay():
    out = _payout(280, "wujin:payout:K-4203:28000", confirm=True)
    assert out["executed"] is False
    assert out["status"] == "confirm_required"
    assert out.get("ok") is not True


def test_same_idempotency_key_does_not_pay_twice():
    key = "wujin:payout:K-dup:2200"
    first = _payout(22, key, confirm=True)
    second = _payout(22, key, confirm=True)
    assert first["idempotency_key"] == second["idempotency_key"] == key
    assert first["executed"] is False
    assert second["executed"] is False
    assert second.get("replayed") is True
    assert first["status"] == second["status"] == "confirm_required"
