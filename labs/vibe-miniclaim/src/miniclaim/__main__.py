"""python -m miniclaim demo [--fixture mute-story]"""

from __future__ import annotations

import sys

from miniclaim import NotBuiltYet, demo


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "demo"
    if cmd != "demo":
        print("用法: python -m miniclaim demo [--fixture mute-story]", file=sys.stderr)
        return 2
    fixture = None
    if "--fixture" in argv:
        i = argv.index("--fixture")
        if i + 1 >= len(argv):
            print("缺少 --fixture 名字", file=sys.stderr)
            return 2
        fixture = argv[i + 1]
    try:
        text = demo(fixture)
    except NotBuiltYet as exc:
        print(exc, file=sys.stderr)
        return 2
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
