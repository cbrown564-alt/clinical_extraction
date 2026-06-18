"""ExECTv2 Stage-2 GPT arbitration pass.

The deferred candidate-selection stage of satellite 09 (Phase C named it the
"next stage … ablation-gated"). The nine focused per-entity passes
(``llm.llm_only_per_entity``) are a strong *recall* engine — the union of their
candidates overlaps 0.84 of gold concepts on dev — but assembling them by a bare
union scatters concepts across entities (a seizure type proposed as PatientHistory
when gold wants Diagnosis), under-emits on the correct entity, and over-emits
spurious mentions. The bare-union hybrid scored only 0.22 semantic item F1; the
item-level error analysis (``docs/research/exectv2_gpt_first_error_analysis_*``)
attributes the gap to entity misassignment (Diagnosis loses 35 recall points to
it) and over-emission, not to candidate recall.

This module adds one GPT call per *letter* that reads the letter plus the union
candidate pool and produces a single coherent labelling: it re-assigns each
concept to the entity(ies) whose definition it satisfies (a concept may belong to
several), merges duplicates, drops spurious candidates, selects the canonical
short phrase, and finalises attributes. The split of labor is unchanged from the
Gan winner — the LLM owns candidate generation, clinical reasoning, *and now
selection*; deterministic code owns evidence faithfulness, schema repair, CUI
projection, and scoring.

Replay-first: the per-entity candidate JSONLs feed the pool with zero extra
generation calls; only the single arbitration call per letter is new.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
    ENTITY_REGISTRY,
    EntitySpec,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_per_entity import (
    _attribute_vocabulary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    check_evidence,
    repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

from .all_entity_assessment import summarize_rows  # reused scorer

PROMPT_VERSION = "exectv2_arbitration_v0.2"
COMPONENT_OWNER = "hybrid_arbitration"
ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)


# ── Entity routing guidance (the de-confusion contract) ─────────────────────────
#
# Derived from the dev gold entity-assignment patterns (see the error-analysis
# doc): named seizure-type/epilepsy diagnoses are Diagnosis; the same type with a
# count/rate is ALSO SeizureFrequency; comorbidities and generic/other historical
# seizure mentions are PatientHistory; the onset-age vs diagnosis-date split
# separates Onset from WhenDiagnosed; structural aetiologies are EpilepsyCause.
ENTITY_ROUTING: dict[str, str] = {
    "Diagnosis": (
        "A NAMED epilepsy diagnosis OR a classified seizure-type that describes the "
        "patient's epilepsy semiology. THIS IS BROAD: every named focal / "
        "generalised / partial / tonic-clonic / myoclonic / absence seizure type "
        "the patient actually has is a Diagnosis, even when the candidate pool "
        "proposed it as PatientHistory or SeizureFrequency. Examples: 'focal "
        "epilepsy', 'juvenile myoclonic epilepsy', 'temporal lobe epilepsy', "
        "'generalised tonic-clonic seizures', 'complex partial seizures', 'focal "
        "seizures', 'focal seizures with altered awareness', 'secondary generalised "
        "seizures', 'absence seizures', 'single seizure'. DiagCategory='Epilepsy' "
        "for an epilepsy diagnosis/syndrome, 'MultipleSeizures' for a recurrent "
        "seizure TYPE not itself called epilepsy, 'SingleSeizure' for one isolated "
        "seizure. Always carries Certainty (1-5, usually 5) and Negation (usually "
        "'Affirmed'). Reserve PatientHistory ONLY for NON-epilepsy attack types "
        "(febrile / dissociative / non-epileptic / psychogenic seizures) and "
        "comorbidities."
    ),
    "SeizureFrequency": (
        "ANY seizure type or event that has an associated count, rate, frequency, "
        "or seizure-free duration. A phrase that is also a Diagnosis is EXPECTED to "
        "ALSO appear here whenever a count/rate/duration is stated for it. Encode "
        "the numbers/time-periods in attributes; never emit Certainty/Negation."
    ),
    "PatientHistory": (
        "Past or background clinical history that is NOT the primary named epilepsy "
        "diagnosis: comorbidities (anxiety, depression, diabetes, migraine, "
        "learning disability), other/historical attack types (febrile seizures, "
        "dissociative / non-epileptic / psychogenic seizures, myoclonic jerks, "
        "absences mentioned historically), generic 'seizures'/'seizure' mentioned "
        "as background, and prior findings/procedures (gliosis, cortical dysplasia, "
        "brain surgery). Carries Certainty and Negation; dates/ages when stated."
    ),
    "Onset": (
        "The condition (usually 'epilepsy', sometimes a seizure type) whose AGE or "
        "TIME OF FIRST ONSET — when it BEGAN — is stated. Age+AgeUnit, or "
        "NumberOfTimePeriods+TimePeriod for a duration-ago, or "
        "PointInTime='From_Birth'. Distinct from WhenDiagnosed."
    ),
    "WhenDiagnosed": (
        "The condition (usually 'epilepsy') whose DIAGNOSIS date or age is stated — "
        "when it was DIAGNOSED, not when it began. Age+AgeUnit, YearDate/MonthDate, "
        "or NumberOfTimePeriods+TimePeriod."
    ),
    "EpilepsyCause": (
        "A structural cause or aetiology offered for the epilepsy (stroke, "
        "traumatic brain injury, encephalitis, meningitis, cortical dysplasia, "
        "hippocampal sclerosis, tuberous sclerosis, brain tumour). The same cause "
        "often ALSO appears as PatientHistory."
    ),
    "Investigations": (
        "An EEG, MRI, or CT investigation. Code *_Performed (Yes/No) and *_Results "
        "(Normal/Abnormal/Unknown), EEG_Type when stated. text is the bare modality "
        "token ('EEG', 'MRI', 'CT')."
    ),
    "Prescription": (
        "An anti-seizure medication the patient takes. text is the drug name; "
        "DrugDose/DoseUnit('mg'/'g')/Frequency('1'/'2'/'3'/'As_Required') in "
        "attributes."
    ),
    "BirthHistory": (
        "How the patient was born and perinatal events (born normally, born "
        "prematurely, full term). PrematureBirth gestation band when stated."
    ),
}


# ── DSPy program ────────────────────────────────────────────────────────────────


class ExECTv2ArbitrationSignature(dspy.Signature):
    """Read one clinical letter plus a pool of candidate findings and produce the
    single coherent, correctly-typed set of entity mentions for the letter.

    Return exactly one JSON object with a 'mentions' list. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON with one clinical letter, the nine-entity routing contract, and "
        "a pool of candidate findings to arbitrate."
    )
    arbitration_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"entity\": ..., \"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyArbitrator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ArbitrationSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


