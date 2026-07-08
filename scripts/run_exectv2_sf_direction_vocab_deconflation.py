#!/usr/bin/env python3
"""SF ``FrequencyChange`` vocab deconflation probe driver (2026-07-08).

Zero-LLM-call re-scoring of two saved dev140 prediction artifacts (the rules arm
and the closed-option-selector arm from the hybrid-integration probe) against a
projected 2-D scoring key that deconflates the gold ``FrequencyChange`` vocab's
change-direction axis (Increased/Decreased/Same) from its frequency-magnitude
axis (Frequent/Infrequent). The question: does the rules-vs-selector gap
survive the deconflation, or is it a measurement artifact of the conflated
vocab?

Predeclaration:
``docs/experiments/exectv2/seizure_frequency/exectv2_sf_direction_vocab_deconflation_predeclaration_2026-07-08.md``

This is the same family of move as the raw-vs-projected decomposition (item 5):
a no-call re-scoring over a frozen prediction artifact that isolates one
scoring variable. The frozen ``state_profile_directional`` metric is reproduced
on both arms as the anchor sanity check (must reproduce 0.8897 rules / 0.8333
selector); the new ``state_profile_direction_deconf`` and
``state_profile_magnitude`` companions carry the deconflated attribution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import PRF1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_frequency_state,
)

ROOT = Path(__file__).resolve().parents[1]
RULES_ARM_JSONL = (
    ROOT / "experiments" / "exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl"
)
SELECTOR_ARM_JSONL = (
    ROOT / "experiments" / "exectv2_sf_closed_option_hybrid_integration_dev140_20260707.jsonl"
)
SUMMARY_JSON = (
    ROOT / "experiments" / "exectv2_sf_direction_vocab_deconflation_summary_20260708.json"
)
SF_ENTITY = "SeizureFrequency"

# Conflated anchor values the in-run scores must reproduce (the hybrid-
# integration probe's cited dev140 numbers). Used as the contract check.
EXPECTED_RULES_DIRECTIONAL_F1 = 0.8897
EXPECTED_SELECTOR_DIRECTIONAL_F1 = 0.8333
ANCHOR_TOLERANCE = 0.0001


def _pred_letters_from_jsonl(
    jsonl_path: Path, gold_by_id: dict[str, ExectLetter]
) -> list[ExectLetter]:
    """Build predicted ExectLetters from a saved-jsonl's SF predicted_mentions.

    Mirrors ``register_inv_sf_inversion_hypotheses._pred_letters_from_jsonl``:
    each mention's attributes are already post-adapter (the v08 union arbitration
    and the closed-option integration both persist their projected attributes),
    so they are wrapped as ExectAnnotations directly. ``FrequencyChange`` is
    already populated, so both the conflated and the deconflated metrics read it.
    """

    out: list[ExectLetter] = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        gold = gold_by_id.get(lid)
        if gold is None:
            continue
        sf_mentions = [
            m for m in row.get("predicted_mentions", []) if m.get("entity") == SF_ENTITY
        ]
        annotations = tuple(
            ExectAnnotation(
                entity=SF_ENTITY,
                text=str(m.get("text", "")),
                attributes={
                    str(k): str(v) for k, v in dict(m.get("attributes", {})).items()
                },
            )
            for m in sf_mentions
        )
        out.append(
            ExectLetter(letter_id=lid, note_text=gold.note_text, annotations=annotations)
        )
    return out


def _prf1_block(prefix: str, score: PRF1) -> dict[str, Any]:
    return {
        f"{prefix}_f1": round(score.f1, 4),
        f"{prefix}_precision": round(score.precision, 4),
        f"{prefix}_recall": round(score.recall, 4),
        f"{prefix}_tp": score.tp,
        f"{prefix}_fp": score.fp,
        f"{prefix}_fn": score.fn,
    }


def _score_arm(
    label: str,
    jsonl_path: Path,
    gold_letters: list[ExectLetter],
    gold_by_id: dict[str, ExectLetter],
) -> dict[str, Any]:
    pred_letters = _pred_letters_from_jsonl(jsonl_path, gold_by_id)
    scores = score_frequency_state(gold_letters, pred_letters)
    block: dict[str, Any] = {
        "label": label,
        "artifact": jsonl_path.name,
        "n_pred_letters": len(pred_letters),
        **_prf1_block("state_profile_directional", scores.state_profile_directional),
        **_prf1_block("state_profile_direction_deconf", scores.state_profile_direction_deconf),
        **_prf1_block("state_profile_magnitude", scores.state_profile_magnitude),
        **_prf1_block("state_profile", scores.state_profile),
    }
    print(f"[deconf] {label} ({jsonl_path.name}):")
    for metric in (
        "state_profile_directional",
        "state_profile_direction_deconf",
        "state_profile_magnitude",
        "state_profile",
    ):
        p = _prf1_block(metric, getattr(scores, metric))
        print(
            f"  {metric}: f1={p[metric + '_f1']:.4f} "
            f"(tp={p[metric + '_tp']} fp={p[metric + '_fp']} fn={p[metric + '_fn']})"
        )
    return block


def main() -> None:
    gold_letters = load_letters_for_split("dev")
    gold_by_id = {le.letter_id: le for le in gold_letters}

    rules = _score_arm("rules (v08 hybrid)", RULES_ARM_JSONL, gold_letters, gold_by_id)
    print()
    selector = _score_arm(
        "selector (closed-option hybrid integration)",
        SELECTOR_ARM_JSONL,
        gold_letters,
        gold_by_id,
    )

    # --- Anchor reproduction (contract check) -------------------------------
    rules_drift = abs(rules["state_profile_directional_f1"] - EXPECTED_RULES_DIRECTIONAL_F1)
    selector_drift = abs(
        selector["state_profile_directional_f1"] - EXPECTED_SELECTOR_DIRECTIONAL_F1
    )
    anchors_ok = rules_drift <= ANCHOR_TOLERANCE and selector_drift <= ANCHOR_TOLERANCE
    anchor_report = {
        "expected_rules_state_profile_directional_f1": EXPECTED_RULES_DIRECTIONAL_F1,
        "expected_selector_state_profile_directional_f1": EXPECTED_SELECTOR_DIRECTIONAL_F1,
        "rules_drift": round(rules_drift, 4),
        "selector_drift": round(selector_drift, 4),
        "anchors_reproduced": anchors_ok,
    }
    print()
    print(f"[anchor] rules drift={rules_drift:.4f} selector drift={selector_drift:.4f} "
          f"-> {'OK' if anchors_ok else 'CONTRACT FAILURE'}")

    # --- The comparison -----------------------------------------------------
    conflated_gap = round(
        rules["state_profile_directional_f1"] - selector["state_profile_directional_f1"], 4
    )
    direction_deconf_gap = round(
        rules["state_profile_direction_deconf_f1"]
        - selector["state_profile_direction_deconf_f1"],
        4,
    )
    magnitude_deconf_gap = round(
        rules["state_profile_magnitude_f1"] - selector["state_profile_magnitude_f1"], 4
    )
    comparison = {
        "conflated_gap": conflated_gap,
        "direction_deconf_gap": direction_deconf_gap,
        "magnitude_deconf_gap": magnitude_deconf_gap,
        # Band 1 threshold: direction-deconflated gap collapses to <= 0.01.
        "direction_gap_collapsed": direction_deconf_gap <= 0.01,
        # Band 3 threshold: direction-deconflated gap unchanged (within 0.005 of conflated).
        "direction_gap_unchanged": abs(direction_deconf_gap - conflated_gap) <= 0.005,
        "state_profile_byte_identical": (
            rules["state_profile_f1"] == selector["state_profile_f1"]
            and rules["state_profile_tp"] == selector["state_profile_tp"]
            and rules["state_profile_fp"] == selector["state_profile_fp"]
            and rules["state_profile_fn"] == selector["state_profile_fn"]
        ),
    }
    print()
    print(f"[gap] conflated={conflated_gap:+.4f} "
          f"direction_deconf={direction_deconf_gap:+.4f} "
          f"magnitude_deconf={magnitude_deconf_gap:+.4f}")

    summary: dict[str, Any] = {
        "date": "2026-07-08",
        "split": "dev140",
        "cost_llm_calls": 0,
        "arms": {"rules": rules, "selector": selector},
        "anchor_check": anchor_report,
        "comparison": comparison,
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"\n[written] {SUMMARY_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
