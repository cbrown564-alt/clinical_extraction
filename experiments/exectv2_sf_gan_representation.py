"""P3 — does the Gan structured-event REPRESENTATION close the ExECTv2 SF gap?

The de-dup `clinical_headline` surface buries SeizureFrequency as 1-of-4 families with a
coarse `state` field and instructs the model to "emit one fact per distinct seizure type"
— directly against gold's exhaustive per-(type x frequency-statement) tagging. This probe
ports the Gan2026 winning representation (per-type structured *events*: applies_to + kind)
to a FOCUSED ExECTv2 SF extractor, projects each event into an ExECTv2 SF clinical-fact via
the EXISTING dedup adapter, and scores on both the convention-strict clinical_headline and
the clinical-recovery state_profile. Same model (gpt-4.1-mini), different schema — the
decisive test of "represent the same concept in a schema that matches gold."

Baselines to beat (best de-dup run, dev140): clinical_headline 0.592 / state_profile 0.713;
hybrid SF ~0.91.

Usage:
    uv run python experiments/exectv2_sf_gan_representation.py --limit 8      # smoke
    uv run python experiments/exectv2_sf_gan_representation.py                # full dev140
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import score_frequency_state
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

EXPERIMENTS = Path("C:/Users/cbrow/Code/clinical_extraction/experiments")

# Ported from gan2026/gepa/program.py OUTPUT_SCHEMA, restricted to the per-type event
# fields ExECTv2 SF needs, with an explicit 'changed' kind (the class the de-dup coarse
# state collapses) and direction.
EVENT_SCHEMA = {
    "events": [
        {
            "applies_to": "the seizure type this frequency statement is about, or 'seizures' if generic",
            "kind": "frequency_rate | cluster_frequency | seizure_free | changed | unknown",
            "change_direction": "increased | decreased | null (only when kind = changed)",
            "evidence": "exact substring copied from the letter",
        }
    ]
}
EVENT_SCHEMA_JSON = json.dumps(EVENT_SCHEMA, ensure_ascii=False, sort_keys=True)

KIND_TO_STATE = {
    "frequency_rate": "active_rate",
    "cluster_frequency": "active_rate",
    "seizure_free": "seizure_free",
    "changed": "changed",
    "unknown": "unknown",
}


class SeizureFrequencyEventSignature(dspy.Signature):
    """You read one clinical letter and list EVERY distinct seizure-frequency statement as an event.

    Emit one event per (seizure type x distinct frequency statement) — list the same
    seizure type MORE THAN ONCE when the letter gives it more than one distinct
    frequency statement (e.g. a current numeric rate AND a separately-reported change).
    For each event give: applies_to (the seizure type, or 'seizures' if generic); kind —
    an explicit numeric rate or cluster cadence = frequency_rate / cluster_frequency;
    seizures stopped / none / X seizure-free = seizure_free; a reported increase, decrease,
    improvement, or worsening WITHOUT a usable number = changed; mentioned but no usable
    frequency = unknown; change_direction only when kind = changed; and evidence copied
    verbatim from the letter. Return exactly one JSON object matching output_schema with an
    'events' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    events_json: str = dspy.OutputField(
        desc="One JSON object with an 'events' list per output_schema. No markdown."
    )


def _events_to_sf_facts(raw_output: str) -> list[dict]:
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
        state = KIND_TO_STATE.get(kind, "unknown")
        facts.append(
            {
                "family": "seizure_frequency",
                "seizure_type": str(ev.get("applies_to") or "seizures"),
                "state": state,
                "evidence": str(ev.get("evidence") or ""),
            }
        )
    return facts


def _mentions_payload(pred_exect) -> list[dict]:
    return [
        {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
        for a in pred_exect.annotations
        if a.entity == "SeizureFrequency"
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--limit", type=int, default=0, help="0 = full dev140")
    parser.add_argument("--out", default="exectv2_sf_gan_representation_gpt41mini_20260628")
    args = parser.parse_args()

    lm = build_dspy_lm(args.model, temperature=0.0, max_tokens=4000, cache=True)
    dspy.configure(lm=lm)
    extractor = dspy.Predict(SeizureFrequencyEventSignature)

    gold = gepa_data.load_dev_letters()
    if args.limit:
        gold = gold[: args.limit]

    gold_list = []
    pred_list = []
    rows = []
    for i, g in enumerate(gold, 1):
        out = extractor(letter_text=g.note_text, output_schema=EVENT_SCHEMA_JSON)
        facts = _events_to_sf_facts(str(getattr(out, "events_json", "") or ""))
        raw = json.dumps({"clinical_facts": facts}, ensure_ascii=False)
        record, _errors = parse_dedup_clinical_facts_json(raw)
        if record is None:
            pred_exect = to_exect_letter(
                to_predicted_letter_from_dedup_facts(
                    g, parse_dedup_clinical_facts_json('{"clinical_facts": []}')[0]
                )[0]
            )
        else:
            predicted, *_ = to_predicted_letter_from_dedup_facts(g, record)
            pred_exect = to_exect_letter(predicted)
        gold_list.append(g)
        pred_list.append(pred_exect)
        rows.append({"letter_id": g.letter_id, "predicted_mentions": _mentions_payload(pred_exect)})
        if i % 20 == 0:
            print(f"  ...{i}/{len(gold)} letters")

    score = score_frequency_state(gold_list, pred_list)
    ch, sp = score.clinical_headline, score.state_profile
    print(f"\nSF over {len(gold)} letters (Gan event representation, {args.model}):")
    print(
        f"  clinical_headline  P={ch.precision:.3f} R={ch.recall:.3f} F1={ch.f1:.3f}"
        f"  (vs de-dup 0.592)"
    )
    print(
        f"  state_profile      P={sp.precision:.3f} R={sp.recall:.3f} F1={sp.f1:.3f}"
        f"  (vs de-dup 0.713)"
    )

    out_path = EXPERIMENTS / f"{args.out}.jsonl"
    out_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    print(f"\nsaved predictions -> {out_path}")


if __name__ == "__main__":
    main()
