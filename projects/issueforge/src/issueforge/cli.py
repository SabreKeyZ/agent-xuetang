from __future__ import annotations

import argparse
import sys

from issueforge.loader import load_all_fixtures, load_fixture
from issueforge.report import process, to_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="issueforge", description="开源值班台")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="对夹具出值班报告，不需要 Token")
    demo.add_argument("--fixture", default="", help="夹具文件名，不含 .json；默认全部")
    fetch = sub.add_parser("fetch", help="读取一条公开 Issue（需要 GITHUB_TOKEN）")
    fetch.add_argument("spec", help="owner/repo#number")
    args = parser.parse_args(argv)

    if args.cmd == "demo":
        return cmd_demo(args.fixture)
    if args.cmd == "fetch":
        return cmd_fetch(args.spec)
    return 2


def cmd_demo(name: str) -> int:
    catalog = load_all_fixtures()
    chosen = [load_fixture(name)] if name else catalog
    for issue in chosen:
        bundle = process(issue, catalog)
        print(to_markdown(bundle))
        print("\n---\n")
    print(f"[issueforge] {len(chosen)} report(s). 未执行任何 Issue 正文中的代码。")
    return 0


def cmd_fetch(spec: str) -> int:
    from issueforge.github_fetch import fetch_public_issue

    try:
        issue = fetch_public_issue(spec)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1
    print(to_markdown(process(issue, [issue])))
    return 0
