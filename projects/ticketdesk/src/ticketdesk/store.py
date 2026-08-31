from __future__ import annotations

from typing import Any


class CaseStore:
    """进程内案件账本：同一 idempotency_key 不得二次补偿。"""

    def __init__(self) -> None:
        self.by_case: dict[str, dict[str, Any]] = {}
        self.by_key: dict[str, str] = {}

    def remember(self, case_id: str, result: dict[str, Any]) -> dict[str, Any]:
        key = result.get("idempotency_key") or ""
        if key and key in self.by_key:
            previous = self.by_case[self.by_key[key]]
            replay = dict(previous)
            replay["replayed"] = True
            replay["audit"] = list(previous.get("audit") or []) + [
                {
                    "role": "store",
                    "action": "idempotent_replay",
                    "detail": f"同一 idempotency_key 已处理，不二次补偿：{key}",
                }
            ]
            return replay
        if case_id in self.by_case:
            previous = self.by_case[case_id]
            replay = dict(previous)
            replay["replayed"] = True
            replay["audit"] = list(previous.get("audit") or []) + [
                {
                    "role": "store",
                    "action": "idempotent_replay",
                    "detail": f"同一案件已出过草稿：{case_id}",
                }
            ]
            return replay
        stored = dict(result)
        stored["replayed"] = False
        self.by_case[case_id] = stored
        if key:
            self.by_key[key] = case_id
        return stored
