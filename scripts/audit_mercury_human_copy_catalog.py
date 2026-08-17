#!/usr/bin/env python3
"""Print Mercury human presentation catalog coverage (S4.3+) / sign queue (S4.6).

Usage:
  .\\.venv\\Scripts\\python.exe scripts\\audit_mercury_human_copy_catalog.py
  .\\.venv\\Scripts\\python.exe scripts\\audit_mercury_human_copy_catalog.py --family sign:Sagittarius
  .\\.venv\\Scripts\\python.exe scripts\\audit_mercury_human_copy_catalog.py --queue signs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.mercury_human_copy_catalog import (
    build_human_copy_catalog,
    build_sign_review_queue,
    format_catalog_summary,
    format_family_detail,
    format_sign_review_queue,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic Mercury human presentation catalog coverage."
    )
    parser.add_argument(
        "--family",
        default=None,
        help="Factor family key, e.g. sign:Sagittarius or aspect:conjunction_Uranus",
    )
    parser.add_argument(
        "--queue",
        choices=("signs",),
        default=None,
        help="Print the Mercury sign human-copy review queue.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="How many incomplete families to list in the summary (default 10).",
    )
    args = parser.parse_args(argv)

    if args.queue and args.family:
        parser.error("Use either --queue or --family, not both.")

    report = build_human_copy_catalog()
    if args.queue == "signs":
        text = format_sign_review_queue(build_sign_review_queue(report))
    elif args.family:
        text = format_family_detail(report, args.family)
    else:
        text = format_catalog_summary(report, top_n=max(0, args.top))

    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write((text + "\n").encode(sys.stdout.encoding or "utf-8", errors="replace"))
        stream.flush()
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
