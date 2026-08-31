from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Kind = Literal["bug", "feature", "question"]


@dataclass
class Issue:
    number: int
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
    fixture_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], fixture_id: str = "") -> "Issue":
        return cls(
            number=int(data.get("number") or data.get("id") or 0),
            title=str(data.get("title") or ""),
            body=str(data.get("body") or ""),
            labels=[str(x) for x in data.get("labels") or []],
            fixture_id=fixture_id,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
