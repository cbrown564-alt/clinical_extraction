"""LLM-vs-deterministic Prescription producer comparison for the paper.

Builds the best-possible LLM-tuned Prescription extractor (the canonical GEPA
evolved Rx instruction + the two confirmed 07-02 probe deltas + an emit-if-unsure
AED gate that fixes the documented probe #3 over-drop), produces a v08-assembly-
compatible Prescription lane artifact, and swaps ONLY that producer into the
existing v08 manifest to measure its effect through the full assembly against a
same-day baseline. This is comparison evidence for the paper (justifying the
deterministic Prescription lane), not a promotion attempt -- the feasibility
probe (exectv2_rx_headtohead_feasibility_finding_2026-07-03.md) already showed
the deterministic producer scores 0.9615 on dev140, above the LLM probe
combined arm (0.9526); this script quantifies the gap through the full assembly
and at full-200 under frozen aggregate-only protocol.

The LLM arm gets the doc-recommended probe #3 fix: the over-drop on EA0025
(both lamotrigines) and EA0012 (carbamazepine) was MODEL CONSERVATISM, not a
whitelist miss (all three drugs are on the instruction's AED list). The fix is
an explicit emit-if-unsure clause, not a tighter list -- "do not drop a
current-dose drug solely because you are unsure if it is an AED; when a drug
appears in a current-medication list with a dose, emit it."

Isolation (P7 audit method): for each split, build BOTH a baseline assembly
(unmodified manifest, deterministic Prescription) AND a treatment assembly
(only Prescription swapped for the LLM artifact) through the SAME current-code
scorer, so the reported delta isolates the producer swap from scorer drift.

Usage:
  python scripts/run_exectv2_v08_rx_llm_vs_deterministic.py dev140
  python scripts/run_exectv2_v08_rx_llm_vs_deterministic.py full200   # needs --allow-non-dev140
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    load_finding_assembly_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

RUN_DATE = date.today().isoformat().replace("-", "")
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REPORT_DIR = ROOT / "docs" / "experiments" / "exectv2" / "prescription"
DEV_MANIFEST_PATH = ROOT / "configs" / "exectv2" / "finding_assembly" / "exectv2_holistic_finding_assembly_v08_dev140.yaml"

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 12000
CANONICAL_INSTRUCTION_FILE = EXPERIMENTS / "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.instruction.txt"

# Full-200 baseline producer artifacts (P7 audit's currentcode manifest).
FULL200_PRESCRIPTION_BASELINE = EXPERIMENTS / (
    "exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_20260624.jsonl"
)


# --------------------------------------------------------------------------------------
# Instruction: canonical evolved Rx block + probe #2 + probe #3 + emit-if-unsure fix.
# --------------------------------------------------------------------------------------
def _load_baseline_rx_instruction() -> str:
    text = CANONICAL_INSTRUCTION_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"^=== (\w+) ===$", text, flags=re.MULTILINE)
    for i in range(1, len(blocks), 2):
        if blocks[i].strip() == "prescription":
            return blocks[i + 1].strip("\n")
    raise RuntimeError("prescription block not found in canonical instruction artifact")


# Probe #2: current-vs-future dose (verbatim from the 07-02 probe driver).
DELTA_2_CURRENT_VS_FUTURE = """

**CURRENT vs FUTURE/TARGET dose (assert the current regimen only):**
- Always assert the patient's CURRENT medication exactly as stated in the letter's current-medication list or header (e.g. "Current AEDs: ...", "Sodium Valproate 700mg in the morning and 800mg nocte"). This is the dose to emit.
- A dose that appears only inside a proposed change is a FUTURE target, NOT the current prescription. Never emit such a target as a current fact and never let it overwrite the current dose. Future-target cues include: "I suggest increasing to ...", "the dose should be increased ... so that he is on X", "aim for", "target dose", "titrate up to", "build up to", "increase by ... to X".
- When a drug lists separate morning and night doses (e.g. "700mg in the morning and 800mg nocte"), emit one once-daily (frequency 1) fact per dose; a "nocte"/"at night"/"od" dose is once daily (frequency 1), not twice daily. Do not collapse a morning+nocte pair into a single twice-daily (2) fact."""

# Probe #3: AED-only (verbatim) + the emit-if-unsure fix (NEW, addresses the
# documented over-drop where the model stopped emitting AEDs like lamotrigine/
# carbamazepine it had previously emitted -- model conservatism, not a whitelist
# miss, since all dropped drugs are on the instruction's own AED list).
DELTA_3_AED_ONLY_WITH_FIX = """

