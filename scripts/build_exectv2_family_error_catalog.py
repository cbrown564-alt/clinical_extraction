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


def _exact_band(block: dict[str, Any]) -> str:
    rates = [
        model["letter_exact_rate"]
        for model in block["models"].values()
        if model["letter_exact_rate"] is not None
    ]
    if not rates:
        return "n/a"
    return f"{min(rates):.2f}–{max(rates):.2f}"


def _top_modes(counts: dict[str, int], limit: int = 3) -> str:
    if not counts:
        return "_(none)_"
    return ", ".join(
        f"`{mode}` ({count})" for mode, count in list(counts.items())[:limit]
    )


def _mode_delta_rows(
    llm_counts: dict[str, int],
    hybrid_counts: dict[str, int],
    *,
    min_either: int = 8,
) -> list[tuple[str, int, int, int]]:
    modes = sorted(
        set(llm_counts) | set(hybrid_counts),
        key=lambda mode: -(llm_counts.get(mode, 0) + hybrid_counts.get(mode, 0)),
    )
    rows: list[tuple[str, int, int, int]] = []
    for mode in modes:
        llm_n = int(llm_counts.get(mode, 0))
        hybrid_n = int(hybrid_counts.get(mode, 0))
        if max(llm_n, hybrid_n) < min_either:
            continue
        rows.append((mode, llm_n, hybrid_n, hybrid_n - llm_n))
    return rows


def _short_token(token: str) -> str:
    text = token.strip()
    # ("Diagnosis", "focal epilepsy") or ("ordinary", "lamotrigine", ...)
    if text.startswith("(") and "'" in text:
        parts = [part for part in text.split("'") if part.strip() not in {"", ",", ", ", "(", ")"}]
        if text.startswith("('Diagnosis'") and len(parts) >= 2:
            return parts[1]
        if text.startswith("('ordinary'") and len(parts) >= 2:
            drug = parts[1]
            dose = parts[2] if len(parts) > 2 else ""
            unit = parts[3] if len(parts) > 3 else ""
            return f"{drug} {dose}{unit}".strip()
        if len(parts) >= 2 and parts[0] in {"EEG", "MRI"}:
            return f"{parts[0]} {' '.join(parts[1:3])}".strip()
    if len(text) > 40:
        return text[:39] + "…"
    return text


FAMILY_BLURBS: dict[str, str] = {
    "Diagnosis": (
        "Inventory problem. Rules convert many substitutions into exact "
        "letters (−167 `substituted_or_mixed`) but can leave a larger "
        "`extra_only` residue (+45)."
    ),
    "SeizureFrequency": (
        "Practical floor on both surfaces. Rules cut some empty-gold "
        "spurious and extra `active-rate`, but missed-state inventory stays."
    ),
    "Prescription": (
        "High without rules; rules are not uniformly helpful—consensus "
        "imperfect widens as `missed_all` / `missed_only` rise."
    ),
    "Investigations": (
        "Same letter-exact modes on both surfaces for this roster "
        "(rules are a no-op here); residual is mostly missed inventory."
    ),
}


