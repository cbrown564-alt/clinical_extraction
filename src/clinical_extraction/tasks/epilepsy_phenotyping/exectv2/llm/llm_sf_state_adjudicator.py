"""Candidate-span SeizureFrequency adjudicator over the v0.5 structured draft."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_verifier as verifier_base,
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
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_frequency_state,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_hybrid_sf_state_adjudicator_v0.1"
PIPELINE_FAMILY = "exectv2_hybrid_sf_state_adjudicator"
COMPONENT_OWNER = "hybrid_sf_state_adjudicator"

_SEIZURE_RE = re.compile(
    r"\b("
    r"seizure(?:s|-free| free)?|absen(?:ce|ces)|myoclonic|tonic(?:-| )clonic|"
    r"tonic(?:-| )chronic|convulsive|focal|dyscognitive|complex partial|"
    r"cluster of seizures|jerks"
    r")\b",
    re.IGNORECASE,
)
_STATE_RE = re.compile(
    r"\b("
    r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|many|"
    r"total|per|every|daily|weekly|monthly|yearly|week|month|year|day|"
    r"frequent|infrequent|occasional|returned|return|improved|improvement|"
    r"worse|increased|decreased|controlled|under control|seizure[- ]free|"
    r"not had|no further|last event|last seizure|last seizures|since|cluster"
    r")\b",
    re.IGNORECASE,
)
_BLOCKING_CONTEXT_RE = re.compile(
    r"\b(family history|no history of|single focal seizure|diagnosis|diagnosed with)\b",
    re.IGNORECASE,
)
_DIRECT_SPAN_RES = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"(?:the\s+)?seizures?\s+have\s+returned",
        r"not\s+had\s+any\s+further\s+seizures?[^.!\n\r]*",
        r"no\s+further\s+seizures?[^.!\n\r]*",
        r"seizure[- ]free\s+for\s+[^.!\n\r]*",
        r"(?:a\s+)?total\s+of\s+\d+\s+in\s+\d{4}",
        r"(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
        r"seizures?\s+(?:a|per|every)\s+[^.!\n\r,;]*",
        r"\d+\s*(?:-|to)\s*\d+\s+[^.!\n\r,;]*seizures?[^.!\n\r,;]*",
        r"(?:very\s+)?frequent\s+myoclonic\s+jerks",
        r"infrequent\s+[^.!\n\r,;]*seizures?",
        r"focal\s+seizures?\s+are\s+completely\s+under\s+control",
        r"last\s+seizures?\s+were\s+in\s+[^.!\n\r,;]*",
        r"[^.!\n\r,;]*last\s+event\s+[^.!\n\r,;]*\d{4}",
    ]
]


@dataclass(frozen=True)
class CandidateSpan:
    """One exact source span offered to the LLM as possible SF evidence."""

    candidate_id: str
    evidence: str
    state_hint: str
    text_hint: str
    source: str
    start: int
    end: int

    def as_payload(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "evidence": self.evidence,
            "state_hint": self.state_hint,
            "text_hint": self.text_hint,
            "source": self.source,
        }


class ExECTv2SFStateAdjudicatorSignature(dspy.Signature):
    """Review a clinical letter and candidate seizure-frequency spans."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft SF mentions, candidate spans, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspySFStateAdjudicator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2SFStateAdjudicatorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return verifier_base.draft_mentions_by_letter(rows)


def read_draft_rows(path: Path | None) -> list[dict[str, Any]]:
    return verifier_base.read_draft_rows(path)


def candidate_spans_for_letter(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]] = (),
    *,
    max_candidates: int = 24,
) -> list[CandidateSpan]:
    text = letter.note_text
    spans: list[CandidateSpan] = []
    seen: set[str] = set()

    def add(evidence: str, source: str, start: int | None = None, end: int | None = None) -> None:
        clean = evidence.strip()
        if not clean or clean not in text:
            return
        normalized = re.sub(r"\s+", " ", clean.lower())
        if normalized in seen:
            return
        if start is None or end is None:
            start = text.index(clean)
            end = start + len(clean)
        seen.add(normalized)
        spans.append(
            CandidateSpan(
                candidate_id=f"C{len(spans)}",
                evidence=clean,
                state_hint=_state_hint(clean),
                text_hint=_text_hint(clean),
                source=source,
                start=start,
                end=end,
            )
        )

    for draft in draft_mentions:
        evidence = str(draft.get("evidence", "")).strip()
        if evidence:
            add(evidence, "draft")

    for pattern in _DIRECT_SPAN_RES:
        for match in pattern.finditer(text):
            add(match.group(0), "candidate-pattern", match.start(), match.end())

    for sentence, start, end in _sentence_spans(text):
        if _SEIZURE_RE.search(sentence) and _STATE_RE.search(sentence):
            add(sentence, "candidate-sentence", start, end)

    return spans[:max_candidates]


