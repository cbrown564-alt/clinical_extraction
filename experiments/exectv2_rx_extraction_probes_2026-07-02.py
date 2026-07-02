"""Phase 2 Prescription extraction-behavior probes (ExECTv2 pipeline assumption audit).

Two COSTED, gated hand-tuned instruction probes on gpt-4.1-mini, dev140 ONLY:

* #2 rx_current_vs_future_dose_conflation_2026-07-02 -- teach the extractor to
  assert the letter's CURRENT regimen, not a proposed titration/target dose
  (EA0021: emits 800mg-bd; true current 700mg-AM + 800mg-nocte).
* #3 rx_non_aed_over_extraction_2026-07-02 -- explicit "anti-epileptic drugs only"
  scoping (model tags clopidogrel/ramipril/metformin; gold tags only AEDs).

Method (economical + valid):
  The canonical run ``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`` is a
  per-family GEPA program; only the Prescription predictor and only the Prescription
  clinical_headline scorer are exercised here (each family is scored independently,
  so a Prescription-only reconstruction is faithful for this metric and 4x cheaper).
  We run a FRESH matched baseline arm (canonical evolved Rx instruction, unchanged)
  plus one arm per probe (baseline instruction + appended delta), all live and
  paired under identical conditions (temp 0, cache OFF), then score every arm with
  the CURRENT finalized scorer ``score_prescription_components(...).clinical_headline``.

This harness GENERALIZES: ``run_arms`` takes a dict of {arm_name: instruction} for one
family predictor + scorer, so the Investigations MRI-crowds-EEG under-extraction analog
and the SF direction-framing analog can reuse it by swapping the signature/scorer.
Only #2 and #3 are RUN here.

dev140 ONLY. Never touches holdout / test / full-200.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multifamily import (
    PRESCRIPTION_SCHEMA_JSON,
    PrescriptionFactsSignature,
    _facts_of,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    prescription_component_keys,
    score_prescription_components,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
CANONICAL_RUN = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
CANONICAL_INSTRUCTION_FILE = EXPERIMENTS / f"{CANONICAL_RUN}.instruction.txt"
CANONICAL_PREDS_JSONL = EXPERIMENTS / f"{CANONICAL_RUN}.jsonl"
OUT_DIR = EXPERIMENTS / "exectv2_rx_extraction_probes_2026-07-02"

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 12000


# --------------------------------------------------------------------------------------
# Instruction: canonical evolved Rx block + the two predeclared probe deltas.
# --------------------------------------------------------------------------------------
def load_baseline_rx_instruction() -> str:
    """Extract the canonical run's evolved Prescription predictor instruction verbatim."""

    text = CANONICAL_INSTRUCTION_FILE.read_text(encoding="utf-8")
    # Blocks are delimited by lines like ``=== prescription ===``.
    blocks = re.split(r"^=== (\w+) ===$", text, flags=re.MULTILINE)
    # re.split yields [pre, name1, body1, name2, body2, ...]
    for i in range(1, len(blocks), 2):
        if blocks[i].strip() == "prescription":
            return blocks[i + 1].strip("\n")
    raise RuntimeError("prescription block not found in canonical instruction artifact")


# Probe #2 delta: current vs future/target dose.
DELTA_2_CURRENT_VS_FUTURE = """

**CURRENT vs FUTURE/TARGET dose (assert the current regimen only):**
- Always assert the patient's CURRENT medication exactly as stated in the letter's current-medication list or header (e.g. "Current AEDs: ...", "Sodium Valproate 700mg in the morning and 800mg nocte"). This is the dose to emit.
- A dose that appears only inside a proposed change is a FUTURE target, NOT the current prescription. Never emit such a target as a current fact and never let it overwrite the current dose. Future-target cues include: "I suggest increasing to ...", "the dose should be increased ... so that he is on X", "aim for", "target dose", "titrate up to", "build up to", "increase by ... to X".
- When a drug lists separate morning and night doses (e.g. "700mg in the morning and 800mg nocte"), emit one once-daily (frequency 1) fact per dose; a "nocte"/"at night"/"od" dose is once daily (frequency 1), not twice daily. Do not collapse a morning+nocte pair into a single twice-daily (2) fact."""

