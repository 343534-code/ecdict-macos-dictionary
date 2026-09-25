#!/usr/bin/env python3
"""Export ECDICT MDX entries to styled Apple Dictionary XHTML."""
from pathlib import Path
from html import unescape
from urllib.parse import quote
from xml.sax.saxutils import escape, quoteattr
from contextlib import nullcontext
import argparse
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from semantic_cleanup import SemanticStore

try:
    from readmdict import MDX
except ImportError:  # Unit tests exercise rendering without the MDX reader.
    MDX = None

marker = re.compile(r"`([1-4])`")
breaks = re.compile(r"<\s*/?br\s*/?\s*>", re.I)
spaces = re.compile(r"[ \t\f\v]+")
cjk_comma = re.compile(r"(?<=[\u3400-\u9fff]),\s*(?=[\u3400-\u9fff])")
metadata = re.compile(
    r"^\((?P<tags>[^\s()]+)?(?:\s+(?P<bnc>\d+)/(?P<coca>\d+))?\)$"
)
part_of_speech = re.compile(
    r"^(?P<pos>n|v[ti]?|a(?:dj)?|ad(?:v)?|prep|conj|pron|aux|num|"
    r"int(?:erj)?|art|abbr|det|modal|phr|prefix|suffix)\.",
    re.I,
)

exam_labels = {
    "中": "中考",
    "高": "高考",
    "研": "考研",
    "四": "CET4",
    "六": "CET6",
    "托": "TOEFL",
    "雅": "IELTS",
    # The upstream marker refers to the GRE “红宝书” word list.
    "宝": "GRE",
}

def clean(s: str) -> str:
    s = unescape(s).replace('\r', '')
    return spaces.sub(' ', s).strip()

def normalize_definition_punctuation(value: str) -> str:
    """Use a semicolon between separate Chinese glosses."""
    value = cjk_comma.sub("；", value)
    # ECDICT's compact subject label is opaque in a general-purpose dictionary.
    return value.replace("[计]", "[计算机]")


def normalize_ipa_symbols(value: str) -> str:
    """Modernize ECDICT's compact phonetic notation into IPA code points."""
    value = value.replace("ә", "ə").replace("'", "ˈ").replace(":", "ː")
    # ECDICT's legacy spelling uses ae/i/u for æ/ɪ/ʊ. Long vowels retain ː.
    value = value.replace("ae", "æ")
    value = re.sub(r"(?<![ɪ])i(?!ː)", "ɪ", value)
    value = re.sub(r"(?<![ʊ])u(?!ː)", "ʊ", value)
    return value

def normalize_pronunciation_variants(value: str) -> list[str]:
    """Normalize safe legacy symbols and split alternate pronunciations."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1].strip()
    if value.startswith("/") and value.endswith("/"):
        value = value[1:-1].strip()
    value = normalize_ipa_symbols(value)
    value = re.sub(r"\.\s+(?=ˈ)", "; ", value)
    return [f"/{variant.strip().strip('/')}/"
            for variant in value.split(";") if variant.strip()]

def normalize_pronunciation(value: str) -> str:
    """Return normalized variants as compact display text."""
    return "  ".join(normalize_pronunciation_variants(value))

def render_rank_badges(value: str) -> str | None:
    """Expand the MDX's compact Oxford/Collins marker into study badges."""
    match = re.fullmatch(r"-?(K)?([1-5])?", value)
    if not match or not any(match.groups()):
        return None
    labels = []
    if match.group(1):
        labels.append("Oxford 3000")
    if match.group(2):
        labels.append(f"Collins {match.group(2)}★")
    badges = ''.join(
        f'<span class="badge badge-rank">{label}</span>' for label in labels
    )
    return f'<span class="badges study-ranks">{badges}</span>'

def render_metadata_badges(value: str) -> str | None:
    """Expand exam tags and BNC/COCA ranks from the MDX metadata line."""
    match = metadata.fullmatch(value)
    if not match or not any(match.groups()):
        return None
    tags = match.group("tags") or ""
    if any(tag not in exam_labels for tag in tags):
        return None

    badges = []
    for tag in tags:
        label = exam_labels.get(tag, tag)
        badges.append(
            f'<span class="badge badge-exam">{escape(label)}</span>'
        )

    for corpus, rank in (("BNC", match.group("bnc")), ("COCA", match.group("coca"))):
        if rank is None:
            continue
        badges.append(
            f'<span class="badge badge-frequency">{corpus} #{rank}</span>'
        )

    return f'<div class="badges meta-badges">{"".join(badges)}</div>'

