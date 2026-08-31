from __future__ import annotations

import os
from pathlib import Path


def load_dotenv() -> None:
    for candidate in (Path.cwd() / ".env", _guess_root() / ".env"):
        if not candidate.is_file():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))
        break


def _guess_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "weeks").is_dir():
            return parent
    return Path.cwd()


def docs_root() -> Path:
    env = os.environ.get("ASKHALL_DOCS", "").strip()
    candidates: list[Path] = []
    if env:
        p = Path(env).expanduser().resolve()
        candidates.extend([p, p.parent])
    candidates.extend(
        [
            _guess_root(),
            Path("/app"),
            Path.cwd(),
            Path(__file__).resolve().parents[4] if len(Path(__file__).resolve().parents) >= 4 else Path.cwd(),
        ]
    )
    seen: set[Path] = set()
    for cand in candidates:
        if cand in seen:
            continue
        seen.add(cand)
        if (cand / "docs" / "weeks").is_dir():
            return cand
        if cand.name == "docs" and (cand / "weeks").is_dir():
            return cand.parent
    raise FileNotFoundError(
        "找不到教材目录 docs/weeks。请在仓库根运行，或设置 ASKHALL_DOCS。"
    )


def has_llm_key() -> bool:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    return bool(key) and key.lower() not in {"", "ollama-disabled"}


def llm_settings() -> tuple[str, str, str]:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    base = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "deepseek-chat")
    return key, base, model
