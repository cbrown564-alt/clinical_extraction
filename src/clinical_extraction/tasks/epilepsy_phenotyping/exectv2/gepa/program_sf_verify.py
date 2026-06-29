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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
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
            "kind": "frequency_rate | cluster_frequency | seizure_free | changed",
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
    "decrease, improvement, or worsening = changed); and evidence copied verbatim. If a "
    "seizure type is only mentioned with no usable frequency, seizure-free, or change "
    "statement, do NOT emit an event for it. Favour recall on real frequency statements. "
    "Return exactly one JSON object matching output_schema with an 'events' list, no markdown."
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


#: v2 verify seed — recall-additive AND change-class disciplined. P2's verify recovered
#: change RECALL (0.48) but over-fired it (0.46 precision) vs the hybrid's 0.85R/1.00P. This
#: seed keeps the recall-additive behaviour but adds an explicit change-boundary rule, while
#: preserving the rate+change per-type multiplicity gold rewards.
VERIFY_SEED_V2 = (
    "You are a recall-additive verifier. You read the clinical letter and a DRAFT list of "
    "seizure-frequency events, and you output the COMPLETED, corrected list. The draft "
    "usually MISSES facts: add every seizure-frequency statement the draft omitted — "
    "especially seizures that have STOPPED (kind=seizure_free) and additional seizure "
    "types the draft consolidated away. Keep every well-supported draft event; remove only "
    "events the letter does not support; do NOT merely prune. "
    "Be PRECISE about kind=changed: emit it ONLY when the letter contains an explicit "
    "statement that the frequency increased, decreased, improved, or worsened (a directional "
    "comparison in words). Do NOT emit changed merely because a numeric rate is present, "
    "because a single dated event occurred, or for vague/non-directional statements "
    "('fluctuates', 'variable', 'ongoing'). When the letter gives BOTH a current rate AND a "
    "separate explicit change statement for the same seizure type, emit BOTH a frequency_rate "
    "event and a changed event. Return exactly one JSON object matching output_schema with "
    "the full 'events' list, no markdown."
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
    """Two-stage SeizureFrequency program: generate -> recall-additive verify.

    ``generate_lm`` / ``verify_lm`` optionally pin a *per-stage* LM (e.g. a reasoner
    extractor with a gpt-4.1-mini verifier); when ``None`` the stage falls back to the
    global ``dspy.settings.lm``. ``generate_demos`` / ``verify_demos`` attach hand-curated
    few-shot demos (Phase 5 H-examples). GEPA's ``build_program`` deepcopies the student and
    mutates only instructions, so both the per-stage LMs and the demos survive optimization.
    """

    def __init__(
        self,
        generate_seed: str = GENERATE_SEED,
        verify_seed: str = VERIFY_SEED,
        *,
        generate_lm: dspy.LM | None = None,
        verify_lm: dspy.LM | None = None,
        generate_demos: list | None = None,
        verify_demos: list | None = None,
    ) -> None:
        super().__init__()
        self.generate = dspy.Predict(SeizureFrequencyGenerateSignature)
        self.verify = dspy.Predict(SeizureFrequencyVerifySignature)
        self.generate.signature = self.generate.signature.with_instructions(generate_seed)
        self.verify.signature = self.verify.signature.with_instructions(verify_seed)
        if generate_lm is not None:
            self.generate.lm = generate_lm
        if verify_lm is not None:
            self.verify.lm = verify_lm
        if generate_demos:
            self.generate.demos = list(generate_demos)
        if verify_demos:
            self.verify.demos = list(verify_demos)

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


def build_sf_verify_program_v2() -> SfVerifyExtractor:
    """SF verify program seeded with the change-class-disciplined verify (VERIFY_SEED_V2)."""

    return SfVerifyExtractor(generate_seed=GENERATE_SEED, verify_seed=VERIFY_SEED_V2)


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


#: Diagnosis categories that count as an epilepsy diagnosis for the SF over-emission gate.
_EPILEPSY_DIAG_CATEGORIES: frozenset[str] = frozenset(
    {"Epilepsy", "MultipleSeizures", "SingleSeizure"}
)


def _states_by_type(annotations) -> dict[str, tuple[str, list[str]]]:
    """Group SF facts by normalized seizure type → (display label, ordered states).

    Keying by :func:`normalize_phrase` aligns gold's hyphenated CUIPhrase types with the
    model's free-text ``applies_to`` so the per-(type, state) diff survives surface drift.
    """

    out: dict[str, tuple[str, list[str]]] = {}
    for a in annotations:
        display = a.text or "seizures"
        key = normalize_phrase(display) or "seizures"
        _, states = out.setdefault(key, (display, []))
        state = frequency_state_faithful(a.attributes)
        if state not in states:
            states.append(state)
    return out


def _render_by_type(by_type: dict[str, tuple[str, list[str]]]) -> str:
    if not by_type:
        return "(none)"
    return "; ".join(f"{label}={states}" for label, states in by_type.values())


def _epilepsy_dx_status(gold_letter) -> str:
    """Epilepsy-diagnosis status for the SF over-emission gate.

    ``confirmed`` = a *definite* (Certainty 5), affirmed epilepsy Diagnosis is present;
    ``uncertain`` = an epilepsy Diagnosis exists but only as probable/possible/negated
    (the "?temporal lobe" / "probable JME" convention the error analysis flagged — gold
    excludes SF for those); ``absent`` = no epilepsy Diagnosis at all (dissociative /
    non-epileptic only). This drives a non-contradictory Cat-B reason: a probable-epilepsy
    letter is no longer told it has "no confirmed diagnosis".
    """

    has_epilepsy = False
    for a in gold_letter.entities("Diagnosis"):
        attrs = a.attributes
        if str(attrs.get("DiagCategory", "")) not in _EPILEPSY_DIAG_CATEGORIES:
            continue
        has_epilepsy = True
        if str(attrs.get("Certainty", "")) == "5" and str(attrs.get("Negation", "Affirmed")) == "Affirmed":
            return "confirmed"
    return "uncertain" if has_epilepsy else "absent"


def build_sf_verify_metric(
    config: LengthPenaltyConfig | None = None,
    *,
    recall_beta: float = 1.0,
    change_precision_weight: float = 0.0,
):
    """GEPA metric: SF ``state_profile`` F-beta minus a length penalty; per-(type, state) feedback.

    Phase 5 (focused-lanes plan §5) redesigns the *feedback* — scoring is unchanged so any
    lift is attributable to feedback precision alone. The diff moves from letter-level
    de-duplicated state sets to **per-(seizure_type, state) keyed facts**, with the reason
    attached for each of the four error classes the SF verify error analysis named
    (``docs/experiments/exectv2/seizure_frequency/exectv2_sf_verify_error_analysis_2026-06-29.md``):
    A. per-type multiplicity (rate AND a separate qualitative change for the same type, and the
    FrequencyChange=Same-is-not-a-fact boundary); B. over-emission on non-epileptic / unconfirmed
    events (gated on whether the gold letter has a confirmed epilepsy diagnosis); C. temporal
    rate↔seizure-free confusion (a historical dated count is an active rate, not the current
    seizure-free status); D. empty output (already covered by the ``record is None`` branch).

    ``change_precision_weight`` > 0 adds targeted pressure on the change class (the one cell
    P2 lost: changed 0.48R/0.46P vs hybrid 0.85R/1.00P). When the prediction asserts a
    ``changed`` state for a letter whose gold has no change, the score is penalized by this
    weight — so the minority change class is disciplined for precision without the aggregate
    state_profile objective washing it out.
    """

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
        quality = _fbeta_from(sp.tp, sp.tp, sp.tp + sp.fp, sp.tp + sp.fn, beta=recall_beta)

        gold_states = list(dict.fromkeys(
            frequency_state_faithful(a.attributes) for a in gold_letter.entities("SeizureFrequency")
        ))
        pred_states = list(dict.fromkeys(
            frequency_state_faithful(a.attributes) for a in pred_exect.entities("SeizureFrequency")
        ))
        missed = [s for s in gold_states if s not in pred_states]
        spurious = [s for s in pred_states if s not in gold_states]

        change_over_called = "changed" in pred_states and "changed" not in gold_states
        if change_precision_weight and change_over_called:
            quality = max(0.0, quality - change_precision_weight)
        score = max(0.0, quality - penalty)

        verdict = "CORRECT" if sp.f1 >= 0.999 else "PARTIAL"
        parts = [
            f"{verdict}. SF state_profile F1={sp.f1:.3f} (P={sp.precision:.2f} R={sp.recall:.2f}).",
        ]
        if missed or spurious:
            # state_profile is TYPE-AGNOSTIC: it scores the per-letter SET of states, ignoring
            # seizure type. So every per-type callout below is gated on the letter-level
            # missed/spurious state sets — the only thing the score actually penalizes — so the
            # feedback never tells the model to "fix" a fact that is already a scored TP (e.g. a
            # generic 'seizures: active-rate' that matches gold's 'tonic-clonic: active-rate').
            missed_set, spurious_set = set(missed), set(spurious)
            gold_bt = _states_by_type(gold_letter.entities("SeizureFrequency"))
            pred_bt = _states_by_type(pred_exect.entities("SeizureFrequency"))
            parts.append(f"GOLD by seizure type: {_render_by_type(gold_bt)}.")
            parts.append(f"YOUR facts by seizure type: {_render_by_type(pred_bt)}.")
            parts.append(
                "(Scoring is type-agnostic on the SET of states; state active-rate = a "
                "frequency_rate/cluster_frequency event, seizure-free = seizure_free, "
                "changed = a qualitative FrequencyChange.)"
            )

            # Category A — per-type multiplicity: gold tags one type with a state you missed
            # AND that state is genuinely missing at the letter level (in missed_set).
            multiplicity = []
            for key, (label, gstates) in gold_bt.items():
                if key not in pred_bt or len(gstates) <= 1:
                    continue
                add = [s for s in gstates if s not in pred_bt[key][1] and s in missed_set]
                if add:
                    multiplicity.append(f"'{label}' needs {gstates} but you emitted {pred_bt[key][1]} (ADD {add})")
            if multiplicity:
                parts.append(
                    "PER-TYPE MULTIPLICITY — emit BOTH facts for the SAME type: "
                    + "; ".join(multiplicity)
                    + ". When a seizure type has a numeric rate AND a separately-stated "
                    "qualitative change ('infrequent', 'increased', 'fewer', 'improved'), emit a "
                    "frequency_rate event AND a changed event for that type."
                )

            # Category A (FP) — FrequencyChange=Same emitted as a changed fact, but ONLY when
            # 'changed' is genuinely spurious at the letter level (no gold type has 'changed').
            same_fp = [
                pred_bt[key][0]
                for key in pred_bt
                if "changed" in spurious_set
                and key in gold_bt
                and "changed" in pred_bt[key][1]
                and "changed" not in gold_bt[key][1]
                and "active-rate" in gold_bt[key][1]
            ]
            if same_fp:
                parts.append(
                    f"FALSE 'changed' (stability is not a separate change): you tagged 'changed' for "
                    f"{same_fp} but gold records only active-rate there. A 'no change' / 'stable' / "
                    "'best it's ever been' statement is NOT a separate changed fact when that type "
                    "already has a rate — emit 'changed' only for an explicit increase/decrease/"
                    "improvement/worsening."
                )

            # Category B — over-emission: a pred type absent from gold that carries a SPURIOUS
            # state (so it actually costs precision). A generic-vs-specific type whose state
            # still matches gold is NOT flagged (it scored as a TP).
            over_types = [
                label
                for key, (label, states) in pred_bt.items()
                if key not in gold_bt and any(s in spurious_set for s in states)
            ]
            if over_types:
                status = _epilepsy_dx_status(gold_letter)
                if not gold_bt and status == "absent":
                    reason = (
                        "this letter has NO epilepsy diagnosis — suspected, dissociative, or "
                        "non-epileptic events must NOT be tagged with a seizure-frequency."
                    )
                elif not gold_bt and status == "uncertain":
                    reason = (
                        "the epilepsy diagnosis here is not definite (suspected / probable / "
                        "under investigation, e.g. a '?' qualifier) — a non-definite diagnosis "
                        "gets no seizure-frequency facts."
                    )
                else:
                    reason = (
                        "these events are non-epileptic, or not part of the seizure-frequency "
                        "picture for the confirmed epilepsy — only count seizures from the "
                        "confirmed diagnosis."
                    )
                parts.append(f"OVER-EMISSION on {over_types}: {reason}")

            # Category C — temporal: a historical dated count read as current seizure-free.
            if "seizure-free" in spurious_set and "active-rate" in missed_set:
                parts.append(
                    "TEMPORAL (rate vs free): you tagged seizure-free where gold records "
                    "active-rate. Gold tags a historical/dated seizure count as active-rate even "
                    "when the patient is 'currently seizure free' — a past dated event is a rate, "
                    "not the current seizure-free status."
                )

            residual = []
            if missed:
                residual.append(f"MISSED states to ADD: {missed}")
            if spurious:
                residual.append(f"SPURIOUS states to remove: {spurious}")
            if residual:
                parts.append("; ".join(residual) + ".")

            # Catch-all change over-call not already localized by Category A/B above.
            if change_over_called and not same_fp and not over_types:
                over = [
                    a.text or "seizures"
                    for a in pred_exect.entities("SeizureFrequency")
                    if frequency_state_faithful(a.attributes) == "changed"
                ]
                parts.append(
                    f"CHANGE OVER-CALL: 'changed' asserted for {list(dict.fromkeys(over))} but "
                    "gold records no qualitative change on this letter. Emit 'changed' ONLY for an "
                    "explicit increase/decrease/improvement/worsening stated in words."
                )
        if cfg.enabled:
            note = f"Instruction is {instr_tokens} tokens (budget {cfg.instruction_token_budget})."
            if instr_tokens > cfg.instruction_token_budget:
                note = "TOO LONG. " + note
            parts.append(note)
        return dspy.Prediction(score=score, feedback=" ".join(parts))

    return metric
