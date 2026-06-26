"""ExECTv2 LLM-only single-pass SeizureFrequency extractor.

One DSPy call per letter emits all SeizureFrequency mentions (Phase 3).
Phase 6 extends the entity scope to all nine entity types.

Architecture family: llm_only.
Contribution thesis: the LLM owns every clinical fact; deterministic code
validates JSON shape, repairs neutral schema mismatches, checks evidence
exactness, and scores — it never introduces or chooses a clinical fact.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import (
    evidence_is_substring,
    repair_evidence_text_if_source_exact,
)
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
    to_exect_letter,
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
    canonicalize_attribute_value,
    score_entity,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.dspy_runner import (
    emit_run_checkpoint,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
    parse_json_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.reporting import (
    ensure_summary,
    format_gate_summary_lines,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_only_single_pass_v0.2"
ENTITY_NAME = SEIZURE_FREQUENCY.name


# ── Output schema ────────────────────────────────────────────────────────────


class MentionRecord(BaseModel):
    """One SeizureFrequency mention emitted by the LLM."""

    model_config = ConfigDict(extra="ignore")

    text: str
    attributes: dict[str, Any] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class ExtractionRecord(BaseModel):
    """Full LLM output for one letter."""

    model_config = ConfigDict(extra="ignore")

    mentions: list[MentionRecord] = []


# ── DSPy program ──────────────────────────────────────────────────────────────


class ExECTv2SinglePassSFSignature(dspy.Signature):
    """Read one clinical letter and produce a list of seizure frequency findings.

    Return a strict JSON object with key 'mentions'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., \"attributes\": {...}, "
            "\"evidence\": ..., \"confidence\": ..., \"rationale\": ...}, ...]}"
        )
    )


class DspySinglePassSFExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2SinglePassSFSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