def render_metadata_groups(value: str) -> tuple[str | None, str | None] | None:
    """Render corpus ranks as secondary text and exams as subdued labels."""
    match = metadata.fullmatch(value)
    if not match or not any(match.groups()):
        return None
    tags = match.group("tags") or ""
    if any(tag not in exam_labels for tag in tags):
        return None

    frequency = " · ".join(
        f'{corpus} #{rank}'
        for corpus, rank in (("BNC", match.group("bnc")), ("COCA", match.group("coca")))
        if rank is not None
    )
    exam_labels_text = " · ".join(escape(exam_labels[tag]) for tag in tags)

    study = (
        f'<span class="frequency-text">{escape(frequency)}</span>'
        if frequency else None
    )
    footer = (
        '<div class="exam-outline"><span class="exam-title">考试：</span>'
        f'<span class="exam-list">{exam_labels_text}</span></div>'
        if exam_labels_text else None
    )
    return study, footer


def circled_number(index: int) -> str:
    """Return a compact dictionary sense number for grouped definitions."""
    symbols = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
    return symbols[index - 1] if index <= len(symbols) else f"{index}."


def render_pos_groups(groups: dict[str, list[str]], plain_senses: list[str]) -> str:
    """Render each part of speech once, numbering only distinct source lines."""
    rendered_groups, continuations = [], []
    sequence = 0
    for pos, definitions in groups.items():
        numbered = len(definitions) > 1
        for index, definition in enumerate(definitions, 1):
            continuation = index > 1
            group_class = 'pos-group pos-continuation' if continuation else 'pos-group'
            pos_class = 'pos continuation-pos' if continuation else 'pos'
            sense = ('<div class="sense">'
                     + (f'<span class="sense-number">{circled_number(index)}</span>' if numbered else '')
                     + f'<span class="definition">{escape(definition)}</span></div>')
            group = (f'<div class="{group_class}" style="order:{sequence}">'
                     f'<span class="{pos_class}">{escape(pos)}</span>'
                     f'<div class="pos-definitions">{sense}</div></div>')
            (continuations if continuation else rendered_groups).append(group)
            sequence += 1
    rendered_groups.extend(continuations)
    rendered_groups.extend(
        f'<div class="sense loose-sense" style="order:{sequence}">{escape(definition)}</div>'
        for definition in plain_senses
    )
    return ''.join(rendered_groups)

def render_inflections(value: str) -> str | None:
    """Render the MDX's flattened verb forms as labelled, wrapping chips."""
    if not value.startswith("时态:"):
        return None
    forms = [form.strip() for form in value.removeprefix("时态:").split(",")]
    forms = [form for form in forms if form]
    if not forms:
        return None

    if len(forms) == 4:
        labels = ("过去式", "过去分词", "现在分词", "第三人称单数")
    elif len(forms) == 3:
        labels = ("过去式 / 过去分词", "现在分词", "第三人称单数")
    else:
        # A very small number of upstream entries use this field for generic
        # word forms rather than a complete four-form verb paradigm.
        labels = tuple("词形" for _ in forms)

    chips = []
    for label, form in zip(labels, forms):
        target = f"x-dictionary:d:{quote(form, safe='')}"
        chips.append(
            f'<a class="inflection" href={quoteattr(target)}>'
            f'<span class="inflection-kind">{escape(label)}</span>'
            f'<span class="inflection-word">{escape(form)}</span></a>'
        )
    return (
        '<div class="inflections"><span class="inflections-title">词形变化</span>'
        f'{"".join(chips)}</div>'
    )


def render_semantic_rank_badges(frequency: dict[str, object]) -> str:
    labels = []
    if frequency.get("oxford_3000"):
        labels.append("Oxford 3000")
    if isinstance(frequency.get("collins"), int) and frequency["collins"]:
        labels.append(f"Collins {frequency['collins']}★")
    return (
        '<span class="badges study-ranks">'
        + ''.join(f'<span class="badge badge-rank">{label}</span>' for label in labels)
        + '</span>'
        if labels else ''
    )


