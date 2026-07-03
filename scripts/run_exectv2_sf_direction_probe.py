"""SF direction-extraction probe — Phase B1 (post-hoc) + B2 (full two-stage).

REFRAMED PURPOSE (post pre-work finding 2026-07-03):
The pre-work free replay showed the v08 hybrid SF union-arbitration producer
already scores 0.8897 on state_profile_directional (NOT direction-blind) — the
direction-blindness finding (0/12 recovery, state_profile_directional 0.6552)
is a property of the RAW two-stage SF-verify LLM program
(exectv2_gepa_sf_verify_gpt41mini_20260628), which the production pipeline does
not use alone. The hybrid sources directions from deterministic/rules/change.py.

So the question this probe answers is NOT "is the deterministic side blind"
(known: the raw LLM program is blind, the hybrid is not). It is:

  Can an LLM-only direction-aware program MATCH the hybrid's deterministic
  direction arbitration on state_profile_directional? This is evidence for/against
  the paper's 'deterministic lanes are not strictly necessary' thread.

Phase B1 (cheap, ~28 calls, dev140 post-hoc adjudication):
  Take the raw SF-verify program's changed-state mentions (35 across 28 dev140
  letters, all FC=Same). For each letter, make ONE LLM call: given the letter +
  the list of changed mentions, assign a 5-way direction. Re-score
  state_profile_directional. This isolates MODEL CAPACITY (can the LLM judge
  direction when explicitly asked?) from SCHEMA DEFECT (the raw program never
  asked).

  Kill criterion: if post-hoc recovery is <=2 of the ~30 gold-directional
  changed facts, the model cannot judge direction even when asked -- kill B2.

Phase B2 (expensive, gated on B1, ~280 dev140 + ~400 full-200 calls):
  Full two-stage direction-aware extraction. Modify the SF-verify program:
    1. Add change_direction to EVENT_SCHEMA (already done in the evolved
       instruction -- the instruction asks for it, but events_to_sf_facts
       ignores it and the schema doesn't list it; this wires it through).
    2. Modify events_to_sf_facts to pass change_direction -> FrequencyChange
       instead of the adapter defaulting to Same.
    3. Run generate->verify on dev140 + full-200, score state_profile_directional.

Usage:
  python scripts/run_exectv2_sf_direction_probe.py b1            # ~28 calls
  python scripts/run_exectv2_sf_direction_probe.py b2 dev140     # ~280 calls (gated on b1)
  python scripts/run_exectv2_sf_direction_probe.py b2 full200 --allow-non-dev140  # ~400 calls
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    EVENT_SCHEMA_JSON,
    GENERATE_SEED,
    SeizureFrequencyGenerateSignature,
    SeizureFrequencyVerifySignature,
    SfVerifyExtractor,
    VERIFY_SEED,
    events_to_sf_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.parsing import (
    parse_dedup_clinical_facts_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_faithful,
    score_frequency_state,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

RUN_DATE = date.today().isoformat().replace("-", "")
ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REPORT_DIR = ROOT / "docs" / "experiments" / "exectv2" / "seizure_frequency"
RAW_SF_VERIFY_JSONL = EXPERIMENTS / "exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl"

TASK_MODEL = "openai/gpt-4.1-mini"
TASK_TEMPERATURE = 0.0
TASK_MAX_TOKENS = 8000

SF_ENTITY = "SeizureFrequency"
DIRECTION_VOCAB = ("Increased", "Decreased", "Frequent", "Infrequent", "Same")


# --------------------------------------------------------------------------------------
# Phase B1: post-hoc direction adjudication (cheap capacity test).
# --------------------------------------------------------------------------------------
class DirectionAdjudicationSignature(dspy.Signature):
    """You read a clinical letter and a list of seizure-frequency change mentions.

    For each change mention, determine the DIRECTION of the change as one of:
    Increased, Decreased, Frequent, Infrequent, Same. Judge direction by comparing
    the CURRENT frequency to the PRIOR frequency described in the letter. If the
    letter does not state a direction, use Same. Return a JSON object mapping each
    change mention (by index) to its direction.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    change_mentions: str = dspy.InputField(desc="JSON list of {index, applies_to} for each change mention to adjudicate.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    directions_json: str = dspy.OutputField(
        desc='One JSON object {"directions": [{"index": 0, "direction": "Increased|Decreased|Frequent|Infrequent|Same"}]}. No markdown.'
    )

