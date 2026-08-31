from __future__ import annotations

import argparse
import sys
from pathlib import Path

from issueforge.loader import load_all_fixtures, load_fixture
from issueforge.report import process, to_markdown, write_html

DEFAULT_HTML = Path("demo-out/duty-report.html")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="issueforge", description="开源值班台")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="对夹具出值班报告，不需要 Token")
    demo.add_argument("--fixture", default="", help="夹具文件名，不含 .json；默认全部")
    demo.add_argument("--out", default=str(DEFAULT_HTML), help="同时写出 HTML 报告的路径")
    demo.add_argument("--no-html", action="store_true", help="只打印 Markdown，不写 HTML")
    board = sub.add_parser("board", help="写出自包含的 HTML 值班报告（30 秒演示）")
    board.add_argument("--fixture", default="", help="夹具文件名，不含 .json；默认全部")
    board.add_argument("--out", default=str(DEFAULT_HTML))
    fetch = sub.add_parser("fetch", help="读取一条公开 Issue（需要 GITHUB_TOKEN）")
    fetch.add_argument("spec", help="owner/repo#number")
    args = parser.parse_args(argv)

    if args.cmd == "demo":
        return cmd_demo(args.fixture, html_out=None if args.no_html else args.out)
    if args.cmd == "board":
        return cmd_board(args.fixture, args.out)
    if args.cmd == "fetch":
        return cmd_fetch(args.spec)
    return 2


def _bundles(name: str) -> list[dict]:
    catalog = load_all_fixtures()
    chosen = [load_fixture(name)] if name else catalog
    return [process(issue, catalog) for issue in chosen]


def cmd_demo(name: str, html_out: str | None) -> int:
    bundles = _bundles(name)
    for bundle in bundles:
        print(to_markdown(bundle))
        print("\n---\n")
    if html_out:
        path = write_html(bundles, Path(html_out))
        print(f"[issueforge] html={path}")
    print(f"[issueforge] {len(bundles)} report(s). 未执行任何 Issue 正文中的代码。")
    return 0


def cmd_board(name: str, html_out: str) -> int:
    bundles = _bundles(name)
    path = write_html(bundles, Path(html_out))
    print(f"[issueforge] board → {path}  ({len(bundles)} issue(s))")
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
