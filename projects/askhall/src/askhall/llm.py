from __future__ import annotations

import json
from typing import Any

import httpx

from askhall.config import has_llm_key, llm_settings


def complete(prompt: str, system: str = "", timeout: float = 45.0) -> str | None:
    """打兼容接口。没有 Key 或失败时返回 None，调用方走抽取式。"""
    if not has_llm_key():
        return None
    key, base, model = llm_settings()
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                f"{base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                content=json.dumps(payload),
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001 — 产品要求失败时回退抽取
        return None