DIRECTION_SCHEMA_JSON = json.dumps(
    {"directions": [{"index": "the change mention index", "direction": "Increased | Decreased | Frequent | Infrequent | Same"}]},
    ensure_ascii=False,
    sort_keys=True,
)


class DirectionAdjudicator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.adjudicate = dspy.Predict(DirectionAdjudicationSignature)

    def forward(self, letter_text: str, change_mentions: str) -> dspy.Prediction:
        out = self.adjudicate(
            letter_text=letter_text,
            change_mentions=change_mentions,
            output_schema=DIRECTION_SCHEMA_JSON,
        )
        return dspy.Prediction(directions_json=str(getattr(out, "directions_json", "") or ""))


def _parse_directions(raw: str) -> dict[int, str]:
    """Parse {index: direction} from the adjudicator output."""

    try:
        payload = json.loads(extract_json_object(raw))
    except Exception:
        return {}
    out: dict[int, str] = {}
    for d in payload.get("directions", []):
        if not isinstance(d, dict):
            continue
        try:
            idx = int(d.get("index"))
        except (TypeError, ValueError):
            continue
        direction = str(d.get("direction", "")).strip()
        # Normalize to title-case match against the closed vocab.
        for v in DIRECTION_VOCAB:
            if direction.lower() == v.lower():
                out[idx] = v
                break
    return out