# Probe #3 delta: AED-only scoping.
DELTA_3_AED_ONLY = """

**ANTI-EPILEPTIC DRUGS ONLY:**
- Emit a prescription fact ONLY for anti-epileptic / anti-seizure drugs (AEDs). Examples of AEDs: sodium valproate/valproate/epilim, levetiracetam/keppra, lamotrigine/lamictal, carbamazepine/tegretol, phenytoin/epanutin, zonisamide, clobazam, clonazepam, lacosamide/vimpat, topiramate/topamax, perampanel/fycompa, brivaracetam/briviact, oxcarbazepine/eslicarbazepine, phenobarbital/primidone, ethosuximide, vigabatrin, gabapentin/pregabalin when prescribed for seizures.
- Do NOT emit non-epilepsy comorbidity medications even when a current dose and frequency are given -- e.g. clopidogrel, aspirin, ramipril, amlodipine, bisoprolol, atorvastatin/simvastatin, metformin, gliclazide, warfarin, apixaban, levothyroxine/thyroxine, omeprazole, antidepressants/antipsychotics not being used as an AED. These are background comorbidity drugs and are not prescription facts for this task."""


def build_arm_instructions() -> dict[str, str]:
    base = load_baseline_rx_instruction()
    return {
        "baseline": base,
        "probe2_current_vs_future": base + DELTA_2_CURRENT_VS_FUTURE,
        "probe3_aed_only": base + DELTA_3_AED_ONLY,
        "probe23_combined": base + DELTA_2_CURRENT_VS_FUTURE + DELTA_3_AED_ONLY,
    }


# --------------------------------------------------------------------------------------
# Program: single Prescription predictor (faithful subset of the canonical program).
# --------------------------------------------------------------------------------------
class RxProbeExtractor(dspy.Module):
    """Runs only the Prescription predictor with a configurable instruction."""

    def __init__(self, instruction: str) -> None:
        super().__init__()
        self.prescription = dspy.Predict(PrescriptionFactsSignature)
        self.prescription.signature = self.prescription.signature.with_instructions(instruction)

    def forward(self, letter_text: str) -> dspy.Prediction:
        out = self.prescription(letter_text=letter_text, output_schema=PRESCRIPTION_SCHEMA_JSON)
        facts = _facts_of(str(getattr(out, "clinical_facts_json", "") or ""))
        return dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": facts}, ensure_ascii=False)
        )


# --------------------------------------------------------------------------------------
# Scoring helpers.
# --------------------------------------------------------------------------------------
def _prf1_row(prf1: Any) -> dict[str, float]:
    return {
        "precision": round(float(prf1.precision), 4),
        "recall": round(float(prf1.recall), 4),
        "f1": round(float(prf1.f1), 4),
        "tp": int(getattr(prf1, "tp", 0)),
        "fp": int(getattr(prf1, "fp", 0)),
        "fn": int(getattr(prf1, "fn", 0)),
    }


def _rx_headline_keys(letter: ExectLetter) -> list:
    return prescription_component_keys(
        list(letter.entities("Prescription")), "clinical_headline", letter.note_text
    )


def _pred_letter_from_facts_json(gold_letter: ExectLetter, raw: str) -> ExectLetter:
    record, _errors = parse_dedup_clinical_facts_json(raw) if raw else (None, ["empty"])
    if record is None:
        predicted = PredictedLetter(letter_id=gold_letter.letter_id, mentions=())
    else:
        predicted, *_ = to_predicted_letter_from_dedup_facts(gold_letter, record)
    return to_exect_letter(predicted)


