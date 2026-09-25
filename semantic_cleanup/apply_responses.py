#!/usr/bin/env python3
"""Validate model candidates and import only safe entries into SQLite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .store import SemanticStore


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="每行含 word 与 semantic_entry 的 JSONL")
    parser.add_argument("database", type=Path, help="semantic_entries.sqlite 输出路径")
    parser.add_argument("--rejects", type=Path, help="保存未通过校验的候选")
    args = parser.parse_args()
    accepted, rejected = 0, []
    with SemanticStore(args.database, writable=True) as store, args.input.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            candidate = json.loads(line)
            entry = candidate.get("semantic_entry", candidate.get("output", candidate))
            try:
                accepted += store.upsert_many([entry])
            except (TypeError, ValueError) as error:
                rejected.append({"line": line_number, "candidate": candidate, "error": str(error)})
    if args.rejects:
        text = "\n".join(json.dumps(item, ensure_ascii=False) for item in rejected)
        args.rejects.write_text(text + ("\n" if text else ""), encoding="utf-8")
    print(f"accepted {accepted}; rejected {len(rejected)}")


if __name__ == "__main__":
    main()