def render_semantic_inflections(forms: list[dict[str, str]]) -> str:
    if not forms:
        return ''
    chips = []
    for form in forms:
        word = form["form"]
        target = f"x-dictionary:d:{quote(word, safe='')}"
        chips.append(
            f'<a class="inflection" href={quoteattr(target)}>'
            f'<span class="inflection-kind">{escape(form["label"])}</span>'
            f'<span class="inflection-word">{escape(word)}</span></a>'
        )
    return '<div class="inflections"><span class="inflections-title">词形：</span>' + ''.join(chips) + '</div>'


def render_semantic_entry(entry: dict[str, object]) -> str:
    """Render a validated semantic overlay in the compact learner layout."""
    word = str(entry["word"])
    pronunciation = entry["pronunciation"]
    variants = []
    labels = ("英", "美") if len(pronunciation) == 2 else (None,) * len(pronunciation)
    for label, value in zip(labels, pronunciation):
        variants.append(
            '<span class="pronunciation-variant">'
            + (f'<span class="pronunciation-label">{label}</span>' if label else '')
            + f'<span class="ipa">{escape(value)}</span></span>'
        )
    pronunciation_html = f'<h3 class="pronunciation">{"".join(variants)}</h3>' if variants else ''
    frequency = entry["frequency"]
    header = (
        f'<div class="entry-header"><h1>{escape(word)}</h1>{pronunciation_html}'
        f'{render_semantic_rank_badges(frequency)}</div>'
    )

    groups: dict[str, list[dict[str, object]]] = {}
    for sense in entry["senses"]:
        groups.setdefault(sense["pos"], []).append(sense)
    rendered_groups = []
    for pos, senses in groups.items():
        rendered_senses = []
        for sense in senses:
            domain = f'<span class="semantic-domain">[{escape(sense["domain"])}]</span>' if sense.get("domain") else ''
            notes = ''.join(f'<span class="usage-note">{escape(note)}</span>' for note in sense["usage_notes"])
            examples = ''.join(
                '<div class="semantic-example"><span class="example-english">'
                f'{escape(example["english"])}</span><span class="example-chinese">{escape(example["chinese"])}</span></div>'
                for example in sense["examples"]
            )
            rendered_senses.append(
                '<div class="sense semantic-sense">'
                f'<span class="sense-number">{circled_number(sense["sense_number"])}</span>'
                '<span class="semantic-content">'
                f'{domain}<span class="english-definition">{escape(sense["english_definition"])}</span>'
                f'<span class="definition">{escape(sense["chinese_definition"])}</span>{notes}{examples}'
                '</span></div>'
            )
        rendered_groups.append(
            f'<div class="pos-group"><span class="pos">{escape(pos)}</span>'
            f'<div class="pos-definitions">{"".join(rendered_senses)}</div></div>'
        )
    core = '<div class="core-senses core-senses-divided">' + ''.join(rendered_groups) + '</div>'

    exam_tags = entry["exam_tags"]
    exams = (
        '<div class="exam-outline"><span class="exam-title">考试：</span>'
        f'<span class="exam-list">{" · ".join(escape(tag) for tag in exam_tags)}</span></div>'
        if exam_tags else ''
    )
    frequency_parts = []
    if frequency.get("bnc") is not None:
        frequency_parts.append(f'BNC {frequency["bnc"]}')
    if frequency.get("coca") is not None:
        frequency_parts.append(f'COCA {frequency["coca"]}')
    frequency_html = (
        '<div class="study-meta"><span class="frequency-label">词频：</span>'
        f'<span class="frequency-text">{" · ".join(frequency_parts)}</span></div>'
        if frequency_parts else ''
    )
    return header + core + render_semantic_inflections(entry["morphology"]) + exams + frequency_html

