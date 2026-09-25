"""Lossless, append-only-by-snapshot raw ECDICT ingestion. No model calls."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import re
from itertools import islice
from pathlib import Path
from typing import Iterable

VERSION = "1"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def encode(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def standardize(row: dict, *, source_sha256: str, ordinal: int, version: str) -> dict:
    """Map field names only; never clean punctuation, IPA, or semantic content."""
    if not isinstance(row, dict) or not isinstance(row.get("word"), str) or not row["word"].strip():
        raise ValueError(f"record {ordinal}: nonempty string word required")
    aliases = {"translation_raw": "translation", "tags": "tag"}
    fields = ("word", "phonetic", "pos", "translation_raw", "definition",
              "exchange", "tags", "bnc", "coca", "frq", "collins", "oxford")
    result = {key: row.get(key, row.get(aliases.get(key, key))) for key in fields}
    result.update(schema_version=VERSION, ecdict_version=version,
                  entry_id=f"{source_sha256}:{ordinal}", source_ordinal=ordinal,
                  source_sha256=source_sha256, raw_fields=row)
    result["missing_fields"] = [key for key in fields if result[key] is None]
    # frq remains frq: an unverified corpus association must not become coca.
    return result


def read_source(path: Path, source_format: str) -> Iterable[dict]:
    if source_format == "mdx":
        try:
            from readmdict import MDX
        except ImportError as exc:
            raise RuntimeError("MDX input requires the existing readmdict/python-lzo environment") from exc
        for key, body in MDX(str(path)).items():
            yield {
                **extract_mdx(body.decode("utf-8", errors="replace")),
                "word": key.decode("utf-8", errors="replace"),
                "mdx_key_base64": base64.b64encode(key).decode("ascii"),
                "mdx_body_base64": base64.b64encode(body).decode("ascii"),
                "mdx_body_text": body.decode("utf-8", errors="replace"),
                "extraction_status": "conservative_mdx_markers_v1",
            }
        return
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if source_format == "csv":
            reader = csv.DictReader(stream)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("CSV needs unique column names")
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("CSV row length differs from header")
                yield row
        elif source_format == "jsonl":
            for line in stream:
                if line.strip():
                    yield json.loads(line)
        else:
            raise ValueError(f"unsupported format: {source_format}")


def extract_mdx(text: str) -> dict:
    """Extract the known 1.0.28 style markers; original bytes remain authoritative."""
    chunks = re.split(r"(`[1-4]`)", text)
    style = "0"
    translations, phonetics, metadata, positions, forms = [], [], [], [], []
    result = {}
    for chunk in chunks:
        if re.fullmatch(r"`[1-4]`", chunk):
            style = chunk[1]
            continue
        if style == "1":
            continue
        for line in re.split(r"<\s*/?br\s*/?\s*>|\r?\n", chunk, flags=re.I):
            if not line.strip():
                continue
            stripped = line.strip()
            if style == "3":
                phonetics.append(stripped)
            elif stripped.startswith("时态:"):
                forms.append(stripped)
            elif style == "4":
                metadata.append(line)
                rank = re.fullmatch(r"-?(K)?([1-5])?", stripped)
                frequency = re.fullmatch(r"\(([^\s()]*)\s+(\d+)/(\d+)\)", stripped)
                tags_only = re.fullmatch(r"\(([中高研四六托雅宝]+)\)", stripped)
                if rank and any(rank.groups()):
                    if rank[1]:
                        result["oxford"] = 1
                    if rank[2]:
                        result["collins"] = int(rank[2])
                elif frequency:
                    result.update(tags=frequency[1], bnc=int(frequency[2]), coca=int(frequency[3]))
                elif tags_only:
                    result["tags"] = tags_only[1]
            else:
                translations.append(line)
                pos = re.match(r"^([A-Za-z]+\.)\s", stripped)
                if pos:
                    positions.append(pos[1])
    result.update(translation_raw="\n".join(translations) or None,
                  phonetic="\n".join(phonetics) or None,
                  pos=positions or None, exchange="\n".join(forms) or None,
                  mdx_metadata_raw=metadata)
    return result


def create_snapshot(source: Path, output: Path, *, source_format: str,
                    version: str, limit: int | None = None) -> dict:
    """Create a new directory exclusively; failed imports never gain a manifest."""
    source, output = Path(source), Path(output)
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive")
    if not version.strip():
        raise ValueError("explicit ECDICT version required")
    before = digest(source)
    output.mkdir(parents=True, exist_ok=False)
    raw_path = output / "raw_entries.jsonl"
    count = 0
    rows = read_source(source, source_format)
    if limit is not None:
        rows = islice(rows, limit)
    with raw_path.open("x", encoding="utf-8", newline="\n") as stream:
        for count, row in enumerate(rows, 1):
            stream.write(encode(standardize(row, source_sha256=before,
                                          ordinal=count, version=version)) + "\n")
    if digest(source) != before:
        raise ValueError("source changed during import; snapshot is incomplete")
    if not count:
        raise ValueError("empty input; snapshot is incomplete")
    manifest = {
        "schema_version": VERSION, "ecdict_version": version,
        "source_name": source.name, "source_format": source_format,
        "source_sha256": before, "source_bytes": source.stat().st_size,
        "entry_count": count, "limit": limit, "scope": "sample" if limit else "full",
        "raw_entries_sha256": digest(raw_path),
        "adapter_sha256": digest(Path(__file__)),
        "field_extraction": "conservative_mdx_markers_v1" if source_format == "mdx" else "field_names_only",
    }
    # The manifest is the completion marker. No reader accepts a partial import.
    with (output / "manifest.json").open("x", encoding="utf-8") as stream:
        stream.write(encode(manifest) + "\n")
    return manifest


def verify_snapshot(output: Path) -> dict:
    output = Path(output)
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    raw_path = output / "raw_entries.jsonl"
    if manifest["schema_version"] != VERSION or digest(raw_path) != manifest["raw_entries_sha256"]:
        raise ValueError("snapshot version or content hash mismatch")
    count = 0
    with raw_path.open(encoding="utf-8") as stream:
        for count, line in enumerate(stream, 1):
            record = json.loads(line)
            expected = standardize(record["raw_fields"], source_sha256=manifest["source_sha256"],
                                   ordinal=count, version=manifest["ecdict_version"])
            if record != expected:
                raise ValueError(f"record {count}: provenance or fields differ from raw input")
    if count != manifest["entry_count"] or not count:
        raise ValueError("snapshot count mismatch")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("source", type=Path)
    create.add_argument("output", type=Path)
    create.add_argument("--format", choices=("csv", "jsonl", "mdx"), required=True)
    create.add_argument("--ecdict-version", required=True)
    create.add_argument("--limit", type=int)
    check = sub.add_parser("verify")
    check.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "verify":
        result = verify_snapshot(args.output)
    else:
        result = create_snapshot(args.source, args.output, source_format=args.format,
                                 version=args.ecdict_version, limit=args.limit)
    print(encode(result))


if __name__ == "__main__":
    main()
