"""A5 probe — a DeepSeek-tailored precision instruction profile (bounded, single model).

Predecessor-lessons avenue A5 (`docs/research/predecessor_lessons/03_promising_unfinished_avenues.md`)
was confirmed fully unbuilt: no model-specific prompt profile has ever been tried on ExECTv2.
This probe targets the one sharply-characterized model-specific failure mode the GEPA workstream
already found (Phase 0c, `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` Sec 6b):
DeepSeek-chat is a better RETRIEVER than gpt-4.1-mini on the per-family GEPA producer (higher
evidence-presence recall) but a worse KEYER (over-emits, costing precision -- headline F1 dropped
to 0.681 from mini's 0.731/0.719 on the *identical*, mini-tuned instruction text, never adapted
for DeepSeek).

This is a bounded, single-failure-mode probe per A5's safe-protocol-shape: ONE model
(deepseek-chat), ONE target failure (over-emission/weak-keying), comparing the EXISTING
mini-evolved per-family instructions verbatim (the baseline DeepSeek already ran in Phase 0c)
against the same instructions plus ONE added precision-discipline clause per family, holding
the scorer, data slice (dev140), and program architecture fixed. No GEPA optimization loop is
run -- this is a single hand-authored comparison, not a re-opened search.

Usage:  uv run python experiments/exectv2_deepseek_precision_profile_probe.py
"""

from __future__ import annotations

import json
from pathlib import Path

import dotenv
import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multifamily import (
    GepaPerFamilyExtractor,
    _FAMILY_PREDICTORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multistage import (
    parse_combined_instruction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import _evaluate_program
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
SEED_INSTRUCTION_PATH = ROOT / "experiments" / "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.instruction.txt"
MODEL = "deepseek/deepseek-chat"
OUT_JSON = ROOT / "experiments" / "exectv2_deepseek_precision_profile_probe_2026-06-30.json"
OUT_MD = ROOT / "docs" / "experiments" / "exectv2" / "reliability" / "exectv2_deepseek_precision_profile_probe_2026-06-30.md"

PRECISION_ADDENDUM = (
    " Precision discipline: only emit a fact when the evidence text itself directly states or "
    "unambiguously implies the specific value you are claiming -- do not emit a fact from a "
    "borderline, generic, or loosely-related mention. When in doubt, omit it rather than guess."
)

# Comparators from the Phase 0c DeepSeek baseline + the mini reference (focused-lanes plan Sec 6b).
COMPARATORS = {
    "mini_per_family_baseline_headline": 0.7313,
    "deepseek_phase0c_model_swap_only_headline": 0.681,
}


def build_program(*, instructions: dict[str, str], addendum: str) -> GepaPerFamilyExtractor:
    program = GepaPerFamilyExtractor()
    for name, _signature, _schema in _FAMILY_PREDICTORS:
        seed = instructions[name].strip()
        predictor = getattr(program, name)
        predictor.signature = predictor.signature.with_instructions(seed + addendum)
    return program


def main() -> None:
    dotenv.load_dotenv(ROOT / ".env")

    instructions = parse_combined_instruction(SEED_INSTRUCTION_PATH.read_text(encoding="utf-8"))
    letters = gepa_data.load_dev_letters()

    lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=4000, cache=True)
    dspy.configure(lm=lm)

    results = {}
    for condition, addendum in (("baseline", ""), ("precision_addendum", PRECISION_ADDENDUM)):
        program = build_program(instructions=instructions, addendum=addendum)
        rows, summary = _evaluate_program(program, letters, num_threads=8)
        results[condition] = summary
        print(f"\n=== {condition} ===")
        print(json.dumps(summary["clinical_headline"], indent=2))
        print("evidence_recall:", json.dumps(summary["evidence_recall"], indent=2))

    out = {
        "model": MODEL,
        "seed_instruction_source": SEED_INSTRUCTION_PATH.name,
        "addendum": PRECISION_ADDENDUM,
        "comparators": COMPARATORS,
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    base_f1 = results["baseline"]["clinical_headline"]["overall_f1"]
    addendum_f1 = results["precision_addendum"]["clinical_headline"]["overall_f1"]
    delta = addendum_f1 - base_f1
    print(f"\nDeepSeek baseline headline F1   : {base_f1:.4f} (Phase 0c comparator: "
          f"{COMPARATORS['deepseek_phase0c_model_swap_only_headline']})")
    print(f"DeepSeek + precision addendum F1: {addendum_f1:.4f}")
    print(f"delta: {delta:+.4f}")

    write_report(out, delta)
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_MD}")


def write_report(out: dict, delta: float) -> None:
    base = out["results"]["baseline"]
    add = out["results"]["precision_addendum"]
    base_hl = base["clinical_headline"]
    add_hl = add["clinical_headline"]

    precision_delta = add_hl["precision"] - base_hl["precision"]
    recall_delta = add_hl["recall"] - base_hl["recall"]
    if delta >= 0.03:
        verdict = "POSITIVE — beats the baseline by a non-trivial margin."
    elif delta > 0 and precision_delta > 0.01 and abs(recall_delta) < 0.01:
        verdict = (
            f"SMALL POSITIVE, mechanistically clean — precision {precision_delta:+.4f}, "
            f"recall {recall_delta:+.4f} (the addendum targeted precision specifically and "
            "recall held flat, exactly as predicted). Worth keeping; not worth iterating "
            "further per the bounded stop rule."
        )
    else:
        verdict = "NEGATIVE — bounded per A5/BP9; bank the result, do not iterate on the addendum wording."

    lines = [
        "# A5 probe — DeepSeek precision prompt profile (dev140, bounded single-model)",
        "",
        f"Model: `{out['model']}`. Seed instructions: the mini-evolved per-family 0.731 run "
        f"(`{out['seed_instruction_source']}`), unchanged except for the addendum below.",
        "",
        f"Added clause (every family, appended verbatim): \"{out['addendum'].strip()}\"",
        "",
        "## Result",
        "",
        "| condition | overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations | ev-recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| baseline (mini instructions verbatim) | {base_hl['overall_f1']:.4f} | "
        f"{base_hl['per_family']['Diagnosis']:.4f} | {base_hl['per_family']['SeizureFrequency']:.4f} | "
        f"{base_hl['per_family']['Prescription']:.4f} | {base_hl['per_family']['Investigations']:.4f} | "
        f"{base['evidence_recall']['overall_recall']:.4f} |",
        f"| + precision addendum | {add_hl['overall_f1']:.4f} | "
        f"{add_hl['per_family']['Diagnosis']:.4f} | {add_hl['per_family']['SeizureFrequency']:.4f} | "
        f"{add_hl['per_family']['Prescription']:.4f} | {add_hl['per_family']['Investigations']:.4f} | "
        f"{add['evidence_recall']['overall_recall']:.4f} |",
        "",
        f"Delta (overall F1): **{delta:+.4f}**",
        "",
        "## Comparators",
        "",
        f"- mini per-family baseline (same instructions, gpt-4.1-mini): "
        f"{out['comparators']['mini_per_family_baseline_headline']}",
        f"- DeepSeek Phase 0c (model-swap only, same instructions verbatim, no addendum): "
        f"{out['comparators']['deepseek_phase0c_model_swap_only_headline']}",
        "",
        f"## Verdict: {verdict}",
        "",
        "## Scope and stop rule",
        "",
        "Per A5's safe-protocol-shape: one model, one pre-named failure mode, scorer/slice/"
        "projection held fixed, reported as a model-specific result not a universal prompt "
        "change. This is a single bounded comparison; per the predeclared stop rule, no "
        "iteration on the addendum wording follows regardless of outcome.",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