def render(key: str, raw: bytes) -> str:
    text = breaks.sub('\n', raw.decode('utf-8', 'replace'))
    # MDX stylesheet markers: 1=headword, 3=phonetic, 4=metadata.
    text = marker.sub(lambda m: f'\u0001{m.group(1)}\u0001', text)
    chunks = re.split(r'(\u0001[1-4]\u0001)', text)
    style = '0'
    pronunciations, rank_badges, frequency_parts = [], [], []
    pos_groups: dict[str, list[str]] = {}
    plain_senses, inflection_parts, metadata_parts, exam_parts = [], [], [], []
    for chunk in chunks:
        hit = re.fullmatch(r'\u0001([1-4])\u0001', chunk)
        if hit:
            style = hit.group(1)
            continue
        for line in chunk.splitlines():
            line = clean(line)
            if not line:
                continue
            if style == '1':
                continue  # the Apple Dictionary heading is emitted below
            if style == '3':
                normalized = normalize_pronunciation_variants(line)
                labels = ("英", "美") if len(normalized) == 2 else (None,) * len(normalized)
                variants = ''.join(
                    '<span class="pronunciation-variant">'
                    + (f'<span class="pronunciation-label">{label}</span>' if label else '')
                    + f'<span class="ipa">{escape(variant)}</span></span>'
                    for label, variant in zip(labels, normalized)
                )
                if variants:
                    pronunciations.append(f'<h3 class="pronunciation">{variants}</h3>')
            elif style == '4' and (badges := render_rank_badges(line)):
                rank_badges.append(badges)
            elif style == '4' and (groups := render_metadata_groups(line)):
                study, footer = groups
                if study:
                    frequency_parts.append(study)
                if footer:
                    exam_parts.append(footer)
            elif (style == '4' or line.startswith('时态:')) and (
                rendered_inflections := render_inflections(line)
            ):
                inflection_parts.append(rendered_inflections)
            elif style == '4' or line.startswith('级别:'):
                metadata_parts.append(f'<div class="meta">{escape(line)}</div>')
            elif match := part_of_speech.match(line):
                pos = match.group("pos") + "."
                definition = normalize_definition_punctuation(line[match.end():].strip())
                pos_groups.setdefault(pos, []).append(definition)
            else:
                definition = normalize_definition_punctuation(line)
                plain_senses.append(definition)
    if not any((pos_groups, plain_senses, inflection_parts, metadata_parts, exam_parts)):
        plain_senses.append('（无释义）')
    header = (
        f'<div class="entry-header"><h1>{escape(key)}</h1>'
        f'{"".join(pronunciations)}{"".join(rank_badges)}</div>'
    )
    study_meta = ''.join(frequency_parts)
    study = f'<div class="study-meta">{study_meta}</div>' if study_meta else ''
    has_details = any((inflection_parts, metadata_parts, exam_parts, study))
    core_class = "core-senses core-senses-divided" if has_details else "core-senses"
    core_content = render_pos_groups(pos_groups, plain_senses)
    core = f'<div class="{core_class}">{core_content}</div>' if core_content else ''
    details = ''.join(inflection_parts + exam_parts + [study] + metadata_parts)
    return header + core + (f'<div class="entry-details">{details}</div>' if details else '')

def main(source: Path, destination: Path, semantic_db: Path | None = None) -> None:
    if MDX is None:
        raise RuntimeError(
            "缺少 readmdict；请先运行 `python3 -m pip install -r requirements.txt`。"
        )
    mdx = MDX(str(source))
    semantic_context = SemanticStore(semantic_db) if semantic_db else nullcontext(None)
    with semantic_context as semantic_store, destination.open('w', encoding='utf-8', buffering=1024*1024) as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write('<d:dictionary xmlns="http://www.w3.org/1999/xhtml" xmlns:d="http://www.apple.com/DTDs/DictionaryService-1.0.rng">\n')
        for ordinal, (raw_key, raw_value) in enumerate(mdx.items(), 1):
            key = raw_key.decode('utf-8', 'replace').strip()
            if not key:
                continue
            semantic_entry = semantic_store.get(key) if semantic_store else None
            body = render_semantic_entry(semantic_entry) if semantic_entry else render(key, raw_value)
            out.write(f'<d:entry id="ecdict_{ordinal}" d:title={quoteattr(key)}><d:index d:value={quoteattr(key)}/>')
            out.write(f'{body}</d:entry>\n')
            if ordinal % 100000 == 0:
                print(f'exported {ordinal}', file=sys.stderr, flush=True)
        out.write('</d:dictionary>\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--semantic-db', type=Path, help='validated semantic_entries.sqlite overlay')
    arguments = parser.parse_args()
    main(arguments.source, arguments.destination, arguments.semantic_db)