def render_report(artifact: dict[str, Any]) -> str:
    llm = artifact["surfaces"]["llm"]["families"]
    hybrid = artifact["surfaces"]["llm_with_rules"]["families"]

    lines: list[str] = [
        "# ExECTv2 four-family error catalog",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development catalog with pipeline ablation reading  ",
        "Protocol: [exect family error catalog protocol]"
        "(exectv2_family_error_catalog_protocol_2026-08-06.md)  ",
        "Parent: [category-cut performance]"
        "(six_model_category_cut_performance_2026-08-06.md)  ",
        "Companions: [task-shape framework]"
        "(task_shape_framework_2026-08-06.md), "
        "[hard-slice modes](six_model_hard_slice_error_modes_2026-08-06.md), "
        "[Gan error catalog](gan2026_category_error_catalog_2026-08-06.md)  ",
        f"Artifact: [`experiments/exectv2_family_error_catalog_{DATE_STAMP}.json`]"
        f"(../../experiments/exectv2_family_error_catalog_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        "Family errors are inventory shapes, not a single low score. On the",
        "model lane, Diagnosis is mostly wrong-set / extra concepts;",
        "SeizureFrequency adds empty-gold spurious `active-rate`; Prescription",
        "and Investigations are smaller missed/extra problems.",
        "",
        "Family rules then do **different jobs by family**:",
        "",
        "1. **Diagnosis** — large rescue: substitutions collapse into exact",
        "   letters; empty-gold spurious nearly vanishes.",
        "2. **SeizureFrequency** — partial rescue: fewer empty-gold over-reads",
        "   and less extra `active-rate`; missed states remain the floor.",
        "3. **Prescription** — can **hurt**: consensus imperfect widens as",
        "   rules drop drugs that the model lane had right.",
        "4. **Investigations** — no change on this roster (rules leave the",
        "   lane alone).",
        "",
        "## Why this document exists",
        "",
        "The [category-cut report]"
        "(six_model_category_cut_performance_2026-08-06.md) shows **which**",
        "families move under rules (F1). This catalog shows **how** at letter",
        "exactness: which imperfect modes dominate, and whether family rules",
        "erase, reshape, or amplify them. Full per-model tables and every",
        "retained example live in the JSON; this page is the readable ablation.",
        "",
        "## Observable ablation layers",
        "",
        "No new calls. Same retained `dev140` letters. Two prediction fields we",
        "can already separate:",
        "",
        "```mermaid",
        "flowchart LR",
        '  lane["1. Model lane<br/>raw_lane_mentions"]',
        '  rules["2. After family rules<br/>predicted_mentions"]',
        "  lane --> rules",
        "```",
        "",
        "| Layer | What it is | What it typically does to errors |",
        "| --- | --- | --- |",
        "| **1. Model lane** | One-call mentions before family transforms "
        "(`raw_lane_mentions`) | Diagnosis substitutions / extras; SF "
        "empty-gold `active-rate`; smaller Rx / Investigations misses |",
        "| **2. After family rules** | Mentions after deterministic family "
        "transforms (`predicted_mentions`) | Diagnosis inventory rescue; SF "
        "precision trim; Prescription drop risk; Investigations unchanged |",
        "",
        "This is an ablation over **saved surfaces**, not a leave-one-rule-out",
        "factorial. Category-cut **family F1** remains the competence metric;",
        "letter exactness here is the mechanism lens.",
        "",
        "## Four cases that explain the catalog",
        "",
        "Read these first. Green end-state = letter-exact for that family;",
        "red = still imperfect. Paired Sol letters unless noted.",
        "",
        "### A. Diagnosis rules strip a spurious extra",
        "",
        "Model lane adds `febrile seizures`; family rules drop it and match gold.",
        "",
        "```mermaid",
        "flowchart LR",
        '  gold["Gold<br/>focal to bilateral<br/>convulsive seizures"]',
        '  lane["1. Model lane<br/>+ febrile seizures"]',
        '  hyb["2. Family rules<br/>gold set only"]',
        "  gold -.-> lane",
        "  lane -->|drops extra| hyb",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class gold gold;",
        "  class lane bad;",
        "  class hyb ok;",
        "```",
        "",
        "EA0009 / Sol (`extra_only` → exact). This is the Diagnosis mass story:",
        "−167 `substituted_or_mixed`, +156 `correct_nonempty` pooled.",
        "",
        "### B. SeizureFrequency rules drop an extra active-rate",
        "",
        "Gold is seizure-free; the lane also emits `active-rate`.",
        "",
        "```mermaid",
        "flowchart LR",
        '  gold["Gold<br/>seizure-free"]',
        '  lane["1. Model lane<br/>active-rate + seizure-free"]',
        '  hyb["2. Family rules<br/>seizure-free"]',
        "  gold -.-> lane",
        "  lane -->|drops active-rate| hyb",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class gold gold;",
        "  class lane bad;",
        "  class hyb ok;",
        "```",
        "",
        "EA0142 / Sol. Extra `active-rate` tokens fall 201→141 pooled; this is",
        "precision help, not a solved inventory floor.",
        "",
        "### C. Two residuals rules do not clear",
        "",
        "Left: empty-gold SF still emits `active-rate` after rules (Sol).",
        "Right: Investigations miss is unchanged by rules.",
        "",
        "```mermaid",
        "flowchart TB",
        "  subgraph sfPersist[\"SF empty-gold tax — still spurious\"]",
        "    direction LR",
        '    sg["Gold<br/>no SF facts"]',
        '    sr["Lane / rules<br/>active-rate"]',
        "    sg -.-> sr",
        "  end",
        "  subgraph invFlat[\"Investigations — rules are a no-op\"]",
        "    direction LR",
        '    ig["Gold<br/>EEG + normal MRI"]',
        '    ir["Lane = rules<br/>MRI only"]',
        "    ig -.-> ir",
        "  end",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class sg,ig gold;",
        "  class sr,ir bad;",
        "```",
        "",
        "EA0092 / Sol (SF) and EA0102 / mini (Investigations `missed_only`).",
        "Empty-gold SF still falls for some weaker models under rules; Sol’s",
        "empty-gold band does not.",
        "",
        "### D. Prescription rules can drop a correct drug",
        "",
        "Model lane matches gold; family rules wipe the prescription set.",
        "",
        "```mermaid",
        "flowchart LR",
        '  gold["Gold<br/>lamotrigine 75 mg"]',
        '  lane["1. Model lane<br/>lamotrigine 75 mg"]',
        '  hyb["2. Family rules<br/>empty / missed_all"]',
        "  gold -.-> lane",
        "  lane -->|drops drug| hyb",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class gold gold;",
        "  class lane ok;",
        "  class hyb bad;",
        "```",
        "",
        "EA0008 / Sol. Consensus imperfect rises 6→14; pooled `missed_all`",
        "+17. Rules are not a free upgrade on Prescription.",
        "",
        "## Ablation map: which step addresses which mode",
        "",
        "```mermaid",
        "flowchart TB",
        '  lane["Model lane"]',
        '  rules["Family rules"]',
        "  lane --> rules",
        '  rules -->|erases| r1["Diagnosis substitutions<br/>SF empty-gold / active-rate"]',
        '  rules -->|amplifies| r2["Prescription missed_all / missed_only"]',
        '  rules -->|leaves| r3["SF missed states<br/>Investigations inventory"]',
        "```",
        "",
        "| Error shape | Main families | Family rules |",
        "| --- | --- | --- |",
        "| Wrong / mixed Diagnosis inventory "
        "(`substituted_or_mixed`) | Diagnosis | "
        "**Clears** most (−167); lifts `correct_nonempty` (+156) |",
        "| Extra Diagnosis concepts (`extra_only`) | Diagnosis | "
        "Mixed: some stripped (case A), pooled count can **rise** (+45) "
        "as substitutions resolve into extras |",
        "| Empty-gold spurious SF | SeizureFrequency | "
        "**Cuts** (−30 pooled); Sol often still emits `active-rate` |",
        "| Extra SF `active-rate` | SeizureFrequency | "
        "**Cuts** token mass (201→141); residual remains |",
        "| Missed SF states | SeizureFrequency | "
        "Mostly **leaves** (`missed_only` +7; `missed_all` unchanged) |",
        "| Prescription drops | Prescription | "
        "**Amplifies** misses (`missed_all` +17, `missed_only` +21) |",
        "| Investigations misses / extras | Investigations | "
        "**No-op** on this roster (all mode deltas 0) |",
        "",
        "## Rules lift by family (llm → hybrid modes)",
        "",
        "Pooled six-model letter cells. Exact bands are letter-exact rates",
        "(mechanism lens), not category-cut F1.",
        "",
        "| Family | llm exact | hybrid exact | Consensus imperfect "
        "llm→hyb | Dominant llm imperfect | What rules do |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]

    for family in FAMILIES:
        llm_block = llm[family]
        hybrid_block = hybrid[family]
        cons = (
            f"{llm_block['consensus_imperfect_all_six']['n']}→"
            f"{hybrid_block['consensus_imperfect_all_six']['n']}"
        )
        lines.append(
            f"| {family} | {_exact_band(llm_block)} | {_exact_band(hybrid_block)} | "
            f"{cons} | {_top_modes(llm_block['pooled_imperfect_mode_counts'], 2)} | "
            f"{FAMILY_BLURBS[family]} |"
        )

    lines.extend(
        [
            "",
            "### Mode deltas worth remembering",
            "",
        ]
    )

    for family in FAMILIES:
        rows = _mode_delta_rows(
            llm[family]["pooled_mode_counts"],
            hybrid[family]["pooled_mode_counts"],
            min_either=10,
        )
        # Investigations is all zeros — still show imperfect modes once.
        if family == "Investigations":
            lines.extend(
                [
                    "#### Investigations",
                    "",
                    "Every pooled mode count is identical on `llm` and",
                    "`llm_with_rules` for this six-model roster.",
                    "",
                ]
            )
            continue
        if not rows:
            continue
        lines.extend(
            [
                f"#### {family}",
                "",
                "| Mode | llm | hybrid | Δ |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for mode, llm_n, hybrid_n, delta in rows:
            lines.append(f"| `{mode}` | {llm_n} | {hybrid_n} | {delta:+d} |")
        lines.append("")

    # SF token lens
    sf_llm_extra = llm["SeizureFrequency"]["pooled_extra_tokens_top"]
    sf_hyb_extra = hybrid["SeizureFrequency"]["pooled_extra_tokens_top"]
    sf_llm_miss = llm["SeizureFrequency"]["pooled_missed_tokens_top"]
    sf_hyb_miss = hybrid["SeizureFrequency"]["pooled_missed_tokens_top"]
    lines.extend(
        [
            "### SeizureFrequency state tokens (pooled)",
            "",
            "| State | llm missed | llm extra | hybrid missed | hybrid extra |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for state in ("active-rate", "seizure-free", "unknown"):
        lines.append(
            f"| `{state}` | {sf_llm_miss.get(state, 0)} | "
            f"{sf_llm_extra.get(state, 0)} | {sf_hyb_miss.get(state, 0)} | "
            f"{sf_hyb_extra.get(state, 0)} |"
        )
    lines.extend(
        [
            "",
            "Extra `active-rate` is the distinctive precision pressure; rules",
            "shrink it without clearing missed `unknown` / inventory under-fill.",
            "",
            "## Family cards",
            "",
            "Letter-exact bands are six-model min–max on `dev140`. Mode counts",
            "are pooled letter×model cells. Mechanism pictures are in",
            "[Four cases](#four-cases-that-explain-the-catalog) above.",
            "",
        ]
    )

    for family in FAMILIES:
        llm_block = llm[family]
        hybrid_block = hybrid[family]
        lines.extend(
            [
                f"### {family}",
                "",
                FAMILY_BLURBS[family],
                "",
                "| Surface | Exact band | Consensus imperfect | Top imperfect |",
                "| --- | --- | ---: | --- |",
                f"| `llm` | {_exact_band(llm_block)} | "
                f"{llm_block['consensus_imperfect_all_six']['n']} | "
                f"{_top_modes(llm_block['pooled_imperfect_mode_counts'])} |",
                f"| `llm_with_rules` | {_exact_band(hybrid_block)} | "
                f"{hybrid_block['consensus_imperfect_all_six']['n']} | "
                f"{_top_modes(hybrid_block['pooled_imperfect_mode_counts'])} |",
                "",
            ]
        )
        # Compact top tokens for Diagnosis / SF only
        if family in {"Diagnosis", "SeizureFrequency"}:
            lines.extend(
                [
                    "Top missed / extra tokens on `llm` (pooled):",
                    "",
                    "| Direction | Token | Count |",
                    "| --- | --- | ---: |",
                ]
            )
            for token, count in list(llm_block["pooled_missed_tokens_top"].items())[:5]:
                lines.append(f"| missed | `{_short_token(token)}` | {count} |")
            for token, count in list(llm_block["pooled_extra_tokens_top"].items())[:5]:
                lines.append(f"| extra | `{_short_token(token)}` | {count} |")
            lines.append("")

    lines.extend(
        [
            "## How to explore further",
            "",
            "| Need | Where |",
            "| --- | --- |",
            "| Per-model exact rates and mode counts | JSON "
            f"`surfaces.*.families.*.models` in "
            f"[`exectv2_family_error_catalog_{DATE_STAMP}.json`]"
            f"(../../experiments/exectv2_family_error_catalog_{DATE_STAMP}.json) |",
            "| Up to two examples per imperfect mode × surface | "
            "JSON `examples_by_mode` |",
            "| SF floor token lens and rescue context | "
            "[hard-slice error modes]"
            "(six_model_hard_slice_error_modes_2026-08-06.md) |",
            "| Family F1 competence (x/y/z) | "
            "[category-cut](six_model_category_cut_performance_2026-08-06.md) |",
            "| Peer Gan ablation catalog | "
            "[Gan category error catalog]"
            "(gan2026_category_error_catalog_2026-08-06.md) |",
            "| Regenerate this page + artifact | "
            "`python scripts/build_exectv2_family_error_catalog.py` |",
            "",
            "## Method",
            "",
            "- Split: ExECT `dev140`. Surfaces: `llm` (`raw_lane_mentions`) and",
            "  `llm_with_rules` (`predicted_mentions`).",
            "- Letter metric: clinical-headline unit-key multiset exactness",
            "  **per family**.",
            "- Imperfect modes: `empty_gold_spurious`, `missed_all`,",
            "  `missed_only`, `extra_only`, `substituted_or_mixed`.",
            "- Ablation: model lane vs after family rules on retained rows.",
            "- Examples in JSON: up to two per imperfect mode; consensus + Sol",
            "  preferred; saved mention texts only; holdout sealed.",
            "",
            "## Claim boundary",
            "",
            "- Development ExECT four-family error catalog on `dev140`.",
            "- Letter exactness is a mechanism lens; category-cut family F1",
            "  remains the competence metric.",
            "- Ablation is across retained surfaces, not a full rule factorial.",
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