def _letters_with_changed_mentions(jsonl_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load the raw SF-verify artifact; return {letter_id: [changed mention dicts]}."""

    out: dict[str, list[dict[str, Any]]] = {}
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        changed: list[dict[str, Any]] = []
        for idx, m in enumerate(row.get("predicted_mentions", [])):
            if m.get("entity") != SF_ENTITY:
                continue
            attrs = m.get("attributes", {})
            if frequency_state_faithful(attrs) == "changed":
                changed.append({"index": idx, "applies_to": m.get("text", "seizures"), "_attrs": attrs})
        if changed:
            out[lid] = changed
    return out


def _pred_letters_from_raw(jsonl_path: Path, gold_by_id: dict[str, ExectLetter]) -> list[ExectLetter]:
    """Build predicted ExectLetters from the raw SF-verify artifact (no adjudication)."""

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
        sf = [m for m in row.get("predicted_mentions", []) if m.get("entity") == SF_ENTITY]
        anns = tuple(
            ExectAnnotation(
                entity=SF_ENTITY,
                text=str(m.get("text", "")),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes", {})).items()},
            )
            for m in sf
        )
        out.append(ExectLetter(letter_id=lid, note_text=gold.note_text, annotations=anns))
    return out


def run_b1(num_threads: int, cache: bool) -> None:
    """Phase B1: post-hoc direction adjudication of the raw SF-verify changed mentions."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    dev_gold = load_letters_for_split("dev")
    gold_by_id = {le.letter_id: le for le in dev_gold}

    # Baseline: score the raw SF-verify artifact unchanged (sanity check the 0.6552).
    baseline_pred = _pred_letters_from_raw(RAW_SF_VERIFY_JSONL, gold_by_id)
    baseline_scores = score_frequency_state(dev_gold, baseline_pred)
    print(f"[b1] RAW SF-verify baseline (unchanged):")
    print(f"  state_profile_directional F1: {baseline_scores.state_profile_directional.f1:.4f} (tp={baseline_scores.state_profile_directional.tp} fp={baseline_scores.state_profile_directional.fp} fn={baseline_scores.state_profile_directional.fn})")
    print(f"  state_profile F1:             {baseline_scores.state_profile.f1:.4f}")

    changed_by_letter = _letters_with_changed_mentions(RAW_SF_VERIFY_JSONL)
    total_changed = sum(len(v) for v in changed_by_letter.values())
    print(f"[b1] {total_changed} changed-state mentions across {len(changed_by_letter)} letters; adjudicating...")

    adjudicator = DirectionAdjudicator()
    lm = build_dspy_lm(TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache)
    dspy.configure(lm=lm)
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)

    pairs = []
    for lid, changed in changed_by_letter.items():
        letter = gold_by_id[lid]
        mentions_json = json.dumps([{"index": c["index"], "applies_to": c["applies_to"]} for c in changed])
        pairs.append((adjudicator, {"letter_text": letter.note_text, "change_mentions": mentions_json}))
    print(f"[b1] firing {len(pairs)} adjudication calls ({TASK_MODEL}, temp {TASK_TEMPERATURE})...", flush=True)
    started = time.time()
    predictions = evaluator(pairs)

    # Apply the adjudicated directions to a copy of the raw artifact. Carry ALL
    # 140 letters through (the 112 without changed mentions pass verbatim) so the
    # scorer sees the complete prediction set -- otherwise the missing letters
    # register as all-FN and collapse the metric.
    direction_counts: dict[str, int] = {}
    adj_by_id: dict[str, dict[str, Any]] = {}
    lids = list(changed_by_letter.keys())
    for lid, prediction in zip(lids, predictions, strict=True):
        dirs = _parse_directions(str(getattr(prediction, "directions_json", "") or "")) if prediction else {}
        changed = changed_by_letter[lid]
        row = json.loads(
            next(
                l for l in RAW_SF_VERIFY_JSONL.read_text(encoding="utf-8").splitlines()
                if l.strip() and json.loads(l)["letter_id"] == lid
            )
        )
        for c in changed:
            idx = c["index"]
            new_dir = dirs.get(idx)
            if new_dir and new_dir != "Same":
                row["predicted_mentions"][idx]["attributes"]["FrequencyChange"] = new_dir
                direction_counts[new_dir] = direction_counts.get(new_dir, 0) + 1
        adj_by_id[lid] = row
    # Build the full 140-row output: adjudicated rows where present, raw rows otherwise.
    adj_rows = []
    for line in RAW_SF_VERIFY_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        lid = json.loads(line)["letter_id"]
        adj_rows.append(adj_by_id.get(lid, json.loads(line)))
    print(f"[b1] done in {time.time() - started:.1f}s; adjudicated directions (non-Same): {direction_counts}; {len(adj_rows)} letters carried through")

    # Score the adjudicated artifact.
    adj_jsonl = EXPERIMENTS / f"exectv2_sf_verify_posthoc_direction_dev140_{RUN_DATE}.jsonl"
    write_jsonl(adj_rows, adj_jsonl)
    adj_pred = _pred_letters_from_raw(adj_jsonl, gold_by_id)
    adj_scores = score_frequency_state(dev_gold, adj_pred)
    print(f"[b1] POST-HOC ADJUDICATED:")
    print(f"  state_profile_directional F1: {adj_scores.state_profile_directional.f1:.4f} (tp={adj_scores.state_profile_directional.tp} fp={adj_scores.state_profile_directional.fp} fn={adj_scores.state_profile_directional.fn})")
    print(f"  state_profile F1:             {adj_scores.state_profile.f1:.4f} (regression check)")

    delta = adj_scores.state_profile_directional.f1 - baseline_scores.state_profile_directional.f1
    print(f"\n[b1] state_profile_directional delta = {delta:+.4f}")
    # Count how many gold-directional changed facts were recovered.
    gold_directional = sum(
        1 for le in dev_gold for a in le.entities(SF_ENTITY)
        if frequency_state_faithful(a.attributes) == "changed"
        and a.attributes.get("FrequencyChange", "Same") != "Same"
    )
    recovered = adj_scores.state_profile_directional.tp - baseline_scores.state_profile_directional.tp
    print(f"[b1] gold-directional changed facts (dev140): {gold_directional}; recovered (tp delta): +{recovered}")
    print(f"[b1] kill-criterion: recovered must be > 2 to proceed to B2")
    if recovered <= 2:
        print("[b1] KILL: model cannot judge direction even when explicitly asked; B2 pointless.")
        sys.exit(2)
    print("[b1] PASS: model can judge direction when asked; B2 (gated) may proceed.")