class ArbitratedMention(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity: str
    text: str
    attributes: dict[str, Any] = {}
    evidence: str = ""
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


# ── Candidate pool (replay of the per-entity passes) ────────────────────────────


def entity_slug(entity: str) -> str:
    return entity.lower()


def load_candidate_pool(
    prefix: str, *, out_dir: Path, entities: Sequence[str] = ENTITY_NAMES
) -> dict[str, list[dict[str, Any]]]:
    """Return ``{letter_id: [candidate, ...]}`` from the per-entity JSONLs.

    Each candidate keeps the proposing entity, its phrase, attributes and
    evidence; the pool is the recall scaffold the arbitration call reasons over.
    """
    by_letter: dict[str, list[dict[str, Any]]] = {}
    for entity in entities:
        path = out_dir / f"{prefix}_{entity_slug(entity)}.jsonl"
        if not path.exists():
            print(f"WARNING: missing per-entity candidates {path}", file=sys.stderr)
            continue
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                letter_id = row.get("letter_id")
                if letter_id is None:
                    continue
                bucket = by_letter.setdefault(letter_id, [])
                for m in row.get("predicted_mentions") or []:
                    bucket.append(
                        {
                            "proposed_entity": entity,
                            "text": str(m.get("text", "")),
                            "attributes": {
                                str(k): str(v)
                                for k, v in (m.get("attributes") or {}).items()
                            },
                            "evidence": str(m.get("evidence", "")),
                        }
                    )
    return by_letter


def _merge_pool(candidates: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse the pool by normalized phrase so the model sees each concept once.

    For each distinct phrase we list which entities proposed it and the union of
    their attribute hints — surfacing the cross-entity confusion the arbitrator
    must resolve while keeping the prompt compact.
    """
    by_phrase: dict[str, dict[str, Any]] = {}
    for cand in candidates:
        key = normalize_phrase(cand["text"])
        if not key:
            continue
        entry = by_phrase.setdefault(
            key,
            {
                "text": cand["text"],
                "proposed_by": [],
                "attribute_hints": {},
                "evidence": [],
            },
        )
        ent = cand["proposed_entity"]
        if ent not in entry["proposed_by"]:
            entry["proposed_by"].append(ent)
        if cand["attributes"]:
            entry["attribute_hints"].setdefault(ent, cand["attributes"])
        ev = cand["evidence"]
        if ev and ev not in entry["evidence"]:
            entry["evidence"].append(ev)
    return list(by_phrase.values())


# ── Prompt builder ──────────────────────────────────────────────────────────────


def build_prompt_input(
    letter: ExectLetter, candidates: Sequence[dict[str, Any]]
) -> str:
    pool = _merge_pool(candidates)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "You are given one clinical letter and a POOL of candidate findings "
            "proposed by nine single-entity extractors. The pool has good recall "
            "but the entity labels are often wrong, duplicated, or spurious. "
            "Produce the SINGLE correct set of entity mentions for this letter."
        ),
        "instructions": [
            "KEEP BY DEFAULT. The pool has high recall; almost every candidate is a "
            "real finding. Your job is mainly to (a) fix the ENTITY label and (b) "
            "ADD the extra entity copies a concept needs — NOT to delete. Drop a "
            "candidate ONLY when it is clearly not a finding in the letter. Never "
            "drop a real clinical concept just because it looks redundant.",
            "Assign every kept finding to the entity whose definition it satisfies, "
            "using 'entity_routing'. The proposing entity in the pool is ONLY a hint "
            "and is frequently WRONG — re-decide it from the routing definitions. In "
            "particular, named seizure types proposed as PatientHistory are almost "
            "always Diagnosis.",
            "A single clinical concept frequently belongs to MORE THAN ONE entity. "
            "Emit it once per entity whose definition it satisfies. Example: "
            "'epilepsy' diagnosed at 18 that began at 12 -> one Diagnosis, one Onset "
            "(Age=12), one WhenDiagnosed (Age=18). 'focal seizures' that are the "
            "diagnosis AND occur 2-3 per month -> one Diagnosis "
            "(DiagCategory=MultipleSeizures, Certainty=5, Negation=Affirmed) AND one "
            "SeizureFrequency with the counts. Add the missing copies the pool did "
            "not propose.",
            "You MUST output every real finding in the letter. A letter typically "
            "yields 8-25 mentions across entities; do not return a short list.",
            "text MUST be the SHORT canonical concept phrase exactly as it appears "
            "in the letter (e.g. 'focal seizures', NOT 'focal seizures without "
            "change in awareness'; 'lamotrigine', NOT 'lamotrigine 200mg bd'). Put "
            "every qualifier, count, dose, and date in attributes.",
            "Include only attributes legal for the chosen entity (see "
            "attribute_vocabulary) and explicitly supported by the letter.",
            "Both text and evidence MUST be exact substrings of the letter.",
            "Return exactly one JSON object {\"mentions\": [...]}. No markdown fences.",
        ],
        "entity_routing": ENTITY_ROUTING,
        "attribute_vocabulary": {
            name: _attribute_vocabulary(ENTITY_REGISTRY[name]) for name in ENTITY_NAMES
        },
        "candidate_pool": pool,
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


# ── Output parsing + gating ─────────────────────────────────────────────────────


def parse_arbitration_json(
    raw_output: str,
) -> tuple[list[ArbitratedMention], list[str]]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
        _extract_json_object,
    )

    try:
        payload = json.loads(_extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return [], [f"invalid_json: {exc.msg}"]
    mentions_raw = payload.get("mentions") if isinstance(payload, dict) else None
    if not isinstance(mentions_raw, list):
        return [], ["no_mentions_list"]
    mentions: list[ArbitratedMention] = []
    errors: list[str] = []
    for i, raw in enumerate(mentions_raw):
        if not isinstance(raw, dict):
            errors.append(f"mention[{i}] not an object")
            continue
        attrs = raw.get("attributes")
        if isinstance(attrs, dict):
            raw = {**raw, "attributes": {str(k): str(v) for k, v in attrs.items() if v is not None}}
        # ``confidence`` is diagnostic only; models sometimes emit it as a number or
        # free string. Normalize to the literal vocabulary, defaulting to "medium".
        conf = str(raw.get("confidence", "")).strip().lower()
        raw = {**raw, "confidence": conf if conf in {"low", "medium", "high"} else "medium"}
        try:
            mentions.append(ArbitratedMention.model_validate(raw))
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f"mention[{i}] invalid: {exc}")
    return mentions, errors


def gate_and_project(
    letter_id: str,
    mentions: Sequence[ArbitratedMention],
    *,
    note_text: str,
) -> tuple[PredictedLetter, dict[str, int], list[str]]:
    """Evidence-faithfulness + schema repair per entity, then CUI projection.

    Drops mentions with an unknown entity or non-substring evidence (logged), and
    collapses exact within-entity duplicates (same entity, normalized phrase,
    repaired attributes).
    """
    warnings: list[str] = []
    drops = {"unknown_entity": 0, "evidence_invalid": 0, "duplicate": 0}
    kept: list[PredictedMention] = []
    seen: set[tuple[str, str, tuple]] = set()

    # Group by entity for the existing per-entity evidence checker / repairer.
    by_entity: dict[str, list[ArbitratedMention]] = {}
    for m in mentions:
        if m.entity not in ENTITY_REGISTRY:
            drops["unknown_entity"] += 1
            warnings.append(f"dropped_unknown_entity: {m.entity!r} text={m.text!r}")
            continue
        by_entity.setdefault(m.entity, []).append(m)

    for entity, ms in by_entity.items():
        spec: EntitySpec = ENTITY_REGISTRY[entity]
        # Reuse MentionRecord-shaped objects for the substring evidence check.
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
            MentionRecord,
        )

        records = [
            MentionRecord(
                text=m.text,
                attributes=dict(m.attributes),
                evidence=m.evidence,
                confidence=m.confidence,
                rationale=m.rationale,
            )
            for m in ms
        ]
        valid, invalid, ev_warnings = check_evidence(records, note_text=note_text)
        drops["evidence_invalid"] += len(invalid)
        warnings.extend(ev_warnings)
        for rec in valid:
            repaired, attr_warnings = repair_attributes(dict(rec.attributes), spec=spec)
            warnings.extend(attr_warnings)
            dedup_key = (
                entity,
                normalize_phrase(rec.text),
                tuple(sorted(repaired.items())),
            )
            if dedup_key in seen:
                drops["duplicate"] += 1
                continue
            seen.add(dedup_key)
            kept.append(
                PredictedMention(
                    entity=entity,
                    text=rec.text,
                    attributes=repaired,
                    evidence=rec.evidence,
                    confidence=rec.confidence,
                    rationale=rec.rationale,
                    component_owner=COMPONENT_OWNER,
                )
            )

    predicted = project_cuis(
        PredictedLetter(
            letter_id=letter_id,
            mentions=tuple(kept),
            diagnostics={"prompt_version": PROMPT_VERSION, "drops": drops},
        )
    )
    return predicted, drops, warnings


# ── Runner ───────────────────────────────────────────────────────────────────────


def run_arbitration(
    letters: Sequence[ExectLetter],
    candidate_pool: dict[str, list[dict[str, Any]]],
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
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyArbitrator()
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
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        candidates = candidate_pool.get(letter.letter_id, [])
        prompt_input_json = build_prompt_input(letter, candidates)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.arbitration_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        mentions, parse_errors = (
            parse_arbitration_json(raw_output) if raw_output else ([], ["not_run"])
        )
        predicted, drops, warnings = gate_and_project(
            letter.letter_id, mentions, note_text=letter.note_text
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "model": model,
                "mode": mode,
                "augment_rules": False,
                "n_candidates": len(candidates),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted.mentions),
                "drops": drops,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": warnings,
                "predicted_mentions": [_mention_to_row(m) for m in predicted.mentions],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.annotations
                    if a.entity in set(ENTITY_NAMES)
                ],
            }
        )
        if progress_every and checkpoint_jsonl_path and (len(rows) - n_resumed) % progress_every == 0:
            write_jsonl(rows, checkpoint_jsonl_path)
            print(
                json.dumps({"processed": len(rows), "total": len(letters)}),
                file=sys.stderr,
                flush=True,
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
    }
    metadata["summary"] = summarize_rows(rows)
    metadata["arbitration_diagnostics"] = _arbitration_diagnostics(rows)
    return rows, metadata


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
        "component_owner": mention.component_owner,
    }


def _arbitration_diagnostics(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    drops = {"unknown_entity": 0, "evidence_invalid": 0, "duplicate": 0}
    for r in rows:
        for k, v in (r.get("drops") or {}).items():
            drops[k] = drops.get(k, 0) + int(v)
    return {
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(
            1 for r in rows if any("invalid_json" in str(e) or "no_mentions_list" in str(e)
                                   for e in (r.get("parse_errors") or []))
        ),
        "n_mentions_raw": sum(int(r.get("n_mentions_raw", 0)) for r in rows),
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "drops": drops,
    }


# ── I/O ────────────────────────────────────────────────────────────────────────


def write_jsonl(rows: Sequence[dict[str, Any]], path: Path) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
        write_jsonl_rows,
    )

    write_jsonl_rows(rows, path)
