"""GEPA-native multi-stage (generate -> verify) program for ExECTv2 de-dup facts.

Follow-up to the single-pass plateau: per-family GEPA (one evolvable instruction
per family) climbed to ~0.731 clinical_headline F1 — beating the hand-tuned 0.710
single prompt — but plateaued ~0.18 below the v08 multi-stage hybrid (0.9155). The
investigation concluded that remaining gap is *architectural*: the hybrid's lift on
Diagnosis (~0.91) and SeizureFrequency (~0.91) comes from dedicated *stages*
(generate -> verify -> arbitrate -> deterministic projection) that GEPA cannot
invent by evolving the instructions of a single-pass extractor.

This program gives GEPA a two-stage program to optimize. *We* author the fixed
stage graph; GEPA evolves all stage instructions jointly under the existing
length-penalized diff-feedback metric:

* **S0 Generate** — four per-family ``dspy.Predict`` (reused from
  ``program_multifamily``) draft facts per family for high recall.
* **S1 Verify** — four per-family ``dspy.Predict`` that re-read the letter and the
  draft facts and return the corrected, well-grounded final facts (precision +
  attribute fidelity). Seeded with a *lean* distillation of the hand-written
  ``entity_verifier`` clinical rules; GEPA grows them, the length penalty keeps
  them honest.

``forward`` runs generate -> verify per family and merges the **verified** facts
into one ``clinical_facts_json``, so the metric / adapter / four canonical scorers
are reused unchanged. The deterministic S3 projection (evidence/render gates +
CUI projection) already runs inside the metric/eval path. The optimizable surface
is now eight instructions (4 generate + 4 verify); the length penalty reads the
summed token count stamped onto the prediction, so bloat in any stage is penalized
in selection. S2 arbitration is deferred to Phase 2 (scope §7).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import (
    approx_tokens,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multifamily import (
    _FAMILY_PREDICTORS,
    _facts_of,
)

#: Family order, mirroring the generate stage. The merged output emission order.
FAMILIES: tuple[str, ...] = tuple(name for name, _sig, _schema in _FAMILY_PREDICTORS)

#: Per-family generate schema (constant input data, never evolved).
_FAMILY_SCHEMA: dict[str, str] = {name: schema for name, _sig, schema in _FAMILY_PREDICTORS}
_FAMILY_GEN_SIGNATURE = {name: sig for name, sig, _schema in _FAMILY_PREDICTORS}


# --- S1 Verify signatures (one per family) ----------------------------------
#
# Each verifier re-reads the letter and the draft facts and returns the corrected
# final facts in the SAME ``clinical_facts`` shape the metric reads. Field names
# are generic (the per-family class identity carries the family); the draft is fed
# as ``draft_facts_json`` and the corrected set returned as ``verified_facts_json``.


class DiagnosisVerifySignature(dspy.Signature):
    """You audit a draft list of diagnosis facts against the clinical letter.

    Keep facts that name an epilepsy syndrome or a named seizure-type diagnosis and
    whose evidence is an exact substring of the letter. Drop comorbidities,
    non-epileptic events, and duplicates. Add any clearly-stated epilepsy or
    named-seizure-type diagnosis the draft missed, at a concise canonical
    granularity (e.g. 'focal epilepsy', not a long qualified phrase). Set
    negation=negated only if the diagnosis is explicitly excluded. Return exactly
    one JSON object matching output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    draft_facts_json: str = dspy.InputField(desc="Draft diagnosis facts to audit (JSON).")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    verified_facts_json: str = dspy.OutputField(
        desc="One JSON object with the corrected 'clinical_facts' list of diagnosis facts. No markdown."
    )


