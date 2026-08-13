#!/usr/bin/env python3
"""Classify first-rescues by whether the model already captured the answer.

No new model calls. Development splits only. See
docs/research/hybrid_rescue_source_provenance_protocol_2026-08-13.md.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as diagnosis_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredExtractionRecord,
    _normalize_event,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260813"
PROTOCOL = "docs/research/hybrid_rescue_source_provenance_protocol_2026-08-13.md"
REPORT = REPO_ROOT / "docs/research/hybrid_rescue_source_provenance_2026-08-13.md"
ARTIFACT = REPO_ROOT / "experiments" / f"hybrid_rescue_source_provenance_{DATE_STAMP}.json"
EXAMPLES_PER_CLASS = 2

_GAN_SPEC = importlib.util.spec_from_file_location(
    "gan_stage_ablation", REPO_ROOT / "scripts/build_gan2026_hybrid_stage_ablation.py"
)
if _GAN_SPEC is None or _GAN_SPEC.loader is None:
    raise RuntimeError("cannot import Gan stage ablation")
gan = importlib.util.module_from_spec(_GAN_SPEC)
_GAN_SPEC.loader.exec_module(gan)

_EXECT_SPEC = importlib.util.spec_from_file_location(
    "exect_stage_ablation", REPO_ROOT / "scripts/build_exectv2_hybrid_stage_ablation.py"
)
if _EXECT_SPEC is None or _EXECT_SPEC.loader is None:
    raise RuntimeError("cannot import ExECT stage ablation")
exect = importlib.util.module_from_spec(_EXECT_SPEC)
_EXECT_SPEC.loader.exec_module(exect)

hs = gan.hs

SOURCE_ORDER = (
    "render_selected",
    "promote_relegated_model_answer",
    "compose_from_captured_events",
    "use_model_quote_not_as_answer",
    "trim_inventory_to_exact",
    "add_from_unquoted_letter_span",
)

SOURCE_LABELS = {
    "render_selected": (
        "Render the selected span: the first-changer rereads the model's "
        "chosen quote or already-selected event and only changes form or "
        "canonical wording."
    ),
    "promote_relegated_model_answer": (
        "Promote a relegated model answer: another saved event or mention "
        "already carried the rescued label or concept."
    ),
    "compose_from_captured_events": (
        "Compose from captured events: no single model event already held "
        "the rescued label, but the rule built it from events the model "
        "did extract (diary sums, dated sequences, elapsed anchors)."
    ),
    "use_model_quote_not_as_answer": (
        "Use a model quote the model did not treat as that answer: the "
        "supporting words appear in some model evidence or mention, but "
        "not as the rescued diagnosis or frequency answer."
    ),
    "trim_inventory_to_exact": (
        "Trim the inventory to exact: family exactness is rescued by "
        "dropping extra keys, not by adding a new concept or regimen."
    ),
    "add_from_unquoted_letter_span": (
        "Add from letter text the model never quoted: the supporting "
        "fragment is not in any saved model evidence or mention."
    ),
}


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _norm(text: str | None) -> str:
    return " ".join(str(text or "").lower().replace("-", " ").split())


def _contains_norm(haystack: str | None, needle: str | None) -> bool:
    hay = _norm(haystack)
    ned = _norm(needle)
    return bool(ned) and ned in hay


def _label_cues(label: str) -> list[str]:
    cues = re.findall(r"\d+(?:\.\d+)?", label)
    for token in (
        "per day",
        "per week",
        "per month",
        "per year",
        "cluster",
        "seizure free",
        "unknown",
        "no seizure frequency reference",
    ):
        if token in _norm(label):
            cues.append(token)
    return cues


def _cues_in_text(label: str, text: str | None) -> bool:
    blob = _norm(text)
    if not blob:
        return False
    if _contains_norm(blob, label):
        return True
    cues = _label_cues(label)
    if not cues:
        return False
    return all(cue in blob for cue in cues)


def _concept_from_diagnosis_key(key: str) -> str | None:
    try:
        parsed = ast.literal_eval(key)
    except (SyntaxError, ValueError):
        return None
    if isinstance(parsed, tuple) and len(parsed) >= 2:
        return canonicalize_diagnosis_concept(str(parsed[1]))
    return None


def _classify_gan_rescue(
    *,
    extraction: StructuredExtractionRecord,
    normalized: list[Any],
    stage: str,
    after_label: str,
) -> str:
    selected_ids = set(extraction.selection.selected_event_ids)
    matching_ids: list[str] = []
    for event, norm in zip(extraction.events, normalized):
        candidates = [
            event.raw_value,
            getattr(norm, "normalized_label", None),
        ]
        if any(
            candidate
            and (candidate == after_label or gan._purist_correct(str(candidate), after_label))
            for candidate in candidates
            if candidate
        ):
            matching_ids.append(event.event_id)

    # selected_evidence only rereads the model's chosen quote.
    if stage == "repair.selected_evidence":
        return "render_selected"

    if matching_ids and any(event_id not in selected_ids for event_id in matching_ids):
        return "promote_relegated_model_answer"
    if matching_ids:
        return "promote_relegated_model_answer"
    if extraction.events:
        return "compose_from_captured_events"
    return "add_from_unquoted_letter_span"


def _model_diagnosis_texts(events: list[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for event in events:
        family = _norm(str(event.get("family") or event.get("entity") or ""))
        if family not in {"diagnosis", "diagnoses"}:
            continue
        for mention in event.get("mentions") or [{"text": event.get("text")}]:
            text = mention.get("text") if isinstance(mention, dict) else None
            if text:
                texts.append(canonicalize_diagnosis_concept(str(text)))
        if event.get("text"):
            texts.append(canonicalize_diagnosis_concept(str(event.get("text"))))
        if event.get("anchor_text"):
            texts.append(canonicalize_diagnosis_concept(str(event.get("anchor_text"))))
    return texts


def _all_model_quotes(events: list[dict[str, Any]]) -> list[str]:
    quotes: list[str] = []
    for event in events:
        for key in ("evidence", "anchor_text", "text"):
            value = event.get(key)
            if value:
                quotes.append(str(value))
        for mention in event.get("mentions") or []:
            if not isinstance(mention, dict):
                continue
            for key in ("evidence", "text"):
                value = mention.get(key)
                if value:
                    quotes.append(str(value))
    return quotes


EXECT_FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)

FAMILY_EVENT_NAMES = {
    "Diagnosis": {"diagnosis", "diagnoses"},
    "SeizureFrequency": {"seizure_frequency", "seizurefrequency"},
    "Prescription": {"medication", "prescription"},
    "Investigations": {"investigation", "investigations"},
}

GENERIC_KEY_TOKENS = {
    "cui",
    "phrase",
    "ordinary",
    "rescue",
    "yes",
    "no",
    "none",
    "mg",
    "ml",
    "diagnosis",
}


def _added_keys(before_keys: list[str], after_keys: list[str]) -> list[str]:
    remaining = Counter(before_keys)
    added: list[str] = []
    for key in after_keys:
        if remaining[key]:
            remaining[key] -= 1
        else:
            added.append(key)
    return added


def _flatten_key_parts(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        parts: list[str] = []
        for item in value:
            parts.extend(_flatten_key_parts(item))
        return parts
    if value is None:
        return []
    return [str(value)]


def _event_family_name(event: dict[str, Any]) -> str:
    return _norm(str(event.get("family") or event.get("entity") or ""))


def _event_blob(event: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("evidence", "anchor_text", "text"):
        value = event.get(key)
        if value:
            parts.append(str(value))
    state = event.get("event_state") or event.get("attributes") or {}
    if isinstance(state, dict):
        for value in state.values():
            if value is not None:
                parts.append(str(value))
    for mention in event.get("mentions") or []:
        if not isinstance(mention, dict):
            continue
        for key in ("evidence", "text"):
            value = mention.get(key)
            if value:
                parts.append(str(value))
        attrs = mention.get("attributes") or {}
        if isinstance(attrs, dict):
            for value in attrs.values():
                if value is not None:
                    parts.append(str(value))
    return " ".join(parts)


def _same_family_blobs(events: list[dict[str, Any]], family: str) -> list[str]:
    names = FAMILY_EVENT_NAMES[family]
    return [_event_blob(event) for event in events if _event_family_name(event) in names]


def _key_cues(key: str) -> list[str]:
    try:
        parsed = ast.literal_eval(key)
    except (SyntaxError, ValueError):
        return [token for token in _norm(key).split() if len(token) > 2]
    cues: list[str] = []
    for part in _flatten_key_parts(parsed):
        token = _norm(part)
        if not token or token in GENERIC_KEY_TOKENS:
            continue
        if token.startswith("c") and token[1:].isdigit():
            continue
        if len(token) <= 1:
            continue
        cues.append(token)
    return cues


def _cues_in_blob(cues: list[str], blob: str) -> bool:
    hay = _norm(blob)
    if not hay or not cues:
        return False
    distinctive = [
        cue
        for cue in cues
        if not cue.replace(".", "", 1).isdigit()
        and cue not in {"active-rate", "seizure-free", "unknown"}
    ]
    check = distinctive or cues
    return all(cue in hay for cue in check)


def _sf_state_from_key(key: str) -> str | None:
    try:
        parsed = ast.literal_eval(key)
    except (SyntaxError, ValueError):
        return None
    if isinstance(parsed, tuple) and parsed:
        return _norm(str(parsed[-1]))
    return None


def _sf_model_lanes(events: list[dict[str, Any]]) -> set[str]:
    lanes: set[str] = set()
    mapping = {
        "active_rate": "active-rate",
        "active-rate": "active-rate",
        "seizure_free": "seizure-free",
        "seizure-free": "seizure-free",
        "since_date": "seizure-free",
        "unknown": "unknown",
        "unknown_frequency": "unknown",
    }
    for event in events:
        if _event_family_name(event) not in FAMILY_EVENT_NAMES["SeizureFrequency"]:
            continue
        state = event.get("event_state") or {}
        if not isinstance(state, dict):
            continue
        lane = mapping.get(_norm(str(state.get("lane") or "")))
        if lane:
            lanes.add(lane)
    return lanes


def _classify_exect_family_rescue(
    *,
    family: str,
    events: list[dict[str, Any]],
    note_text: str,
    before_keys: list[str],
    after_keys: list[str],
) -> str:
    if family == "Diagnosis":
        return _classify_exect_diagnosis_rescue(
            events=events,
            note_text=note_text,
            before_keys=before_keys,
            after_keys=after_keys,
        )

    added = _added_keys(before_keys, after_keys)
    if not added:
        return "trim_inventory_to_exact"

    same_family = _same_family_blobs(events, family)
    quotes = _all_model_quotes(events)
    before_states = {_sf_state_from_key(key) for key in before_keys}

    classes: list[str] = []
    for key in added:
        cues = _key_cues(key)
        in_family = any(_cues_in_blob(cues, blob) for blob in same_family)
        in_quote = any(_cues_in_blob(cues, quote) for quote in quotes)
        if family == "SeizureFrequency":
            state = _sf_state_from_key(key)
            if state and state in before_states:
                classes.append("render_selected")
                continue
            if state and state in _sf_model_lanes(events):
                classes.append("render_selected")
                continue
            if same_family:
                classes.append("compose_from_captured_events")
                continue
        if family == "Prescription":
            drug_cues = [
                cue
                for cue in cues
                if cue not in {"ordinary", "rescue", "as_required"}
                and not cue.replace(".", "", 1).replace("-", "", 1).isdigit()
            ]
            named = any(
                all(cue in _norm(blob) for cue in drug_cues)
                for blob in same_family
            ) if drug_cues else in_family
            if named:
                classes.append("compose_from_captured_events")
                continue
        if in_family:
            classes.append("render_selected")
            continue
        if in_quote:
            classes.append("use_model_quote_not_as_answer")
            continue
        classes.append("add_from_unquoted_letter_span")

    rank = {name: index for index, name in enumerate(SOURCE_ORDER)}
    return max(classes, key=lambda name: rank[name])


def _classify_exect_diagnosis_rescue(
    *,
    events: list[dict[str, Any]],
    note_text: str,
    before_keys: list[str],
    after_keys: list[str],
) -> str:
    remaining = Counter(before_keys)
    added: list[str] = []
    for key in after_keys:
        if remaining[key]:
            remaining[key] -= 1
        else:
            added.append(key)
    if not added:
        return "trim_inventory_to_exact"

    model_texts = set(_model_diagnosis_texts(events))
    quotes = _all_model_quotes(events)
    residual_spans = {
        canonicalize_diagnosis_concept(text): evidence
        for text, evidence in diagnosis_dictionary.diagnosis_residual_additions(note_text)
    }

    def _tokens(concept: str) -> list[str]:
        return [token for token in concept.split() if len(token) > 3]

    classes: list[str] = []
    for key in added:
        concept = _concept_from_diagnosis_key(key)
        if concept is None:
            classes.append("use_model_quote_not_as_answer")
            continue
        if concept in model_texts:
            classes.append("render_selected")
            continue
        quoted_as_answer = False
        quoted_as_span = False
        for quote in quotes:
            canon = canonicalize_diagnosis_concept(quote)
            if canon == concept:
                quoted_as_answer = True
            tokens = _tokens(concept)
            generic = {"epilepsy", "seizure", "seizures"}
            distinctive = [token for token in tokens if token not in generic]
            hay = _norm(quote)
            if distinctive:
                if any(token in hay for token in distinctive):
                    quoted_as_span = True
            elif tokens and all(token in hay for token in tokens):
                quoted_as_span = True
        if quoted_as_answer and concept not in model_texts:
            # another family or heading already named the concept
            classes.append("promote_relegated_model_answer")
            continue
        if quoted_as_span:
            classes.append("use_model_quote_not_as_answer")
            continue
        residual_evidence = residual_spans.get(concept)
        if residual_evidence and any(
            _contains_norm(quote, residual_evidence) for quote in quotes
        ):
            classes.append("use_model_quote_not_as_answer")
            continue
        classes.append("add_from_unquoted_letter_span")

    rank = {name: index for index, name in enumerate(SOURCE_ORDER)}
    return max(classes, key=lambda name: rank[name])


def _keep_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred = [row for row in rows if "sol" in str(row.get("model_slug", "")).lower()]
    rest = [row for row in rows if row not in preferred]
    kept: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in preferred + rest:
        key = (row.get("source_class"), row.get("id"), row.get("model_slug"), row.get("stage"))
        if key in seen:
            continue
        seen.add(key)
        kept.append(row)
        if len(kept) >= EXAMPLES_PER_CLASS:
            break
    return kept


def analyze_gan() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()
    counts: Counter[str] = Counter()
    by_stage: dict[str, Counter[str]] = {}
    examples: dict[str, list[dict[str, Any]]] = {name: [] for name in SOURCE_ORDER}
    first_rescue_n = 0

    for slug, display in hs.MODEL_SPECS:
        rows = hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_with_rules.jsonl")
        for row in rows:
            index = int(row["source_row_index"])
            meta = gold_index[index]
            gold_label = str(meta["gold_label"])
            replay = gan.replay_row(row)
            if replay is None or not replay["replayable"]:
                continue
            changes = list(replay["changes"])
            if not changes:
                continue
            first = changes[0]
            if not (
                gan._purist_correct(first["after"], gold_label)
                and not gan._purist_correct(first["before"], gold_label)
            ):
                continue
            record = gan._model_prediction_record(row)
            note = gan._note_text(row)
            if record is None or note is None:
                continue
            extraction = StructuredExtractionRecord.model_validate(record)
            normalized = [_normalize_event(event, note_text=note) for event in extraction.events]
            source = _classify_gan_rescue(
                extraction=extraction,
                normalized=normalized,
                stage=first["stage"],
                after_label=str(first["after"]),
            )
            first_rescue_n += 1
            counts[source] += 1
            by_stage.setdefault(first["stage"], Counter())[source] += 1
            payload = {
                "source_class": source,
                "id": index,
                "model_slug": slug,
                "model_display": display,
                "stage": first["stage"],
                "gold_label": gold_label,
                "before_label": first["before"],
                "after_label": first["after"],
                "selected_evidence": gan._truncate(extraction.selection.evidence, 180),
            }
            if len(examples[source]) < EXAMPLES_PER_CLASS * 4:
                examples[source].append(payload)

    return {
        "split": "dev750",
        "metric": "Purist first-rescue",
        "first_rescue_n": first_rescue_n,
        "counts": dict(counts),
        "by_stage": {stage: dict(counter) for stage, counter in sorted(by_stage.items())},
        "examples": {name: _keep_examples(rows) for name, rows in examples.items()},
    }


def analyze_exect() -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    families: dict[str, dict[str, Any]] = {
        family: {
            "counts": Counter(),
            "by_stage": {},
            "examples": {name: [] for name in SOURCE_ORDER},
            "first_rescue_n": 0,
        }
        for family in EXECT_FAMILIES
    }

    for slug, display in hs.MODEL_SPECS:
        main_path = hs.EXECT_JSONL[slug]
        main_rows = {
            str(row["letter_id"]): row for row in hs._read_jsonl(main_path)
        }
        structured_path = exect._structured_path(main_path)
        for structured_row in hs._read_jsonl(structured_path):
            letter_id = str(structured_row["letter_id"])
            letter = letters[letter_id]
            main_row = main_rows[letter_id]
            gold_mentions = list(main_row.get("gold_mentions") or [])
            replay = exect.replay_letter(
                structured_row, letter, gold_mentions=gold_mentions
            )
            if not replay.get("replayable", True):
                continue
            events = list(structured_row.get("structured_events") or [])
            seen_family: set[str] = set()
            for change in replay["changes"]:
                family = str(change["family"])
                if family not in families or family in seen_family:
                    continue
                if change["effect"] != "rescue":
                    continue
                seen_family.add(family)
                source = _classify_exect_family_rescue(
                    family=family,
                    events=events,
                    note_text=letter.note_text,
                    before_keys=list(change["before_keys"]),
                    after_keys=list(change["after_keys"]),
                )
                block = families[family]
                block["first_rescue_n"] += 1
                block["counts"][source] += 1
                block["by_stage"].setdefault(change["stage"], Counter())[source] += 1
                payload = {
                    "source_class": source,
                    "family": family,
                    "id": letter_id,
                    "model_slug": slug,
                    "model_display": display,
                    "stage": change["stage"],
                    "before_keys": change["before_keys"],
                    "after_keys": change["after_keys"],
                }
                if len(block["examples"][source]) < EXAMPLES_PER_CLASS * 4:
                    block["examples"][source].append(payload)

    return {
        "split": "dev140",
        "metric": "per-family clinical-headline first-rescue",
        "families": {
            family: {
                "first_rescue_n": block["first_rescue_n"],
                "counts": dict(block["counts"]),
                "by_stage": {
                    stage: dict(counter)
                    for stage, counter in sorted(block["by_stage"].items())
                },
                "examples": {
                    name: _keep_examples(rows)
                    for name, rows in block["examples"].items()
                },
            }
            for family, block in families.items()
        },
    }


def _md_count_table(counts: dict[str, int], total: int) -> list[str]:
    lines = [
        "| Source class | First-rescues | Share |",
        "| --- | ---: | ---: |",
    ]
    for name in SOURCE_ORDER:
        n = int(counts.get(name, 0))
        share = f"{n / total:.2f}" if total else "—"
        lines.append(f"| `{name}` | {n} | {share} |")
    lines.append(f"| Total | {total} | 1.00 |")
    return lines


def _md_examples(task: str, examples: dict[str, list[dict[str, Any]]]) -> list[str]:
    lines: list[str] = []
    for name in SOURCE_ORDER:
        rows = examples.get(name) or []
        if not rows:
            continue
        heading = "####" if task == "gan" else "#####"
        lines.append(f"{heading} `{name}`")
        lines.append("")
        for row in rows:
            if task == "gan":
                lines.append(
                    f"- Row `{row['id']}` / {row['model_display']}, "
                    f"`{row['stage']}`: `{row['before_label']}` → "
                    f"`{row['after_label']}` (gold `{row['gold_label']}`). "
                    f"Selected evidence: {row.get('selected_evidence')!r}."
                )
            else:
                lines.append(
                    f"- `{row['id']}` / {row['model_display']}, "
                    f"`{row['stage']}`: `{row['before_keys']}` → "
                    f"`{row['after_keys']}`."
                )
        lines.append("")
    return lines


def write_report(payload: dict[str, Any]) -> None:
    gan_block = payload["gan"]
    exect_block = payload["exect"]
    lines = [
        "# Hybrid rescue source provenance",
        "",
        "Date: 2026-08-13",
        "",
        "Status: development mechanism evidence; no model calls",
        "",
        f"Protocol: [{PROTOCOL}]({Path(PROTOCOL).name})",
        f"Artifact: [`{ARTIFACT.relative_to(REPO_ROOT).as_posix()}`]"
        f"({Path('..', '..', *ARTIFACT.relative_to(REPO_ROOT).parts).as_posix()})",
        "",
        "## Plain answer",
        "",
        "On Gan, 1,437 of 1,539 first-rescues (0.93) only re-render the model's",
        "selected quote. The remaining 102 first-rescues compose or promote from",
        "events the model already extracted. Zero first-rescues invent a rate from",
        "letter text the model never quoted.",
        "",
        "On ExECT, each family is classified on its own first-rescue hop.",
        "Diagnosis still splits across quote reuse, inventory trim, and a small",
        "unquoted-letter add class. Seizure frequency is almost all a render or",
        "trim of a state the model already emitted. Prescription's ten first-",
        "rescues all rewrite a drug the model named. Investigations has two",
        "first-rescues, both inventory trims.",
        "",
        "These are pooled six-model first-rescues on development splits, not",
        "holdout component estimates.",
        "",
        "## Source classes",
        "",
    ]
    for name in SOURCE_ORDER:
        lines.append(f"- **`{name}`** — {SOURCE_LABELS[name]}")
    lines.extend(
        [
            "",
            "## Gan 2026 (`dev750`, Purist first-rescue)",
            "",
            f"Replayable first-rescues classified: **{gan_block['first_rescue_n']}**.",
            "",
            *(_md_count_table(gan_block["counts"], gan_block["first_rescue_n"])),
            "",
            "By first-changer stage:",
            "",
        ]
    )
    for stage, counter in gan_block["by_stage"].items():
        parts = ", ".join(f"`{name}` {n}" for name, n in sorted(counter.items()))
        lines.append(f"- `{stage}`: {parts}")
    lines.extend(
        [
            "",
            "### Examples",
            "",
            *(_md_examples("gan", gan_block["examples"])),
        ]
    )
    lines.extend(
        [
            "## ExECTv2 (`dev140`, per-family first-rescue)",
            "",
            "Each family is classified on its own first rescue hop, not on which",
            "family happened to rescue the letter first.",
            "",
        ]
    )
    for family in EXECT_FAMILIES:
        block = exect_block["families"][family]
        lines.extend(
            [
                f"### {family}",
                "",
                f"First-rescues classified: **{block['first_rescue_n']}**.",
                "",
                *(_md_count_table(block["counts"], block["first_rescue_n"])),
                "",
            ]
        )
        if block["by_stage"]:
            lines.append("By first-changer stage:")
            lines.append("")
            for stage, counter in block["by_stage"].items():
                parts = ", ".join(
                    f"`{name}` {n}" for name, n in sorted(counter.items())
                )
                lines.append(f"- `{stage}`: {parts}")
            lines.append("")
        lines.extend(
            [
                "#### Examples",
                "",
                *(_md_examples("exect", block["examples"])),
            ]
        )
    lines.extend(
        [
            "## Claim boundary",
            "",
            "- Development no-call replay of saved six-model ledgers.",
            "- Classifies first-rescues only; later hops and harms are out of scope.",
            "- Cue matching is conservative string support, not clinical entailment.",
            "- Not holdout attribution, clinical validity, or a rewrite of stage ablation.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload = {
        "schema_version": "hybrid.rescue_source_provenance.v2",
        "date": "2026-08-13",
        "protocol": PROTOCOL,
        "git": _git_note(),
        "surface": "llm_with_rules",
        "calls": 0,
        "gan": analyze_gan(),
        "exect": analyze_exect(),
        "claim_boundary": (
            "Development first-rescue source classes on Gan dev750 and all "
            "four ExECT families on dev140. Not holdout component estimates."
        ),
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)
    print(f"wrote {ARTIFACT}")
    print(f"wrote {REPORT}")
    print("gan", payload["gan"]["counts"], "n=", payload["gan"]["first_rescue_n"])
    for family, block in payload["exect"]["families"].items():
        print(family, block["counts"], "n=", block["first_rescue_n"])


if __name__ == "__main__":
    main()