# --------------------------------------------------------------------------------------
# Phase B2: full two-stage direction-aware extraction.
# --------------------------------------------------------------------------------------
# The evolved instruction already asks for change_direction (the instruction text
# contains "change_direction only when kind = changed"). The SCHEMA defect is that
# EVENT_SCHEMA_JSON doesn't list it and events_to_sf_facts ignores it. B2 wires it
# through: a direction-aware schema + a direction-aware events_to_sf_facts.

DIRECTIONAL_EVENT_SCHEMA: dict[str, object] = {
    "events": [
        {
            "applies_to": "the seizure type this frequency statement is about, or 'seizures' if generic",
            "kind": "frequency_rate | cluster_frequency | seizure_free | changed",
            "change_direction": "increased | decreased | frequent | infrequent | null (only when kind = changed)",
            "evidence": "exact substring copied from the letter",
        }
    ]
}
DIRECTIONAL_EVENT_SCHEMA_JSON = json.dumps(DIRECTIONAL_EVENT_SCHEMA, ensure_ascii=False, sort_keys=True)


def events_to_sf_facts_directional(raw_output: str) -> list[dict]:
    """Direction-aware variant of events_to_sf_facts: passes change_direction through."""

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
        fact = {
            "family": "seizure_frequency",
            "seizure_type": str(ev.get("applies_to") or "seizures"),
            "state": {"frequency_rate": "active_rate", "cluster_frequency": "active_rate",
                      "seizure_free": "seizure_free", "changed": "changed"}.get(kind, "unknown"),
            "evidence": str(ev.get("evidence") or ""),
        }
        if kind == "changed":
            direction = str(ev.get("change_direction") or "").strip().lower()
            mapping = {"increased": "Increased", "decreased": "Decreased",
                       "frequent": "Frequent", "infrequent": "Infrequent", "same": "Same"}
            if direction in mapping:
                fact["attributes"] = {"FrequencyChange": mapping[direction]}
        facts.append(fact)
    return facts


# Direction-discipline delta appended to the evolved verify instruction.
DIRECTION_DISCIPLINE_DELTA = """

**DIRECTION DISCIPLINE (critical for this task):**
- For EVERY event with kind = changed, you MUST set change_direction by comparing
  the CURRENT frequency to the PRIOR frequency stated in the letter.
- "increased" / "decreased" = a directional change in COUNT or RATE (more/fewer
  seizures than before; "worse"/"more frequent" = increased; "improved"/"better
  controlled" = decreased).
- "frequent" / "infrequent" = a qualitative change toward a frequent or infrequent
  pattern (not a count comparison).
- Only use "same" if the letter explicitly says the frequency is unchanged.
- NEVER default a changed event to null or same out of uncertainty — read the
  letter's comparison and assert the direction."""


def _load_evolved_sf_instructions() -> tuple[str, str]:
    """Load the evolved generate + verify instructions from the canonical artifact."""

    path = EXPERIMENTS / "exectv2_gepa_sf_verify_gpt41mini_20260628.instruction.txt"
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^=== (\w+) ===$", text, flags=re.MULTILINE)
    generate = verify = None
    for i in range(1, len(blocks), 2):
        if blocks[i].strip() == "generate":
            generate = blocks[i + 1].strip("\n")
        elif blocks[i].strip() == "verify":
            verify = blocks[i + 1].strip("\n")
    if generate is None or verify is None:
        raise RuntimeError("could not parse generate/verify blocks from SF instruction artifact")
    return generate, verify + DIRECTION_DISCIPLINE_DELTA


