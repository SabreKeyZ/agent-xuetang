from __future__ import annotations

import os
from pathlib import Path


def load_dotenv() -> None:
    for candidate in (Path.cwd() / ".env", _guess_course_root() / ".env"):
        if not candidate.is_file():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))
        break


def _guess_course_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "weeks").is_dir():
            return parent
    return Path.cwd()


def project_root() -> Path:
    env = os.environ.get("CLAIMDESK_ROOT", "").strip()
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser().resolve())
    here = Path(__file__).resolve()
    candidates.extend(
        [
            here.parents[2] if len(here.parents) >= 2 else Path.cwd(),
            Path("/app/projects/claimdesk"),
            Path("/app"),
            Path.cwd(),
        ]
    )
    seen: set[Path] = set()
    for cand in candidates:
        if cand in seen:
            continue
        seen.add(cand)
        if (cand / "docs" / "policy").is_dir() and (cand / "fixtures" / "claims").is_dir():
            return cand
    raise FileNotFoundError("找不到理赔台项目根。设置 CLAIMDESK_ROOT。")


def has_llm_key() -> bool:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    return bool(key) and key.lower() not in {"", "ollama-disabled"}


def llm_settings() -> tuple[str, str, str]:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    base = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "deepseek-chat")
    return key, base, model
