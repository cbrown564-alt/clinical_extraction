"""ExECTv2 LLM-only per-entity SeizureFrequency extractor.

One focused DSPy call per entity type per letter. For Phase 3 this covers
SeizureFrequency only; Phase 6 calls this extractor once per entity name.

The focused prompt gives more detailed entity-specific clinical guidance than
the single-pass variant, at the cost of one LLM call per entity per letter.
Core parse/validate/adapt logic is shared with llm_only_single_pass.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    summarize_rows,
    to_predicted_letter,
    write_jsonl,
    write_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_only_per_entity_v0.2"
ENTITY_NAME = SEIZURE_FREQUENCY


# ── DSPy program ──────────────────────────────────────────────────────────────


class ExECTv2PerEntitySFSignature(dspy.Signature):
    """Read one clinical letter and list all seizure frequency findings for one finding type.

    Return exactly one JSON object with a 'mentions' list. No markdown wrapper.
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


class DspyPerEntitySFExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2PerEntitySFSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


# ── Prompt builder ────────────────────────────────────────────────────────────


def build_prompt_input(letter: ExectLetter, *, entity_name: str = ENTITY_NAME) -> str:
    """Build a focused per-entity v0.2 prompt for SeizureFrequency extraction.

    v0.2 fix: 'text' is explicitly the SHORT seizure-type anchor phrase
    (e.g. 'focal seizures'), not the full frequency sentence. Worked examples
    illustrate the distinction. The 'evidence' field holds the full
    supporting clause.
    """
    payload = {
        "prompt_version": PROMPT_VERSION,
        "entity": entity_name,
        "task": (
            "Read the clinical letter. For each seizure type that has associated "
            "frequency information, produce one record in the 'mentions' list."
        ),
        "field_definitions": {
            "text": (
                "The seizure-type anchor phrase — the SHORT noun phrase naming the "
                "seizure or event type as it appears in the letter. Typically 2 to 6 "
                "words. Valid examples: 'focal seizures with altered awareness', "
                "'generalised tonic-clonic seizures', 'myoclonic jerks', 'absences', "
                "'seizures', 'seizure-free', 'cluster of seizures'. "
                "Must be an exact substring of the letter. "
                "Do NOT put the full frequency sentence in this field."
            ),
            "attributes": (
                "Coded clinical features for this seizure type. Include only those "
                "explicitly present. All values must be strings."
            ),
            "evidence": (
                "The clause or sentence from the letter that provides the frequency "
                "context for this seizure type. Must be an exact substring of the letter."
            ),
            "confidence": (
                "'high': unambiguous fact, exact count and period stated. "
                "'medium': frequency clear but a vague count, conditional qualifier, "
                "or relative change only. "
                "'low': competing current claims that cannot be resolved."
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
            },
            {
                "note_fragment": "He remains seizure-free for 8 months following surgery.",
                "correct": {
                    "text": "seizure-free",
                    "attributes": {
                        "TimeSince_or_TimeOfEvent": "Since",
                        "PointInTime": "Surgery",
                        "NumberOfTimePeriods": "8",
                        "TimePeriod": "Month",
                    },
                    "evidence": "seizure-free for 8 months following surgery",
                    "confidence": "high",
                    "rationale": "Seizure-free for 8 months since surgery.",
                },
            },
            {
                "note_fragment": (
                    "His tonic-clonic seizures occur roughly twice a week, "
                    "while his absence seizures have decreased."
                ),
                "correct": [
                    {
                        "text": "tonic-clonic seizures",
                        "attributes": {
                            "NumberOfSeizures": "2",
                            "NumberOfTimePeriods": "1",
                            "TimePeriod": "Week",
                        },
                        "evidence": "tonic-clonic seizures occur roughly twice a week",
                        "confidence": "high",
                        "rationale": "Tonic-clonic seizures twice per week.",
                    },
                    {
                        "text": "absence seizures",
                        "attributes": {"FrequencyChange": "Decreased"},
                        "evidence": "absence seizures have decreased",
                        "confidence": "medium",
                        "rationale": "Absence seizures decreased — rate not stated.",
                    },
                ],
                "note": "One record per seizure TYPE.",
            },
        ],
        "attribute_vocabulary": {
            "NumberOfSeizures": "single count as string, e.g. '2'",
            "LowerNumberOfSeizures": "lower end of count range",
            "UpperNumberOfSeizures": "upper end of count range",
            "NumberOfTimePeriods": "period length as string, usually '1'",
            "LowerNumberOfTimePeriods": "lower end of period range",
            "UpperNumberOfTimePeriods": "upper end of period range",
            "TimePeriod": "exactly 'Day', 'Week', 'Month', or 'Year'",
            "FrequencyChange": "exactly one of 'Decreased', 'Frequent', 'Increased', 'Infrequent', 'Same'",
            "PointInTime": "exactly one of 'Birthday', 'DrugChange', 'LastClinic', 'Last_Month', 'Last_Week', 'Last_Year', 'Surgery'",
            "TimeSince_or_TimeOfEvent": "exactly 'During' or 'Since'",
            "DayDate": "day as string",
            "MonthDate": "month as string",
            "YearDate": "4-digit year as string",
            "AgeLower": "lower age bound as string",
            "AgeUpper": "upper age bound as string",
            "AgeUnit": "exactly 'Year' or 'Month'",
        },
        "clinical_rules": [
            "Each seizure TYPE that has frequency information gets one record.",
            (
                "text MUST be the SHORT seizure-type anchor phrase (2 to 6 words), "
                "not the full frequency sentence."
            ),
            "Both text and evidence must be exact substrings of the letter.",
            "Extract historical and current frequency statements as separate records.",
            (
                "Seizure-free: text='seizure-free' or 'seizure free'; encode duration "
                "in NumberOfTimePeriods + TimePeriod; use TimeSince_or_TimeOfEvent='Since'."
            ),
            (
                "Ranges: '2 to 4 per month' → LowerNumberOfSeizures='2', "
                "UpperNumberOfSeizures='4', TimePeriod='Month'."
            ),
            (
                "Cluster cadence: if clusters occur 'every 3 weeks', that is the "
                "frequency — not the per-episode daily burst rate."
            ),
            "If no seizure frequency information is present, return {\"mentions\": []}.",
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


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
    """Run the per-entity extractor for SeizureFrequency over a split.

    When ``resume`` is set and ``checkpoint_jsonl_path`` already holds a partial
    run, letters already present are skipped and only the remainder is processed
    (see ``core.run_resume``).
    """
    import json
    import sys

    from clinical_extraction.core.run_resume import (
        merge_rows,
        pending_items,
        read_completed,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
        _emit_checkpoint,
    )

    spec = ENTITY_REGISTRY[ENTITY_NAME]
    program = DspyPerEntitySFExtractor()
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
