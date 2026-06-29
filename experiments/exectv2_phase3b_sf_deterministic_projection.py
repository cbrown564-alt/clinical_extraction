"""Phase 3b — wire the hybrid's deterministic SF state/change projection into the GEPA re-key.

Plan: docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md, Phase 3 extension.
Phase 3 (exectv2_phase3_deterministic_rekey.py) applied Dx+Rx convention projection but
left SF untouched, and the plan concluded "deterministic projection cannot touch SF."
That conclusion was wrong: the hybrid has a full deterministic SF state/change projection
(deterministic/sf_state_projection.py, 766 lines) plus deterministic change extraction
(deterministic/rules/change.py). This script wires both into the GEPA re-key path.

Two operations, mirroring sf_state_projection.py:

1. FILTER/REPAIR — apply the drop/repair rules from sf_state_projection.py to the GEPA
   producer's existing SF facts:
   - _change_reject: drop changed facts whose evidence is historical/hypothetical/family-history
   - _state_drop_rule: drop unlabelled/historical active-rates, advice-only seizure-free
   - _repair: active-rate with last-event duration -> seizure_free

2. RECALL-ADDITIVE — run the deterministic change extraction (CHANGE_EXTRACT_IMPLS from
   rules/change.py) over the note text and add change facts the producer missed, guarded
   by the same _change_reject + seizure-word checks sf_state_projection.py uses.

CRITICAL scorer note: clinical_headline's _frequency_state is count-only and FrequencyChange-
   blind (changed -> unknown). So recall-additive change facts are invisible on
   clinical_headline but visible on state_profile. Both metrics are reported.

Usage:
    uv run python experiments/exectv2_phase3b_sf_deterministic_projection.py
"""

from __future__ import annotations

import json
import re
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import clean_span
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    ExtractionContext,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import (
    CHANGE_EXTRACT_IMPLS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_state_projection import (
    _NAMED_TYPE_PATTERNS,
    _SEIZURE_WORD_RE,
    _UNLABELLED_EVENT_RE,
    _change_attrs,
    _change_reject,
    _drug_change_context,
    _last_event_duration,
    _seizure_free_reject,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import score_frequency_state
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
RUN = "exectv2_gepa_recall_lanes_deepseekchat_20260628"
MODEL = "deepseek/deepseek-chat"

_HISTORICAL_RATE_RE = re.compile(r"\b(at the onset|when (?:he|she) was younger)\b", re.IGNORECASE)
_PRECEDED_FREE_RE = re.compile(r"\b(up until|until)\b", re.IGNORECASE)
_CONTROLLED_RE = re.compile(r"\b(well controlled|under control|controlled)\b", re.IGNORECASE)


def _parse_instruction_blocks(path: Path) -> dict[str, str]:
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


def _apply_dx_rx_projection(facts: list[dict], *, dx: bool = True, rx: bool = True) -> list[dict]:
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


def _norm_ev(evidence: str) -> str:
    return re.sub(r"\s+", " ", evidence.strip().lower())


def _seizure_type_from_evidence(evidence: str) -> str:
    for pattern, text in _NAMED_TYPE_PATTERNS:
        if pattern.search(evidence):
            return text
    return "seizures"


def _apply_sf_projection(facts: list[dict], note_text: str) -> list[dict]:
    sf = [f for f in facts if str(f.get("family", "")).lower() == "seizure_frequency"]
    other = [f for f in facts if str(f.get("family", "")).lower() != "seizure_frequency"]

    has_seizure_free = any(
        str(f.get("state", "")).lower().replace("-", "_") == "seizure_free" for f in sf
    )

    kept: list[dict] = []
    for fact in sf:
        state = str(fact.get("state", "")).lower().replace("-", "_")
        evidence = str(fact.get("evidence", ""))
        lower = evidence.lower()

        if state == "changed" and _change_reject(evidence):
            continue
        if state == "active_rate" and not _SEIZURE_WORD_RE.search(evidence):
            if _UNLABELLED_EVENT_RE.search(evidence):
                continue
        if state == "active_rate" and _HISTORICAL_RATE_RE.search(evidence):
            continue
        if state == "active_rate" and has_seizure_free and _PRECEDED_FREE_RE.search(lower):
            continue
        if state == "seizure_free" and _seizure_free_reject(evidence):
            continue
        if state == "active_rate":
            duration = _last_event_duration(evidence)
            if duration is not None:
                fact = dict(fact)
                fact["state"] = "seizure_free"

        kept.append(fact)

    ctx = ExtractionContext(text=note_text)
    existing_evidence = {_norm_ev(str(f.get("evidence", ""))) for f in kept}
    n_added = 0
    for _rule_id, impl in CHANGE_EXTRACT_IMPLS.items():
        for match in impl.pattern.finditer(note_text):
            if any(pred(match, ctx) for pred in impl.exclude):
                continue
            result = impl.build(match, ctx)
            if result is None:
                continue
            evidence = str(result.evidence).strip()
            ev_norm = _norm_ev(evidence)
            if ev_norm in existing_evidence:
                continue
            if not _SEIZURE_WORD_RE.search(evidence):
                continue
            if _change_reject(evidence):
                continue
            attrs = _change_attrs(evidence)
            if not attrs:
                continue
            fc = attrs.get("FrequencyChange", "")
            if fc in {"Same", "Infrequent"} and _CONTROLLED_RE.search(evidence.lower()):
                if _drug_change_context(evidence.lower()):
                    pass
                else:
                    continue
            seizure_type = _seizure_type_from_evidence(evidence)
            kept.append({
                "family": "seizure_frequency",
                "seizure_type": seizure_type,
                "state": "changed",
                "evidence": evidence,
            })
            existing_evidence.add(ev_norm)
            n_added += 1

    return other + kept, n_added


def _apply_all_projection(
    facts: list[dict], note_text: str, *, dx: bool, rx: bool, sf: bool,
) -> tuple[list[dict], int]:
    facts = _apply_dx_rx_projection(facts, dx=dx, rx=rx)
    if sf:
        facts, n_added = _apply_sf_projection(facts, note_text)
        return facts, n_added
    return facts, 0


def _score(pred_by_id: dict[str, ExectLetter]):
    agg = [0, 0, 0, 0]
    fam = {f: [0, 0, 0, 0] for f in KEY_FAMILIES}
    for g in GOLD:
        p = pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ())
        s = _family_scores(g, p)
        for f in KEY_FAMILIES:
            c = _counts(s[f])
            for i in range(4):
                fam[f][i] += c[i]
                agg[i] += c[i]
    return _f1_from(*agg), {f: _f1_from(*fam[f]) for f in KEY_FAMILIES}


def _sf_state_score(pred_by_id: dict[str, ExectLetter]):
    gold_list = list(GOLD)
    pred_list = [pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ()) for g in GOLD]
    return score_frequency_state(gold_list, pred_list)


