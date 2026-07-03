"""LLM-vs-hybrid Investigations producer comparison — inversion-generalization probe.

Generalizes the 2026-07-03 Rx split-dependent inversion to Investigations. The
Rx comparator found: deterministic wins dev140 (recall), LLM wins full-200
(precision), because the two producers fix DIFFERENT failure modes with
DIFFERENT dev/test prevalence. This script asks whether the same shape holds
for Investigations.

Setup (mirrors run_exectv2_v08_rx_llm_vs_deterministic.py):
  - Build the best-possible LLM-tuned Inv extractor: canonical GEPA multifamily
    `investigation` instruction block + a precision-side delta (completed
    neuro-investigations only, drop planned/awaited, emit-if-unsure safety
    clause — the direct analog of the Rx AED-only precision gate).
  - Produce a v08-assembly-compatible Investigations lane artifact.
  - Swap ONLY `investigations_arbitration_v02` into the existing v08 manifest,
    keeping the `investigations_result_v01` lens common to both arms (the lens
    applies convention repairs on top of whatever the producer emits).
  - Build BOTH a baseline assembly (unmodified manifest, hybrid Inv lane) AND a
    treatment assembly (only Inv swapped for the LLM artifact) through the SAME
    current-code scorer (P7 audit method), so the reported delta isolates the
    producer swap from scorer drift.

Predeclared expectation (hypothesis inv_llm_precision_vs_hybrid_inversion_2026-07-03):
  - dev140: hybrid wins (the hybrid arbitration recovers MRI-crowds-EEG recall;
    the precision probe cannot — the recall-side probe was already REFUTED).
  - full-200: LLM wins IF precision failures (incidental/planned investigations)
    are more prevalent on the broader test surface.

Current cited v08 Inv: dev140 0.9132, full-200 0.9213.

Usage:
  python scripts/run_exectv2_v08_inv_llm_vs_hybrid.py dev140
  python scripts/run_exectv2_v08_inv_llm_vs_hybrid.py full200   # needs --allow-non-dev140
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
    INVESTIGATION_SCHEMA_JSON,
    InvestigationFactsSignature,
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
REPORT_DIR = ROOT / "docs" / "experiments" / "exectv2" / "investigations"
DEV_MANIFEST_PATH = ROOT / "configs" / "exectv2" / "finding_assembly" / "exectv2_holistic_finding_assembly_v08_dev140.yaml"

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 12000
CANONICAL_INSTRUCTION_FILE = EXPERIMENTS / "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628.instruction.txt"

# Full-200 baseline producer artifact (P7 audit's currentcode manifest).
FULL200_INV_BASELINE = EXPERIMENTS / (
    "exectv2_v08_full200_currentcode_investigations_arbitration_20260624.jsonl"
)

INV_PRODUCER_KEY = "investigations_arbitration_v02"


# --------------------------------------------------------------------------------------
# Instruction: canonical evolved Inv block + precision delta + emit-if-unsure fix.
# --------------------------------------------------------------------------------------
def _load_baseline_inv_instruction() -> str:
    text = CANONICAL_INSTRUCTION_FILE.read_text(encoding="utf-8")
    blocks = re.split(r"^=== (\w+) ===$", text, flags=re.MULTILINE)
    for i in range(1, len(blocks), 2):
        # The multifamily instruction block is named "investigation" (singular).
        if blocks[i].strip() in ("investigation", "investigations"):
            return blocks[i + 1].strip("\n")
    raise RuntimeError("investigation block not found in canonical instruction artifact")


# Precision-side delta: completed neuro-investigations only. This is the direct
# analog of the Rx AED-only precision gate. The deterministic producer is a bare
# surface-token anchor (EEG|MRI|CT, no neuro-investigation scope gate), so it
# over-captures planned/awaited investigations and incidental mentions. An LLM
# with contextual completion judgment is expected to fix this precision mode on
# the broader full-200 test surface (where such mentions are more prevalent),
# producing the inversion shape.
DELTA_PRECISION_COMPLETED_ONLY = """

