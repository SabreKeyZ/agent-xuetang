"""第 0 周：一次普通的聊天补全。还不是 Agent。

只用标准库。Key 和 Base URL 从仓库根目录的 .env 读取。
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "docs" / "weeks").is_dir():
            return parent
    return here.parents[1]


def main() -> int:
    root = repo_root()
    env_path = root / ".env"
    env_exists = env_path.is_file()
    load_dotenv(env_path)

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "deepseek-chat")

    if not api_key:
        if not env_exists:
            print("缺少 .env。复制 .env.example 为 .env，再填入 OPENAI_API_KEY。", file=sys.stderr)
        else:
            print(
                "OPENAI_API_KEY 是空的。打开 .env 填入 Key 后再跑。"
                "复制 .env.example 只是建文件，不会自动带钥匙。",
                file=sys.stderr,
            )
        print("只有 Ollama 时：OPENAI_API_KEY=ollama 且 BASE_URL 指向本地。", file=sys.stderr)
        return 2

    url = f"{base}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "用一句话说明：你是一次普通的聊天补全，还不是 Agent。请用中文。",
            }
        ],
        "temperature": 0,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"[fail] HTTP {exc.code} {url}\n{detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"[fail] 网络: {exc.reason}  url={url}", file=sys.stderr)
        print("代理和 SSL 见 docs/faq.md", file=sys.stderr)
        return 1

    try:
        reply = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        print(f"[fail] 返回结构不像 chat completions: {body!r}", file=sys.stderr)
        return 1

    print(f"[ok] model={model}")
    print(f"[ok] reply={reply.strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
