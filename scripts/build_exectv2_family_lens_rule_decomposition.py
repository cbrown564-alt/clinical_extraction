#!/usr/bin/env python3
"""Leave-one-out decomposition of the ExECTv2 family lens rules.

No model calls. Each arm is a study-local monkeypatch around the ordered replay
of the retained structured sidecars. Production code and prompt construction
remain unchanged.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections import Counter
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import patch

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses import (
    diagnosis as diagnosis_lens,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as diagnosis_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
    clinical_headline_scores,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/exectv2_family_lens_rule_decomposition_protocol_2026-08-10.md"
OUT = REPO_ROOT / "experiments" / "exectv2_family_lens_rule_decomposition_20260810.json"
REPORT = REPO_ROOT / "docs/research/exectv2/exectv2_family_lens_rule_decomposition_2026-08-10.md"
FAMILIES = ("Diagnosis", "SeizureFrequency", "Investigations")

RULES: dict[str, tuple[str, ...]] = {
    "Diagnosis": (
        "diagnosis_heading_recovery",
        "diagnosis_alias_rewrites",
        "diagnosis_residual_rewrites",
        "diagnosis_noise_drop",
        "diagnosis_attribute_repairs",
        "diagnosis_residual_additions",
        "diagnosis_generic_epilepsy_companion",
    ),
    "SeizureFrequency": (
        "sf_convention_rewrites",
        "sf_convention_noise_drop",
        "sf_residual_additions",
        "sf_unknown_suppression.drug_response_scope",
        "sf_unknown_suppression.contextual_or_historical_change",
    ),
    "Investigations": (
        "investigation_attribute_repairs",
        "investigation_noise_drop",
        "investigation_residual_additions",
    ),
}

_STAGE_PATH = REPO_ROOT / "scripts/build_exectv2_hybrid_stage_ablation.py"
_SPEC = importlib.util.spec_from_file_location("exect_hybrid_stage_ablation", _STAGE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import replay helpers from {_STAGE_PATH}")
stage = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(stage)


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _without_alias_rewrites(text: str, evidence: str) -> str | None:
    del text, evidence
    return None


def _without_residual_rewrites(text: str, evidence: str) -> str | None:
    surface = normalize_phrase(text)
    target = diagnosis_dictionary.DIAGNOSIS_SURFACE_CONVENTION_REPAIRS.get(surface)
    if target is not None:
        return target
    for pattern, target in diagnosis_dictionary._PREFIX_DIAGNOSIS_CONVENTION_REPAIRS:
        if pattern.search(" ".join(part for part in (text, evidence) if part)):
            return target
    return diagnosis_dictionary.DIAGNOSIS_CONVENTION_ALIAS_REPAIRS.get(
        canonicalize_diagnosis_concept(text)
    )


@contextmanager
def disabled_rule(rule: str | None) -> Iterator[None]:
    """Disable one rule while preserving every other current implementation."""

    if rule is None:
        yield
        return
    with ExitStack() as stack:
        if rule == "diagnosis_heading_recovery":
            stack.enter_context(
                patch.object(
                    diagnosis_lens,
                    "_focal_epilepsy_heading_findings",
                    lambda *a, **k: (),
                    create=True,
                )
            )
        elif rule == "diagnosis_alias_rewrites":
            stack.enter_context(
                patch.object(sd, "diagnosis_convention_target", _without_alias_rewrites)
            )
        elif rule == "diagnosis_residual_rewrites":
            stack.enter_context(
                patch.object(sd, "diagnosis_convention_target", _without_residual_rewrites)
            )
        elif rule == "diagnosis_noise_drop":
            stack.enter_context(
                patch.object(sd, "is_diagnosis_convention_noise", lambda *a, **k: False)
            )
        elif rule == "diagnosis_attribute_repairs":
            stack.enter_context(
                patch.object(
                    sd,
                    "diagnosis_convention_attribute_repairs",
                    lambda text, *, evidence, attributes: {
                        str(key): str(value) for key, value in attributes.items()
                    },
                )
            )
        elif rule == "diagnosis_residual_additions":
            stack.enter_context(
                patch.object(sd, "diagnosis_residual_additions", lambda *a, **k: [])
            )
        elif rule == "diagnosis_generic_epilepsy_companion":
            stack.enter_context(
                patch.object(
                    sd,
                    "should_add_generic_epilepsy_companion",
                    lambda *a, **k: False,
                    create=True,
                )
            )
        elif rule == "sf_convention_rewrites":
            stack.enter_context(patch.object(sd, "sf_convention_rewrite", lambda *a, **k: None))
        elif rule == "sf_convention_noise_drop":
            stack.enter_context(patch.object(sd, "is_sf_convention_noise", lambda *a, **k: False))
        elif rule == "sf_residual_additions":
            stack.enter_context(patch.object(sd, "sf_residual_additions", lambda *a, **k: []))
        elif rule.startswith("sf_unknown_suppression."):
            original = sf_unknown_suppression._suppression_rule

            def without_selected_suppression(mention: dict[str, Any]) -> str | None:
                found = original(mention)
                if found == rule:
                    return None
                return found

            stack.enter_context(
                patch.object(
                    sf_unknown_suppression,
                    "_suppression_rule",
                    without_selected_suppression,
                )
            )
        elif rule == "investigation_attribute_repairs":
            stack.enter_context(
                patch.object(
                    sd,
                    "investigation_convention_attribute_repairs",
                    lambda text, *, evidence, attributes: {
                        str(key): str(value) for key, value in attributes.items()
                    },
                )
            )
        elif rule == "investigation_noise_drop":
            stack.enter_context(
                patch.object(sd, "is_investigation_convention_noise", lambda *a, **k: False)
            )
        elif rule == "investigation_residual_additions":
            stack.enter_context(
                patch.object(sd, "investigation_residual_additions", lambda *a, **k: [])
            )
        else:
            raise ValueError(f"unknown rule arm: {rule}")
        yield


def _family_keys(replay: dict[str, Any], family: str) -> list[str]:
    return list(replay["band_keys"]["evidence_gate"].get(family, []))


def _family_mentions(replay: dict[str, Any], family: str) -> list[dict[str, Any]]:
    return [
        dict(mention)
        for mention in replay.get("final_mentions", [])
        if str(mention.get("entity", "")) == family
    ]


def _gold_keys(gold_mentions: list[dict[str, Any]], family: str) -> list[str]:
    return list(
        stage.headline_keys(
            {"gold_mentions": gold_mentions, "predicted_mentions": []},
            family,
            field="gold_mentions",
        )
    )


def _exact(gold: list[str], predicted: list[str]) -> bool:
    return Counter(gold) == Counter(predicted)


def _mode(gold: list[str], predicted: list[str]) -> str:
    return stage._mode(gold, predicted)


def _micro(gold_by_cell: list[list[str]], pred_by_cell: list[list[str]]) -> dict[str, float]:
    tp = fp = fn = 0
    for gold, pred in zip(gold_by_cell, pred_by_cell, strict=True):
        g, p = Counter(gold), Counter(pred)
        hit = sum((g & p).values())
        tp += hit
        fp += sum(p.values()) - hit
        fn += sum(g.values()) - hit
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "micro_f1": round(f1, 4),
    }


def _clinical_f1(cells: list[dict[str, Any]], family: str, prediction_field: str) -> float:
    gold_letters = [
        ExectLetter(
            letter_id=str(cell["letter_id"]),
            note_text="",
            annotations=tuple(annotation_from_mapping(m) for m in cell["gold_mentions"]),
        )
        for cell in cells
    ]
    predicted_letters = [
        ExectLetter(
            letter_id=str(cell["letter_id"]),
            note_text="",
            annotations=tuple(annotation_from_mapping(m) for m in cell[prediction_field]),
        )
        for cell in cells
    ]
    return round(float(clinical_headline_scores(gold_letters, predicted_letters)[family]["f1"]), 4)


def _score_rule(rule: str, family: str, cells: list[dict[str, Any]]) -> dict[str, Any]:
    changed = rescue = harm = neutral = 0
    examples: dict[str, list[dict[str, Any]]] = {"rescue": [], "harm": []}
    for cell in cells:
        gold = cell["gold_keys"]
        before = cell["baseline_keys"]
        after = cell["candidate_keys"]
        if Counter(before) == Counter(after):
            continue
        changed += 1
        before_exact = _exact(gold, before)
        after_exact = _exact(gold, after)
        effect = "neutral_change"
        if after_exact and not before_exact:
            rescue += 1
            effect = "rescue"
        elif before_exact and not after_exact:
            harm += 1
            effect = "harm"
        else:
            neutral += 1
        if effect in examples and len(examples[effect]) < 2:
            examples[effect].append(
                {
                    "model_slug": cell["model_slug"],
                    "letter_id": cell["letter_id"],
                    "before_mode": _mode(gold, before),
                    "after_mode": _mode(gold, after),
                    "baseline_keys": before,
                    "candidate_keys": after,
                }
            )

    by_model: dict[str, Any] = {}
    for model in sorted({str(cell["model_slug"]) for cell in cells}):
        subset = [cell for cell in cells if cell["model_slug"] == model]
        baseline_micro = _micro(
            [cell["gold_keys"] for cell in subset],
            [cell["baseline_keys"] for cell in subset],
        )
        candidate_micro = _micro(
            [cell["gold_keys"] for cell in subset],
            [cell["candidate_keys"] for cell in subset],
        )
        baseline_exact = sum(_exact(c["gold_keys"], c["baseline_keys"]) for c in subset)
        candidate_exact = sum(_exact(c["gold_keys"], c["candidate_keys"]) for c in subset)
        by_model[model] = {
            "n": len(subset),
            "baseline_exact_rate": round(baseline_exact / len(subset), 4),
            "candidate_exact_rate": round(candidate_exact / len(subset), 4),
            "exactness_delta": round((candidate_exact - baseline_exact) / len(subset), 4),
            "baseline_micro": baseline_micro,
            "candidate_micro": candidate_micro,
            "micro_f1_delta": round(candidate_micro["micro_f1"] - baseline_micro["micro_f1"], 4),
            "sign": (
                "positive"
                if candidate_micro["micro_f1"] > baseline_micro["micro_f1"]
                else "negative"
                if candidate_micro["micro_f1"] < baseline_micro["micro_f1"]
                else "flat"
            ),
        }

    baseline_micro = _micro(
        [cell["gold_keys"] for cell in cells],
        [cell["baseline_keys"] for cell in cells],
    )
    candidate_micro = _micro(
        [cell["gold_keys"] for cell in cells],
        [cell["candidate_keys"] for cell in cells],
    )
    baseline_exact = sum(_exact(c["gold_keys"], c["baseline_keys"]) for c in cells)
    candidate_exact = sum(_exact(c["gold_keys"], c["candidate_keys"]) for c in cells)
    return {
        "family": family,
        "rule": rule,
        "n_cells": len(cells),
        "cells_changed": changed,
        "rescue_cells": rescue,
        "harm_cells": harm,
        "neutral_changed_cells": neutral,
        "baseline_exact_rate": round(baseline_exact / len(cells), 4),
        "candidate_exact_rate": round(candidate_exact / len(cells), 4),
        "exactness_delta": round((candidate_exact - baseline_exact) / len(cells), 4),
        "baseline_micro": baseline_micro,
        "candidate_micro": candidate_micro,
        "micro_f1_delta": round(candidate_micro["micro_f1"] - baseline_micro["micro_f1"], 4),
        "baseline_clinical_f1": _clinical_f1(cells, family, "baseline_mentions"),
        "candidate_clinical_f1": _clinical_f1(cells, family, "candidate_mentions"),
        "by_model": by_model,
        "examples": examples,
    }


def _prompt_consumer_audit() -> dict[str, Any]:
    return {
        "prompt_file": (
            "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/"
            "pipelines/key_entities_structured/prompt_content.py"
        ),
        "consumers": {
            "diagnosis_residual_additions": "high_priority_evidence_ledger_for_letter lines 71-77",
            "sf_residual_additions": "candidate residual adapter consumed at lines 78-84",
            "investigation_residual_additions": (
                "high_priority_evidence_ledger_for_letter lines 92-98"
            ),
        },
        "decision": (
            "Keep prompt-side residual providers unchanged; ablate only "
            "assembly-side lens consumption."
        ),
    }


def build_artifact() -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    cells_by_family_rule: dict[tuple[str, str], list[dict[str, Any]]] = {
        (family, rule): [] for family, rules in RULES.items() for rule in rules
    }
    replayable = 0
    unreplayable = Counter()

    for slug, _display in stage.hs.MODEL_SPECS:
        main_path = stage.hs.EXECT_JSONL[slug]
        main_rows = {str(row["letter_id"]): row for row in stage.hs._read_jsonl(main_path)}
        structured_path = main_path.with_name(main_path.name.replace(".jsonl", "_structured.jsonl"))
        for structured_row in stage.hs._read_jsonl(structured_path):
            letter_id = str(structured_row["letter_id"])
            letter = letters.get(letter_id)
            main_row = main_rows.get(letter_id)
            if letter is None or main_row is None:
                unreplayable["missing_letter_or_main_row"] += 1
                continue
            gold_mentions = list(main_row.get("gold_mentions") or [])
            with disabled_rule(None):
                baseline = stage.replay_letter(structured_row, letter, gold_mentions=gold_mentions)
            if not baseline.get("replayable"):
                unreplayable[str(baseline.get("reason", "unknown"))] += 1
                continue
            replayable += 1
            for family, rules in RULES.items():
                base_keys = _family_keys(baseline, family)
                base_mentions = _family_mentions(baseline, family)
                gold_keys = _gold_keys(gold_mentions, family)
                for rule in rules:
                    with disabled_rule(rule):
                        candidate = stage.replay_letter(
                            structured_row, letter, gold_mentions=gold_mentions
                        )
                    if not candidate.get("replayable"):
                        unreplayable[f"candidate:{rule}"] += 1
                        continue
                    cells_by_family_rule[(family, rule)].append(
                        {
                            "model_slug": slug,
                            "letter_id": letter_id,
                            "gold_mentions": gold_mentions,
                            "gold_keys": gold_keys,
                            "baseline_keys": base_keys,
                            "candidate_keys": _family_keys(candidate, family),
                            "baseline_mentions": base_mentions,
                            "candidate_mentions": _family_mentions(candidate, family),
                        }
                    )

    rule_results = {
        f"{family}:{rule}": _score_rule(rule, family, cells)
        for (family, rule), cells in cells_by_family_rule.items()
    }
    return {
        "schema_version": "exectv2.family_lens_rule_decomposition.v1",
        "date": "2026-08-10",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "development_cell_ledger_with_permitted_examples",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained structured sidecars",
        "policy": {
            "diagnosis": "default",
            "prescription": "default",
            "sf_projection": "combined",
        },
        "scorer": "clinical-headline family unit-key exactness and clinical fact F1",
        "replayable_cells": replayable,
        "unreplayable": dict(unreplayable),
        "rules": RULES,
        "prompt_consumer_audit": _prompt_consumer_audit(),
        "results": rule_results,
        "selection_rule": {
            "eligible_if": (
                "exactness delta >= 0 and micro-F1 delta >= -0.005 "
                "with no evidence-gate regression"
            ),
            "zero_fire": "eligible for dead-code removal only after prompt-consumer audit",
            "sf_unknown_note": "suppression remains proxy-risk and requires mechanism review",
        },
        "claim_boundary": (
            "Development ExECTv2 leave-one-out decomposition on dev140 across six retained "
            "structured sidecars. Per-cell family scoring, no model calls, prompt-side "
            "residual providers preserved. Not holdout evidence or clinical validation."
        ),
        "git": _git_note(),
    }


def _fmt_delta(value: float) -> str:
    return f"{value:+.4f}"


def render_report(artifact: dict[str, Any]) -> str:
    lines = [
        "# ExECTv2 Diagnosis, SeizureFrequency, and Investigations rule decomposition",
        "",
        "Date: 2026-08-10  ",
        "Status: development leave-one-out no-call replay  ",
        "Protocol: [predeclared protocol]("
        "exectv2_family_lens_rule_decomposition_protocol_2026-08-10.md)  ",
        "Artifact: `experiments/exectv2_family_lens_rule_decomposition_20260810.json`",
        "",
        "## Plain answer",
        "",
        f"The replay covers **{artifact['replayable_cells']}** retained model×letter "
        "cells. Each rule is removed in isolation and scored at its own family "
        "cell surface; no prompt-side residual provider is changed.",
        "",
        "## Leave-one-out results",
        "",
        "| Family | Rule removed | Cells changed | Rescue | Harm | Exactness Δ | "
        "Micro-F1 Δ | Clinical F1 Δ |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _key, result in artifact["results"].items():
        f1_delta = result["candidate_clinical_f1"] - result["baseline_clinical_f1"]
        lines.append(
            f"| `{result['family']}` | `{result['rule']}` | "
            f"{result['cells_changed']} | {result['rescue_cells']} | "
            f"{result['harm_cells']} | {_fmt_delta(result['exactness_delta'])} | "
            f"{_fmt_delta(result['micro_f1_delta'])} | {_fmt_delta(f1_delta)} |"
        )
    lines.extend(
        [
            "",
            "Positive deltas mean the rule-removal arm is better. `Cells changed` "
            "is the observable fire count for the leave-one-out arm; zero is a "
            "simplification result only when prompt construction remains intact.",
            "",
            "## Per-model sign checks",
            "",
        ]
    )
    for key, result in artifact["results"].items():
        signs = ", ".join(
            f"`{model}` {_fmt_delta(payload['micro_f1_delta'])} ({payload['sign']})"
            for model, payload in result["by_model"].items()
        )
        lines.append(f"- `{key}`: {signs}")
    lines.extend(
        [
            "",
            "## Prompt-consumer audit",
            "",
            "The residual providers remain in prompt construction. The study "
            "ablates only their later assembly-side consumption:",
            "",
            "- Diagnosis residual additions: `prompt_content.py` lines 71–77.",
            "- SeizureFrequency residual candidates: `prompt_content.py` lines 78–84.",
            "- Investigations residual additions: `prompt_content.py` lines 92–98.",
            "",
            "This preserves the retained model sidecars and avoids invalidating "
            "every prompt-content artifact when a lens rule is removed.",
            "",
            "## Development decision boundary",
            "",
            "Only arms meeting the predeclared exactness and micro-F1 rule are "
            "eligible for a frozen `test59` deletion bundle. SF unknown suppression "
            "remains a proxy-risk diagnostic even when its aggregate delta is "
            "positive. The holdout runner must be predeclared before scoring and "
            "must publish aggregate-only output.",
            "",
            "## Claim boundary",
            "",
            artifact["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()
    artifact = build_artifact()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    for key, result in artifact["results"].items():
        print(
            f"{key}: changed={result['cells_changed']} rescue={result['rescue_cells']} "
            f"harm={result['harm_cells']} exact_delta={result['exactness_delta']:+.4f} "
            f"micro_f1_delta={result['micro_f1_delta']:+.4f}"
        )


if __name__ == "__main__":
    main()
