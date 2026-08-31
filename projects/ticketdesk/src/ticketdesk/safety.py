from __future__ import annotations

NEVER_EXECUTE = True
NEVER_PAY = True
NEVER_MUTATE_ORDER = True

DANGEROUS_PATTERNS = (
    "os.system",
    "subprocess",
    "curl | sh",
    "curl|sh",
    "| sh",
    "| bash",
    "rm -rf",
    "eval(",
    "__import__",
    "powershell",
    "refund_api",
    "alipay.trade.refund",
    "wxpay",
)

ABUSE_PATTERNS = (
    "找消协",
    "找律师",
    "投诉工商",
    "曝光你们",
    "死妈",
    "智障",
    "垃圾客服",
    "滚",
    "傻逼",
    "律师函",
)


def looks_dangerous(text: str) -> list[str]:
    blob = (text or "").lower()
    hits = [p for p in DANGEROUS_PATTERNS if p.lower() in blob]
    return hits


def looks_abuse(text: str) -> list[str]:
    blob = text or ""
    return [p for p in ABUSE_PATTERNS if p in blob]