class SeizureFrequencyVerifySignature(dspy.Signature):
    """You audit a draft list of seizure-frequency facts against the clinical letter.

    Keep a fact only when its evidence (an exact substring of the letter) names a
    seizure type (or 'seizures') AND gives a concrete state: a count/rate
    (active_rate), a stated seizure-free period (seizure_free), or an explicit
    frequency change (changed). Drop bare 'unknown' states, facts inferred from
    generic 'episodes'/'events'/'blackouts', and duplicates. Do not turn a
    historical active count into seizure_free. Return exactly one JSON object
    matching output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    draft_facts_json: str = dspy.InputField(desc="Draft seizure_frequency facts to audit (JSON).")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    verified_facts_json: str = dspy.OutputField(
        desc="One JSON object with the corrected 'clinical_facts' list of seizure_frequency facts. No markdown."
    )


class PrescriptionVerifySignature(dspy.Signature):
    """You audit a draft list of prescription facts against the clinical letter.

    Keep only current regimens whose evidence (an exact substring of the letter)
    states both a numeric dose and a dosing frequency. Drop past, planned-only, or
    dose/frequency-less drugs and duplicates. Normalize dose_unit to mg or g and
    frequency to 1/2/3/As_Required. Return exactly one JSON object matching
    output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    draft_facts_json: str = dspy.InputField(desc="Draft prescription facts to audit (JSON).")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    verified_facts_json: str = dspy.OutputField(
        desc="One JSON object with the corrected 'clinical_facts' list of prescription facts. No markdown."
    )