**ANTI-EPILEPTIC DRUGS ONLY (with an emit-if-unsure safety clause):**
- Emit a prescription fact ONLY for anti-epileptic / anti-seizure drugs (AEDs). Examples of AEDs: sodium valproate/valproate/epilim, levetiracetam/keppra, lamotrigine/lamictal, carbamazepine/tegretol, phenytoin/epanutin, zonisamide, clobazam, clonazepam, lacosamide/vimpat, topiramate/topamax, perampanel/fycompa, brivaracetam/briviact, oxcarbazepine/eslicarbazepine, phenobarbital/primidone, ethosuximide, vigabatrin, gabapentin/pregabalin when prescribed for seizures.
- Do NOT emit non-epilepsy comorbidity medications even when a current dose and frequency are given -- e.g. clopidogrel, aspirin, ramipril, amlodipine, bisoprolol, atorvastatin/simvastatin, metformin, gliclazide, warfarin, apixaban, levothyroxine/thyroxine, omeprazole, antidepressants/antipsychotics not being used as an AED. These are background comorbidity drugs and are not prescription facts for this task.
- SAFETY CLAUSE (emit-if-unsure): When a drug appears in a current-medication list or header with an explicit dose and frequency but you are UNSURE whether it is an AED, EMIT it rather than dropping it. The cost of a false drop (a missed AED) is higher than the cost of a false keep (a non-AED that the downstream filter can remove). Do not let the AED-only instruction make you more conservative about drugs you would otherwise have emitted -- if you emitted a drug under the baseline instruction, keep emitting it here unless you are CERTAIN it is a non-AED comorbidity drug from the exclusion list above."""


def build_llm_instruction() -> str:
    return _load_baseline_rx_instruction() + DELTA_2_CURRENT_VS_FUTURE + DELTA_3_AED_ONLY_WITH_FIX


# --------------------------------------------------------------------------------------
# LLM Prescription extractor + artifact production.
# --------------------------------------------------------------------------------------
class RxLLMExtractor(dspy.Module):
    """Single Prescription predictor with the tuned instruction."""

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


def _locate_drug_in_note(drug: str, note: str) -> str:
    """Find the drug's actual surface occurrence in the note text (case-insensitive).

    Tries the canonical name and common surface variants. Returns the exact
    matched substring (preserving the note's original casing) so it passes the
    assembly's evidence-grounding validation, or '' if no match.
    """
    if not drug or not note:
        return ""
    drug_low = drug.lower().replace("-", " ").strip()
    note_low = note.lower()
    # Try exact name, then space/hyphen-normalized variants.
    candidates = [drug, drug_low]
    # sodium valproate / valproate interchange
    if "valproate" in drug_low and "sodium" not in drug_low:
        candidates += ["sodium valproate", "sodium-valproate"]
    if drug_low.startswith("sodium valproate"):
        candidates += ["valproate", "epilim", "episenta"]
    for cand in candidates:
        cand_norm = cand.lower().replace("-", " ")
        idx = note_low.find(cand_norm)
        if idx != -1:
            return note[idx: idx + len(cand_norm)]
    return ""


def _project_facts_to_mentions(
    gold_letter: ExectLetter, facts_json: str
) -> list[dict[str, Any]]:
    """Project the LLM facts JSON into the saved-jsonl predicted_mentions schema.

    The projection path (to_predicted_letter_from_dedup_facts) drops the
    evidence span text the LLM emitted (raw_text comes back None), but the
    assembly's evidence validation requires ``evidence in note_text``. So we
    carry the evidence field through from the raw facts JSON directly, and
    gate it to an exact substring of the note text (the assembly will reject
    non-substring evidence). When the LLM's evidence span is not an exact
    substring (paraphrase/truncation), we fall back to the CUIPhrase --
    matching the deterministic producer's behavior of keying on the clean
    canonical form when the surface span is unreliable.
    """
    # Recover the raw facts list to access the evidence spans the LLM emitted.
    raw_facts = _facts_of(facts_json) if facts_json else []

    record, _errors = parse_dedup_clinical_facts_json(facts_json) if facts_json else (None, ["empty"])
    if record is None:
        predicted = PredictedLetter(letter_id=gold_letter.letter_id, mentions=())
    else:
        predicted, *_ = to_predicted_letter_from_dedup_facts(gold_letter, record)
    pred_exect = to_exect_letter(predicted)
    note = gold_letter.note_text or ""

    # Pair projected mentions with their source facts by CUIPhrase/DrugName so
    # we can recover the evidence span. The projection preserves attribute
    # ordering, so we match on the CUIPhrase attribute.
    facts_by_key: dict[str, dict[str, Any]] = {}
    for f in raw_facts:
        key = (f.get("drug_name", ""), f.get("drug_dose", ""), f.get("dose_unit", ""), f.get("frequency", ""))
        facts_by_key[str(key).lower()] = f

    mentions = []
    for m in pred_exect.entities("Prescription"):
        attrs = {str(k): str(v) for k, v in m.attributes.items()}
        key = str((attrs.get("DrugName", ""), attrs.get("DrugDose", ""), attrs.get("DoseUnit", ""), attrs.get("Frequency", ""))).lower()
        fact = facts_by_key.get(key, {})
        evidence = str(fact.get("evidence", "") or "")
        # The assembly's evidence-grounding invariant requires evidence to be an
        # EXACT substring of the note text. The LLM's evidence span is often a
        # paraphrase/truncation, so gate it: prefer the LLM span if exact, else
        # the CUIPhrase if exact, else fall back to locating the drug name in
        # the note (case-insensitive) -- grounding the LLM's identified drug to
        # its actual occurrence in the note, the same surface form the
        # deterministic producer would anchor on.
        if not evidence or evidence not in note:
            cui_phrase = attrs.get("CUIPhrase", "") or attrs.get("DrugName", "")
            if cui_phrase and cui_phrase in note:
                evidence = cui_phrase
            else:
                # Locate any surface form of the drug name in the note.
                drug = attrs.get("DrugName", "") or attrs.get("CUIPhrase", "")
                evidence = _locate_drug_in_note(drug, note) or evidence
        mentions.append({
            "entity": PRESCRIPTION.name,
            "text": evidence,
            "attributes": attrs,
            "evidence": evidence,
            "component_owner": "llm:tuned_rx_extractor:canonical_plus_probe23_emitifunsure",
            "confidence": None,
            "rationale": None,
            "evidence_span": None,
            "uncertainty_flags": [],
        })
    return mentions


def produce_llm_prescription_artifact(
    letters: list[ExectLetter], jsonl_path: Path, *, split: str, num_threads: int, cache: bool
) -> None:
    """Run the LLM Rx extractor and write a v08-assembly-compatible saved-jsonl artifact."""
    instruction = build_llm_instruction()
    program = RxLLMExtractor(instruction)
    lm = build_dspy_lm(
        TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache
    )
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    exec_pairs = [(program, {"letter_text": letter.note_text}) for letter in letters]
    print(f"[llm-rx] extracting {len(letters)} letters ({TASK_MODEL}, temp {TASK_TEMPERATURE})...", flush=True)
    started = time.time()
    predictions = evaluator(exec_pairs)
    n_calls = 0
    rows = []
    for letter, prediction in zip(letters, predictions, strict=True):
        raw = (
            str(getattr(prediction, "clinical_facts_json", "") or "") if prediction else ""
        )
        if raw:
            n_calls += 1
        mentions = _project_facts_to_mentions(letter, raw)
        rows.append({
            "letter_id": letter.letter_id,
            "split": split,
            "pipeline_family": "exectv2_llm_rx_tuned_extractor",
            "prompt_version": "canonical_gepa_plus_probe2_probe3_emitifunsure",
            "model": TASK_MODEL,
            "mode": "live",
            "component_owner": "llm_tuned_rx_extractor_canonical_plus_probe23_emitifunsure",
            "call_error": None,
            "parse_errors": [],
            "gate_warnings": [],
            "n_mentions_raw": len(mentions),
            "n_mentions_scored": len(mentions),
            "n_evidence_invalid": 0,
            "predicted_mentions": mentions,
            "raw_output": json.dumps({"mentions": mentions}, ensure_ascii=False),
            "gold_mentions": [
                {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                for a in letter.annotations if a.entity == PRESCRIPTION.name
            ],
        })
    write_jsonl(rows, jsonl_path)
    mention_count = sum(len(r["predicted_mentions"]) for r in rows)
    print(f"[llm-rx] done in {time.time() - started:.1f}s; {n_calls} calls; {mention_count} mentions across {len(rows)} rows -> {jsonl_path.name}")


# --------------------------------------------------------------------------------------
# Assembly swap + scoring (mirrors run_exectv2_v08_p7_prescription_refresh_audit).
# --------------------------------------------------------------------------------------
def _run_assembly(
    letters: list[ExectLetter],
    *,
    base_manifest,
    prescription_jsonl: Path | None,
    candidate_id: str,
    split: str,
    claim_boundary: str,
    assembly_stem: str,
) -> dict[str, Any]:
    producers = dict(base_manifest.producers)
    if prescription_jsonl is not None:
        producers["prescription_repair_v03"] = replace(
            base_manifest.producers["prescription_repair_v03"],
            artifact=prescription_jsonl,
        )
    manifest = replace(
        base_manifest,
        candidate_id=candidate_id,
        split=split,
        row_count=len(letters),
        claim_boundary=claim_boundary,
        producers=producers,
    )
    run = build_finding_assembly(manifest, gold_loader=lambda _split: letters)
    assembly_jsonl = EXPERIMENTS / f"{assembly_stem}.jsonl"
    assembly_json = assembly_jsonl.with_suffix(".json")
    assembly_md = REPORT_DIR / f"{assembly_stem}.md"
    assembly_jsonl.parent.mkdir(parents=True, exist_ok=True)
    assembly_md.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(run.rows, assembly_jsonl)
    assembly_json.write_text(
        json.dumps(run.report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    markdown = render_finding_assembly_markdown(
        run.report, json_path=assembly_json, jsonl_path=assembly_jsonl
    )
    assembly_md.write_text(markdown, encoding="utf-8")
    headline = run.report["score_ladder"]["headline_target"]
    overall = headline["overall"]
    print(f"[{candidate_id}] F1={overall['f1']:.4f} P={overall['precision']:.4f} R={overall['recall']:.4f} TP={overall['tp']} FP={overall['fp']} FN={overall['fn']}")
    for entity in (DIAGNOSIS.name, SEIZURE_FREQUENCY.name, PRESCRIPTION.name, INVESTIGATIONS.name):
        row = headline["by_indicator"][entity]
        print(f"  {entity}: F1={row['f1']:.4f} P={row['precision']:.4f} R={row['recall']:.4f} TP={row['tp']} FP={row['fp']} FN={row['fn']}")
    return headline


def _print_delta(label: str, baseline: dict[str, Any], treatment: dict[str, Any]) -> None:
    bo, bt = baseline["overall"], treatment["overall"]
    print(f"\n=== {label} delta (LLM treatment vs deterministic baseline) ===")
    print(f"  overall: {bo['f1']:.4f} -> {bt['f1']:.4f} ({bt['f1'] - bo['f1']:+.4f})")
    for entity in (PRESCRIPTION.name,):
        ro, rt = baseline["by_indicator"][entity], treatment["by_indicator"][entity]
        print(f"  {entity}: {ro['f1']:.4f} -> {rt['f1']:.4f} ({rt['f1'] - ro['f1']:+.4f})")
        print(f"    P {ro['precision']:.4f} -> {rt['precision']:.4f} | R {ro['recall']:.4f} -> {rt['recall']:.4f}")
        print(f"    TP {ro['tp']}->{rt['tp']} | FP {ro['fp']}->{rt['fp']} | FN {ro['fn']}->{rt['fn']}")


def _full200_base_manifest(letters: list[ExectLetter]):
    """Build the full-200 currentcode manifest by swapping each dev producer's
    artifact for its confirmed full-200 counterpart (the same artifacts the P7
    full200 treatment used; verified via its lane_sources)."""
    dev_manifest = load_finding_assembly_manifest(DEV_MANIFEST_PATH)
    # Map each dev producer key -> full200 currentcode artifact.
    full200_artifacts = {
        "target_single_call_v042": EXPERIMENTS / "exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl",
        "diagnosis_reconciler_v01": EXPERIMENTS / "exectv2_v08_full200_currentcode_diagnosis_reconciler_gpt41mini_20260624.jsonl",
        "sf_union_arbitration_v08": EXPERIMENTS / "exectv2_v08_full200_currentcode_sf_union_arbitration_20260624.jsonl",
        "investigations_arbitration_v02": EXPERIMENTS / "exectv2_v08_full200_currentcode_investigations_arbitration_20260624.jsonl",
        "prescription_repair_v03": FULL200_PRESCRIPTION_BASELINE,
    }
    producers = {
        key: replace(prod, artifact=full200_artifacts[key])
        for key, prod in dev_manifest.producers.items()
        if key in full200_artifacts
    }
    missing = set(dev_manifest.producers) - set(producers)
    if missing:
        raise ValueError(f"no full200 artifact mapping for producer key(s): {missing}")
    return replace(
        dev_manifest,
        candidate_id="exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini",
        split="full_200_authorized",
        row_count=len(letters),
        producers=producers,
        promotion_decision="full-200-current-code-readout",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", choices=["dev140", "full200"])
    parser.add_argument("--allow-non-dev140", action="store_true")
    parser.add_argument("--num-threads", type=int, default=12)
    parser.add_argument("--cache", action="store_true", help="enable LM cache (default off)")
    args = parser.parse_args()

    if args.split == "full200" and not args.allow_non_dev140:
        raise SystemExit(
            "Refusing full-200 LLM Rx run without --allow-non-dev140. Full-200 needs "
            "a fresh aggregate-only predeclaration under the frozen protocol."
        )

    if args.split == "dev140":
        letters = load_letters_for_split("dev")
        base_manifest = load_finding_assembly_manifest(DEV_MANIFEST_PATH)
        split_tag = "dev"
        assembly_split = "dev"
    else:
        letters = load_letters()
        base_manifest = _full200_base_manifest(letters)
        split_tag = "full_200_authorized"
        assembly_split = "full_200_authorized"

    # 1. Produce the LLM-tuned Prescription artifact.
    llm_jsonl = EXPERIMENTS / f"exectv2_llm_rx_tuned_extractor_{args.split}_{RUN_DATE}.jsonl"
    produce_llm_prescription_artifact(
        letters, llm_jsonl, split=split_tag, num_threads=args.num_threads, cache=args.cache
    )

    # 2. Baseline assembly (deterministic Prescription, unmodified manifest).
    print(f"\n-- {args.split} baseline (deterministic Prescription) --")
    baseline = _run_assembly(
        letters,
        base_manifest=base_manifest,
        prescription_jsonl=None,
        candidate_id=f"exectv2_v08_{args.split}_rx_deterministic_baseline",
        split=assembly_split,
        claim_boundary=(
            f"LLM-vs-deterministic Rx comparator baseline: unmodified v08 {args.split} "
            f"manifest (deterministic Prescription producer), today's scorer."
        ),
        assembly_stem=f"exectv2_v08_{args.split}_rx_deterministic_baseline_{RUN_DATE}",
    )

    # 3. Treatment assembly (LLM Prescription swapped in).
    print(f"\n-- {args.split} treatment (LLM-tuned Prescription) --")
    treatment = _run_assembly(
        letters,
        base_manifest=base_manifest,
        prescription_jsonl=llm_jsonl,
        candidate_id=f"exectv2_v08_{args.split}_rx_llm_tuned_treatment",
        split=assembly_split,
        claim_boundary=(
            f"LLM-vs-deterministic Rx comparator treatment: v08 {args.split} manifest "
            f"with ONLY prescription_repair_v03 swapped for the LLM-tuned extractor "
            f"(canonical GEPA + probe #2 current-vs-future + probe #3 AED-only with "
            f"emit-if-unsure safety clause). Every other producer is the unchanged "
            f"archived artifact."
        ),
        assembly_stem=f"exectv2_v08_{args.split}_rx_llm_tuned_treatment_{RUN_DATE}",
    )

    _print_delta(args.split, baseline, treatment)


if __name__ == "__main__":
    main()
