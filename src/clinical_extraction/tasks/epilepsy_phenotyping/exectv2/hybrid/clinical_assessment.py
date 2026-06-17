"""Hybrid SeizureFrequency extractor — clinical assessment over a candidate set.

The reset-native hybrid (satellite 04). A deterministic stage builds a live,
high-recall candidate set (``candidate_set.py``); the LLM **selects and judges**
among those candidates and assigns the clinical interpretation; a deterministic
stage normalizes and renders the attribute values (shared normalizer + CUI
lexicon); a verify/route stage gates evidence and plausibility.

Architecture family: hybrid. Contribution thesis: representation/normalization
and format are deterministic; clinical judgment (which candidate is real, current
vs historical, seizure-free vs active, cluster cadence vs intra-cluster rate) is
the LLM's. The LLM does not parse open text and does not format attribute values.
"""

from __future__ import annotations

import ast
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
    EntitySpec,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    SF_BENCHMARK,
    SF_SEMANTIC,
    EntityScore,
    score_entity,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

from ..contract.prediction import to_exect_letter
from ..deterministic.normalizer import normalize_count, normalize_month, normalize_unit
from ..llm.llm_only_single_pass import _extract_json_object, repair_attributes
from .candidate_set import (
    SFCandidate,
    build_candidate_set,
    candidate_set_as_payload,
)
from .verify_route import RoutedMention, routed_taxonomy, verify_and_route

PROMPT_VERSION = "exectv2_hybrid_candidate_assessment_v0.2"
ENTITY_NAME = SEIZURE_FREQUENCY.name
COMPONENT_OWNER = "hybrid_candidate_assessment"

# Closed vocabularies the assessment LLM may draw from (satellite 04 §3 / 07).
UNCERTAINTY_FLAGS: frozenset[str] = frozenset({
    "current_vs_historical_ambiguous",
    "vague_count",
    "conditional_window",
    "competing_current_claims",
    "cluster_vs_intracluster",
    "seizure_free_duration_unclear",
    "range_window_ambiguous",
})
AGGREGATION_POLICIES: frozenset[str] = frozenset({
    "one_mention_per_seizure_type",
    "merge_co_located_statements",
    "split_per_statement",
})
_DEFAULT_AGGREGATION = "one_mention_per_seizure_type"


# ── Output schema ────────────────────────────────────────────────────────────


class CandidateAssessment(BaseModel):
    """The LLM's verdict on one offered candidate."""

    model_config = ConfigDict(extra="ignore")

    candidate_id: str = ""
    keep: bool = False
    text: str = ""
    attributes: dict[str, Any] = {}
    confidence: Literal["low", "medium", "high"] = "medium"
    uncertainty_flags: list[str] = []
    rationale: str = ""


class AdditionalMention(BaseModel):
    """A real mention the candidate set missed (optional LLM recall)."""

    model_config = ConfigDict(extra="ignore")

    text: str = ""
    attributes: dict[str, Any] = {}
    evidence: str = ""
    confidence: Literal["low", "medium", "high"] = "medium"
    uncertainty_flags: list[str] = []
    rationale: str = ""


class AssessmentRecord(BaseModel):
    """Full assessment output for one letter."""

    model_config = ConfigDict(extra="ignore")

    assessments: list[CandidateAssessment] = []
    additional_mentions: list[AdditionalMention] = []
    aggregation_policy: str = _DEFAULT_AGGREGATION


# ── DSPy program ──────────────────────────────────────────────────────────────


