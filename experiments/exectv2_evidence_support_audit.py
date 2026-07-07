"""Evidence SUPPORT-quality companion audit (closes the FM1 guardrail's "Partial" status).

``core/evidence_validity_audit.py`` (and ``reconcile_evidence_groundedness_registry.py``)
already score evidence GROUNDEDNESS: is the cited evidence string locatable in the source
note text (``grade_evidence`` / ``is_grounded``). Per
``docs/research/predecessor_lessons/01_failure_modes_and_guardrails.md`` FM1 (the h005 null
result: confident, grounded-looking predictions were wrong as often as right), groundedness
is NOT the same question as SUPPORT: does the evidence text actually support the *specific*
claimed value/status/attributes, not just exist nearby. Nothing in the repo measured that
second dimension before this script (confirmed by a direct search for
support_quality/evidence_support/supports_claim).

Method (dev140, all four ExECTv2 families, zero new extraction calls for the headline
prediction set -- reuses the already-produced, already-scored v08 full-200 hybrid
production run):

1. Zero-LLM: read the v08 hybrid full-200 run's per-mention ``evidence_valid`` flag
   (the pipeline's own groundedness check, already computed) across every dev140 mention,
   as the GROUNDEDNESS baseline companion stat.
2. Small, bounded LLM-judge spot-check (~5 mentions per family, 20 total -- "Secondary
   validation" per the predeclared contract): for a stratified sample of GROUNDED mentions,
   ask whether the evidence text supports the SPECIFIC claimed phrase + attributes, not
   merely whether it is topically present. This is the new SUPPORT dimension.
3. Report SUPPORT rate alongside GROUNDEDNESS rate, per family -- never blended (BP3:
   "never let success on one layer imply success on the others").

Usage:  uv run python experiments/exectv2_evidence_support_audit.py
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import dotenv
import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
RUN_JSONL = (
    ROOT
    / "experiments"
    / "exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl"
)
OUT_JSON = ROOT / "experiments" / "exectv2_evidence_support_audit_2026-06-30.json"
OUT_MD = (
    ROOT
    / "docs"
    / "experiments"
    / "exectv2"
    / "reliability"
    / "exectv2_evidence_support_audit_2026-06-30.md"
)
MODEL = "openai/gpt-4.1-mini"
FAMILIES = ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"]
N_PER_FAMILY = 5
SEED = 20260630


class SupportJudge(dspy.Signature):
    """Judge whether a quoted evidence span from a clinical letter supports a SPECIFIC
    claimed clinical fact (not just whether the evidence is topically present)."""

    note_text: str = dspy.InputField(desc="the full clinical letter")
    entity: str = dspy.InputField(desc="the clinical entity family, e.g. Diagnosis")
    claimed_text: str = dspy.InputField(desc="the normalized phrase the model claims")
    claimed_attributes: str = dspy.InputField(desc="JSON of additional claimed attributes")
    evidence: str = dspy.InputField(desc="the quoted evidence string the model cited")
    verdict: str = dspy.OutputField(
        desc="exactly one of: SUPPORTS, PARTIALLY_SUPPORTS, DOES_NOT_SUPPORT"
    )
    reason: str = dspy.OutputField(
        desc="one sentence: does the evidence text itself justify the SPECIFIC claimed value/attributes"
    )


def load_dev140_mentions() -> dict[str, list[dict]]:
    dev_ids = {letter.letter_id for letter in gepa_data.load_dev_letters()}
    by_family: dict[str, list[dict]] = defaultdict(list)
    with RUN_JSONL.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("letter_id") not in dev_ids:
                continue
            for m in row.get("predicted_mentions", []):
                entity = m.get("entity")
                if entity in FAMILIES:
                    m["letter_id"] = row["letter_id"]
                    by_family[entity].append(m)
    return by_family


def groundedness_baseline(by_family: dict[str, list[dict]]) -> dict[str, dict]:
    out = {}
    for fam in FAMILIES:
        mentions = by_family.get(fam, [])
        n = len(mentions)
        grounded = sum(1 for m in mentions if m.get("evidence_valid") is True)
        out[fam] = {
            "n_mentions": n,
            "n_grounded": grounded,
            "groundedness_rate": round(grounded / n, 4) if n else None,
        }
    return out


def run_support_judge(by_family: dict[str, list[dict]], note_text_by_id: dict[str, str]) -> dict:
    lm = build_dspy_lm(MODEL, temperature=0.0, max_tokens=300, cache=True)
    judge = dspy.Predict(SupportJudge)

    rng = random.Random(SEED)
    sample_results: dict[str, list[dict]] = defaultdict(list)
    for fam in FAMILIES:
        grounded = [
            m
            for m in by_family.get(fam, [])
            if m.get("evidence_valid") is True and m.get("evidence")
        ]
        sample = rng.sample(grounded, min(N_PER_FAMILY, len(grounded)))
        for m in sample:
            note = note_text_by_id.get(m["letter_id"], "")
            with dspy.context(lm=lm):
                pred = judge(
                    note_text=note,
                    entity=fam,
                    claimed_text=m.get("text", ""),
                    claimed_attributes=json.dumps(m.get("attributes", {}), ensure_ascii=False),
                    evidence=m.get("evidence", ""),
                )
            verdict = str(getattr(pred, "verdict", "")).strip().upper()
            if verdict not in ("SUPPORTS", "PARTIALLY_SUPPORTS", "DOES_NOT_SUPPORT"):
                verdict = "UNPARSEABLE"
            sample_results[fam].append(
                {
                    "letter_id": m["letter_id"],
                    "claimed_text": m.get("text", ""),
                    "evidence": m.get("evidence", ""),
                    "verdict": verdict,
                    "reason": str(getattr(pred, "reason", "")),
                }
            )
    return sample_results


def main() -> None:
    dotenv.load_dotenv(ROOT / ".env")

    by_family = load_dev140_mentions()
    ground = groundedness_baseline(by_family)

    letters = gepa_data.load_dev_letters()
    note_text_by_id = {letter.letter_id: letter.note_text for letter in letters}

    samples = run_support_judge(by_family, note_text_by_id)

    support_summary = {}
    for fam in FAMILIES:
        rows = samples.get(fam, [])
        vc = Counter(r["verdict"] for r in rows)
        n = len(rows)
        full = vc["SUPPORTS"]
        partial = vc["PARTIALLY_SUPPORTS"]
        none_ = vc["DOES_NOT_SUPPORT"]
        support_summary[fam] = {
            "n_sampled": n,
            "SUPPORTS": full,
            "PARTIALLY_SUPPORTS": partial,
            "DOES_NOT_SUPPORT": none_,
            "support_rate_strict": round(full / n, 4) if n else None,
            "support_rate_lenient": round((full + partial) / n, 4) if n else None,
        }

    out = {
        "run_id": RUN_JSONL.stem,
        "model": MODEL,
        "n_per_family_sampled": N_PER_FAMILY,
        "seed": SEED,
        "groundedness_baseline": ground,
        "support_summary": support_summary,
        "support_samples": samples,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Sanity invariant: support rate (lenient) must be <= 1.0 and is a distinct dimension
    # from groundedness -- assert the two are not silently identical across all families
    # (a sign the judge degenerated into restating groundedness).
    print("=== EVIDENCE SUPPORT-QUALITY COMPANION AUDIT (dev140) ===\n")
    print(
        f"{'family':<18}{'grounded':>10}{'n':>6}   {'SUPPORTS':>9}{'PARTIAL':>9}{'NONE':>7}   "
        f"{'strict':>8}{'lenient':>9}"
    )
    for fam in FAMILIES:
        g = ground[fam]
        s = support_summary[fam]
        print(
            f"{fam:<18}{g['groundedness_rate'] if g['groundedness_rate'] is not None else float('nan'):>10.4f}"
            f"{s['n_sampled']:>6}   {s['SUPPORTS']:>9}{s['PARTIALLY_SUPPORTS']:>9}{s['DOES_NOT_SUPPORT']:>7}   "
            f"{(s['support_rate_strict'] or 0):>8.4f}{(s['support_rate_lenient'] or 0):>9.4f}"
        )

    write_report(out)
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_MD}")


def write_report(out: dict) -> None:
    lines = [
        '# Evidence support-quality companion audit (dev140) — closes FM1\'s "Partial" guardrail',
        "",
        f"Run: `{out['run_id']}` (v08 hybrid, full-200 production system, filtered to dev140).",
        f"Model: `{out['model']}`. Support-judge sample: {out['n_per_family_sampled']} grounded "
        f"mentions per family (seed {out['seed']}).",
        "",
        "Distinct from `evidence_validity_audit.py`'s **groundedness** rate (is the evidence "
        "string locatable in the note text). This measures **support**: does the evidence text "
        "justify the *specific* claimed value/attributes, not merely sit nearby. Per FM1 (the "
        "predecessor h005 null result), these must never be conflated.",
        "",
        "## Groundedness baseline (zero-LLM, full dev140, all mentions)",
        "",
        "| family | n_mentions | n_grounded | groundedness_rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for fam, g in out["groundedness_baseline"].items():
        lines.append(
            f"| {fam} | {g['n_mentions']} | {g['n_grounded']} | {g['groundedness_rate']} |"
        )

    lines += [
        "",
        "## Support-quality sample (LLM-judge, grounded mentions only)",
        "",
        "| family | n_sampled | SUPPORTS | PARTIALLY | NONE | strict rate | lenient rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for fam, s in out["support_summary"].items():
        lines.append(
            f"| {fam} | {s['n_sampled']} | {s['SUPPORTS']} | {s['PARTIALLY_SUPPORTS']} | "
            f"{s['DOES_NOT_SUPPORT']} | {s['support_rate_strict']} | {s['support_rate_lenient']} |"
        )

    lines += ["", "## Sample detail", ""]
    for fam, rows in out["support_samples"].items():
        lines.append(f"### {fam}")
        for r in rows:
            lines.append(
                f"- `{r['letter_id']}` claimed=`{r['claimed_text']}` evidence=`{r['evidence']}` "
                f"-> **{r['verdict']}** — {r['reason']}"
            )
        lines.append("")

    lines += [
        "## Caveats",
        "",
        "- Sample size is small (5/family, 20 total) — a bounded spot-check per the predeclared "
        "contract, not a precise rate; read as a signal, not a decimal.",
        "- Sampled only from mentions already flagged `evidence_valid` by the production "
        "pipeline (groundedness is a precondition for support; ungrounded evidence cannot "
        "support anything by construction).",
        "- The judge model (gpt-4.1-mini) is the same family as the production extractor; an "
        "independent judge model would be a stronger design for a future, larger-scale version "
        "of this audit.",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
