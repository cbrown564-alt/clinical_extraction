"""P2 — a recall-ADDITIVE generate->verify SF program for GEPA, scored on state_profile.

The prior multistage GEPA attempt failed because its verify stage only *filtered*
(it cut recall 805->783 facts). The decisive diagnostic then showed the v08 hybrid
holds 0.930 on the fair, type-agnostic ``state_profile`` via *precision-preserving
recall recovery* (changed 0.85R/1.00P) — a verify that ADDS missing facts, not one
that prunes. See ``docs/research/exectv2_sf_representation_not_recall_2026-06-28.md``.

This is a focused SeizureFrequency-only two-stage program:

* S0 (generate) — an exhaustive per-type structured-event SF extractor (the P3 schema).
* S1 (verify)   — a recall-ADDITIVE verifier: it reads the letter + S0's draft and
  outputs a COMPLETED + corrected event list, told to ADD the facts the draft missed
  (seizures that stopped, reported frequency changes, additional seizure types) and
  remove only the unsupported ones.

``forward`` runs S0 then S1, maps the verified events into ExECTv2 SF clinical-facts,
and emits ``clinical_facts_json`` so the existing dedup adapter + scorers are reused
unchanged. GEPA evolves BOTH instructions jointly. The metric scores the clinical
``state_profile`` (the fair clinical-recovery target) with a length penalty, and its
feedback shows the per-letter STATE diff so reflection learns to add missing states.
"""

from __future__ import annotations

import json
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import (
    LengthPenaltyConfig,
    _fbeta_from,
    _length_penalty,
    _prompt_lengths,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import approx_tokens
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)

EVENT_SCHEMA: dict[str, object] = {
    "events": [
        {
            "applies_to": "the seizure type this frequency statement is about, or 'seizures' if generic",
            "kind": "frequency_rate | cluster_frequency | seizure_free | changed | unknown",
            "change_direction": "increased | decreased | null (only when kind = changed)",
            "evidence": "exact substring copied from the letter",
        }
    ]
}
EVENT_SCHEMA_JSON: str = json.dumps(EVENT_SCHEMA, ensure_ascii=False, sort_keys=True)

KIND_TO_STATE: dict[str, str] = {
    "frequency_rate": "active_rate",
    "cluster_frequency": "active_rate",
    "seizure_free": "seizure_free",
    "changed": "changed",
    "unknown": "unknown",
}

GENERATE_SEED = (
    "You read one clinical letter and list EVERY distinct seizure-frequency statement "
    "as an event. Emit one event per (seizure type x distinct frequency statement) and "
    "list the same seizure type more than once when the letter gives it more than one "
    "distinct statement (e.g. a current numeric rate AND a separately-reported change). "
    "For each event give applies_to (the seizure type, or 'seizures' if generic); kind "
    "(an explicit numeric rate or cluster cadence = frequency_rate / cluster_frequency; "
    "seizures stopped / none / X seizure-free = seizure_free; a reported increase, "
    "decrease, improvement, or worsening WITHOUT a usable number = changed; mentioned "
    "but no usable frequency = unknown); change_direction only when kind = changed; and "
    "evidence copied verbatim. Favour recall — list every statement. Return exactly one "
    "JSON object matching output_schema with an 'events' list, no markdown."
)

VERIFY_SEED = (
    "You are a recall-additive verifier. You read the clinical letter and a DRAFT list "
    "of seizure-frequency events, and you output the COMPLETED, corrected list. The "
    "draft usually MISSES facts: add every seizure-frequency statement in the letter the "
    "draft omitted — especially seizures that have STOPPED (kind=seizure_free), reported "
    "INCREASES / DECREASES / improvements / worsening (kind=changed), and additional "
    "seizure types the draft consolidated away. Correct any wrong kind, and remove only "
    "events the letter does not support. Do NOT merely prune the draft. Keep every "
    "well-supported draft event. Return exactly one JSON object matching output_schema "
    "with the full 'events' list, no markdown."
)


class SeizureFrequencyGenerateSignature(dspy.Signature):
    """Generate an exhaustive per-type structured-event list of seizure-frequency facts."""

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    events_json: str = dspy.OutputField(
        desc="One JSON object with an 'events' list per output_schema. No markdown."
    )


class SeizureFrequencyVerifySignature(dspy.Signature):
    """Recall-additively verify: complete and correct the draft seizure-frequency events."""

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    draft_events_json: str = dspy.InputField(desc="The draft 'events' list to complete and correct.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    events_json: str = dspy.OutputField(
        desc="One JSON object with the COMPLETED 'events' list per output_schema. No markdown."
    )


def events_to_sf_facts(raw_output: str) -> list[dict]:
    """Map a structured-event JSON string into ExECTv2 SF clinical-fact dicts."""

    try:
        payload = json.loads(extract_json_object(raw_output))
    except Exception:
        return []
    events = payload.get("events") or [] if isinstance(payload, dict) else []
    facts: list[dict] = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        kind = str(ev.get("kind") or "unknown").strip().lower()
        facts.append(
            {
                "family": "seizure_frequency",
                "seizure_type": str(ev.get("applies_to") or "seizures"),
                "state": KIND_TO_STATE.get(kind, "unknown"),
                "evidence": str(ev.get("evidence") or ""),
            }
        )
    return facts