class ExECTv2HybridAssessmentSignature(dspy.Signature):
    """Review pre-extracted seizure findings from one clinical letter and decide
    which are genuine seizure frequency facts.

    You are given the letter and a list of candidate seizure-type phrases, each
    with the surrounding sentence and a draft of its frequency details. Keep the
    candidates that are real seizure-frequency statements, correct their details,
    and add any genuine statement the list missed.

    Return a strict JSON object with keys 'assessments', 'additional_mentions',
    and 'aggregation_policy'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON with one clinical letter, candidate findings, and task instructions."
    )
    assessment_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"assessments\": [{\"candidate_id\": ..., "
            "\"keep\": true/false, \"text\": ..., \"attributes\": {...}, "
            "\"confidence\": ..., \"uncertainty_flags\": [...], \"rationale\": ...}], "
            "\"additional_mentions\": [...], \"aggregation_policy\": ...}"
        )
    )


class DspyHybridAssessor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.assess = dspy.Predict(ExECTv2HybridAssessmentSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.assess(prompt_input_json=prompt_input_json)


# ── Prompt builder ────────────────────────────────────────────────────────────


def build_prompt_input(letter: ExectLetter, candidates: Sequence[SFCandidate]) -> str:
    """Build the assessment prompt payload for one letter + its candidate set.

    Hygiene (ADR 0015): a plain clinical brief, no internal architecture
    vocabulary. The model is told it is reviewing a draft list of findings.
    """
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "You are reviewing a draft list of seizure-frequency findings pulled "
            "from one clinical letter. For each candidate, decide whether it is a "
            "genuine seizure-frequency statement. Keep the real ones, fix their "
            "frequency details, and add any genuine statement the draft missed. "
            "Return one JSON object."
        ),
        "how_to_decide": [
            (
                "Keep a candidate only if the letter gives it real frequency "
                "information: a count with a time period, a date, a relative "
                "change (more/fewer/the same), or a seizure-free statement."
            ),
            (
                "Drop a candidate that names a seizure type but has no frequency "
                "information attached (set keep=false). A bare seizure type with "
                "no rate, change, or date is not a frequency statement."
            ),
            (
                "Each distinct seizure type with its own frequency gets its own "
                "kept candidate. Keep current and clearly historical statements "
                "as separate findings."
            ),
            (
                "If the letter states a genuine frequency for a seizure type that "
                "is not in the candidate list, add it under 'additional_mentions' "
                "with an exact-substring 'evidence' span."
            ),
            (
                "The draft frequency details attached to each candidate are usually "
                "correct. Keep them as they are unless the letter clearly shows a "
                "different count, period, change, or date — then correct only what "
                "is wrong. Do not add details the letter does not state."
            ),
        ],
        "field_definitions": {
            "candidate_id": "Echo the id of the candidate you are judging.",
            "keep": "true if this candidate is a genuine seizure-frequency finding.",
            "text": (
                "The seizure-type anchor phrase as it appears in the letter — the "
                "SHORT noun phrase (2 to 6 words), e.g. 'focal seizures', "
                "'generalised tonic-clonic seizures', 'absences', 'seizure-free'. "
                "Must be an exact substring of the letter. Usually the candidate's "
                "own anchor phrase; correct it only if the candidate's phrase is wrong."
            ),
            "attributes": (
                "The corrected coded frequency details for this seizure type. "
                "Use only the listed attribute names and values. Correct the draft "
                "where it is wrong; include only details the letter supports."
            ),
            "confidence": (
                "'high': one unambiguous frequency fact, exact count and period. "
                "'medium': frequency clear but vague count, conditional, or only a "
                "relative change. 'low': competing current claims you cannot resolve."
            ),
            "uncertainty_flags": (
                "Zero or more flags from the allowed list naming what is uncertain."
            ),
            "rationale": "One sentence: the deciding evidence and coded result.",
            "aggregation_policy": (
                "How you grouped statements into findings — one value from the "
                "allowed list."
            ),
        },
        "attribute_vocabulary": {
            "NumberOfSeizures": "single count as string, e.g. '2'; '0' for seizure-free",
            "LowerNumberOfSeizures": "lower end of a count range, e.g. '2' for '2 to 4 per month'",
            "UpperNumberOfSeizures": "upper end of a count range, e.g. '4' for '2 to 4 per month'",
            "NumberOfTimePeriods": "period length as string, usually '1'",
            "LowerNumberOfTimePeriods": (
                "lower end of a period range, e.g. '2' for 'every 2 to 3 weeks'"
            ),
            "UpperNumberOfTimePeriods": "upper end of a period range",
            "TimePeriod": "exactly 'Day', 'Week', 'Month', or 'Year'",
            "FrequencyChange": (
                "exactly one of 'Decreased', 'Frequent', 'Increased', "
                "'Infrequent', 'Same'"
            ),
            "PointInTime": (
                "exactly one of 'Birthday', 'DrugChange', 'LastClinic', "
                "'Last_Month', 'Last_Week', 'Last_Year', 'Surgery'"
            ),
            "TimeSince_or_TimeOfEvent": "exactly 'During' or 'Since'",
            "DayDate": "day of month as string",
            "MonthDate": "month as string",
            "YearDate": "4-digit year as string",
            "AgeLower": "lower age bound as string",
            "AgeUpper": "upper age bound as string",
            "AgeUnit": "exactly 'Year' or 'Month'",
        },
        "allowed_uncertainty_flags": sorted(UNCERTAINTY_FLAGS),
        "allowed_aggregation_policies": sorted(AGGREGATION_POLICIES),
        "clinical_rules": [
            (
                "Seizure-free: keep 'seizure-free' as the text anchor and set "
                "NumberOfSeizures='0'. Only add a duration (NumberOfTimePeriods + "
                "TimePeriod) and TimeSince_or_TimeOfEvent='Since' when the letter "
                "states how long or names a trigger event (then add PointInTime). "
                "If the letter just says 'seizure-free' with no duration, use "
                "NumberOfSeizures='0' alone."
            ),
            (
                "Count ranges: '2 to 4 per month' gives LowerNumberOfSeizures='2', "
                "UpperNumberOfSeizures='4', NumberOfTimePeriods='1', TimePeriod='Month'."
            ),
            (
                "Period gaps: 'one every 3 weeks' gives NumberOfSeizures='1', "
                "NumberOfTimePeriods='3', TimePeriod='Week'. 'one every 3 to 4 weeks' "
                "gives NumberOfSeizures='1', LowerNumberOfTimePeriods='3', "
                "UpperNumberOfTimePeriods='4', TimePeriod='Week'. The number of weeks "
                "is the period count, NOT NumberOfTimePeriods='1'."
            ),
            (
                "A count tied to a specific calendar date (a month and/or year, e.g. "
                "'6 to 9 seizures in August 2017') is a dated event: use the count "
                "plus MonthDate / YearDate and TimeSince_or_TimeOfEvent. Do NOT also "
                "add NumberOfTimePeriods / TimePeriod unless the letter states a "
                "recurring rate as well."
            ),
            (
                "Cluster cadence ('clusters every 3 weeks') is a frequency. Events "
                "within a single cluster day are not the same as daily ongoing events "
                "— flag 'cluster_vs_intracluster' if unsure which is meant."
            ),
            (
                "Extract a conditional or triggered window as stated; do not infer "
                "an unconditional overall rate from it — flag 'conditional_window'."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "candidates": candidate_set_as_payload(candidates),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


# ── Parser ────────────────────────────────────────────────────────────────────


def _loads_lenient(text: str) -> tuple[Any, str | None]:
    """Load a JSON object, tolerating Python-dict-style model output.

    Some models (notably qwen3.6) emit the object as a Python literal — single
    quotes, ``True``/``False``/``None`` — which strict JSON rejects. Falling back
    to ``ast.literal_eval`` recovers the structure without touching any value
    (semantically-neutral repair). Returns (obj, note) where note is a coercion
    breadcrumb or None.
    """
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        try:
            obj = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return None, f"invalid_json: {exc.msg}"
        if isinstance(obj, dict):
            return obj, "repaired_python_dict_literal"
        return None, f"invalid_json: {exc.msg}"


def parse_assessment_json(
    raw_output: str,
) -> tuple[AssessmentRecord | None, list[str]]:
    """Parse and schema-validate one assessment output string."""
    payload, load_note = _loads_lenient(_extract_json_object(raw_output))
    if payload is None:
        return None, [load_note or "invalid_json: unparseable"]

    payload, coerce_notes = _coerce_assessment_payload(payload)
    errors: list[str] = ([load_note] if load_note else []) + list(coerce_notes)

    try:
        record = AssessmentRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def _coerce_assessment_payload(payload: Any) -> tuple[Any, list[str]]:
    """Stringify attribute values across assessments and additional mentions."""
    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes

    def _coerce_attrs(obj: Any, where: str) -> Any:
        if not isinstance(obj, dict):
            return obj
        attrs = obj.get("attributes")
        if not isinstance(attrs, dict):
            return obj
        new_attrs: dict[str, str] = {}
        for k, v in attrs.items():
            if v is None:
                continue
            str_v = str(v)
            if str_v != v:
                notes.append(f"coerced_attribute_value: {where} {k!r} {v!r} -> {str_v!r}")
            new_attrs[str(k)] = str_v
        return {**obj, "attributes": new_attrs}

    out = dict(payload)
    if isinstance(out.get("assessments"), list):
        out["assessments"] = [
            _coerce_attrs(a, f"assessment[{i}]") for i, a in enumerate(out["assessments"])
        ]
    if isinstance(out.get("additional_mentions"), list):
        out["additional_mentions"] = [
            _coerce_attrs(m, f"additional[{i}]")
            for i, m in enumerate(out["additional_mentions"])
        ]
    return out, notes


# ── Deterministic normalize / render ──────────────────────────────────────────

_COUNT_KEYS = (
    "NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures",
    "NumberOfTimePeriods", "LowerNumberOfTimePeriods", "UpperNumberOfTimePeriods",
)


def normalize_attributes(attrs: dict[str, str]) -> dict[str, str]:
    """Deterministic normalize: coerce LLM-supplied values to canonical forms.

    The shared epilepsy normalizer owns representation; the LLM should not have
    to get casing/number-word formatting right. Illegal keys/values are stripped
    afterwards by ``repair_attributes``.
    """
    out = dict(attrs)
    for key in _COUNT_KEYS:
        if key in out:
            out[key] = normalize_count(out[key])
    if "TimePeriod" in out:
        out["TimePeriod"] = normalize_unit(out["TimePeriod"])
    if "MonthDate" in out:
        out["MonthDate"] = normalize_month(out["MonthDate"])
    return out


def _filter_flags(flags: Sequence[str]) -> tuple[tuple[str, ...], list[str]]:
    kept = tuple(f for f in flags if f in UNCERTAINTY_FLAGS)
    dropped = [f"dropped_uncertainty_flag: {f!r}" for f in flags if f not in UNCERTAINTY_FLAGS]
    return kept, dropped


def render_mentions(
    letter: ExectLetter,
    candidates: Sequence[SFCandidate],
    record: AssessmentRecord,
    *,
    spec: EntitySpec,
) -> tuple[list[PredictedMention], list[str]]:
    """Build PredictedMentions from kept assessments + additional mentions.

    Deterministic normalize + CUI render; attribute repair (neutral). Returns
    (mentions, warnings) before the verify/route gate.
    """
    note_text = letter.note_text
    by_id = {c.candidate_id: c for c in candidates}
    warnings: list[str] = []
    mentions: list[PredictedMention] = []

    for a in record.assessments:
        if not a.keep:
            continue
        cand = by_id.get(a.candidate_id)
        # Candidate anchor representation is deterministic. The LLM judges and
        # corrects attributes; letting it rewrite the anchor can turn a valid
        # candidate into a non-gold phrase such as "seizures per year".
        text = cand.anchor_text if cand else a.text
        evidence = cand.evidence if cand else ""
        raw_attrs = dict(a.attributes) or (dict(cand.suggested_attributes) if cand else {})
        attrs = normalize_attributes(raw_attrs)
        repaired, attr_warn = repair_attributes(attrs, spec=spec)
        warnings.extend(attr_warn)
        flags, flag_warn = _filter_flags(a.uncertainty_flags)
        warnings.extend(flag_warn)
        mentions.append(
            PredictedMention(
                entity=ENTITY_NAME,
                text=text,
                attributes=repaired,
                evidence=evidence,
                confidence=a.confidence,
                uncertainty_flags=flags,
                rationale=a.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    for m in record.additional_mentions:
        if not (m.text and m.text in note_text):
            warnings.append(f"dropped_additional_text_not_substring: {m.text!r}")
            continue
        attrs = normalize_attributes(dict(m.attributes))
        repaired, attr_warn = repair_attributes(attrs, spec=spec)
        warnings.extend(attr_warn)
        flags, flag_warn = _filter_flags(m.uncertainty_flags)
        warnings.extend(flag_warn)
        mentions.append(
            PredictedMention(
                entity=ENTITY_NAME,
                text=m.text,
                attributes=repaired,
                evidence=m.evidence,
                confidence=m.confidence,
                uncertainty_flags=flags,
                rationale=m.rationale,
                component_owner=COMPONENT_OWNER + "_additional",
            )
        )

    return mentions, warnings


def assess_letter(
    letter: ExectLetter,
    candidates: Sequence[SFCandidate],
    record: AssessmentRecord,
    *,
    spec: EntitySpec,
) -> tuple[PredictedLetter, list[RoutedMention], list[str]]:
    """Full render + verify/route for one letter's assessment."""
    rendered, warnings = render_mentions(letter, candidates, record, spec=spec)
    kept, routed = verify_and_route(rendered, note_text=letter.note_text)
    predicted = project_cuis(
        PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(kept),
            diagnostics={
                "prompt_version": PROMPT_VERSION,
                "n_candidates": len(candidates),
                "aggregation_policy": record.aggregation_policy,
                "n_routed": len(routed),
                "routed_taxonomy": routed_taxonomy(routed),
                "warnings": warnings,
            },
        )
    )
    return predicted, routed, warnings


