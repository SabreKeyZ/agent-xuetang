from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from askhall.config import docs_root, has_llm_key, load_dotenv


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(prog="askhall", description="问学堂")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="离线走一遍规划 / 讲解 / 出题 / 空答拒绝")
    serve = sub.add_parser("serve", help="打开本地页面")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    ev = sub.add_parser("eval", help="跑十行评测")
    ev.add_argument("--set", dest="eval_set", default="")

    args = parser.parse_args(argv)
    if args.cmd == "demo":
        return cmd_demo()
    if args.cmd == "serve":
        return cmd_serve(args.host, args.port)
    if args.cmd == "eval":
        return cmd_eval(args.eval_set)
    return 2


def cmd_demo() -> int:
    from askhall.agents.supervisor import Supervisor

    root = docs_root()
    print(f"[askhall] docs={root}")
    print(f"[askhall] llm={'on' if has_llm_key() else 'off (extractive)'}")
    result = Supervisor().demo()
    for i, block in enumerate(result["script"], start=1):
        print()
        print(f"===== 第 {i} 幕  问：{block.get('ask', '')!r}  路由：{block.get('route')} =====")
        for turn in block.get("turns", []):
            print(f"[{turn.get('role')}] {turn.get('title')}")
            print(turn.get("body", ""))
            cites = turn.get("citations") or []
            if cites:
                print("引用: " + ", ".join(cites))
            if turn.get("refused"):
                print("（考试官拒绝了空答案）")
    print()
    print("[askhall] demo 结束。下一步: python -m askhall serve")
    return 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    from askhall.web import app

    print(f"[askhall] http://{host}:{port}  llm={'on' if has_llm_key() else 'extractive'}")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


def cmd_eval(eval_set: str) -> int:
    from askhall.agents.supervisor import Supervisor
    from askhall.rag import citation_exists

    path = Path(eval_set) if eval_set else _default_eval_path()
    cases = json.loads(path.read_text(encoding="utf-8"))
    sup = Supervisor()
    failed = 0
    for case in cases:
        kind = case.get("kind", "ask")
        if kind == "empty_grade":
            from askhall.agents.examiner import grade_answer

            out = grade_answer("", case.get("answer_key", "x"), case.get("question", ""))
            ok = out.get("refused") is True
        elif kind == "route":
            dest = sup.route(case["query"])
            ok = dest == case["expect_route"]
            out = {"route": dest}
        elif kind == "citation":
            result = sup.handle(case["query"])
            cites = []
            for t in result["turns"]:
                cites.extend(t.get("citations") or [])
            ok = any(citation_exists(c) for c in cites) if case.get("must_cite") else True
            if case.get("must_cite") and not cites:
                ok = False
            out = {"citations": cites}
        else:
            result = sup.handle(case["query"])
            blob = json.dumps(result, ensure_ascii=False)
            needles = case.get("expect_contains", [])
            if isinstance(needles, str):
                needles = [needles]
            ok = all(n in blob for n in needles)
            out = result
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {case['id']} {case.get('note', '')}")
        if not ok:
            failed += 1
            print("       ", json.dumps(out, ensure_ascii=False)[:240])
    print(f"[askhall] {len(cases) - failed}/{len(cases)} passed  file={path}")
    return 0 if failed == 0 else 1


def _default_eval_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "evals" / "set10.json"
        if cand.is_file():
            return cand
    raise FileNotFoundError("找不到 evals/set10.json")
