from __future__ import annotations

from typing import Any


class CaseStore:
    def __init__(self) -> None:
        self.by_case: dict[str, dict[str, Any]] = {}
        self.by_key: dict[str, str] = {}

    def remember(self, case_id: str, result: dict[str, Any]) -> dict[str, Any]:
        key = result.get("idempotency_key") or ""
        if key and key in self.by_key:
            prev = dict(self.by_case[self.by_key[key]])
            prev["replayed"] = True
            prev.setdefault("audit", []).append(
                {"role": "store", "action": "idempotent_replay", "detail": f"不二次打款 {key}"}
            )
            return prev
        if case_id in self.by_case:
            prev = dict(self.by_case[case_id])
            prev["replayed"] = True
            return prev
        stored = dict(result)
        stored["replayed"] = False
        self.by_case[case_id] = stored
        if key:
            self.by_key[key] = case_id
        return stored