class DirectionAwareSfVerifyExtractor(SfVerifyExtractor):
    """Two-stage SF program that wires change_direction through to FrequencyChange.

    Subclasses SfVerifyExtractor so the evolved instructions + (optional) demos are
    preserved; overrides forward to use the direction-aware schema + facts mapper.
    """

    def forward(self, letter_text: str) -> dspy.Prediction:
        drafted = self.generate(letter_text=letter_text, output_schema=DIRECTIONAL_EVENT_SCHEMA_JSON)
        draft_json = str(getattr(drafted, "events_json", "") or "")
        verified = self.verify(
            letter_text=letter_text,
            draft_events_json=draft_json,
            output_schema=DIRECTIONAL_EVENT_SCHEMA_JSON,
        )
        facts = events_to_sf_facts_directional(str(getattr(verified, "events_json", "") or ""))
        return dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": facts}, ensure_ascii=False)
        )


def _project_sf_facts_to_letter(gold_letter: ExectLetter, facts_json: str) -> ExectLetter:
    """Project SF clinical_facts JSON through the dedup adapter to an ExectLetter."""

    record, _errors = parse_dedup_clinical_facts_json(facts_json) if facts_json else (None, ["empty"])
    if record is None:
        predicted = PredictedLetter(letter_id=gold_letter.letter_id, mentions=())
    else:
        predicted, *_ = to_predicted_letter_from_dedup_facts(gold_letter, record)
    pred_exect = to_exect_letter(predicted)
    return pred_exect


