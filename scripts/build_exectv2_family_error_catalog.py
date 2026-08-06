#!/usr/bin/env python3
"""ExECTv2 four-family error catalog with examples.

No new model calls. No locked-test row inspection. See
docs/research/exectv2_family_error_catalog_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    headline_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_MODE = 2
FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)
_STATE_RE = re.compile(r"'(active-rate|seizure-free|unknown|changed)'")

_HS_PATH = REPO_ROOT / "scripts/build_six_model_hard_slice_error_modes.py"
_SPEC = importlib.util.spec_from_file_location("hard_slice_error_modes", _HS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_HS_PATH}")
hs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(hs)

MODEL_PREFERENCE = (
    "gpt56sol",
    "gpt56luna",
    "gpt41mini",
    "deepseek_v4_flash",
    "qwen36_35b",
    "gemma4_26b",
)


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _mode(gold_keys: list[str], pred_keys: list[str]) -> str:
    gold = Counter(gold_keys)
    pred = Counter(pred_keys)
    fp = sum(max(0, pred[key] - gold.get(key, 0)) for key in pred)
    fn = sum(max(0, gold[key] - pred.get(key, 0)) for key in gold)
    gold_n = sum(gold.values())
    pred_n = sum(pred.values())
    if fp == 0 and fn == 0:
        return "correct_empty" if gold_n == 0 else "correct_nonempty"
    if gold_n == 0 and pred_n > 0:
        return "empty_gold_spurious"
    if gold_n > 0 and pred_n == 0:
        return "missed_all"
    if fp > 0 and fn == 0:
        return "extra_only"
    if fn > 0 and fp == 0:
        return "missed_only"
    return "substituted_or_mixed"


def _token_from_key(family: str, key: str) -> str:
    if family == "SeizureFrequency":
        match = _STATE_RE.search(key)
        return match.group(1) if match else key
    # Strip outer repr noise for display; keep a short readable token.
    text = key.strip()
    if len(text) > 80:
        return text[:79] + "…"
    return text


def _compact_mentions(mentions: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for mention in mentions:
        if str(mention.get("entity", "")) != family:
            continue
        attrs = {
            str(key): str(value)
            for key, value in (mention.get("attributes") or {}).items()
            if value is not None
        }
        out.append({"text": mention.get("text"), "attributes": attrs})
    return out


def _pick_examples(
    candidates: list[dict[str, Any]],
    *,
    consensus: set[str],
) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(MODEL_PREFERENCE)
        consensus_rank = 0 if str(row["letter_id"]) in consensus else 1
        gold_states = set(row.get("gold_tokens") or [])
        pred_states = set(row.get("pred_tokens") or [])
        clarity = 0 if gold_states != pred_states else 1
        return (consensus_rank, clarity, model_rank, str(row["letter_id"]))

    picked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in sorted(candidates, key=sort_key):
        letter_id = str(row["letter_id"])
        if letter_id in seen:
            continue
        picked.append(row)
        seen.add(letter_id)
        if len(picked) >= EXAMPLES_PER_MODE:
            break
    return picked


def build_surface(*, surface: str) -> dict[str, Any]:
    field = "raw_lane_mentions" if surface == "llm" else "predicted_mentions"
    families_out: dict[str, Any] = {}

    for family in FAMILIES:
        per_model: dict[str, Any] = {}
        imperfect_by_model: dict[str, set[str]] = {}
        all_imperfect: list[dict[str, Any]] = []
        mode_counter: Counter[str] = Counter()
        missed_tokens: Counter[str] = Counter()
        extra_tokens: Counter[str] = Counter()

        for slug, display in hs.MODEL_SPECS:
            rows = hs._read_jsonl(hs.EXECT_JSONL[slug])
            model_modes: Counter[str] = Counter()
            imperfect_ids: set[str] = set()
            n_correct = 0
            for row in rows:
                letter_id = str(row["letter_id"])
                gold_keys = headline_keys(row, family, field="gold_mentions")
                pred_keys = headline_keys(row, family, field=field)
                mode = _mode(gold_keys, pred_keys)
                model_modes[mode] += 1
                mode_counter[mode] += 1
                if mode.startswith("correct_"):
                    n_correct += 1
                    continue
                imperfect_ids.add(letter_id)
                gold_counter = Counter(gold_keys)
                pred_counter = Counter(pred_keys)
                for key, count in gold_counter.items():
                    missing = count - pred_counter.get(key, 0)
                    if missing > 0:
                        missed_tokens[_token_from_key(family, key)] += missing
                for key, count in pred_counter.items():
                    extra = count - gold_counter.get(key, 0)
                    if extra > 0:
                        extra_tokens[_token_from_key(family, key)] += extra
                payload = {
                    "model_slug": slug,
                    "model_display": display,
                    "letter_id": letter_id,
                    "family": family,
                    "prediction_field": field,
                    "error_mode": mode,
                    "gold_key_count": len(gold_keys),
                    "pred_key_count": len(pred_keys),
                    "gold_tokens": sorted(
                        {_token_from_key(family, key) for key in gold_keys}
                    ),
                    "pred_tokens": sorted(
                        {_token_from_key(family, key) for key in pred_keys}
                    ),
                    "gold_keys": gold_keys,
                    "pred_keys": pred_keys,
                    "gold_mentions": _compact_mentions(
                        row.get("gold_mentions") or [], family
                    ),
                    "pred_mentions": _compact_mentions(row.get(field) or [], family),
                }
                all_imperfect.append(payload)
            imperfect_by_model[slug] = imperfect_ids
            n_letters = len(rows)
            per_model[slug] = {
                "display_name": display,
                "n_letters": n_letters,
                "n_correct_letters": n_correct,
                "n_imperfect_letters": n_letters - n_correct,
                "letter_exact_rate": (
                    round(n_correct / n_letters, 4) if n_letters else None
                ),
                "modes": dict(
                    sorted(model_modes.items(), key=lambda item: (-item[1], item[0]))
                ),
            }

        consensus = (
            set.intersection(*imperfect_by_model.values())
            if imperfect_by_model
            else set()
        )
        imperfect_modes = sorted(
            mode
            for mode in mode_counter
            if not mode.startswith("correct_")
        )
        examples = {
            mode: _pick_examples(
                [row for row in all_imperfect if row["error_mode"] == mode],
                consensus=consensus,
            )
            for mode in imperfect_modes
        }
        families_out[family] = {
            "family": family,
            "prediction_field": field,
            "models": per_model,
            "pooled_mode_counts": dict(
                sorted(mode_counter.items(), key=lambda item: (-item[1], item[0]))
            ),
            "pooled_imperfect_mode_counts": {
                mode: mode_counter[mode] for mode in imperfect_modes
            },
            "consensus_imperfect_all_six": {
                "n": len(consensus),
                "letter_ids": sorted(consensus),
            },
            "pooled_missed_tokens_top": dict(
                sorted(missed_tokens.items(), key=lambda item: (-item[1], item[0]))[:20]
            ),
            "pooled_extra_tokens_top": dict(
                sorted(extra_tokens.items(), key=lambda item: (-item[1], item[0]))[:20]
            ),
            "examples_by_mode": examples,
        }

    return {
        "surface": surface,
        "split": "dev140",
        "metric": "clinical_headline_unit_key_letter_exact",
        "prediction_field": field,
        "families": families_out,
    }


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def _render_example(row: dict[str, Any]) -> str:
    gold_texts = [str(m.get("text") or "") for m in row.get("gold_mentions") or []]
    pred_texts = [str(m.get("text") or "") for m in row.get("pred_mentions") or []]
    lines = [
        f"- **{row['letter_id']} / {row['model_display']}.** "
        f"Mode `{row['error_mode']}`; keys {row['gold_key_count']}→"
        f"{row['pred_key_count']}."
    ]
    lines.append(
        "  Tokens: "
        f"{row.get('gold_tokens')} → {row.get('pred_tokens')}."
    )
    if gold_texts or pred_texts:
        lines.append(
            "  Mentions: gold "
            f"`{_md_escape(', '.join(gold_texts) or '∅')}` vs pred "
            f"`{_md_escape(', '.join(pred_texts) or '∅')}`."
        )
    return "\n".join(lines)


def render_report(artifact: dict[str, Any]) -> str:
    lines: list[str] = [
        "# ExECTv2 four-family error catalog",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development catalog on retained no-call artifacts  ",
        "Protocol: [exect family error catalog protocol]"
        "(exectv2_family_error_catalog_protocol_2026-08-06.md)  ",
        "Parent: [category-cut performance]"
        "(six_model_category_cut_performance_2026-08-06.md)  ",
        f"Artifact: [`experiments/exectv2_family_error_catalog_{DATE_STAMP}.json`]"
        f"(../../experiments/exectv2_family_error_catalog_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        "All four families have imperfect letter modes on both surfaces.",
        "Diagnosis is an inventory problem (large `extra_only` /",
        "`substituted_or_mixed`; dozens of consensus imperfect letters).",
        "SeizureFrequency adds empty-gold spurious active-rate and missed state",
        "inventory. Prescription and Investigations are smaller but real:",
        "missed-only, missed-all, and empty-gold spurious still appear. Rules",
        "improve Diagnosis letter-exact rates and cut some SF empty-gold",
        "over-reads; Prescription consensus imperfect can widen under rules",
        "(missed-all rises)—rules are not uniformly helpful by family.",
        "",
        "## Method",
        "",
        "- Split: `dev140`. Surfaces: `llm` (`raw_lane_mentions`) and",
        "  `llm_with_rules` (`predicted_mentions`).",
        "- Letter metric: clinical-headline unit-key multiset exactness **per family**.",
        "- Imperfect modes: `empty_gold_spurious`, `missed_all`, `missed_only`,",
        "  `extra_only`, `substituted_or_mixed`.",
        "- Examples: up to two per observed imperfect mode; consensus + Sol preferred;",
        "  mention texts/attributes from saved rows only; holdout sealed.",
        "- Category-cut family F1 remains the competence metric; letter exactness is",
        "  the mechanism lens used here.",
        "- Regenerate: `python scripts/build_exectv2_family_error_catalog.py`.",
        "",
    ]

    for surface in ("llm", "llm_with_rules"):
        surface_block = artifact["surfaces"][surface]
        lines.extend(
            [
                f"## Surface: `{surface}`",
                "",
                "### Family letter-exact overview",
                "",
                (
                    "| Family | Sol exact | Exact min–max | Consensus imperfect | "
                    "Top imperfect modes |"
                ),
                "| --- | ---: | --- | ---: | --- |",
            ]
        )
        for family in FAMILIES:
            block = surface_block["families"][family]
            rates = [
                model["letter_exact_rate"]
                for model in block["models"].values()
                if model["letter_exact_rate"] is not None
            ]
            band = f"{min(rates):.2f}–{max(rates):.2f}" if rates else "n/a"
            sol = block["models"]["gpt56sol"]["letter_exact_rate"]
            top = ", ".join(
                f"{mode} ({count})"
                for mode, count in list(
                    block["pooled_imperfect_mode_counts"].items()
                )[:3]
            ) or "_(none)_"
            lines.append(
                f"| {family} | {sol:.4f} | {band} | "
                f"{block['consensus_imperfect_all_six']['n']} | {top} |"
            )
        lines.append("")

        for family in FAMILIES:
            block = surface_block["families"][family]
            lines.extend(
                [
                    f"### {family}",
                    "",
                    "#### Per-model letter exactness",
                    "",
                    "| Model | Exact | Imperfect | Mode counts |",
                    "| --- | ---: | ---: | --- |",
                ]
            )
            for slug, _display in hs.MODEL_SPECS:
                model = block["models"][slug]
                mode_txt = ", ".join(
                    f"{mode}:{count}" for mode, count in model["modes"].items()
                )
                lines.append(
                    f"| {model['display_name']} | {model['letter_exact_rate']:.4f} | "
                    f"{model['n_imperfect_letters']} | {mode_txt} |"
                )
            lines.extend(
                [
                    "",
                    "#### Pooled modes",
                    "",
                    "| Mode | Count |",
                    "| --- | ---: |",
                ]
            )
            for mode, count in block["pooled_mode_counts"].items():
                lines.append(f"| `{mode}` | {count} |")
            lines.extend(["", "#### Top missed / extra tokens (pooled)", ""])
            if block["pooled_missed_tokens_top"] or block["pooled_extra_tokens_top"]:
                lines.append("| Direction | Token | Count |")
                lines.append("| --- | --- | ---: |")
                for token, count in list(block["pooled_missed_tokens_top"].items())[:8]:
                    lines.append(f"| missed | `{_md_escape(token)}` | {count} |")
                for token, count in list(block["pooled_extra_tokens_top"].items())[:8]:
                    lines.append(f"| extra | `{_md_escape(token)}` | {count} |")
            else:
                lines.append("_No imperfect token mass._")
            lines.extend(["", "#### Examples by imperfect mode", ""])
            if not block["examples_by_mode"]:
                lines.append("_No imperfect letters on this surface._")
                lines.append("")
                continue
            for mode, examples in block["examples_by_mode"].items():
                lines.append(f"##### `{mode}`")
                lines.append("")
                for example in examples:
                    lines.append(_render_example(example))
                lines.append("")

    lines.extend(
        [
            "## Claim boundary",
            "",
            "- Development ExECT four-family error catalog on `dev140`.",
            "- Letter exactness is a mechanism lens; category-cut family F1 remains",
            "  the competence metric.",
            "- Mention texts are from saved prediction rows, not full notes.",
            "- Not sealed holdout competence; not a Decision 0046 rewrite.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact() -> dict[str, Any]:
    return {
        "schema_version": "exectv2.family_error_catalog.v1",
        "date": REPORT_DATE,
        "protocol": "docs/research/exectv2_family_error_catalog_protocol_2026-08-06.md",
        "parent_category_cut": (
            "docs/research/six_model_category_cut_performance_2026-08-06.md"
        ),
        "call_mode": "saved_output_no_call",
        "text_policy": "development_saved_mention_texts_only",
        "git": _git_note(),
        "models": [
            {"slug": slug, "display_name": display}
            for slug, display in hs.MODEL_SPECS
        ],
        "families": list(FAMILIES),
        "surfaces": {
            "llm": build_surface(surface="llm"),
            "llm_with_rules": build_surface(surface="llm_with_rules"),
        },
        "claim_boundary": (
            "Development ExECT four-family error catalog with examples. "
            "Not holdout competence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / f"experiments/exectv2_family_error_catalog_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT / "docs/research/exectv2_family_error_catalog_2026-08-06.md",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Do not sort_keys: mode-count object order is frequency-ranked.
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.report}")
    for surface, block in artifact["surfaces"].items():
        for family, fam in block["families"].items():
            print(
                f"  {surface}.{family}: imperfect_modes="
                f"{list(fam['pooled_imperfect_mode_counts'])}"
            )


if __name__ == "__main__":
    main()