def score_arm(
    gold_letters: list[ExectLetter], raw_by_id: dict[str, str]
) -> tuple[dict[str, float], list[ExectLetter]]:
    pred_letters = [
        _pred_letter_from_facts_json(g, raw_by_id.get(g.letter_id, "")) for g in gold_letters
    ]
    ch = score_prescription_components(gold_letters, pred_letters).clinical_headline
    return _prf1_row(ch), pred_letters


# --------------------------------------------------------------------------------------
# Live arm runner.
# --------------------------------------------------------------------------------------
def run_arm(
    instruction: str, letters: list[ExectLetter], num_threads: int
) -> dict[str, str]:
    program = RxProbeExtractor(instruction)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    exec_pairs = [(program, {"letter_text": letter.note_text}) for letter in letters]
    predictions = evaluator(exec_pairs)
    raw_by_id: dict[str, str] = {}
    for letter, prediction in zip(letters, predictions, strict=True):
        raw_by_id[letter.letter_id] = (
            str(getattr(prediction, "clinical_facts_json", "") or "") if prediction else ""
        )
    return raw_by_id


# --------------------------------------------------------------------------------------
# Cached-canonical reference (free): score the stored predicted_mentions.
# --------------------------------------------------------------------------------------
def cached_canonical_pred_letters(gold_letters: list[ExectLetter]) -> list[ExectLetter]:
    by_id: dict[str, list[ExectAnnotation]] = {}
    with CANONICAL_PREDS_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            anns = [
                ExectAnnotation(
                    entity=m["entity"], text=m["text"], attributes=dict(m.get("attributes", {}))
                )
                for m in row.get("predicted_mentions", [])
                if m.get("entity") == "Prescription"
            ]
            by_id[row["letter_id"]] = anns
    return [
        ExectLetter(
            letter_id=g.letter_id,
            note_text="",
            annotations=tuple(by_id.get(g.letter_id, [])),
        )
        for g in gold_letters
    ]


# --------------------------------------------------------------------------------------
# Per-letter diff between two arms (which letters changed + EA0021/EA0073 detail).
# --------------------------------------------------------------------------------------
def per_letter_headline(gold_letters: list[ExectLetter], pred_letters: list[ExectLetter]) -> dict:
    detail: dict[str, dict] = {}
    for g, p in zip(gold_letters, pred_letters, strict=True):
        gk = _rx_headline_keys(g)
        pk = _rx_headline_keys(p)
        gc = _multiset_counts(gk)
        pc = _multiset_counts(pk)
        missed = _multiset_sub(gc, pc)
        spurious = _multiset_sub(pc, gc)
        detail[g.letter_id] = {
            "gold": sorted(str(k) for k in gk),
            "pred": sorted(str(k) for k in pk),
            "missed": [str(k) for k in missed],
            "spurious": [str(k) for k in spurious],
        }
    return detail


def _multiset_counts(keys: list) -> dict:
    counts: dict = {}
    for k in keys:
        counts[k] = counts.get(k, 0) + 1
    return counts


def _multiset_sub(a: dict, b: dict) -> list:
    out = []
    for k, n in a.items():
        extra = n - b.get(k, 0)
        out.extend([k] * max(0, extra))
    return out