def _prf1_str(scores) -> str:
    return f"{scores.f1:.3f}(P{scores.precision:.2f}/R{scores.recall:.2f})"


GOLD = gepa_data.load_dev_letters()


def main() -> None:
    dotenv.load_dotenv(ROOT / ".env")
    lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=12000, cache=True)
    dspy.configure(lm=lm)

    program = _rebuild_program()
    evaluator = dspy.Parallel(num_threads=12, provide_traceback=True)
    predictions = evaluator(
        [(program, {"letter_text": g.note_text, "output_schema": OUTPUT_SCHEMA_JSON}) for g in GOLD]
    )

    stores: dict[str, dict[str, ExectLetter]] = {}
    sf_added: dict[str, int] = {}
    for g, prediction in zip(GOLD, predictions, strict=True):
        raw = str(getattr(prediction, "clinical_facts_json", "") or "") if prediction else ""
        try:
            facts = (json.loads(extract_json_object(raw)) or {}).get("clinical_facts", []) if raw else []
        except Exception:
            facts = []
        facts = [f for f in facts if isinstance(f, dict)]

        for label, projected, n_add in (
            ("base", facts, 0),
            ("dx_rx", _apply_all_projection(facts, g.note_text, dx=True, rx=True, sf=False)[0], 0),
            ("dx_rx_sf", *_apply_all_projection(facts, g.note_text, dx=True, rx=True, sf=True)),
        ):
            payload = json.dumps({"clinical_facts": projected}, ensure_ascii=False)
            record, _err = parse_dedup_clinical_facts_json(payload)
            store = stores.setdefault(label, {})
            if record is None:
                store[g.letter_id] = ExectLetter(g.letter_id, "", ())
                continue
            predicted, *_ = to_predicted_letter_from_dedup_facts(g, record)
            store[g.letter_id] = to_exect_letter(predicted)
            if label == "dx_rx_sf":
                sf_added[g.letter_id] = n_add

    print("# Phase 3b — deterministic SF projection on recall-lanes (replayed, dev140)\n")

    header = (
        f"{'config':<38}{'headline':>9}{'Dx':>7}{'SF':>7}{'Rx':>7}{'Inv':>7}"
        f"{'ev-rcl':>8}{'SF-state':>9}"
    )
    print(header)

    for label in ("base", "dx_rx", "dx_rx_sf"):
        store = stores[label]
        f1, fam = _score(store)
        ev = _evidence_recall(GOLD, [store.get(g.letter_id) or ExectLetter(g.letter_id, "", ()) for g in GOLD])
        sf_state = _sf_state_score(store)
        tag = {
            "base": "recall-lanes (replayed)",
            "dx_rx": "+ Dx+Rx re-key (Phase 3)",
            "dx_rx_sf": "+ SF projection (Phase 3b)",
        }[label]
        print(
            f"{tag:<38}{f1:>9.3f}{fam['Diagnosis']:>7.3f}{fam['SeizureFrequency']:>7.3f}"
            f"{fam['Prescription']:>7.3f}{fam['Investigations']:>7.3f}"
            f"{ev['overall_recall']:>8.3f}{sf_state.state_profile.f1:>9.3f}"
        )

    print()
    sf_base = _sf_state_score(stores["base"])
    sf_proj = _sf_state_score(stores["dx_rx_sf"])
    print("## SF state_profile detail (4-way, type-agnostic)")
    print(f"  {'config':<38}{'state_profile':>14}{'clin_headline':>14}")
    print(f"  {'recall-lanes':<38}{_prf1_str(sf_base.state_profile):>14}{_prf1_str(sf_base.clinical_headline):>14}")
    print(f"  {'+ SF projection':<38}{_prf1_str(sf_proj.state_profile):>14}{_prf1_str(sf_proj.clinical_headline):>14}")

    total_added = sum(sf_added.values())
    print(f"\n  Recall-additive change facts added: {total_added} across {sum(1 for v in sf_added.values() if v > 0)} letters")
    print(f"\n  Comparators: recall-lanes SF headline 0.580 / state_profile 0.710;")
    print(f"  Phase 3 (Dx+Rx) headline 0.763; hybrid SF 0.926 / state_profile 0.930")


if __name__ == "__main__":
    main()