# ── Runner ────────────────────────────────────────────────────────────────────


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the hybrid assessor over a split.

    When ``resume`` is set and ``checkpoint_jsonl_path`` already holds a partial
    run, letters already present are skipped and only the remainder is processed;
    old and new rows are merged back into split order (see ``core.run_resume``).
    """
    spec = ENTITY_REGISTRY[ENTITY_NAME]
    program = DspyHybridAssessor()
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

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [
        r for r in existing_rows if r.get("letter_id") in requested
    ]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        candidates = build_candidate_set(letter)
        prompt_input_json = build_prompt_input(letter, candidates)
        raw_output = ""
        call_error: str | None = None

        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.assessment_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        record, parse_errors = (
            parse_assessment_json(raw_output) if raw_output else (None, ["not_run"])
        )

        if record is not None:
            predicted_letter, routed, _warn = assess_letter(
                letter, candidates, record, spec=spec
            )
        else:
            predicted_letter = PredictedLetter(letter_id=letter.letter_id, mentions=())
            routed = []

        n_kept_candidates = sum(
            1 for a in (record.assessments if record else []) if a.keep
        )
        n_additional = len(record.additional_mentions) if record else 0
        n_raw = n_kept_candidates + n_additional

        gold_sf = letter.entities(ENTITY_NAME)
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "aggregation_policy": record.aggregation_policy if record else "",
                "n_candidates": len(candidates),
                "n_mentions_raw": n_raw,
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_routed": len(routed),
                "routed_taxonomy": routed_taxonomy(routed),
                "predicted_mentions": [
                    {
                        "text": m.text,
                        "attributes": dict(m.attributes),
                        "evidence": m.evidence,
                        "confidence": m.confidence,
                        "uncertainty_flags": list(m.uncertainty_flags),
                        "rationale": m.rationale,
                    }
                    for m in predicted_letter.mentions
                ],
                "routed_mentions": [
                    {"text": r.mention.text, "reason": r.reason} for r in routed
                ],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)} for a in gold_sf
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate gate health, routing taxonomy, and F1 across all rows."""
    n = len(rows)
    if n == 0:
        return {"examples": 0}

    call_failures = sum(bool(r.get("call_error")) for r in rows)
    parse_failures = sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows)
    n_candidates = sum(int(r.get("n_candidates", 0)) for r in rows)
    n_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_scored = sum(int(r.get("n_mentions_scored", 0)) for r in rows)
    n_routed = sum(int(r.get("n_routed", 0)) for r in rows)

    routed_tax: dict[str, int] = {}
    for r in rows:
        for reason, count in (r.get("routed_taxonomy") or {}).items():
            routed_tax[reason] = routed_tax.get(reason, 0) + int(count)

    gold_letters = _reconstruct_letters(rows, "gold_mentions")
    pred_letters = _reconstruct_letters(rows, "predicted_mentions")

    scores: dict[str, Any] = {}
    for config_name, config in [
        ("phrase_only", PHRASE_ONLY),
        ("sf_semantic", SF_SEMANTIC),
        ("sf_benchmark", SF_BENCHMARK),
    ]:
        entity_score: EntityScore = score_entity(
            gold_letters, pred_letters, ENTITY_NAME, config
        )
        scores[config_name] = {
            "per_item": _score_dict(entity_score.per_item),
            "per_letter": _score_dict(entity_score.per_letter),
        }

    return {
        "examples": n,
        "call_failures": call_failures,
        "parse_failures": parse_failures,
        "n_candidates": n_candidates,
        "n_mentions_raw": n_raw,
        "n_mentions_scored": n_scored,
        "n_routed": n_routed,
        "routed_taxonomy": routed_tax,
        "scores": scores,
    }