# --------------------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--arms",
        default="baseline,probe2_current_vs_future,probe3_aed_only,probe23_combined",
        help="comma-separated arm names to run live",
    )
    parser.add_argument("--num-threads", type=int, default=12)
    parser.add_argument("--cache", action="store_true", help="enable LM cache (default off)")
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="skip live runs; re-score raw artifacts already in OUT_DIR",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gold_letters = gepa_data.load_dev_letters()
    assert len(gold_letters) == 140, f"expected dev140, got {len(gold_letters)}"

    arm_instructions = build_arm_instructions()
    arm_names = [a.strip() for a in args.arms.split(",") if a.strip()]

    if not args.score_only:
        lm = build_dspy_lm(
            TASK_MODEL,
            temperature=TASK_TEMPERATURE,
            max_tokens=TASK_MAX_TOKENS,
            cache=args.cache,
        )
        dspy.configure(lm=lm)

    results: dict[str, Any] = {
        "run_meta": {
            "task_model": TASK_MODEL,
            "task_temperature": TASK_TEMPERATURE,
            "cache": args.cache,
            "n_letters": len(gold_letters),
            "canonical_run": CANONICAL_RUN,
            "scorer": "score_prescription_components(...).clinical_headline (finalized)",
        },
        "arms": {},
    }

    # Cached-canonical reference (secondary; free).
    cached_pred = cached_canonical_pred_letters(gold_letters)
    cached_ch = score_prescription_components(gold_letters, cached_pred).clinical_headline
    results["cached_canonical_reference"] = _prf1_row(cached_ch)

    raw_by_arm: dict[str, dict[str, str]] = {}
    pred_by_arm: dict[str, list[ExectLetter]] = {}
    for name in arm_names:
        raw_path = OUT_DIR / f"raw_{name}.json"
        if args.score_only:
            raw_by_id = json.loads(raw_path.read_text(encoding="utf-8"))
        else:
            print(f"[probe] running arm '{name}' ({len(gold_letters)} letters)...", flush=True)
            started = time.time()
            raw_by_id = run_arm(arm_instructions[name], gold_letters, args.num_threads)
            print(f"[probe]   done in {time.time() - started:.1f}s", flush=True)
            raw_path.write_text(json.dumps(raw_by_id, ensure_ascii=False, indent=2), encoding="utf-8")
        raw_by_arm[name] = raw_by_id
        row, pred_letters = score_arm(gold_letters, raw_by_id)
        pred_by_arm[name] = pred_letters
        results["arms"][name] = {"clinical_headline": row}

    # Deltas vs fresh baseline + changed-letter diffs.
    if "baseline" in pred_by_arm:
        base_detail = per_letter_headline(gold_letters, pred_by_arm["baseline"])
        base_f1 = results["arms"]["baseline"]["clinical_headline"]["f1"]
        for name in arm_names:
            if name == "baseline":
                continue
            arm_detail = per_letter_headline(gold_letters, pred_by_arm[name])
            changed = []
            for lid in base_detail:
                if base_detail[lid]["pred"] != arm_detail[lid]["pred"]:
                    changed.append(
                        {
                            "letter_id": lid,
                            "baseline_pred": base_detail[lid]["pred"],
                            "arm_pred": arm_detail[lid]["pred"],
                            "gold": base_detail[lid]["gold"],
                        }
                    )
            arm_f1 = results["arms"][name]["clinical_headline"]["f1"]
            results["arms"][name]["delta_f1_vs_fresh_baseline"] = round(arm_f1 - base_f1, 4)
            results["arms"][name]["n_letters_changed"] = len(changed)
            results["arms"][name]["changed_letters"] = changed

    out_path = OUT_DIR / "results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Console summary.
    print("\n==== Prescription clinical_headline (finalized scorer) ====")
    ref = results["cached_canonical_reference"]
    print(
        f"  cached-canonical reference: P={ref['precision']:.4f} R={ref['recall']:.4f} "
        f"F1={ref['f1']:.4f} (tp={ref['tp']} fp={ref['fp']} fn={ref['fn']})"
    )
    for name in arm_names:
        row = results["arms"][name]["clinical_headline"]
        extra = ""
        if "delta_f1_vs_fresh_baseline" in results["arms"][name]:
            extra = (
                f"  dF1={results['arms'][name]['delta_f1_vs_fresh_baseline']:+.4f} "
                f"changed={results['arms'][name]['n_letters_changed']}"
            )
        print(
            f"  {name:28s}: P={row['precision']:.4f} R={row['recall']:.4f} "
            f"F1={row['f1']:.4f} (tp={row['tp']} fp={row['fp']} fn={row['fn']}){extra}"
        )
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