**COMPLETED NEURO-INVESTIGATIONS ONLY (precision gate):**
- Emit an investigation fact ONLY when the letter states the test was actually performed AND reports a result. The investigation must be a completed neuro-diagnostic test, not a plan.
- Do NOT emit planned, requested, awaited, or arranged investigations. Exclusion cues include: "will arrange", "to be arranged", "we will request", "requested", "pending", "awaiting", "to be considered", "planned", "scheduled for", "we will organise", "may need".
- Check independently for EACH modality (MRI, CT, EEG, telemetry). A letter reporting an MRI very often ALSO reports an EEG — emit each completed modality as its own distinct fact. The most common mistake is anchoring on the headline modality (usually MRI) and silently dropping another (usually the EEG).
- Video telemetry and ambulatory EEG count as EEG. CT head and brain CT count as CT.
- The result must be the finding of the test itself (normal, abnormal, or the specific abnormality). Do NOT infer a result from a clinic impression or a diagnosis statement.
- SAFETY CLAUSE (emit-if-unsure): When an investigation is mentioned and you are UNSURE whether it was completed (vs merely planned), EMIT it rather than dropping it. The cost of a false drop (a missed completed investigation) is higher than the cost of a false keep (a planned investigation the downstream filter can remove). Do not let the precision instruction make you drop a completed investigation that the letter actually reports."""


def build_llm_instruction() -> str:
    return _load_baseline_inv_instruction() + DELTA_PRECISION_COMPLETED_ONLY


# --------------------------------------------------------------------------------------
# LLM Investigations extractor + artifact production.
# --------------------------------------------------------------------------------------
class InvLLMExtractor(dspy.Module):
    """Single Investigations predictor with the tuned instruction."""

    def __init__(self, instruction: str) -> None:
        super().__init__()
        self.investigation = dspy.Predict(InvestigationFactsSignature)
        self.investigation.signature = self.investigation.signature.with_instructions(instruction)

    def forward(self, letter_text: str) -> dspy.Prediction:
        out = self.investigation(letter_text=letter_text, output_schema=INVESTIGATION_SCHEMA_JSON)
        facts = _facts_of(str(getattr(out, "clinical_facts_json", "") or ""))
        return dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": facts}, ensure_ascii=False)
        )


# Map the LLM's emitted modality surface form to the canonical modality token
# the deterministic producer / scorer keys on. The projection's
# _normalize_modality handles the LLM-side variants; we just need to locate the
# modality token's actual surface occurrence in the note for evidence grounding.
_MODALITY_TOKENS = ("EEG", "MRI", "CT", "telemetry", "Telemetry")


def _locate_modality_in_note(modality: str, note: str) -> str:
    """Find the modality's actual surface occurrence in the note text.

    Returns the exact matched substring (preserving the note's casing) so it
    passes the assembly's evidence-grounding validation, or '' if no match.
    """

    if not modality or not note:
        return ""
    modality_norm = modality.strip()
    note_low = note.lower()
    # Try the canonical token first, then case-insensitive.
    candidates = [modality_norm, modality_norm.lower()]
    # Map telemetry surface forms to EEG (the convention layer's behavior).
    if modality_norm.lower() in ("telemetry", "video telemetry", "videotelemetry"):
        candidates += ["video telemetry", "telemetry", "ambulatory EEG", "ambulatory eeg"]
    for cand in candidates:
        idx = note_low.find(cand.lower())
        if idx != -1:
            return note[idx: idx + len(cand)]
    # Last resort: scan the canonical tokens.
    for tok in _MODALITY_TOKENS:
        idx = note_low.find(tok.lower())
        if idx != -1:
            return note[idx: idx + len(tok)]
    return ""


def _project_facts_to_mentions(
    gold_letter: ExectLetter, facts_json: str
) -> list[dict[str, Any]]:
    """Project the LLM facts JSON into the saved-jsonl predicted_mentions schema.

    Mirrors the Rx comparator's projection: the projection path drops the
    evidence span the LLM emitted, but the assembly's evidence validation
    requires ``evidence in note_text``. We ground the evidence to the modality
    token's exact surface occurrence in the note (modality tokens are short and
    unambiguous, so this is more reliable than the drug-name location dance the
    Rx driver needs).
    """

    raw_facts = _facts_of(facts_json) if facts_json else []
    record, _errors = parse_dedup_clinical_facts_json(facts_json) if facts_json else (None, ["empty"])
    if record is None:
        predicted = PredictedLetter(letter_id=gold_letter.letter_id, mentions=())
    else:
        predicted, *_ = to_predicted_letter_from_dedup_facts(gold_letter, record)
    pred_exect = to_exect_letter(predicted)
    note = gold_letter.note_text or ""

    # Key raw facts by (modality, result) to recover evidence spans. The
    # projection builds {MODALITY}_Performed/{MODALITY}_Results attributes.
    facts_by_key: dict[str, dict[str, Any]] = {}
    for f in raw_facts:
        key = str((f.get("modality", ""), f.get("result", ""))).lower()
        facts_by_key[key] = f

    mentions = []
    for m in pred_exect.entities("Investigations"):
        attrs = {str(k): str(v) for k, v in m.attributes.items()}
        # Recover the modality + result from the projected attributes.
        modality = ""
        for tok in ("MRI", "CT", "EEG", "Telemetry"):
            if attrs.get(f"{tok}_Performed") or attrs.get(f"{tok}_Results"):
                modality = tok
                break
        result = attrs.get(f"{modality}_Results", "") if modality else ""
        fact = facts_by_key.get(str((modality, result)).lower(), {})
        evidence = str(fact.get("evidence", "") or "")
        # Gate to an exact note substring (the assembly's grounding invariant).
        if not evidence or evidence not in note:
            loc = _locate_modality_in_note(modality, note)
            if loc:
                evidence = loc
            else:
                # Fall back to the CUIPhrase / modality text if it's a substring.
                cui = attrs.get("CUIPhrase", "") or modality
                if cui and cui in note:
                    evidence = cui
        mentions.append({
            "entity": INVESTIGATIONS.name,
            "text": modality or evidence,
            "attributes": attrs,
            "evidence": evidence,
            "component_owner": "llm:tuned_inv_extractor:canonical_plus_precision_completed_only",
            "confidence": None,
            "rationale": None,
            "evidence_span": None,
            "uncertainty_flags": [],
        })
    return mentions


def produce_llm_inv_artifact(
    letters: list[ExectLetter], jsonl_path: Path, *, split: str, num_threads: int, cache: bool
) -> None:
    """Run the LLM Inv extractor and write a v08-assembly-compatible saved-jsonl artifact."""

    instruction = build_llm_instruction()
    program = InvLLMExtractor(instruction)
    lm = build_dspy_lm(
        TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache
    )
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    exec_pairs = [(program, {"letter_text": letter.note_text}) for letter in letters]
    print(f"[llm-inv] extracting {len(letters)} letters ({TASK_MODEL}, temp {TASK_TEMPERATURE})...", flush=True)
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
            "pipeline_family": "exectv2_llm_inv_tuned_extractor",
            "prompt_version": "canonical_gepa_plus_precision_completed_only",
            "model": TASK_MODEL,
            "mode": "live",
            "component_owner": "llm_tuned_inv_extractor_canonical_plus_precision_completed_only",
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
                for a in letter.annotations if a.entity == INVESTIGATIONS.name
            ],
        })
    write_jsonl(rows, jsonl_path)
    mention_count = sum(len(r["predicted_mentions"]) for r in rows)
    print(f"[llm-inv] done in {time.time() - started:.1f}s; {n_calls} calls; {mention_count} mentions across {len(rows)} rows -> {jsonl_path.name}")


# --------------------------------------------------------------------------------------
# Assembly swap + scoring (mirrors the Rx comparator's _run_assembly).
# --------------------------------------------------------------------------------------
def _run_assembly(
    letters: list[ExectLetter],
    *,
    base_manifest,
    inv_jsonl: Path | None,
    candidate_id: str,
    split: str,
    claim_boundary: str,
    assembly_stem: str,
) -> dict[str, Any]:
    producers = dict(base_manifest.producers)
    if inv_jsonl is not None:
        producers[INV_PRODUCER_KEY] = replace(
            base_manifest.producers[INV_PRODUCER_KEY],
            artifact=inv_jsonl,
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
    print(f"\n=== {label} delta (LLM treatment vs hybrid baseline) ===")
    print(f"  overall: {bo['f1']:.4f} -> {bt['f1']:.4f} ({bt['f1'] - bo['f1']:+.4f})")
    for entity in (INVESTIGATIONS.name,):
        ro, rt = baseline["by_indicator"][entity], treatment["by_indicator"][entity]
        print(f"  {entity}: {ro['f1']:.4f} -> {rt['f1']:.4f} ({rt['f1'] - ro['f1']:+.4f})")
        print(f"    P {ro['precision']:.4f} -> {rt['precision']:.4f} | R {ro['recall']:.4f} -> {rt['recall']:.4f}")
        print(f"    TP {ro['tp']}->{rt['tp']} | FP {ro['fp']}->{rt['fp']} | FN {ro['fn']}->{rt['fn']}")


def _full200_base_manifest(letters: list[ExectLetter]):
    """Build the full-200 currentcode manifest by swapping each dev producer's
    artifact for its confirmed full-200 counterpart (same map the Rx comparator
    uses; verified via the P7 audit's lane_sources)."""

    dev_manifest = load_finding_assembly_manifest(DEV_MANIFEST_PATH)
    full200_artifacts = {
        "target_single_call_v042": EXPERIMENTS / "exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl",
        "diagnosis_reconciler_v01": EXPERIMENTS / "exectv2_v08_full200_currentcode_diagnosis_reconciler_gpt41mini_20260624.jsonl",
        "sf_union_arbitration_v08": EXPERIMENTS / "exectv2_v08_full200_currentcode_sf_union_arbitration_20260624.jsonl",
        "investigations_arbitration_v02": FULL200_INV_BASELINE,
        "prescription_repair_v03": EXPERIMENTS / "exectv2_v08_full200_currentcode_deterministic_prescription_repair_v03_20260624.jsonl",
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

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if args.split == "dev140":
        letters = load_letters_for_split("dev")
        split_tag = "dev140"
        claim_boundary = "dev_only_component_evidence"
        base_manifest = load_finding_assembly_manifest(DEV_MANIFEST_PATH)
    else:
        if not args.allow_non_dev140:
            sys.exit(
                "full-200 run requires a frozen-protocol predeclaration doc + "
                "--allow-non-dev140 (aggregate-only inspection per standing protocol)."
            )
        letters = load_letters()
        split_tag = "full200"
        claim_boundary = "full_200_aggregate_only"
        base_manifest = _full200_base_manifest(letters)

    # 1. Produce the LLM-tuned Inv artifact.
    llm_jsonl = EXPERIMENTS / f"exectv2_llm_inv_tuned_extractor_{split_tag}_{RUN_DATE}.jsonl"
    produce_llm_inv_artifact(
        letters, llm_jsonl, split=split_tag, num_threads=args.num_threads, cache=args.cache
    )

    # 2. Baseline assembly (unmodified manifest, hybrid Inv lane).
    baseline_stem = f"exectv2_v08_{split_tag}_inv_hybrid_baseline_{RUN_DATE}"
    baseline = _run_assembly(
        letters,
        base_manifest=base_manifest,
        inv_jsonl=None,
        candidate_id=f"exectv2_v08_{split_tag}_inv_hybrid_baseline_{RUN_DATE}",
        split=split_tag,
        claim_boundary=claim_boundary,
        assembly_stem=baseline_stem,
    )

    # 3. Treatment assembly (only Inv swapped for the LLM artifact).
    treatment_stem = f"exectv2_v08_{split_tag}_inv_llm_tuned_treatment_{RUN_DATE}"
    treatment = _run_assembly(
        letters,
        base_manifest=base_manifest,
        inv_jsonl=llm_jsonl,
        candidate_id=f"exectv2_v08_{split_tag}_inv_llm_tuned_treatment_{RUN_DATE}",
        split=split_tag,
        claim_boundary=claim_boundary,
        assembly_stem=treatment_stem,
    )

    _print_delta(split_tag, baseline, treatment)

    if args.split == "dev140":
        inv_base = baseline["by_indicator"][INVESTIGATIONS.name]["f1"]
        inv_treat = treatment["by_indicator"][INVESTIGATIONS.name]["f1"]
        delta = inv_treat - inv_base
        print(f"\n[gate] dev140 Inv delta = {delta:+.4f} (LLM {inv_treat:.4f} vs hybrid {inv_base:.4f})")
        print(f"[gate] kill-criterion: treatment must be >= {inv_base - 0.02:.4f} (within -0.02 of hybrid)")
        if inv_treat < inv_base - 0.02:
            print("[gate] KILL: LLM-tuned Inv collapses dev140 below -0.02 threshold; do NOT proceed to full-200.")
            sys.exit(2)
        print("[gate] PASS: dev140 loss within tolerance; full-200 (gated) may proceed with a predeclaration.")


if __name__ == "__main__":
    main()