def _score_dict(prf: Any) -> dict[str, Any]:
    return {
        "precision": round(prf.precision, 4),
        "recall": round(prf.recall, 4),
        "f1": round(prf.f1, 4),
        "tp": prf.tp,
        "fp": prf.fp,
        "fn": prf.fn,
    }


def _reconstruct_letters(rows: Sequence[dict[str, Any]], key: str) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=ENTITY_NAME, text=m["text"], attributes=m.get("attributes", {})
            )
            for m in (row.get(key) or [])
        )
        if key == "predicted_mentions":
            pred = PredictedLetter(
                letter_id=row["letter_id"],
                mentions=tuple(
                    PredictedMention(
                        entity=ENTITY_NAME,
                        text=m["text"],
                        attributes=m.get("attributes", {}),
                        evidence=m.get("evidence", ""),
                    )
                    for m in (row.get(key) or [])
                ),
            )
            letters.append(to_exect_letter(pred))
        else:
            letters.append(
                ExectLetter(letter_id=row["letter_id"], note_text="", annotations=annotations)
            )
    return letters


# ── I/O helpers ───────────────────────────────────────────────────────────────


def write_jsonl(rows: Sequence[dict[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write a concise Markdown run report for the hybrid assessor."""
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    scores = summary.get("scores", {})
    lines = [
        "# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        "## Gate & routing summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Candidates offered: {summary.get('n_candidates', 0)}",
        f"- Mentions kept by LLM: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored (post verify/route): {summary.get('n_mentions_scored', 0)}",
        f"- Routed (excluded): {summary.get('n_routed', 0)}",
        f"- Routed taxonomy: {summary.get('routed_taxonomy', {})}",
        "",
        "## Scores",
        "",
    ]
    for config_name in ("phrase_only", "sf_semantic", "sf_benchmark"):
        s = scores.get(config_name, {})
        pi = s.get("per_item", {})
        pl = s.get("per_letter", {})
        lines.append(f"### {config_name}")
        lines.append("")
        lines.append(
            f"  per-item: P={pi.get('precision', 0):.3f} "
            f"R={pi.get('recall', 0):.3f} F1={pi.get('f1', 0):.3f} "
            f"(TP={pi.get('tp', 0)} FP={pi.get('fp', 0)} FN={pi.get('fn', 0)})"
        )
        lines.append(
            f"  per-letter: P={pl.get('precision', 0):.3f} "
            f"R={pl.get('recall', 0):.3f} F1={pl.get('f1', 0):.3f} "
            f"(TP={pl.get('tp', 0)} FP={pl.get('fp', 0)} FN={pl.get('fn', 0)})"
        )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(e).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for e in (errors or [])
    )


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    summary = summarize_rows(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
            },
            report_path,
            jsonl_path=jsonl_path,
        )
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "n_mentions_scored": summary.get("n_mentions_scored", 0),
        "n_routed": summary.get("n_routed", 0),
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)