def build_prompt_input(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]],
    candidate_spans: Sequence[CandidateSpan] | None = None,
) -> str:
    candidates = (
        list(candidate_spans)
        if candidate_spans is not None
        else candidate_spans_for_letter(letter, draft_mentions)
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Review the clinical letter, the draft SeizureFrequency mentions, "
            "and the candidate evidence spans. Return final SeizureFrequency "
            "mentions only. The candidate spans are possible evidence anchors; "
            "keep, reject, split, merge, or add mentions based on the letter."
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean seizure/event type anchor phrase owned by you.",
                    "attributes": {
                        "NumberOfSeizures": "string count, including 0 for seizure-free",
                        "LowerNumberOfSeizures": "lower bound count",
                        "UpperNumberOfSeizures": "upper bound count",
                        "NumberOfTimePeriods": "period count",
                        "LowerNumberOfTimePeriods": "lower bound period count",
                        "UpperNumberOfTimePeriods": "upper bound period count",
                        "TimePeriod": "Day | Week | Month | Year",
                        "TimeSince_or_TimeOfEvent": "Since | During",
                        "FrequencyChange": (
                            "Decreased | Frequent | Increased | Infrequent | Same"
                        ),
                        "PointInTime": (
                            "Birthday | DrugChange | LastClinic | Last_Month | "
                            "Last_Week | Last_Year | Surgery"
                        ),
                        "DayDate": "day number",
                        "MonthDate": "month number",
                        "YearDate": "year number",
                        "AgeLower": "lower age",
                        "AgeUpper": "upper age",
                        "AgeUnit": "Year | Month",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "draft_seizure_frequency_mentions": list(draft_mentions),
        "candidate_evidence_spans": [candidate.as_payload() for candidate in candidates],
        "state_decision_guide": _state_decision_guide(),
        "attribute_vocabulary": verifier_base._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": verifier_base._worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _clinical_rules() -> list[str]:
    return [
        (
            "Candidate spans are not predictions. Reject any candidate that is "
            "diagnosis-only, family-history-only, unlabelled episodes/events, or "
            "a bare seizure type without frequency state."
        ),
        (
            "Prefer candidate evidence when it exactly supports a final mention, "
            "but you may use another exact substring from the letter when the "
            "candidate list misses a better span."
        ),
        (
            "A candidate with state_hint='reject' should usually be omitted unless "
            "the letter clearly contains a count, seizure-free target, last-event "
            "anchor, or frequency-change statement."
        ),
    ] + verifier_base._clinical_rules()


def _state_decision_guide() -> dict[str, list[str]]:
    return {
        "active-rate": [
            "Nonzero count or range with a seizure/event type.",
            "Rate such as per day, per week, per month, per year, or every N weeks.",
            "A dated historical count that the annotation scheme treats as an event frequency.",
        ],
        "seizure-free": [
            "NumberOfSeizures='0'.",
            "Last-event/last-seizure anchors such as last event July 2016.",
            "No further seizures since a supported point in time.",
        ],
        "unknown": [
            (
                "Relative or qualitative change without a count, such as "
                "returned, frequent, improved, or controlled."
            ),
            "Use FrequencyChange and omit numeric seizure-count fields.",
        ],
        "reject": [
            "Diagnosis or seizure type with no frequency state.",
            (
                "Family history, no history, or unlabelled episodes/events not "
                "explicitly scored as seizures."
            ),
        ],
    }


def _sentence_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for match in re.finditer(r"[^.!?\n\r]+(?:[.!?]+|$)", text):
        start, end = match.span()
        raw = match.group(0)
        leading = len(raw) - len(raw.lstrip())
        trailing = len(raw.rstrip())
        clean = raw.strip()
        if clean:
            spans.append((clean, start + leading, start + trailing))
    return spans


def _state_hint(evidence: str) -> str:
    lower = evidence.lower()
    if _BLOCKING_CONTEXT_RE.search(lower):
        return "reject"
    if re.search(r"\b(seizure[- ]free|not had|no further|last event|last seizures?)\b", lower):
        return "seizure-free"
    if re.search(
        r"\b(returned|increased|decreased|frequent|infrequent|improved|improvement)\b",
        lower,
    ):
        return "unknown"
    if re.search(
        r"\b("
        r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|"
        r"total|per|every|cluster"
        r")\b",
        lower,
    ):
        return "active-rate"
    return "reject"


def _text_hint(evidence: str) -> str:
    lower = evidence.lower()
    ordered = [
        (
            r"focal\s+to\s+bilateral\s+convulsive\s+seizures?",
            "focal to bilateral convulsive seizures",
        ),
        (
            r"generalised\s+tonic\s+(?:clonic|chronic)\s+seizures?",
            "generalised tonic clonic seizures",
        ),
        (
            r"generalized\s+tonic\s+(?:clonic|chronic)\s+seizures?",
            "generalised tonic clonic seizures",
        ),
        (r"tonic\s+(?:clonic|chronic)\s+seizures?", "tonic clonic seizures"),
        (r"complex\s+partial\s+seizures?", "complex partial seizures"),
        (r"dyscognitive\s+seizures?", "dyscognitive seizures"),
        (r"absence\s+like\s+seizures?", "absence like seizures"),
        (r"absence\s+seizures?", "absence seizures"),
        (r"\babsences\b", "absences"),
        (r"myoclonic\s+jerks", "myoclonic jerks"),
        (r"focal\s+seizures?", "focal seizures"),
        (r"convulsive\s+seizures?", "convulsive seizures"),
        (r"cluster\s+of\s+seizures", "cluster of seizures"),
        (r"\bseizure[- ]free\b", "seizures"),
        (r"\bseizures\b", "seizures"),
        (r"\bseizure\b", "seizure"),
    ]
    for pattern, hint in ordered:
        if re.search(pattern, lower):
            return hint
    return "seizures"


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{SEIZURE_FREQUENCY.name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{SEIZURE_FREQUENCY.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=SEIZURE_FREQUENCY.name,
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
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def run_split(
    letters: Sequence[ExectLetter],
    *,
    draft_rows: Sequence[Mapping[str, Any]] = (),
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
    program = DspySFStateAdjudicator()
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

    drafts = draft_mentions_by_letter(draft_rows)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        draft_mentions = drafts.get(letter.letter_id, [])
        candidate_spans = candidate_spans_for_letter(letter, draft_mentions)
        prompt_input_json = build_prompt_input(letter, draft_mentions, candidate_spans)
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
            note_text=letter.note_text,
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "draft_mentions": list(draft_mentions),
                "candidate_spans": [candidate.as_payload() for candidate in candidate_spans],
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_draft_mentions": len(draft_mentions),
                "n_candidate_spans": len(candidate_spans),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(SEIZURE_FREQUENCY.name)
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
        "pipeline_family": PIPELINE_FAMILY,
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
    if not rows:
        return {"examples": 0}
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)
    phrase = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        PHRASE_ONLY,
    )
    semantic = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        semantic_config_for(SEIZURE_FREQUENCY.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        benchmark_config_for(SEIZURE_FREQUENCY.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [SEIZURE_FREQUENCY.name],
        semantic_config_for,
    ).per_entity[SEIZURE_FREQUENCY.name]
    frequency = score_frequency_state(gold_letters, pred_letters)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_candidate_spans": sum(int(r.get("n_candidate_spans", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            (n_mentions_raw - n_evidence_invalid) / n_mentions_raw if n_mentions_raw else 1.0
        ),
        "phrase_only": phrase.model_dump(),
        "semantic": semantic.model_dump(),
        "benchmark": benchmark.model_dump(),
        "source_near": source_near.model_dump(),
        "clinical_recovery": {
            "seizure_frequency": frequency.clinical_headline.model_dump(),
            "active_rate": frequency.active_rate.model_dump(),
            "seizure_free": frequency.seizure_free.model_dump(),
            "unknown": frequency.unknown.model_dump(),
            "target_headline_f1": 0.8,
        },
    }


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("seizure_frequency", {})
    source_near = summary.get("source_near", {})
    lines = [
        "# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Pipeline family: `{metadata.get('pipeline_family')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Draft SF mentions: {summary.get('n_draft_mentions', 0)}",
        f"- Candidate spans: {summary.get('n_candidate_spans', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## SeizureFrequency Clinical-Recovery Headline",
        "",
        "| Target F1 | F1 | P | R | TP | FP | FN |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 0.80 | {clinical.get('f1', 0):.3f} | "
            f"{clinical.get('precision', 0):.3f} | {clinical.get('recall', 0):.3f} | "
            f"{clinical.get('tp', 0)} | {clinical.get('fp', 0)} | "
            f"{clinical.get('fn', 0)} |"
        ),
        "",
        "## Source-Near Diagnostic",
        "",
        (
            f"- Overlap F1={source_near.get('overlap', {}).get('f1', 0):.3f} "
            f"R={source_near.get('overlap', {}).get('recall', 0):.3f}"
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=SEIZURE_FREQUENCY.name,
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                )
                for m in row.get("gold_mentions", [])
            ),
        )
        for row in rows
    ]


def _reconstruct_pred_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=SEIZURE_FREQUENCY.name,
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                    evidence=str(m.get("evidence", "")),
                    confidence=str(m.get("confidence", "medium")),
                    rationale=str(m.get("rationale", "")),
                )
                for m in row.get("predicted_mentions", [])
            ),
        )
        letters.append(to_exect_letter(pred))
    return letters


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
    if jsonl_path:
        write_jsonl(rows, jsonl_path)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "mode": mode,
        "split": split,
        "n_letters": total,
        "summary": summarize_rows(rows),
    }
    if report_path:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path or Path(""))
    summary = metadata["summary"]
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": summary.get("call_failures", 0),
                "parse_failures": summary.get("parse_failures", 0),
                "n_mentions_scored": summary.get("n_mentions_scored", 0),
            },
            sort_keys=True,
        ),
        flush=True,
    )
