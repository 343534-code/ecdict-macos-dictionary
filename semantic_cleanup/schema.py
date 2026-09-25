"""Schema validation and deterministic cleanup for AI semantic entries."""

from __future__ import annotations

from copy import deepcopy
from collections import defaultdict
import re
from typing import Any


SCHEMA_VERSION = "1.0"
GLOSS_SEPARATOR = "；"
GLOSS_SPLIT = re.compile(r"[；、]+")
SPACE = re.compile(r"\s+")
FORM_LABELS = {"过去式", "过去分词", "现在分词", "三单", "复数", "比较级", "最高级", "词形"}


class SemanticValidationError(ValueError):
    """Raised when a candidate cannot safely enter the semantic overlay."""


def canonicalize_glosses(value: str) -> str:
    """Deduplicate AI-provided Chinese glosses without inferring new senses."""
    seen: set[str] = set()
    glosses: list[str] = []
    for item in GLOSS_SPLIT.split(value):
        item = SPACE.sub(" ", item).strip(" ；、")
        if item and item not in seen:
            seen.add(item)
            glosses.append(item)
    return GLOSS_SEPARATOR.join(glosses)


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not (result := SPACE.sub(" ", value).strip()):
        raise SemanticValidationError(f"{field} 必须是非空文本。")
    return result


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise SemanticValidationError(f"{field} 必须是列表。")
    return value


def validate_semantic_entry(payload: dict[str, Any], *, limits: dict[str, int] | None = None) -> dict[str, Any]:
    """Validate, normalize and return a safe semantic entry.

    This is intentionally strict: invalid model output is rejected rather than
    silently rendered into a production dictionary.
    """
    if not isinstance(payload, dict):
        raise SemanticValidationError("语义词条必须是对象。")
    entry = deepcopy(payload)
    if entry.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise SemanticValidationError("不支持的 schema_version。")
    entry["schema_version"] = SCHEMA_VERSION
    entry["word"] = _string(entry.get("word"), "word")

    pronunciation = _list(entry.get("pronunciation", []), "pronunciation")
    if len(pronunciation) > 2:
        raise SemanticValidationError("音标最多保留英音和美音两项。")
    entry["pronunciation"] = [_string(item, "pronunciation") for item in pronunciation]

    limits = limits or {}
    max_senses = limits.get("max_senses_per_pos", 5)
    max_en = limits.get("max_english_definition_characters", 180)
    max_zh = limits.get("max_chinese_definition_characters", 72)
    max_examples = limits.get("max_examples_per_entry", 1)
    max_notes = limits.get("max_usage_notes_per_sense", 2)

    senses = _list(entry.get("senses"), "senses")
    if not senses:
        raise SemanticValidationError("至少需要一个义项。")
    counters: dict[str, int] = defaultdict(int)
    normalized_senses: list[dict[str, Any]] = []
    total_examples = 0
    for index, sense in enumerate(senses, 1):
        if not isinstance(sense, dict):
            raise SemanticValidationError(f"senses[{index}] 必须是对象。")
        result = deepcopy(sense)
        pos = _string(result.get("pos"), f"senses[{index}].pos")
        counters[pos] += 1
        if counters[pos] > max_senses:
            raise SemanticValidationError(f"{pos} 的义项超过上限 {max_senses}。")
        if result.get("sense_number") != counters[pos]:
            raise SemanticValidationError(f"{pos} 的义项编号必须从 1 连续递增。")
        english = _string(result.get("english_definition"), f"senses[{index}].english_definition")
        if len(english) > max_en:
            raise SemanticValidationError(f"senses[{index}] 的英文释义过长。")
        chinese = canonicalize_glosses(_string(result.get("chinese_definition"), f"senses[{index}].chinese_definition"))
        if not chinese or len(chinese) > max_zh:
            raise SemanticValidationError(f"senses[{index}] 的中文释义为空或过长。")
        result.update(pos=pos, english_definition=english, chinese_definition=chinese)
        if "domain" in result:
            result["domain"] = _string(result["domain"], f"senses[{index}].domain")

        examples = _list(result.get("examples", []), f"senses[{index}].examples")
        if len(examples) > 1:
            raise SemanticValidationError("单个义项最多保留一个例句。")
        total_examples += len(examples)
        normalized_examples = []
        for example in examples:
            if not isinstance(example, dict):
                raise SemanticValidationError("例句必须是对象。")
            normalized_examples.append({
                "english": _string(example.get("english"), "example.english"),
                "chinese": _string(example.get("chinese"), "example.chinese"),
            })
        result["examples"] = normalized_examples

        notes = _list(result.get("usage_notes", []), f"senses[{index}].usage_notes")
        if len(notes) > max_notes:
            raise SemanticValidationError("单个义项的用法提示过多。")
        result["usage_notes"] = [_string(note, "usage_note") for note in notes]
        normalized_senses.append(result)
    if total_examples > max_examples:
        raise SemanticValidationError(f"每个词条最多保留 {max_examples} 个例句。")
    entry["senses"] = normalized_senses

    morphology = _list(entry.get("morphology", []), "morphology")
    normalized_forms = []
    for form in morphology:
        if not isinstance(form, dict):
            raise SemanticValidationError("morphology 项必须是对象。")
        label = _string(form.get("label"), "morphology.label")
        if label not in FORM_LABELS:
            raise SemanticValidationError(f"不支持的词形标签：{label}")
        normalized_forms.append({"label": label, "form": _string(form.get("form"), "morphology.form")})
    entry["morphology"] = normalized_forms
    entry["exam_tags"] = [_string(tag, "exam_tag") for tag in _list(entry.get("exam_tags", []), "exam_tags")]
    if not isinstance(entry.get("frequency"), dict):
        raise SemanticValidationError("frequency 必须是对象。")
    return entry