class InvestigationVerifySignature(dspy.Signature):
    """You audit a draft list of investigation facts against the clinical letter.

    Keep only completed MRI/CT/EEG/telemetry investigations with a stated result
    (normal or abnormal) whose evidence is an exact substring of the letter. Drop
    requested/planned-only investigations and duplicates (de-duplicate by
    modality+result). Return exactly one JSON object matching output_schema with a
    'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    draft_facts_json: str = dspy.InputField(desc="Draft investigation facts to audit (JSON).")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    verified_facts_json: str = dspy.OutputField(
        desc="One JSON object with the corrected 'clinical_facts' list of investigation facts. No markdown."
    )


_FAMILY_VERIFY_SIGNATURE: dict[str, type[dspy.Signature]] = {
    "diagnosis": DiagnosisVerifySignature,
    "seizure_frequency": SeizureFrequencyVerifySignature,
    "prescription": PrescriptionVerifySignature,
    "investigation": InvestigationVerifySignature,
}


def _gen_attr(family: str) -> str:
    return f"generate_{family}"


def _verify_attr(family: str) -> str:
    return f"verify_{family}"


class GepaMultiStageExtractor(dspy.Module):
    """Per-family generate -> verify; every stage instruction is evolved by GEPA."""

    def __init__(
        self,
        s0_seed_instructions: dict[str, str] | None = None,
        s1_seed_instructions: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        for family in FAMILIES:
            generate = dspy.Predict(_FAMILY_GEN_SIGNATURE[family])
            verify = dspy.Predict(_FAMILY_VERIFY_SIGNATURE[family])
            if s0_seed_instructions and s0_seed_instructions.get(family):
                generate.signature = generate.signature.with_instructions(
                    s0_seed_instructions[family]
                )
            if s1_seed_instructions and s1_seed_instructions.get(family):
                verify.signature = verify.signature.with_instructions(s1_seed_instructions[family])
            setattr(self, _gen_attr(family), generate)
            setattr(self, _verify_attr(family), verify)

    def _predictors(self) -> list[dspy.Predict]:
        predictors: list[dspy.Predict] = []
        for family in FAMILIES:
            predictors.append(getattr(self, _gen_attr(family)))
            predictors.append(getattr(self, _verify_attr(family)))
        return predictors

    def forward(self, letter_text: str, output_schema: str | None = None) -> dspy.Prediction:
        merged: list[dict] = []
        for family in FAMILIES:
            schema = _FAMILY_SCHEMA[family]
            generate = getattr(self, _gen_attr(family))
            verify = getattr(self, _verify_attr(family))

            drafted = generate(letter_text=letter_text, output_schema=schema)
            draft_facts = _facts_of(str(getattr(drafted, "clinical_facts_json", "") or ""))

            verified = verify(
                letter_text=letter_text,
                draft_facts_json=json.dumps({"clinical_facts": draft_facts}, ensure_ascii=False),
                output_schema=schema,
            )
            # The verified facts are the family's contribution. _facts_of returns the
            # raw fact dicts exactly as emitted, so the merged output carries no
            # synthetic 'attributes' key — the metric parser coerces an empty
            # attributes dict into a string and rejects it (the per-family trap).
            merged.extend(_facts_of(str(getattr(verified, "verified_facts_json", "") or "")))

        prediction = dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": merged}, ensure_ascii=False)
        )
        # Stamp summed prompt size across ALL evolvable stages (4 generate + 4 verify)
        # so the length penalty sees the whole evolved surface during GEPA selection.
        prediction.instruction_tokens = sum(
            approx_tokens(p.signature.instructions) for p in self._predictors()
        )
        prediction.demo_tokens = sum(
            approx_tokens(str(dict(demo))) for p in self._predictors() for demo in (p.demos or [])
        )
        return prediction


def build_multistage_program(
    s0_seed_instructions: dict[str, str] | None = None,
) -> GepaMultiStageExtractor:
    """Two-stage program. S0 uses the lean per-family generate signatures by default
    (pass ``s0_seed_instructions`` to warm-start from the evolved 0.731 run); S1
    uses the lean distilled verify seeds defined above."""

    return GepaMultiStageExtractor(s0_seed_instructions=s0_seed_instructions)


def combined_instruction(program: GepaMultiStageExtractor) -> str:
    """All eight evolved stage instructions, for the instruction artifact + tokens.

    Labelled ``=== generate.<family> ===`` / ``=== verify.<family> ===`` so the
    artifact (and the summed token count it implies) mirrors the per-family helper.
    """

    blocks: list[str] = []
    for family in FAMILIES:
        gen = getattr(program, _gen_attr(family)).signature.instructions
        blocks.append(f"=== generate.{family} ===\n{gen}")
    for family in FAMILIES:
        ver = getattr(program, _verify_attr(family)).signature.instructions
        blocks.append(f"=== verify.{family} ===\n{ver}")
    return "\n\n".join(blocks)


# --- Warm-start: load the evolved S0 seeds from the 0.731 multifamily artifact ---

#: The per-family multifamily run whose evolved instructions are the S0 warm-start.
EVOLVED_MULTIFAMILY_INSTRUCTION = (
    Path(__file__).resolve().parents[6]
    / "experiments"
    / "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.instruction.txt"
)

_BLOCK_RE = re.compile(r"^=== (?P<name>[\w.]+) ===\s*$", re.MULTILINE)


def _unwrap_instruction(text: str) -> str:
    """Unwrap a ``{"instructions": "..."}`` block to its inner text.

    GEPA's reflection sometimes evolves an instruction into a JSON object literal
    (the diagnosis family did in the 0.731 run); warm-starting a signature wants the
    inner instruction text, not the JSON wrapper.
    """

    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            return stripped
        if isinstance(payload, dict) and isinstance(payload.get("instructions"), str):
            return payload["instructions"].strip()
    return stripped


def parse_combined_instruction(text: str) -> dict[str, str]:
    """Parse a ``combined_instruction`` artifact into a ``{block_name: text}`` map.

    Block names are the labels emitted by ``combined_instruction`` — for the
    per-family artifact these are bare family names (``diagnosis``); for a
    multi-stage artifact they are ``generate.diagnosis`` etc.
    """

    matches = list(_BLOCK_RE.finditer(text))
    blocks: dict[str, str] = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks[match.group("name")] = _unwrap_instruction(text[start:end])
    return blocks


def load_evolved_s0_seeds(path: Path | None = None) -> dict[str, str]:
    """Per-family S0 warm-start seeds parsed from the evolved multifamily artifact.

    Returns ``{family: instruction}`` for the four families. Raises if the artifact
    is missing or any family is absent, so a warm-start run fails loudly rather than
    silently seeding lean.
    """

    artifact = path or EVOLVED_MULTIFAMILY_INSTRUCTION
    if not artifact.exists():
        raise FileNotFoundError(f"Evolved S0 seed artifact not found: {artifact}")
    blocks = parse_combined_instruction(artifact.read_text(encoding="utf-8"))
    seeds = {family: blocks[family] for family in FAMILIES if family in blocks}
    missing = [family for family in FAMILIES if family not in seeds or not seeds[family]]
    if missing:
        raise ValueError(f"Evolved S0 seed artifact {artifact} is missing families: {missing}")
    return seeds