class SfVerifyExtractor(dspy.Module):
    """Two-stage SeizureFrequency program: generate -> recall-additive verify."""

    def __init__(self, generate_seed: str = GENERATE_SEED, verify_seed: str = VERIFY_SEED) -> None:
        super().__init__()
        self.generate = dspy.Predict(SeizureFrequencyGenerateSignature)
        self.verify = dspy.Predict(SeizureFrequencyVerifySignature)
        self.generate.signature = self.generate.signature.with_instructions(generate_seed)
        self.verify.signature = self.verify.signature.with_instructions(verify_seed)

    def forward(self, letter_text: str, output_schema: str = EVENT_SCHEMA_JSON) -> dspy.Prediction:
        drafted = self.generate(letter_text=letter_text, output_schema=output_schema)
        draft_json = str(getattr(drafted, "events_json", "") or "")
        verified = self.verify(
            letter_text=letter_text,
            draft_events_json=draft_json,
            output_schema=output_schema,
        )
        facts = events_to_sf_facts(str(getattr(verified, "events_json", "") or ""))
        prediction = dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": facts}, ensure_ascii=False)
        )
        prediction.instruction_tokens = approx_tokens(
            self.generate.signature.instructions
        ) + approx_tokens(self.verify.signature.instructions)
        prediction.demo_tokens = sum(
            approx_tokens(str(dict(demo)))
            for p in (self.generate, self.verify)
            for demo in (p.demos or [])
        )
        return prediction


def build_sf_verify_program() -> SfVerifyExtractor:
    return SfVerifyExtractor()


def combined_instruction(program: SfVerifyExtractor) -> str:
    return (
        f"=== generate ===\n{program.generate.signature.instructions}\n\n"
        f"=== verify ===\n{program.verify.signature.instructions}"
    )


def _facts_json_of(pred: Any) -> str:
    value = getattr(pred, "clinical_facts_json", None)
    if value is None and isinstance(pred, dict):
        value = pred.get("clinical_facts_json")
    return str(value) if value is not None else ""


def _state_labels(annotations) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for a in annotations:
        label = f"{a.text or 'seizures'}: {frequency_state_faithful(a.attributes)}"
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def build_sf_verify_metric(config: LengthPenaltyConfig | None = None, *, recall_beta: float = 1.0):
    """GEPA metric: SF ``state_profile`` F-beta minus a length penalty; state-diff feedback."""

    cfg = config or LengthPenaltyConfig()

    def metric(
        gold: Any,
        pred: Any,
        trace: Any = None,
        pred_name: str | None = None,
        pred_trace: Any = None,
    ) -> dspy.Prediction:
        gold_letter = getattr(gold, "letter", None)
        if gold_letter is None:
            raise ValueError("GEPA example is missing the gold ExectLetter ('letter').")
        raw = _facts_json_of(pred)
        record, errors = (
            parse_dedup_clinical_facts_json(raw) if raw else (None, ["empty_output"])
        )
        instr_tokens, demo_tokens = _prompt_lengths(pred, pred_trace)
        out_tokens = approx_tokens(raw)
        penalty = _length_penalty(instr_tokens, demo_tokens, out_tokens, cfg)

        if record is None:
            fb = (
                f"OUTPUT NOT SCORABLE ({(errors or ['unknown'])[0]}). The verify stage must "
                "return one JSON object with an 'events' list per output_schema; no markdown; "
                "every 'evidence' an exact substring of the letter."
            )
            return dspy.Prediction(score=0.0, feedback=fb)

        predicted, *_ = to_predicted_letter_from_dedup_facts(gold_letter, record)
        pred_exect = to_exect_letter(predicted)
        scores = score_frequency_state([gold_letter], [pred_exect])
        sp = scores.state_profile
        ch = scores.clinical_headline
        quality = _fbeta_from(sp.tp, sp.tp, sp.tp + sp.fp, sp.tp + sp.fn, beta=recall_beta)
        score = max(0.0, quality - penalty)

        gold_states = list(dict.fromkeys(
            frequency_state_faithful(a.attributes) for a in gold_letter.entities("SeizureFrequency")
        ))
        pred_states = list(dict.fromkeys(
            frequency_state_faithful(a.attributes) for a in pred_exect.entities("SeizureFrequency")
        ))
        missed = [s for s in gold_states if s not in pred_states]
        spurious = [s for s in pred_states if s not in gold_states]

        verdict = "CORRECT" if sp.f1 >= 0.999 else "PARTIAL"
        parts = [
            f"{verdict}. SF state_profile F1={sp.f1:.3f} (P={sp.precision:.2f} R={sp.recall:.2f}); "
            f"clinical_headline F1={ch.f1:.3f}.",
        ]
        if missed or spurious:
            if missed:
                parts.append(f"MISSED states you must ADD: {missed}.")
            if spurious:
                parts.append(f"SPURIOUS states to remove: {spurious}.")
            parts.append(
                f"GOLD facts={_state_labels(gold_letter.entities('SeizureFrequency'))}; "
                f"YOUR facts={_state_labels(pred_exect.entities('SeizureFrequency'))}."
            )
            parts.append(
                "The verify stage must ADD the missing seizure-frequency facts (seizures that "
                "stopped = seizure_free, reported increases/decreases/improvements = changed, "
                "additional seizure types) grounded in verbatim evidence, and remove only "
                "unsupported ones — do not merely filter the draft."
            )
        if cfg.enabled:
            note = f"Instruction is {instr_tokens} tokens (budget {cfg.instruction_token_budget})."
            if instr_tokens > cfg.instruction_token_budget:
                note = "TOO LONG. " + note
            parts.append(note)
        return dspy.Prediction(score=score, feedback=" ".join(parts))

    return metric
