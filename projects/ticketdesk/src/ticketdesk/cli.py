from __future__ import annotations

import argparse
import json

from ticketdesk.config import has_llm_key, load_dotenv, project_root


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(prog="ticketdesk", description="青匣记客服工单台")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="离线跑脏数据夹具，打印芯片或红条")
    demo.add_argument("--fixture", default="", help="夹具名，不含 .json")
    serve = sub.add_parser("serve", help="打开本地队列页")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    ev = sub.add_parser("eval", help="跑闸门评测")
    ev.add_argument("--set", dest="eval_set", default="")
    args = parser.parse_args(argv)
    if args.cmd == "demo":
        return cmd_demo(args.fixture)
    if args.cmd == "serve":
        return cmd_serve(args.host, args.port)
    if args.cmd == "eval":
        return cmd_eval(args.eval_set)
    return 2


def cmd_demo(name: str) -> int:
    from ticketdesk.agents.supervisor import Supervisor

    root = project_root()
    print(f"[ticketdesk] root={root}")
    print(f"[ticketdesk] llm={'on' if has_llm_key() else 'off (extractive)'}")
    print("[ticketdesk] 演示不打款、不改单、不执行正文命令。")
    sup = Supervisor()
    cases = [sup.process_fixture(name)] if name else sup.demo()["cases"]
    for case in cases:
        ticket = case["ticket"]
        print()
        print(f"===== {ticket['id']}  {ticket['title']}  fixture={ticket.get('fixture_id')} =====")
        print(f"[classifier] {case['classify']['title']}  labels={case['labels']}")
        sim = case["classify"].get("citations") or []
        if sim:
            print("相似夹具: " + ", ".join(sim))
        pol = case["policy"]
        print(f"[policy] {pol['title']}")
        if pol.get("citations"):
            print("引用: " + ", ".join(pol["citations"]))
        if pol.get("refused"):
            print("没有引用，就先不答")
        gate = case["gate"]
        print(f"[gate] {gate['title']}  verdict={gate['verdict']}  next={gate['next_action']}")
        print(f"idempotency_key={case['idempotency_key']}  executed={case['executed']}")
        if case.get("banner"):
            print(f"红条: {case['banner']}")
        if gate.get("draft_reply"):
            print("草稿: " + gate["draft_reply"])
        print(f"payment.status={gate['payment']['status']}")
    print()
    print("[ticketdesk] demo 结束。下一步: python -m ticketdesk serve")
    return 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    from ticketdesk.web import app

    print(f"[ticketdesk] http://{host}:{port}  llm={'on' if has_llm_key() else 'extractive'}")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


def cmd_eval(eval_set: str) -> int:
    from pathlib import Path

    from ticketdesk.agents.supervisor import Supervisor

    path = Path(eval_set) if eval_set else _default_eval()
    cases = json.loads(path.read_text(encoding="utf-8"))
    sup = Supervisor()
    failed = 0
    for case in cases:
        out = sup.process_fixture(case["fixture"])
        ok = True
        if "expect_verdict" in case:
            ok = ok and out["gate"]["verdict"] == case["expect_verdict"]
        if case.get("must_cite"):
            ok = ok and bool(out.get("citations"))
        if case.get("must_refuse_banner"):
            ok = ok and "没有引用" in (out.get("banner") or out["policy"].get("title") or "")
        if case.get("executed_must_be_false"):
            ok = ok and out["executed"] is False
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {case['id']} {case.get('note', '')}")
        if not ok:
            failed += 1
            print("       ", json.dumps({"verdict": out["gate"]["verdict"], "cites": out.get("citations")}, ensure_ascii=False)[:240])
    print(f"[ticketdesk] {len(cases) - failed}/{len(cases)} passed  file={path}")
    return 0 if failed == 0 else 1


def _default_eval() -> "Path":
    from pathlib import Path

    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "evals" / "set8.json"
        if cand.is_file():
            return cand
    raise FileNotFoundError("找不到 evals/set8.json")
