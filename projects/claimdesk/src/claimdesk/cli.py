from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from claimdesk.config import has_llm_key, load_dotenv, project_root


def _apply_import_flags(csv_path: str = "", json_path: str = "") -> None:
    if csv_path:
        os.environ["CLAIMDESK_IMPORT_CSV"] = csv_path
    if json_path:
        os.environ["CLAIMDESK_IMPORT_JSON"] = json_path


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(prog="claimdesk", description="青途保理赔初审台")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="离线跑案件夹具")
    demo.add_argument("--fixture", default="")
    demo.add_argument("--csv", default="", help="可选：导入 Claim CSV，未设则走夹具")
    demo.add_argument("--json", dest="import_json", default="", help="可选：导入 JSON 文件或目录")
    serve = sub.add_parser("serve", help="打开支付表 / 卷宗")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8001)
    serve.add_argument("--csv", default="", help="可选：导入 Claim CSV")
    serve.add_argument("--json", dest="import_json", default="", help="可选：导入 JSON 文件或目录")
    ev = sub.add_parser("eval")
    ev.add_argument("--set", dest="eval_set", default="")
    args = parser.parse_args(argv)
    if args.cmd == "demo":
        _apply_import_flags(args.csv, args.import_json)
        return cmd_demo(args.fixture)
    if args.cmd == "serve":
        _apply_import_flags(args.csv, args.import_json)
        return cmd_serve(args.host, args.port)
    if args.cmd == "eval":
        return cmd_eval(args.eval_set)
    return 2


def cmd_demo(name: str) -> int:
    from claimdesk.agents.supervisor import Supervisor

    print(f"[claimdesk] root={project_root()}")
    print(f"[claimdesk] llm={'on' if has_llm_key() else 'off (extractive)'}")
    print("[claimdesk] 演示不打款。")
    sup = Supervisor()
    cases = [sup.process_fixture(name)] if name else sup.demo()["cases"]
    for case in cases:
        c = case["claim"]
        print()
        print(f"===== {c['id']}  {c['fixture_id']}  ¥{c['amount_yuan']} =====")
        print(f"[docs] {case['docs']['title']} missing={case['docs']['missing']}")
        print(f"[clause] {case['clause']['title']}")
        if case["citations"]:
            print("引用: " + ", ".join(case["citations"]))
        if case["clause"].get("refused"):
            print("没有引用，就先不答")
        d = case["decision"]
        print(f"[adjudicator] {d['recommendation']}  {d['title']}")
        print(f"状态: {d.get('case_status') or case.get('case_status')}")
        math = d.get("settlement") or case.get("settlement") or {}
        if math.get("formula"):
            print(f"试算: {math['formula']}")
        if case.get("banner"):
            print("红条: " + case["banner"])
        if d.get("decision_letter"):
            print("决定书: " + d["decision_letter"])
        print(f"idempotency_key={case['idempotency_key']} executed={case['executed']}")
    print()
    print("[claimdesk] demo 结束。下一步: python -m claimdesk serve")
    return 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    from claimdesk.web import app

    print(f"[claimdesk] http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


def cmd_eval(eval_set: str) -> int:
    from claimdesk.agents.supervisor import Supervisor

    path = Path(eval_set) if eval_set else _default()
    cases = json.loads(path.read_text(encoding="utf-8"))
    sup = Supervisor()
    failed = 0
    for case in cases:
        out = sup.process_fixture(case["fixture"])
        ok = True
        if "expect_rec" in case:
            ok = ok and out["decision"]["recommendation"] == case["expect_rec"]
        if case.get("must_cite"):
            ok = ok and bool(out["citations"])
        if case.get("executed_must_be_false"):
            ok = ok and out["executed"] is False
        print(f"[{'PASS' if ok else 'FAIL'}] {case['id']} {case.get('note','')}")
        failed += 0 if ok else 1
    print(f"[claimdesk] {len(cases) - failed}/{len(cases)} passed")
    return 0 if failed == 0 else 1


def _default() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "evals" / "set8.json"
        if cand.is_file():
            return cand
    raise FileNotFoundError("evals/set8.json")
