#!/usr/bin/env python3
"""Prepare provider-neutral JSONL jobs for semantic sense reconstruction.

This command never calls a model. It makes each candidate and its constraints
auditable before a provider-specific batch submission is chosen.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SYSTEM_INSTRUCTIONS = """You are restructuring ECDICT data into a modern English learner's dictionary.
Return JSON only, matching the supplied schema. Work from English meaning, not from punctuation in
the Chinese translation list. Merge Chinese near-synonyms only when they express the same English
sense; keep unrelated meanings separate. Order senses by common learner value, then exam value, then
specialist value. Write original, simple, one-sentence English definitions; never quote or imitate
Oxford, Cambridge, Collins, or another commercial dictionary. Use Chinese semicolons between distinct
glosses. Keep at most one original bilingual example for the whole entry, and omit it for low-value
specialist words. Do not invent frequency, exam tags, morphology, or facts absent from the input."""


def load_rules(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_priority(entry: dict[str, Any], rules: dict[str, Any]) -> bool:
    priority = rules["priority"]
    frequency = entry.get("frequency") or {}
    return bool(
        (priority["include_oxford_3000"] and frequency.get("oxford_3000"))
        or (frequency.get("collins", 0) >= priority["minimum_collins_stars"])
        or (isinstance(frequency.get("bnc"), int) and frequency["bnc"] <= priority["bnc_core_max"])
        or (isinstance(frequency.get("coca"), int) and frequency["coca"] <= priority["coca_core_max"])
        or (priority["include_exam_tagged"] and bool(entry.get("exam_tags")))
    )


def build_request(entry: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    return {
        "custom_id": entry["word"],
        "model_input": {
            "instructions": SYSTEM_INSTRUCTIONS,
            "raw_entry": entry,
            "rules": rules,
            "required_output": "semantic_cleanup/schema.json",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="标准化后的 ECDICT JSONL")
    parser.add_argument("output", type=Path, help="待提交给模型的 JSONL")
    parser.add_argument("--rules", type=Path, default=Path(__file__).with_name("word_rules.json"))
    parser.add_argument("--all", action="store_true", help="不只选择高学习价值词条")
    args = parser.parse_args()
    rules = load_rules(args.rules)
    count = 0
    with args.input.open(encoding="utf-8") as source, args.output.open("w", encoding="utf-8") as destination:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            entry = json.loads(line)
            if not entry.get("word"):
                raise ValueError(f"第 {line_number} 行缺少 word")
            if args.all or is_priority(entry, rules):
                destination.write(json.dumps(build_request(entry, rules), ensure_ascii=False) + "\n")
                count += 1
    print(f"prepared {count} semantic requests")


if __name__ == "__main__":
    main()