def run_b2(split: str, num_threads: int, cache: bool, allow_non_dev140: bool) -> None:
    """Phase B2: full two-stage direction-aware extraction + score."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if split == "dev140":
        gold_letters = load_letters_for_split("dev")
        split_tag = "dev140"
    else:
        if not allow_non_dev140:
            sys.exit("full-200 B2 requires --allow-non-dev140 (aggregate-only per standing protocol).")
        gold_letters = load_letters()
        split_tag = "full200"
    gold_by_id = {le.letter_id: le for le in gold_letters}

    # Baseline: raw SF-verify program (no direction wiring) on this split.
    # For dev140 we have the stored artifact; for full-200 we must re-run.
    generate_seed, verify_seed = _load_evolved_sf_instructions()
    lm = build_dspy_lm(TASK_MODEL, temperature=TASK_TEMPERATURE, max_tokens=TASK_MAX_TOKENS, cache=cache)
    dspy.configure(lm=lm)

    # Run the direction-aware program.
    program = DirectionAwareSfVerifyExtractor(
        generate_seed=generate_seed, verify_seed=verify_seed, generate_lm=lm, verify_lm=lm,
    )
    evaluator = dspy.Parallel(num_threads=num_threads, provide_traceback=True)
    pairs = [(program, {"letter_text": le.note_text}) for le in gold_letters]
    print(f"[b2-{split_tag}] running direction-aware two-stage SF-verify on {len(gold_letters)} letters ({TASK_MODEL}, temp {TASK_TEMPERATURE})...", flush=True)
    started = time.time()
    predictions = evaluator(pairs)
    n_calls = sum(1 for p in predictions if p and str(getattr(p, "clinical_facts_json", "") or ""))
    print(f"[b2-{split_tag}] done in {time.time() - started:.1f}s; {n_calls} non-empty outputs")

    # Also run the NON-directional baseline program on the same split for a same-day comparison.
    baseline_program = SfVerifyExtractor(
        generate_seed=generate_seed, verify_seed=verify_seed.removesuffix(DIRECTION_DISCIPLINE_DELTA),
        generate_lm=lm, verify_lm=lm,
    )
    print(f"[b2-{split_tag}] running NON-directional baseline on {len(gold_letters)} letters...", flush=True)
    base_predictions = evaluator([(baseline_program, {"letter_text": le.note_text}) for le in gold_letters])

    # Build pred letters + score both.
    def to_pred_letters(preds) -> list[ExectLetter]:
        out = []
        for letter, pred in zip(gold_letters, preds, strict=True):
            facts_json = str(getattr(pred, "clinical_facts_json", "") or "") if pred else ""
            pred_exect = _project_sf_facts_to_letter(letter, facts_json)
            out.append(ExectLetter(
                letter_id=letter.letter_id, note_text=letter.note_text,
                annotations=pred_exect.entities(SF_ENTITY),
            ))
        return out

    base_pred = to_pred_letters(base_predictions)
    dir_pred = to_pred_letters(predictions)
    base_scores = score_frequency_state(gold_letters, base_pred)
    dir_scores = score_frequency_state(gold_letters, dir_pred)

    print(f"\n[b2-{split_tag}] NON-directional baseline (this run):")
    print(f"  state_profile_directional F1: {base_scores.state_profile_directional.f1:.4f} (tp={base_scores.state_profile_directional.tp} fp={base_scores.state_profile_directional.fp} fn={base_scores.state_profile_directional.fn})")
    print(f"  state_profile F1:             {base_scores.state_profile.f1:.4f}")
    print(f"  clinical_headline F1:         {base_scores.clinical_headline.f1:.4f}")
    print(f"[b2-{split_tag}] DIRECTION-AWARE treatment:")
    print(f"  state_profile_directional F1: {dir_scores.state_profile_directional.f1:.4f} (tp={dir_scores.state_profile_directional.tp} fp={dir_scores.state_profile_directional.fp} fn={dir_scores.state_profile_directional.fn})")
    print(f"  state_profile F1:             {dir_scores.state_profile.f1:.4f} (regression check)")
    print(f"  clinical_headline F1:         {dir_scores.clinical_headline.f1:.4f} (regression check)")

    d_delta = dir_scores.state_profile_directional.f1 - base_scores.state_profile_directional.f1
    sp_delta = dir_scores.state_profile.f1 - base_scores.state_profile.f1
    print(f"\n[b2-{split_tag}] deltas (direction-aware vs baseline):")
    print(f"  state_profile_directional: {d_delta:+.4f}")
    print(f"  state_profile (regression): {sp_delta:+.4f}")

    # Reference: the v08 hybrid production number (free-replay baseline from pre-work).
    hybrid_ref = {"dev140": 0.8897, "full200": 0.8483}
    print(f"\n[b2-{split_tag}] REFERENCE: v08 hybrid production state_profile_directional = {hybrid_ref[split_tag]}")
    gap_to_hybrid = dir_scores.state_profile_directional.f1 - hybrid_ref[split_tag]
    print(f"  direction-aware LLM gap to hybrid: {gap_to_hybrid:+.4f} (negative = LLM trails the hybrid)")

    # Write artifacts.
    out_jsonl = EXPERIMENTS / f"exectv2_sf_direction_aware_{split_tag}_{RUN_DATE}.jsonl"
    rows = []
    for letter, pred in zip(gold_letters, predictions, strict=True):
        facts_json = str(getattr(pred, "clinical_facts_json", "") or "") if pred else ""
        pred_exect = _project_sf_facts_to_letter(letter, facts_json)
        mentions = [
            {"entity": SF_ENTITY, "text": str(a.text), "attributes": dict(a.attributes)}
            for a in pred_exect.entities(SF_ENTITY)
        ]
        rows.append({"letter_id": letter.letter_id, "split": split_tag, "predicted_mentions": mentions})
    write_jsonl(rows, out_jsonl)
    print(f"[b2-{split_tag}] artifact -> {out_jsonl.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="phase", required=True)
    b1 = sub.add_parser("b1", help="post-hoc direction adjudication (~28 calls)")
    b1.add_argument("--num-threads", type=int, default=12)
    b1.add_argument("--cache", action="store_true")
    b2 = sub.add_parser("b2", help="full two-stage direction-aware extraction (gated on b1)")
    b2.add_argument("split", choices=["dev140", "full200"])
    b2.add_argument("--allow-non-dev140", action="store_true")
    b2.add_argument("--num-threads", type=int, default=12)
    b2.add_argument("--cache", action="store_true")
    args = parser.parse_args()

    if args.phase == "b1":
        run_b1(num_threads=args.num_threads, cache=args.cache)
    elif args.phase == "b2":
        run_b2(args.split, num_threads=args.num_threads, cache=args.cache, allow_non_dev140=args.allow_non_dev140)


if __name__ == "__main__":
    main()
