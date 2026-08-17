#!/usr/bin/env python3
"""Print a concise Mercury human-copy readability audit (S4.1).

Usage:
  .\\.venv\\Scripts\\python.exe scripts\\audit_mercury_human_copy.py
  .\\.venv\\Scripts\\python.exe scripts\\audit_mercury_human_copy.py --all
  .\\.venv\\Scripts\\python.exe scripts\\audit_mercury_human_copy.py --reason technical_scaffolding
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.mercury_human_copy_audit import (
    ALL_AUDIT_REASONS,
    format_human_copy_audit_report,
    run_human_copy_audit,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic Mercury human-copy readability audit."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include every candidate ID (not only top still-raw).",
    )
    parser.add_argument(
        "--reason",
        choices=list(ALL_AUDIT_REASONS),
        default=None,
        help="Filter still-raw candidates to one audit reason.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="How many still-raw candidates to print (default 20).",
    )
    args = parser.parse_args(argv)

    report = run_human_copy_audit()
    text = format_human_copy_audit_report(
        report,
        top_n=max(0, args.top),
        reason_filter=args.reason,
        show_all=args.all,
    )
    # Windows consoles may be non-UTF8; avoid hard crash on Cyrillic samples.
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write((text + "\n").encode(sys.stdout.encoding or "utf-8", errors="replace"))
        stream.flush()
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
