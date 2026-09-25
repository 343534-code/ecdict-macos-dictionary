"""Validate v2 candidates and report review needs; never approve or import them."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

from .raw_snapshot import verify_snapshot
from .schema import SemanticValidationError


SCHEMA = json.loads(Path(__file__).with_name("schema-v2.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
WORD = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")


def _canonical(text: str) -> str:
    return " ".join(text.split()).casefold().rstrip(".")


def validate_candidate(payload: dict) -> dict:
    """Strict structural checks only. Success is not semantic or factual approval."""
    # Reject NaN/Infinity, including values accepted by permissive JSON decoders.
    try:
        json.dumps(payload, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SemanticValidationError("candidate must contain finite JSON values") from exc
    error = next(VALIDATOR.iter_errors(payload), None)
    if error:
        location = ".".join(map(str, error.absolute_path)) or "candidate"
        raise SemanticValidationError(f"{location}: {error.message}")
    entry = deepcopy(payload)
    source = entry["provenance"]
    allowed_refs = set(source["raw_entry_ids"])
    if any(not ref.startswith(source["source_sha256"] + ":") for ref in allowed_refs):
        raise SemanticValidationError("raw_entry_ids must match source_sha256")
    if source["source"] == "ai_candidate" and source["prompt_version"] is None:
        raise SemanticValidationError("AI candidates require prompt_version")
    counters, identifiers, meanings = Counter(), set(), set()
    examples = 0
    for sense in entry["senses"]:
        pos = sense["pos"]
        counters[pos] += 1
        if type(sense["sense_number"]) is not int or sense["sense_number"] != counters[pos]:
            raise SemanticValidationError("sense_number must be an integer, continuous from 1 within each POS")
        if sense["sense_id"] in identifiers:
            raise SemanticValidationError("sense_id must be unique within entry")
        identifiers.add(sense["sense_id"])
        if not set(sense["source_entry_ids"]).issubset(allowed_refs):
            raise SemanticValidationError("sense references must be listed in provenance.raw_entry_ids")
        english = sense["english_definition"].strip()
        if not 1 <= len(WORD.findall(english)) <= 15:
            raise SemanticValidationError("English definition must contain 1–15 English words")
        if re.search(r"[.!?](?:\s+\S|\S)", english):
            raise SemanticValidationError("English definition must be a single sentence")
        chinese = sense["chinese_definition"]
        if not re.search(r"[\u3400-\u9fff]", chinese):
            raise SemanticValidationError("Chinese definition requires Chinese text")
        if "、" in chinese or ";" in chinese:
            raise SemanticValidationError("use Chinese semicolons between glosses")
        glosses = [part.strip() for part in chinese.split("；")]
        if any(not part for part in glosses) or len(glosses) != len(set(glosses)):
            raise SemanticValidationError("empty or duplicate glosses within sense")
        meaning = (pos, _canonical(english))
        if meaning in meanings:
            raise SemanticValidationError("duplicate English definition within POS")
        meanings.add(meaning)
        examples += len(sense["examples"])
    if examples > 1:
        raise SemanticValidationError("at most one bilingual example per entry")
    return entry


def assess_candidate(payload: dict, *, raw_entries: dict[str, dict] | None = None) -> dict:
    entry = validate_candidate(payload)
    reasons = []
    if len(entry["senses"]) > 5:
        reasons.append("more_than_five_senses")
    elif len(entry["senses"]) > 3:
        reasons.append("above_three_sense_display_target")
    if any(sense["confidence"] < 0.8 for sense in entry["senses"]):
        reasons.append("low_self_reported_confidence")
    if entry["provenance"]["source"] == "design_example":
        reasons.append("design_example_not_production_data")
    source_verified = False
    if raw_entries is None:
        reasons.append("raw_source_not_verified")
    else:
        provenance = entry["provenance"]
        for ref in provenance["raw_entry_ids"]:
            raw = raw_entries.get(ref)
            if raw is None or raw["word"] != entry["word"]:
                raise SemanticValidationError("raw source reference missing or word mismatch")
            if raw["source_sha256"] != provenance["source_sha256"] or raw["ecdict_version"] != provenance["ecdict_version"]:
                raise SemanticValidationError("raw source hash or ECDICT version mismatch")
        source_verified = True
    if any(sense["learning_priority"] == "unknown" for sense in entry["senses"]):
        reasons.append("unknown_learning_priority")
    # Rank data alone cannot establish individual sense frequency or correctness.
    # Model-supplied confidence cannot substitute for an independent reviewer.
    reasons.append("human_semantic_review_required")
    return {
        "word": entry["word"], "schema_version": "2.0",
        "structurally_valid": True, "raw_source_verified": source_verified,
        "review_status": "needs_review", "production_eligible": False,
        "review_reasons": reasons,
        "review_checks": ["sense_boundaries", "example_matches_sense", "source_metadata_accuracy",
                          "definition_originality", "pronunciation_accuracy", "learning_priority",
                          "native_lookup_layout"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="single v2 candidate JSON")
    parser.add_argument("--raw-snapshot", type=Path, help="optional verified Phase 1 snapshot")
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    wanted = set(validate_candidate(candidate)["provenance"]["raw_entry_ids"])
    raw_entries = None
    if args.raw_snapshot:
        verify_snapshot(args.raw_snapshot)
        raw_entries = {}
        with (args.raw_snapshot / "raw_entries.jsonl").open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["entry_id"] in wanted:
                    raw_entries[row["entry_id"]] = row
    print(json.dumps(assess_candidate(candidate, raw_entries=raw_entries), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
