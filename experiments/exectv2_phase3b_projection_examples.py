"""Diagnostic: trace what Dx/Rx/SF deterministic projections do to specific facts.

Prints concrete examples of each projection type for documentation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import dotenv
import dspy

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import OUTPUT_SCHEMA_JSON
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_recall_lanes import (
    _RECALL_PREDICTORS,
    build_recall_lanes_program,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
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


def _norm_ev(evidence: str) -> str:
    return re.sub(r"\s+", " ", evidence.strip().lower())


def _seizure_type_from_evidence(evidence: str) -> str:
    for pattern, text in _NAMED_TYPE_PATTERNS:
        if pattern.search(evidence):
            return text
    return "seizures"


def _sf_reason(fact: dict, has_seizure_free: bool) -> str | None:
    """Return the drop/repair reason for an SF fact, or None if kept unchanged."""
    state = str(fact.get("state", "")).lower().replace("-", "_")
    evidence = str(fact.get("evidence", ""))
    lower = evidence.lower()
    if state == "changed" and _change_reject(evidence):
        return "DROP changed (reject pattern: historical/hypothetical)"
    if state == "active_rate" and not _SEIZURE_WORD_RE.search(evidence):
        if _UNLABELLED_EVENT_RE.search(evidence):
            return "DROP active_rate (unlabelled event, no seizure word)"
    if state == "active_rate" and _HISTORICAL_RATE_RE.search(evidence):
        return f"DROP active_rate (historical: {_HISTORICAL_RATE_RE.search(evidence).group(0)!r})"
    if state == "active_rate" and has_seizure_free and _PRECEDED_FREE_RE.search(lower):
        return "DROP active_rate (preceded by current seizure-free)"
    if state == "seizure_free" and _seizure_free_reject(evidence):
        return f"DROP seizure_free (advice/historical: {_seizure_free_reject(evidence)})"
    if state == "active_rate":
        duration = _last_event_duration(evidence)
        if duration is not None:
            return f"REPAIR active_rate -> seizure_free (last-event duration: {duration[0]} {duration[1]})"
    return None


def _dx_reason(fact: dict) -> str | None:
    family = str(fact.get("family", "")).lower()
    if family != "diagnosis":
        return None
    concept = str(fact.get("concept", ""))
    evidence = str(fact.get("evidence", ""))
    target = diagnosis_convention_target(concept, evidence)
    new_concept = target if target is not None else concept
    diag_cat = diagnosis_category_for_concept(new_concept)
    if is_diagnosis_convention_noise(new_concept, evidence=evidence, diag_category=diag_cat):
        return f"DROP (convention noise: {concept!r} -> {new_concept!r})"
    if target is not None and target != concept:
        return f"RE-KEY concept: {concept!r} -> {target!r}"
    return None


def _rx_reason(fact: dict) -> str | None:
    family = str(fact.get("family", "")).lower()
    if family != "prescription":
        return None
    drug = str(fact.get("drug", ""))
    evidence = str(fact.get("evidence", ""))
    if is_prescription_convention_noise(drug, evidence=evidence, attributes={"DrugName": drug}):
        return f"DROP (convention noise: planned/historical {drug!r})"
    return None


def main() -> None:
    dotenv.load_dotenv(ROOT / ".env")
    lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=12000, cache=True)
    dspy.configure(lm=lm)

    program = _rebuild_program()
    evaluator = dspy.Parallel(num_threads=12, provide_traceback=True)
    gold = list(gepa_data.load_dev_letters())
    predictions = evaluator(
        [(program, {"letter_text": g.note_text, "output_schema": OUTPUT_SCHEMA_JSON}) for g in gold]
    )

    # Collect examples by type
    sf_filter_examples: list[tuple[str, dict, str]] = []  # (letter_id, fact, reason)
    sf_add_examples: list[tuple[str, dict, str]] = []  # (letter_id, new_fact, note_context)
    dx_examples: list[tuple[str, dict, str]] = []
    rx_examples: list[tuple[str, dict, str]] = []

    for g, prediction in zip(gold, predictions, strict=True):
        raw = str(getattr(prediction, "clinical_facts_json", "") or "") if prediction else ""
        try:
            facts = (
                (json.loads(extract_json_object(raw)) or {}).get("clinical_facts", [])
                if raw
                else []
            )
        except Exception:
            facts = []
        facts = [f for f in facts if isinstance(f, dict)]

        sf_facts = [f for f in facts if str(f.get("family", "")).lower() == "seizure_frequency"]
        has_seizure_free = any(
            str(f.get("state", "")).lower().replace("-", "_") == "seizure_free" for f in sf_facts
        )

        # SF filter/repair
        for fact in sf_facts:
            reason = _sf_reason(fact, has_seizure_free)
            if reason:
                sf_filter_examples.append((g.letter_id, fact, reason))

        # SF recall-additive
        existing_ev = {_norm_ev(str(f.get("evidence", ""))) for f in sf_facts}
        ctx = ExtractionContext(text=g.note_text)
        for _rule_id, impl in CHANGE_EXTRACT_IMPLS.items():
            for match in impl.pattern.finditer(g.note_text):
                if any(pred(match, ctx) for pred in impl.exclude):
                    continue
                result = impl.build(match, ctx)
                if result is None:
                    continue
                evidence = str(result.evidence).strip()
                ev_norm = _norm_ev(evidence)
                if ev_norm in existing_ev:
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
                    if not _drug_change_context(evidence.lower()):
                        continue
                sf_add_examples.append(
                    (
                        g.letter_id,
                        {"evidence": evidence, "FrequencyChange": fc, "rule": _rule_id},
                        g.note_text[max(0, match.start() - 80) : match.end() + 80].strip(),
                    )
                )
                existing_ev.add(ev_norm)

        # Dx
        for fact in facts:
            reason = _dx_reason(fact)
            if reason:
                dx_examples.append((g.letter_id, fact, reason))

        # Rx
        for fact in facts:
            reason = _rx_reason(fact)
            if reason:
                rx_examples.append((g.letter_id, fact, reason))

    def _print_section(title: str, examples: list, max_n: int = 6) -> None:
        print(f"\n{'=' * 80}")
        print(f"## {title} ({len(examples)} total, showing {min(max_n, len(examples))})")
        print(f"{'=' * 80}")
        for i, item in enumerate(examples[:max_n]):
            if len(item) == 3:
                lid, data, reason = item
                print(f"\n  [{i + 1}] Letter {lid}")
                print(f"      reason: {reason}")
                print(f"      fact:   {json.dumps(data, ensure_ascii=False)}")
            elif len(item) == 3:
                lid, data, ctx = item
                print(f"\n  [{i + 1}] Letter {lid}")
                print(f"      fact:   {json.dumps(data, ensure_ascii=False)}")
                print(f"      context: ...{ctx}...")

    # SF filter/repair — separate REPAIR from DROP for clarity
    sf_repairs = [(lid, f, r) for lid, f, r in sf_filter_examples if "REPAIR" in r]
    sf_drops = [(lid, f, r) for lid, f, r in sf_filter_examples if "DROP" in r]

    _print_section("SF REPAIR (state changed by deterministic rule)", sf_repairs, max_n=3)
    _print_section("SF DROP (fact removed by deterministic rule)", sf_drops, max_n=4)
    _print_section(
        "SF RECALL-ADDITIVE (new fact from note text, model never selected)",
        sf_add_examples,
        max_n=4,
    )
    _print_section("Dx RE-KEY / DROP (concept label rewrite or noise drop)", dx_examples, max_n=5)
    _print_section("Rx DROP (planned/historical medication removed)", rx_examples, max_n=4)


if __name__ == "__main__":
    main()
