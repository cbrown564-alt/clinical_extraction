"""Residual-panel GPT-4.1-mini experiments for ExECTv2 Diagnosis Phase 2."""

from __future__ import annotations
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.diagnosis_verification import (
    reconciler,
    verifier as verifier_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    _has_blocking_parse_issue,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _concept_keys as concept_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        score_concept_identity,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_diagnosis_phase2_residual_panel_v0.1"
PIPELINE_FAMILY = "exectv2_diagnosis_phase2_residual_panel"
COMPONENT_OWNER = "diagnosis_phase2_residual_panel"
Variant = Literal["candidate_selector", "direct_rereader"]
VARIANTS: tuple[Variant, ...] = ("candidate_selector", "direct_rereader")

RESIDUAL_FAMILY_ORDER: tuple[str, ...] = (
    "generic_epilepsy",
    "tonic_clonic",
    "focal_family",
    "secondary_generalised",
    "syndrome_structural",
    "other_diagnosis",
)


@dataclass(frozen=True)
class PanelItem:
    letter_id: str
    rank: int
    residual_families: tuple[str, ...]
    reasons: tuple[str, ...]


class ExECTv2DiagnosisPhase2Signature(dspy.Signature):
    """Resolve Diagnosis residuals for one ExECTv2 letter."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one letter, diagnosis policy, variant, and candidates."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}. No markdown fences."
        )
    )


class DspyDiagnosisPhase2Panel(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2DiagnosisPhase2Signature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_panel_from_ledger(
    ledger_path: Path,
    *,
    panel_size: int = 32,
) -> list[PanelItem]:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    records = [
        dict(record)
        for record in ledger.get("records", [])
        if record.get("entity") == DIAGNOSIS.name
    ]
    return select_panel(records, panel_size=panel_size)


def select_panel(
    records: Sequence[Mapping[str, Any]],
    *,
    panel_size: int = 32,
) -> list[PanelItem]:
    """Select a deterministic residual-enriched panel from Diagnosis ledger rows."""

    by_family: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    all_reasons: dict[str, list[str]] = defaultdict(list)
    all_families: dict[str, set[str]] = defaultdict(set)
    for record in sorted(
        records,
        key=lambda r: (
            str(r.get("letter_id", "")),
            str(r.get("side", "")),
            str(r.get("key", "")),
        ),
    ):
        letter_id = str(record.get("letter_id", ""))
        if not letter_id:
            continue
        family = residual_family(record)
        by_family[family].append(record)
        all_families[letter_id].add(family)
        all_reasons[letter_id].append(_reason(record, family))

    selected: list[str] = []
    selected_set: set[str] = set()
    exhausted = False
    cursor = 0
    while len(selected) < panel_size and not exhausted:
        exhausted = True
        for family in RESIDUAL_FAMILY_ORDER:
            bucket = by_family.get(family, [])
            if cursor >= len(bucket):
                continue
            exhausted = False
            letter_id = str(bucket[cursor].get("letter_id", ""))
            if letter_id and letter_id not in selected_set:
                selected.append(letter_id)
                selected_set.add(letter_id)
                if len(selected) >= panel_size:
                    break
        cursor += 1

    return [
        PanelItem(
            letter_id=letter_id,
            rank=index + 1,
            residual_families=tuple(
                family for family in RESIDUAL_FAMILY_ORDER if family in all_families[letter_id]
            ),
            reasons=tuple(dict.fromkeys(all_reasons[letter_id])),
        )
        for index, letter_id in enumerate(selected)
    ]


def residual_family(record: Mapping[str, Any]) -> str:
    text = normalize_phrase(
        " ".join(
            str(record.get(key, ""))
            for key in ("key", "example_text", "evidence", "note_excerpt")
        )
    )
    if any(term in text for term in ("tonic clonic", "tonic chronic")):
        return "tonic_clonic"
    if any(
        term in text
        for term in (
            "focal epilepsy",
            "focal seizures",
            "focal onset",
            "temporal lobe",
            "complex partial",
            "dyscognitive",
        )
    ):
        return "focal_family"
    if "secondary generalised" in text or "secondary generalized" in text:
        return "secondary_generalised"
    if any(
        term in text
        for term in (
            "symptomatic",
            "structural",
            "juvenile myoclonic",
            "myoclonic epilepsy",
            "intractable",
        )
    ):
        return "syndrome_structural"
    if "epilepsy" in text:
        return "generic_epilepsy"
    return "other_diagnosis"


def build_prompt_input(
    letter: ExectLetter,
    *,
    variant: Variant,
    current_mentions: Sequence[Mapping[str, Any]],
    verifier_mentions: Sequence[Mapping[str, Any]],
    decomposer_mentions: Sequence[Mapping[str, Any]],
    diagnosis_spans: Sequence[Mapping[str, Any]],
) -> str:
    candidate_groups = reconciler.candidate_concept_groups(
        verifier_mentions=[*current_mentions, *verifier_mentions],
        decomposer_mentions=decomposer_mentions,
        diagnosis_spans=diagnosis_spans,
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "variant": variant,
        "task": _task_for_variant(variant),
        "strict_constraints": [
            "Return final Diagnosis mentions only.",
            "Use exact source substrings for evidence; unsupported mentions are dropped.",
            "Do not include CUI or CUIPhrase in attributes.",
            (
                "Do not emit seizure-frequency facts as Diagnosis unless the source "
                "asserts a diagnosis or seizure type."
            ),
            "Do not infer structural or symptomatic epilepsy from imaging or history alone.",
        ],
        "candidate_sources": {
            "current_v02_mentions": list(current_mentions),
            "verifier_mentions": list(verifier_mentions),
            "decomposer_mentions": list(decomposer_mentions),
            "diagnosis_candidate_spans": list(diagnosis_spans),
        },
        "candidate_concept_groups": candidate_groups,
        "diagnosis_policy": {
            "generic_epilepsy": (
                "Emit generic epilepsy only when patient-level established epilepsy is "
                "directly asserted. Reject section headers, clinic names, family history, "
                "or medication context alone."
            ),
            "tonic_clonic": (
                "Keep tonic-clonic concepts only when they are asserted as the patient's "
                "diagnosis/seizure type, not merely as episode frequency or historical "
                "description."
            ),
            "focal_family": (
                "Recover focal epilepsy or focal seizure concepts when the evidence "
                "directly asserts them, including compact diagnosis headings."
            ),
            "secondary_generalised": (
                "Preserve secondary-generalised concepts when directly asserted; do not "
                "collapse them to tonic-clonic unless separate evidence says so."
            ),
            "certainty": (
                "Use Certainty 5 for unqualified established assertions, 4 for probable "
                "or likely, and 3 for possible/query/suspected."
            ),
        },
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean core Diagnosis concept phrase.",
                    "attributes": {
                        "DiagCategory": "Epilepsy | MultipleSeizures | SingleSeizure",
                        "Certainty": "1 | 2 | 3 | 4 | 5",
                        "Negation": "Affirmed | Negated",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "attribute_vocabulary": verifier_base._attribute_vocabulary(),
        "worked_examples": verifier_base._worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
    variant: Variant,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions,
        note_text=note_text,
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[DIAGNOSIS.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{DIAGNOSIS.name}: dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{DIAGNOSIS.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "variant": variant,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def run_panel(
    letters: Sequence[ExectLetter],
    *,
    panel: Sequence[PanelItem],
    current_rows: Sequence[Mapping[str, Any]],
    verifier_rows: Sequence[Mapping[str, Any]],
    decomposer_rows: Sequence[Mapping[str, Any]],
    variants: Sequence[Variant] = VARIANTS,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    progress_every: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyDiagnosisPhase2Panel()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    letters_by_id = {letter.letter_id: letter for letter in letters}
    panel = [item for item in panel if item.letter_id in letters_by_id]
    panel_ids = [item.letter_id for item in panel]
    current_by_id = reconciler.mentions_by_letter(current_rows)
    verifier_by_id = reconciler.mentions_by_letter(verifier_rows)
    decomposer_by_id = reconciler.mentions_by_letter(decomposer_rows)
    spans_by_id = reconciler.spans_by_letter(decomposer_rows)
    panel_by_id = {item.letter_id: item for item in panel}

    requested = [f"{variant}:{letter_id}" for variant in variants for letter_id in panel_ids]
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="row_id",
    )
    rows: list[dict[str, Any]] = [
        row for row in existing_rows if str(row.get("row_id", "")) in set(requested)
    ]
    n_resumed = len(rows)

    processed_new = 0
    for variant in variants:
        for letter_id in panel_ids:
            row_id = f"{variant}:{letter_id}"
            if row_id in completed:
                continue
            letter = letters_by_id[letter_id]
            item = panel_by_id[letter_id]
            current_mentions = current_by_id.get(letter_id, [])
            verifier_mentions = verifier_by_id.get(letter_id, [])
            decomposer_mentions = decomposer_by_id.get(letter_id, [])
            diagnosis_spans = spans_by_id.get(letter_id, [])
            prompt_input_json = build_prompt_input(
                letter,
                variant=variant,
                current_mentions=current_mentions,
                verifier_mentions=verifier_mentions,
                decomposer_mentions=decomposer_mentions,
                diagnosis_spans=diagnosis_spans,
            )
            raw_output = ""
            call_error: str | None = None
            if mode == "live":
                try:
                    prediction = program(prompt_input_json=prompt_input_json)
                    raw_output = str(prediction.extraction_json)
                except Exception as exc:  # pragma: no cover
                    call_error = f"{type(exc).__name__}: {exc}"

            extraction, parse_errors = (
                parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
            )
            mentions = extraction.mentions if extraction else []
            predicted_letter, gate_warnings = to_predicted_letter(
                letter_id,
                mentions,
                note_text=letter.note_text,
                variant=variant,
            )
            rows.append(
                {
                    "row_id": row_id,
                    "letter_id": letter_id,
                    "split": split,
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "variant": variant,
                    "model": model,
                    "mode": mode,
                    "panel_rank": item.rank,
                    "panel_residual_families": list(item.residual_families),
                    "panel_reasons": list(item.reasons),
                    "current_v02_mentions": list(current_mentions),
                    "verifier_mentions": list(verifier_mentions),
                    "decomposer_mentions": list(decomposer_mentions),
                    "diagnosis_spans": list(diagnosis_spans),
                    "prompt_input_json": prompt_input_json,
                    "raw_output": raw_output,
                    "call_error": call_error,
                    "parse_errors": parse_errors,
                    "gate_warnings": gate_warnings,
                    "n_current_mentions": len(current_mentions),
                    "n_verifier_mentions": len(verifier_mentions),
                    "n_decomposer_mentions": len(decomposer_mentions),
                    "n_diagnosis_spans": len(diagnosis_spans),
                    "n_mentions_raw": len(mentions),
                    "n_mentions_scored": len(predicted_letter.mentions),
                    "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                    "predicted_mentions": [
                        _mention_to_row(mention) for mention in predicted_letter.mentions
                    ],
                    "gold_mentions": [
                        {"text": a.text, "attributes": dict(a.attributes)}
                        for a in letter.entities(DIAGNOSIS.name)
                    ],
                }
            )
            processed_new += 1
            if progress_every and processed_new % progress_every == 0:
                _emit_checkpoint(
                    rows,
                    current_rows=current_rows,
                    panel_ids=panel_ids,
                    total=len(requested),
                    jsonl_path=checkpoint_jsonl_path,
                    report_path=checkpoint_report_path,
                    split=split,
                    model=model,
                    mode=mode,
                )

    rows = merge_rows(rows, requested, key="row_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_panel_letters": len(panel_ids),
        "n_rows": len(rows),
        "n_resumed": n_resumed,
        "variants": list(variants),
        "panel": [item.__dict__ for item in panel],
        "summary": summarize_rows(rows, current_rows=current_rows, panel_ids=panel_ids),
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    return rows, metadata


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    current_rows: Sequence[Mapping[str, Any]],
    panel_ids: Sequence[str],
) -> dict[str, Any]:
    baseline = _baseline_rows(current_rows, panel_ids=panel_ids)
    baseline_score = _score_rows(baseline)
    summary: dict[str, Any] = {
        "panel_letters": len(panel_ids),
        "baseline_v02": baseline_score,
        "variant_scores": {},
    }
    for variant in VARIANTS:
        variant_rows = [dict(row) for row in rows if row.get("variant") == variant]
        if not variant_rows:
            continue
        score = _score_rows(variant_rows)
        score["delta_f1_vs_v02"] = round(
            score["f1"] - baseline_score.get("f1", 0.0),
            4,
        )
        score["call_failures"] = sum(bool(row.get("call_error")) for row in variant_rows)
        score["parse_failures"] = sum(
            _has_blocking_parse_issue(row.get("parse_errors")) for row in variant_rows
        )
        n_raw = sum(int(row.get("n_mentions_raw", 0)) for row in variant_rows)
        n_invalid = sum(int(row.get("n_evidence_invalid", 0)) for row in variant_rows)
        score["n_mentions_raw"] = n_raw
        score["n_mentions_scored"] = sum(
            int(row.get("n_mentions_scored", 0)) for row in variant_rows
        )
        score["n_evidence_invalid"] = n_invalid
        score["evidence_validity_rate"] = (
            round((n_raw - n_invalid) / n_raw, 4) if n_raw else 1.0
        )
        score["changed_rows_vs_v02"] = _changed_row_count(
            variant_rows,
            current_rows=current_rows,
        )
        summary["variant_scores"][variant] = score
    family_counts: Counter[str] = Counter()
    if rows:
        first_variant = rows[0].get("variant")
        for row in rows:
            if row.get("variant") == first_variant:
                family_counts.update(str(f) for f in row.get("panel_residual_families", []))
    summary["panel_residual_family_counts"] = dict(family_counts)
    return summary


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    current_rows: Sequence[Mapping[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary", {})
    baseline = summary.get("baseline_v02", {})
    lines = [
        "# ExECTv2 Diagnosis Phase 2 Residual Panel",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Panel letters: {summary.get('panel_letters', 0)}",
        "",
        "## Panel Control",
        "",
        "| Control | F1 | P | R | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        _score_table_row("v02", baseline),
        "",
        "## Variant Results",
        "",
        "| Variant | F1 | Delta | P | R | TP | FP | FN | Calls | Parses | Evidence | Changed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, score in summary.get("variant_scores", {}).items():
        lines.append(
            f"| {variant} | {score.get('f1', 0):.3f} | "
            f"{score.get('delta_f1_vs_v02', 0):+.3f} | "
            f"{score.get('precision', 0):.3f} | {score.get('recall', 0):.3f} | "
            f"{score.get('tp', 0)} | {score.get('fp', 0)} | {score.get('fn', 0)} | "
            f"{score.get('call_failures', 0)} | {score.get('parse_failures', 0)} | "
            f"{score.get('evidence_validity_rate', 0):.3f} | "
            f"{score.get('changed_rows_vs_v02', 0)} |"
        )
    lines.extend(["", "## Residual Family Mix", ""])
    lines.extend(_panel_table(metadata.get("panel", [])))
    lines.extend(["", "## Changed Row Sample", ""])
    lines.extend(_changed_rows_table(rows, current_rows=current_rows, limit=20))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _task_for_variant(variant: Variant) -> str:
    if variant == "candidate_selector":
        return (
            "Adjudicate fixed Diagnosis candidates. Keep, reject, or edit candidate "
            "concepts only when the exact evidence supports the decision. Do not "
            "invent a concept that has no support in current, verifier, decomposer, "
            "or diagnosis-span candidates."
        )
    return (
        "Re-read the note for Diagnosis. You may emit new Diagnosis concepts from "
        "the letter text, but every emitted concept needs exact evidence and must "
        "satisfy the Diagnosis policy."
    )


def _score_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    score = score_concept_identity(
        _letters_from_rows(rows, key="gold_mentions"),
        _letters_from_rows(rows, key="predicted_mentions"),
        DIAGNOSIS.name,
    ).concept_assertion
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
        "precision_tp": score.precision_tp,
        "recall_tp": score.recall_tp,
        "pred_count": score.pred_count,
        "gold_count": score.gold_count,
    }


def _baseline_rows(
    current_rows: Sequence[Mapping[str, Any]],
    *,
    panel_ids: Sequence[str],
) -> list[dict[str, Any]]:
    current_by_id = {str(row["letter_id"]): row for row in current_rows}
    return [
        {
            "letter_id": letter_id,
            "gold_mentions": [
                m
                for m in current_by_id[letter_id].get("gold_mentions", [])
                if m.get("entity", DIAGNOSIS.name) == DIAGNOSIS.name
            ],
            "predicted_mentions": [
                m
                for m in current_by_id[letter_id].get("predicted_mentions", [])
                if m.get("entity", DIAGNOSIS.name) == DIAGNOSIS.name
            ],
        }
        for letter_id in panel_ids
        if letter_id in current_by_id
    ]


def _letters_from_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    key: str,
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = []
        for mention in row.get(key, []):
            entity = str(mention.get("entity", DIAGNOSIS.name))
            if entity != DIAGNOSIS.name:
                continue
            annotations.append(
                ExectAnnotation(
                    entity=DIAGNOSIS.name,
                    text=str(mention.get("text", "")),
                    attributes={
                        str(k): str(v)
                        for k, v in dict(mention.get("attributes") or {}).items()
                    },
                )
            )
        letters.append(
            ExectLetter(
                letter_id=str(row.get("letter_id", "")),
                note_text="",
                annotations=tuple(annotations),
            )
        )
    return letters


def _changed_row_count(
    rows: Sequence[Mapping[str, Any]],
    *,
    current_rows: Sequence[Mapping[str, Any]],
) -> int:
    current_by_id = {str(row["letter_id"]): row for row in current_rows}
    changed = 0
    for row in rows:
        letter_id = str(row.get("letter_id", ""))
        before = _diagnosis_keys(current_by_id.get(letter_id, {}).get("predicted_mentions", []))
        after = _diagnosis_keys(row.get("predicted_mentions", []))
        if before != after:
            changed += 1
    return changed


def _diagnosis_keys(mentions: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    annotations = [
        ExectAnnotation(
            entity=DIAGNOSIS.name,
            text=str(mention.get("text", "")),
            attributes={str(k): str(v) for k, v in dict(mention.get("attributes") or {}).items()},
        )
        for mention in mentions
        if mention.get("entity", DIAGNOSIS.name) == DIAGNOSIS.name
    ]
    return tuple(sorted(str(key) for key in concept_keys(annotations, DIAGNOSIS.name, "assertion")))


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    row = verifier_base._mention_to_row(mention)
    row["component_owner"] = mention.component_owner
    return row


def _reason(record: Mapping[str, Any], family: str) -> str:
    return (
        f"{family}:{record.get('side')}:{record.get('example_text')} "
        f"{record.get('key')}"
    )


def _score_table_row(label: str, score: Mapping[str, Any]) -> str:
    return (
        f"| {label} | {score.get('f1', 0):.3f} | {score.get('precision', 0):.3f} | "
        f"{score.get('recall', 0):.3f} | {score.get('tp', 0)} | "
        f"{score.get('fp', 0)} | {score.get('fn', 0)} |"
    )


def _panel_table(panel: Sequence[Any]) -> list[str]:
    lines = [
        "| Rank | Letter | Families | Reasons |",
        "| ---: | --- | --- | --- |",
    ]
    for item in panel:
        if hasattr(item, "__dict__"):
            item = item.__dict__
        reasons = "; ".join(str(reason) for reason in item.get("reasons", [])[:3])
        lines.append(
            f"| {item.get('rank')} | {item.get('letter_id')} | "
            f"{', '.join(item.get('residual_families', []))} | {reasons} |"
        )
    return lines


def _changed_rows_table(
    rows: Sequence[Mapping[str, Any]],
    *,
    current_rows: Sequence[Mapping[str, Any]],
    limit: int,
) -> list[str]:
    current_by_id = {str(row["letter_id"]): row for row in current_rows}
    lines = [
        "| Variant | Letter | Families | Gold | v02 | Variant |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    n = 0
    for row in rows:
        letter_id = str(row.get("letter_id", ""))
        current = current_by_id.get(letter_id, {})
        before = _diagnosis_keys(current.get("predicted_mentions", []))
        after = _diagnosis_keys(row.get("predicted_mentions", []))
        if before == after:
            continue
        gold = _diagnosis_keys(row.get("gold_mentions", []))
        lines.append(
            f"| {row.get('variant')} | {letter_id} | "
            f"{', '.join(row.get('panel_residual_families', []))} | "
            f"{_short_keys(gold)} | {_short_keys(before)} | {_short_keys(after)} |"
        )
        n += 1
        if n >= limit:
            break
    if n == 0:
        lines.append("| none | - | - | - | - | - |")
    return lines


def _short_keys(keys: Sequence[str], *, max_items: int = 4) -> str:
    values = [key.replace("|", "/") for key in keys[:max_items]]
    suffix = " ..." if len(keys) > max_items else ""
    return "<br>".join(values) + suffix


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    current_rows: Sequence[Mapping[str, Any]],
    panel_ids: Sequence[str],
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        metadata = {
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "split": split,
            "model": model,
            "mode": mode,
            "summary": summarize_rows(
                rows,
                current_rows=current_rows,
                panel_ids=panel_ids,
            ),
        }
        write_report(
            rows,
            metadata,
            report_path,
            jsonl_path=jsonl_path,
            current_rows=current_rows,
        )
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": sum(bool(row.get("call_error")) for row in rows),
                "parse_failures": sum(
                    _has_blocking_parse_issue(row.get("parse_errors")) for row in rows
                ),
            },
            sort_keys=True,
        ),
        flush=True,
    )