# ── Prompt builder ────────────────────────────────────────────────────────────


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the single-pass v0.2 prompt payload for one letter.

    v0.2 fix: clearly distinguishes the seizure-type anchor phrase (text)
    from the full supporting sentence (evidence), matching the annotation
    scheme where SeizureFrequency.text is a SHORT noun phrase like
    'focal seizures' or 'generalised tonic-clonic seizures'.
    """
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read the clinical letter. For each seizure type that has associated "
            "frequency information, produce one record. Return one JSON object with "
            "a 'mentions' list."
        ),
        "field_definitions": {
            "text": (
                "The seizure-type anchor phrase — the SHORT noun phrase naming the "
                "specific seizure or event type as it appears in the letter. This is "
                "typically 2 to 6 words: the seizure type descriptor, not the full "
                "frequency sentence. Valid examples: 'focal seizures with altered "
                "awareness', 'generalised tonic-clonic seizures', 'myoclonic jerks', "
                "'absences', 'seizures', 'seizure-free', 'cluster of seizures'. "
                "MUST be an exact substring of the letter text."
            ),
            "attributes": (
                "Coded clinical features for this seizure type. Include only those "
                "present in the letter. All values must be strings."
            ),
            "evidence": (
                "An exact substring of the letter that gives the frequency context — "
                "the clause or sentence containing the seizure type and its frequency "
                "information. Must appear verbatim in the letter."
            ),
            "confidence": (
                "'high': one unambiguous frequency fact, exact count and time period "
                "stated, no competing claims. "
                "'medium': frequency is clear but a vague count, conditional qualifier, "
                "or only a relative change is present. "
                "'low': multiple competing current claims that cannot be resolved."
            ),
            "rationale": "One sentence: the deciding evidence and the coded result.",
        },
        "worked_examples": [
            {
                "note_fragment": (
                    "She has had 2 to 3 focal seizures per month since the medication change."
                ),
                "correct": {
                    "text": "focal seizures",
                    "attributes": {
                        "LowerNumberOfSeizures": "2",
                        "UpperNumberOfSeizures": "3",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "PointInTime": "DrugChange",
                    },
                    "evidence": "2 to 3 focal seizures per month since the medication change",
                    "confidence": "high",
                    "rationale": "2 to 3 focal seizures per month since medication change.",
                },
                "note": (
                    "text is the SHORT seizure-type phrase 'focal seizures', "
                    "NOT the full sentence."
                ),
            },
            {
                "note_fragment": (
                    "He has been seizure-free for 6 months following surgery."
                ),
                "correct": {
                    "text": "seizure-free",
                    "attributes": {
                        "TimeSince_or_TimeOfEvent": "Since",
                        "PointInTime": "Surgery",
                        "NumberOfTimePeriods": "6",
                        "TimePeriod": "Month",
                    },
                    "evidence": "seizure-free for 6 months following surgery",
                    "confidence": "high",
                    "rationale": "Seizure-free for 6 months since surgery.",
                },
            },
            {
                "note_fragment": (
                    "His generalised tonic clonic seizures have decreased since "
                    "starting levetiracetam, whilst his absence seizures remain "
                    "at roughly 3 per day."
                ),
                "correct": [
                    {
                        "text": "generalised tonic clonic seizures",
                        "attributes": {"FrequencyChange": "Decreased"},
                        "evidence": (
                            "generalised tonic clonic seizures have decreased "
                            "since starting levetiracetam"
                        ),
                        "confidence": "medium",
                        "rationale": "GTC seizures decreased — rate not stated.",
                    },
                    {
                        "text": "absence seizures",
                        "attributes": {
                            "NumberOfSeizures": "3",
                            "NumberOfTimePeriods": "1",
                            "TimePeriod": "Day",
                        },
                        "evidence": "absence seizures remain at roughly 3 per day",
                        "confidence": "high",
                        "rationale": "Absence seizures 3 per day.",
                    },
                ],
                "note": "Each seizure TYPE gets its own record.",
            },
        ],
        "attribute_vocabulary": {
            "NumberOfSeizures": "single count as string, e.g. '2'",
            "LowerNumberOfSeizures": "lower end of count range, e.g. '2' for '2 to 4 per month'",
            "UpperNumberOfSeizures": "upper end of count range, e.g. '4' for '2 to 4 per month'",
            "NumberOfTimePeriods": "period length as string, usually '1'",
            "LowerNumberOfTimePeriods": "lower end of period range",
            "UpperNumberOfTimePeriods": "upper end of period range",
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
        "clinical_rules": [
            (
                "One record per seizure TYPE. If the note describes focal seizures "
                "AND tonic-clonic seizures, each gets its own record with its own "
                "frequency attributes."
            ),
            (
                "The 'text' field MUST be a SHORT anchor phrase: the seizure-type "
                "descriptor as it appears in the letter (2 to 6 words). Never put "
                "the full frequency sentence in 'text'."
            ),
            (
                "Both 'text' and 'evidence' must be exact substrings of the letter. "
                "If you cannot copy them verbatim, omit the record."
            ),
            (
                "Include historical frequency statements with PointInTime or "
                "TimeSince_or_TimeOfEvent to mark their temporal context."
            ),
            (
                "Seizure-free: use 'seizure-free' as the text anchor; encode duration "
                "in NumberOfTimePeriods + TimePeriod; use TimeSince_or_TimeOfEvent='Since' "
                "and PointInTime when a trigger event is stated."
            ),
            (
                "Ranges: '2 to 4 per month' → LowerNumberOfSeizures='2', "
                "UpperNumberOfSeizures='4', NumberOfTimePeriods='1', TimePeriod='Month'."
            ),
            (
                "Period ranges: 'every 2 to 3 weeks' → NumberOfSeizures='1', "
                "LowerNumberOfTimePeriods='2', UpperNumberOfTimePeriods='3', TimePeriod='Week'."
            ),
            (
                "Cluster patterns: if a cluster cadence is stated ('clusters every "
                "3 weeks'), that is a frequency — use it. Events within a single cluster "
                "day are NOT the same as daily ongoing events."
            ),
            (
                "Conditional windows: extract frequency as stated even if conditional. "
                "Do not infer an unconditional overall rate from a conditional window."
            ),
            (
                "If the letter has no seizure frequency information, return "
                "{\"mentions\": []}."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


# ── Parser ────────────────────────────────────────────────────────────────────


def parse_extraction_json(
    raw_output: str,
) -> tuple[ExtractionRecord | None, list[str]]:
    """Parse and schema-validate one LLM output string.

    Returns (record, errors). If errors contains a blocking issue
    (invalid_json or schema_validation_error), record is None.
    Non-blocking issues (coercions, unknown fields) are noted in errors.
    """
    try:
        payload, dialect_notes = parse_json_payload(raw_output, schema_repair=True)
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    payload, coerce_notes = _coerce_payload(payload)
    errors: list[str] = [*dialect_notes, *coerce_notes]

    try:
        record = ExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def raw_output_from_adapter_parse_error(error_text: str) -> str | None:
    """Recover the model payload embedded in a DSPy adapter parse error."""

    marker = "LM Response:"
    if marker not in error_text:
        return None
    tail = error_text.split(marker, 1)[1]
    for stop in (
        "\n\nExpected to find output fields",
        "\r\n\r\nExpected to find output fields",
    ):
        if stop in tail:
            tail = tail.split(stop, 1)[0]
            break
    payload = tail.strip()
    return payload or None


_extract_json_object = extract_json_object


def _coerce_payload(payload: Any) -> tuple[Any, list[str]]:
    """Coerce numeric attribute values to strings; note coercions."""
    notes: list[str] = []
    if isinstance(payload, list):
        notes.append("coerced_top_level_mention_array")
        payload = {"mentions": payload}
    if not isinstance(payload, dict):
        return payload, notes
    mentions_raw = payload.get("mentions")
    if not isinstance(mentions_raw, list):
        return payload, notes
    coerced_mentions = []
    for i, mention in enumerate(mentions_raw):
        if not isinstance(mention, dict):
            coerced_mentions.append(mention)
            continue
        attrs = mention.get("attributes")
        if isinstance(attrs, dict):
            new_attrs: dict[str, str] = {}
            for k, v in attrs.items():
                if v is None:
                    continue
                str_v = str(v)
                if str_v != v:
                    notes.append(f"coerced_attribute_value: mention[{i}] {k!r} {v!r} -> {str_v!r}")
                new_attrs[str(k)] = str_v
            mention = dict(mention)
            mention["attributes"] = new_attrs
        coerced_mentions.append(mention)
    return {**payload, "mentions": coerced_mentions}, notes


# ── Attribute repair gate ─────────────────────────────────────────────────────


def repair_attributes(
    attrs: dict[str, str],
    *,
    spec: EntitySpec,
) -> tuple[dict[str, str], list[str]]:
    """Strip illegal attribute keys and illegal closed-vocab values.

    Semantically-neutral: the LLM clinical fact is never altered, only
    schema-invalid keys are dropped. Both actions are logged.
    """
    repaired: dict[str, str] = {}
    warnings: list[str] = []
    for key, value in attrs.items():
        if key in spec.noise_attributes:
            continue
        if key not in spec.legal_attributes:
            warnings.append(f"dropped_illegal_attribute: {key!r}")
            continue
        normalized_value = canonicalize_attribute_value(key, value)
        if normalized_value != value:
            warnings.append(
                f"normalized_attribute_value: {key!r}={value!r} -> {normalized_value!r}"
            )
        if key in spec.closed_vocab and normalized_value not in spec.closed_vocab[key]:
            warnings.append(
                f"dropped_illegal_value: {key!r}={normalized_value!r} not in "
                f"{sorted(spec.closed_vocab[key])}"
            )
            continue
        repaired[key] = normalized_value
    return repaired, warnings


# ── Evidence gate ─────────────────────────────────────────────────────────────


def check_evidence(
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[list[MentionRecord], list[MentionRecord], list[str]]:
    """Partition mentions into (evidence_valid, evidence_invalid).

    Per policy: mentions whose evidence is not an exact substring of the note
    are dropped from the scored set and logged. They are never silently kept.
    """
    valid: list[MentionRecord] = []
    invalid: list[MentionRecord] = []
    warnings: list[str] = []
    for mention in mentions:
        repaired_evidence = repair_evidence_text_if_source_exact(mention.evidence, note_text)
        if repaired_evidence and evidence_is_substring(note_text, repaired_evidence):
            if repaired_evidence != mention.evidence:
                warnings.append(f"repaired_evidence_exact_copy: text={mention.text!r}")
                mention = mention.model_copy(update={"evidence": repaired_evidence})
            valid.append(mention)
            continue
        invalid.append(mention)
        reason = "empty_evidence" if not mention.evidence else "evidence_not_substring"
        warnings.append(f"dropped_{reason}: text={mention.text!r}")
    return valid, invalid, warnings


# ── Adapter ───────────────────────────────────────────────────────────────────


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    spec: EntitySpec,
    note_text: str,
    entity_name: str = ENTITY_NAME,
) -> tuple[PredictedLetter, list[str]]:
    """Repair attributes and build a PredictedLetter from scored mentions.

    Returns (predicted_letter, all_warnings). The predicted_letter only
    contains evidence-valid mentions with repaired attributes.
    """
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        repaired_attrs, attr_warnings = repair_attributes(
            dict(mention.attributes), spec=spec
        )
        all_warnings.extend(attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=entity_name,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner="llm_only_single_pass",
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


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
    """Run the single-pass extractor over a split.

    mode='live' makes real LLM calls. mode='prompt-only' builds prompts only
    and emits a not_run sentinel for downstream inspection.

    When ``resume`` is set and ``checkpoint_jsonl_path`` already holds a partial
    run, letters already present are skipped and only the remainder is processed
    (see ``core.run_resume``).
    """
    spec = ENTITY_REGISTRY[ENTITY_NAME]
    program = DspySinglePassSFExtractor()
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
        prompt_input_json = build_prompt_input(letter)
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
            letter.letter_id,
            mentions,
            spec=spec,
            note_text=letter.note_text,
        )
        evidence_valid_count = len(predicted_letter.mentions)
        evidence_invalid_count = len(mentions) - evidence_valid_count

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
                "gate_warnings": gate_warnings,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": evidence_valid_count,
                "n_evidence_invalid": evidence_invalid_count,
                "predicted_mentions": [
                    {
                        "text": m.text,
                        "attributes": dict(m.attributes),
                        "evidence": m.evidence,
                        "confidence": m.confidence,
                        "rationale": m.rationale,
                    }
                    for m in predicted_letter.mentions
                ],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in gold_sf
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
    """Aggregate statistics and F1 scores across all rows."""
    n = len(rows)
    if n == 0:
        return {"examples": 0}

    call_failures = sum(bool(r.get("call_error")) for r in rows)
    parse_failures = sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_scored = sum(int(r.get("n_mentions_scored", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)

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
            "per_item": {
                "precision": round(entity_score.per_item.precision, 4),
                "recall": round(entity_score.per_item.recall, 4),
                "f1": round(entity_score.per_item.f1, 4),
                "tp": entity_score.per_item.tp,
                "fp": entity_score.per_item.fp,
                "fn": entity_score.per_item.fn,
            },
            "per_letter": {
                "precision": round(entity_score.per_letter.precision, 4),
                "recall": round(entity_score.per_letter.recall, 4),
                "f1": round(entity_score.per_letter.f1, 4),
                "tp": entity_score.per_letter.tp,
                "fp": entity_score.per_letter.fp,
                "fn": entity_score.per_letter.fn,
            },
        }

    return {
        "examples": n,
        "call_failures": call_failures,
        "parse_failures": parse_failures,
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": n_scored,
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "scores": scores,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=ENTITY_NAME,
                text=m["text"],
                attributes=m["attributes"],
            )
            for m in (row.get("gold_mentions") or [])
        )
        letters.append(
            ExectLetter(
                letter_id=row["letter_id"],
                note_text="",
                annotations=annotations,
            )
        )
    return letters


def _reconstruct_pred_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred_letter = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=ENTITY_NAME,
                    text=m["text"],
                    attributes=m["attributes"],
                    evidence=m.get("evidence", ""),
                    confidence=m.get("confidence", "medium"),
                    rationale=m.get("rationale", ""),
                )
                for m in (row.get("predicted_mentions") or [])
            ),
        )
        letters.append(to_exect_letter(pred_letter))
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
    """Write a concise Markdown run report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = ensure_summary(rows, metadata, summarize_rows)
    scores = summary.get("scores", {})
    lines = [
        "# ExECTv2 LLM-Only Single-Pass — SeizureFrequency",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        *format_gate_summary_lines(summary),
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
            f"R={pi.get('recall', 0):.3f} "
            f"F1={pi.get('f1', 0):.3f} "
            f"(TP={pi.get('tp', 0)} FP={pi.get('fp', 0)} FN={pi.get('fn', 0)})"
        )
        lines.append(
            f"  per-letter: P={pl.get('precision', 0):.3f} "
            f"R={pl.get('recall', 0):.3f} "
            f"F1={pl.get('f1', 0):.3f} "
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
    emit_run_checkpoint(
        rows,
        total=total,
        jsonl_path=jsonl_path,
        report_path=report_path,
        metadata={
            "prompt_version": PROMPT_VERSION,
            "split": split,
            "model": model,
            "mode": mode,
        },
        summarize_rows=summarize_rows,
        write_jsonl=write_jsonl,
        write_report=write_report,
    )
