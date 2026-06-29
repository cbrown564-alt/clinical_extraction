"""Phase 3 — does deterministic KEYING convert the recall-lanes retrieved evidence to F1?

Plan: docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md, Phase 3.
The recall-lanes producers retrieved more evidence (ev-recall 0.694->0.781) but the
realized headline stayed flat (0.728) because the extra evidence is un-keyed (oracle
re-key ceiling 0.876). This applies the hybrid's deterministic Diagnosis convention
projection (the +0.058 lever, which is evidence-coupled) to the recall-lanes output and
re-scores — zero new optimization.

It reconstructs the evolved recall-lanes program from its saved instruction artifact and
replays inference at temp 0 with cache=True (the recall-lanes run cached its calls, so
this is cheap/free), capturing each fact's evidence — which the saved mentions dropped.
Then for each diagnosis fact it applies ``diagnosis_convention_target(concept, evidence)``
(v04 alias + v05 residual-benchmark/prefix repairs) and drops convention noise, re-projects
through the existing dedup adapter, and scores clinical_headline + per-family + ev-recall.

Usage:
    uv run python experiments/exectv2_phase3_deterministic_rekey.py
"""

from __future__ import annotations

import json
from pathlib import Path

import dotenv
import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import to_exect_letter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions.diagnosis import (
    diagnosis_convention_target,
    is_diagnosis_convention_noise,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions.prescription import (
    is_prescription_convention_noise,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import (
    KEY_FAMILIES,
    _counts,
    _f1_from,
    _family_scores,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import OUTPUT_SCHEMA_JSON
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_recall_lanes import (
    _RECALL_PREDICTORS,
    build_recall_lanes_program,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import _evidence_recall
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
RUN = "exectv2_gepa_recall_lanes_deepseekchat_20260628"
MODEL = "deepseek/deepseek-chat"


def _parse_instruction_blocks(path: Path) -> dict[str, str]:
    """Split the combined instruction artifact back into per-lane instruction strings."""
    blocks: dict[str, str] = {}
    name: str | None = None
    buf: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("=== ") and line.endswith(" ==="):
            if name is not None:
                blocks[name] = "\n".join(buf).strip("\n")
            name = line[4:-4].strip()
            buf = []
        else:
            buf.append(line)
    if name is not None:
        blocks[name] = "\n".join(buf).strip("\n")
    return blocks


def _rebuild_program() -> dspy.Module:
    program = build_recall_lanes_program()
    blocks = _parse_instruction_blocks(EXPERIMENTS / f"{RUN}.instruction.txt")
    for name, _sig, _schema in _RECALL_PREDICTORS:
        if name in blocks:
            pred = getattr(program, name)
            pred.signature = pred.signature.with_instructions(blocks[name])
    return program


def _apply_projection(facts: list[dict], *, dx: bool = True, rx: bool = True) -> list[dict]:
    """Apply the hybrid's deterministic convention projection at the fact level.

    Dx: rewrite concept to gold convention (evidence-coupled) + drop convention noise.
    Rx: drop planned/historical regimens (the over-emission DeepSeek produces).
    """
    out: list[dict] = []
    for fact in facts:
        family = str(fact.get("family", "")).lower()
        evidence = str(fact.get("evidence", ""))
        if dx and family == "diagnosis":
            concept = str(fact.get("concept", ""))
            target = diagnosis_convention_target(concept, evidence)
            new_concept = target if target is not None else concept
            diag_cat = diagnosis_category_for_concept(new_concept)
            if is_diagnosis_convention_noise(new_concept, evidence=evidence, diag_category=diag_cat):
                continue
            fact = dict(fact)
            fact["concept"] = new_concept
            out.append(fact)
            continue
        if rx and family == "prescription":
            drug = str(fact.get("drug", ""))
            if is_prescription_convention_noise(drug, evidence=evidence, attributes={"DrugName": drug}):
                continue
            out.append(fact)
            continue
        out.append(fact)
    return out


def _score(pred_by_id: dict[str, ExectLetter]):
    agg = [0, 0, 0, 0]
    fam = {f: [0, 0, 0, 0] for f in KEY_FAMILIES}
    gold = GOLD
    for g in gold:
        p = pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ())
        s = _family_scores(g, p)
        for f in KEY_FAMILIES:
            c = _counts(s[f])
            for i in range(4):
                fam[f][i] += c[i]
                agg[i] += c[i]
    return _f1_from(*agg), {f: _f1_from(*fam[f]) for f in KEY_FAMILIES}


GOLD = gepa_data.load_dev_letters()


def main() -> None:
    dotenv.load_dotenv(ROOT / ".env")
    lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=12000, cache=True)
    dspy.configure(lm=lm)

    program = _rebuild_program()
    evaluator = dspy.Parallel(num_threads=12, provide_traceback=True)
    predictions = evaluator([(program, {"letter_text": g.note_text, "output_schema": OUTPUT_SCHEMA_JSON})
                             for g in GOLD])

    base: dict[str, ExectLetter] = {}
    proj: dict[str, ExectLetter] = {}
    for g, prediction in zip(GOLD, predictions, strict=True):
        raw = str(getattr(prediction, "clinical_facts_json", "") or "") if prediction else ""
        try:
            facts = (json.loads(extract_json_object(raw)) or {}).get("clinical_facts", []) if raw else []
        except Exception:
            facts = []
        facts = [f for f in facts if isinstance(f, dict)]

        for label, fact_list, store in (("base", facts, base), ("proj", _apply_projection(facts), proj)):
            payload = json.dumps({"clinical_facts": fact_list}, ensure_ascii=False)
            record, _err = parse_dedup_clinical_facts_json(payload)
            if record is None:
                store[g.letter_id] = ExectLetter(g.letter_id, "", ())
                continue
            predicted, *_ = to_predicted_letter_from_dedup_facts(g, record)
            store[g.letter_id] = to_exect_letter(predicted)

    f_base, fam_base = _score(base)
    f_proj, fam_proj = _score(proj)
    ev_base = _evidence_recall(GOLD, [base.get(g.letter_id) or ExectLetter(g.letter_id, "", ()) for g in GOLD])
    ev_proj = _evidence_recall(GOLD, [proj.get(g.letter_id) or ExectLetter(g.letter_id, "", ()) for g in GOLD])

    print(f"# Phase 3 — deterministic Dx re-key on recall-lanes (replayed, dev140)\n")
    print(f"{'config':<34}{'headline':>9}{'Dx':>7}{'SF':>7}{'Rx':>7}{'Inv':>7}{'ev-recall':>11}")
    print(f"{'recall-lanes (replayed)':<34}{f_base:>9.3f}{fam_base['Diagnosis']:>7.3f}"
          f"{fam_base['SeizureFrequency']:>7.3f}{fam_base['Prescription']:>7.3f}"
          f"{fam_base['Investigations']:>7.3f}{ev_base['overall_recall']:>11.3f}")
    print(f"{'+ deterministic Dx+Rx projection':<34}{f_proj:>9.3f}{fam_proj['Diagnosis']:>7.3f}"
          f"{fam_proj['SeizureFrequency']:>7.3f}{fam_proj['Prescription']:>7.3f}"
          f"{fam_proj['Investigations']:>7.3f}{ev_proj['overall_recall']:>11.3f}")
    print(f"\n  Δ headline {f_proj - f_base:+.3f}  (Dx {fam_proj['Diagnosis'] - fam_base['Diagnosis']:+.3f})")
    print(f"  comparators: mini per-family 0.731 / hybrid 0.920; Phase-1 gate 0.761; oracle re-key ceiling 0.876")


if __name__ == "__main__":
    main()
