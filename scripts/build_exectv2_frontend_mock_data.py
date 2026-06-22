"""Build static ExECTv2 frontend review data from assembly artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MOCK_ROOT = ROOT / "frontend" / "public" / "mock-data"
EXECTV2_ROOT = MOCK_ROOT / "exectv2"
ARTIFACT_ROOT = MOCK_ROOT / "artifacts"

FAMILIES = ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"]


RUN_SPECS: list[dict[str, Any]] = [
    {
        "run_id": "exectv2_holistic_finding_assembly_v08_dev140",
        "label": "v08 dev140 control",
        "model": "openai/gpt-4.1-mini",
        "architecture_family": "holistic_finding_assembly",
        "pipeline_family": "exectv2_holistic_finding_assembly",
        "split": "dev140",
        "decision": "control",
        "promotion_decision": "performance-control",
        "claim_boundary": "Dev-only component-attributed architecture evidence.",
        "scorer_view": "headline_target",
        "config_path": "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml",
        "report_path": "docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md",
        "summary_path": "experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json",
        "assembly_jsonl_path": "experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl",
        "text_source_paths": [
            "experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl"
        ],
    },
    {
        "run_id": "exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140",
        "label": "v09 partial hybrid",
        "model": "openai/gpt-4.1-mini",
        "architecture_family": "partial_hybrid_simplification",
        "pipeline_family": "exectv2_holistic_finding_assembly",
        "split": "dev140",
        "decision": "control",
        "promotion_decision": "simplicity-control",
        "claim_boundary": "Dev-only simplification evidence.",
        "scorer_view": "headline_target",
        "config_path": "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml",
        "report_path": "docs/experiments/exectv2/key_entities/exectv2_v09_single_gpt_simplification_study_dev140_20260621.md",
        "summary_path": "experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json",
        "assembly_jsonl_path": "experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.jsonl",
        "text_source_paths": [
            "experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl"
        ],
    },
    {
        "run_id": "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140",
        "label": "DeepSeek v0.9.16 dev140",
        "model": "deepseek/deepseek-chat",
        "architecture_family": "single_model_dictionary_reparse",
        "pipeline_family": "exectv2_holistic_finding_assembly",
        "split": "dev140",
        "decision": "diagnostic",
        "promotion_decision": "do-not-promote",
        "claim_boundary": "Diagnostic no-call same-raw DeepSeek v0.9.10→v0.9.16 dictionary reparse, dev140.",
        "scorer_view": "headline_target",
        "config_path": "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140.yaml",
        "report_path": "experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.md",
        "summary_path": "experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json",
        "assembly_jsonl_path": "experiments/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl",
        "text_source_paths": [
            "experiments/exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl",
            "experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl",
        ],
    },
    {
        "run_id": "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140",
        "label": "Qwen v0.9.22 dev140",
        "model": "ollama_chat/qwen3.6:35b",
        "architecture_family": "qwen_compact_residual_repair",
        "pipeline_family": "exectv2_holistic_finding_assembly",
        "split": "dev140",
        "decision": "diagnostic",
        "promotion_decision": "do-not-promote",
        "claim_boundary": "Local-Qwen v0.9.10 qwen-compact live dev140 (ctx12288, maxtok2500) with standard-dictionary residual-repair v1.3.",
        "scorer_view": "headline_target",
        "config_path": "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140.yaml",
        "report_path": "experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.md",
        "summary_path": "experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json",
        "assembly_jsonl_path": "experiments/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.jsonl",
        "text_source_paths": [
            "experiments/exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl",
            "experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl",
        ],
    },
]


def repo_path(path: str | None) -> Path | None:
    if not path:
        return None
    return ROOT / path


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_jsonl(path: str) -> list[dict[str, Any]]:
    full_path = ROOT / path
    return [
        json.loads(line)
        for line in full_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def extract_letter_texts(paths: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in paths:
        full_path = ROOT / path
        if not full_path.exists():
            continue
        for row in load_jsonl(path):
            letter_id = str(row.get("letter_id", ""))
            if not letter_id or letter_id in texts:
                continue
            prompt_input = row.get("prompt_input_json")
            if isinstance(prompt_input, str):
                try:
                    prompt_input = json.loads(prompt_input)
                except json.JSONDecodeError:
                    prompt_input = {}
            if isinstance(prompt_input, dict) and isinstance(prompt_input.get("letter_text"), str):
                texts[letter_id] = prompt_input["letter_text"]
    return texts


def simplify_attributes(attributes: Any) -> dict[str, str]:
    if not isinstance(attributes, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in attributes.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            result[str(key)] = str(value)
    return result


def simplify_mention(mention: dict[str, Any], fallback_id: str, source: str) -> dict[str, Any]:
    return {
        "id": str(mention.get("finding_id") or mention.get("mention_id") or fallback_id),
        "source": source,
        "entity": str(mention.get("entity") or "Unknown"),
        "text": str(mention.get("text") or ""),
        "evidence": str(mention.get("evidence") or mention.get("text") or ""),
        "evidence_valid": bool(mention.get("evidence_valid", True)),
        "component_owner": str(mention.get("component_owner") or ""),
        "source_lane": str(mention.get("source_lane") or mention.get("lane") or ""),
        "source_model": str(mention.get("source_model") or ""),
        "confidence": str(mention.get("confidence") or ""),
        "assertion": str(mention.get("assertion") or ""),
        "attributes": simplify_attributes(mention.get("attributes")),
        "status": source,
    }


def evidence_spans(letter_text: str, mentions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str, str]] = set()
    for mention in mentions:
        evidence = str(mention.get("evidence") or mention.get("text") or "").strip()
        if not evidence:
            continue
        start = letter_text.find(evidence)
        if start < 0:
            start = letter_text.lower().find(evidence.lower())
        if start < 0:
            continue
        end = start + len(evidence)
        key = (start, end, str(mention.get("entity")), str(mention.get("source")))
        if key in seen:
            continue
        seen.add(key)
        spans.append(
            {
                "start": start,
                "end": end,
                "text": letter_text[start:end],
                "entity": mention.get("entity"),
                "kind": "gold" if mention.get("source") == "gold" else "llm",
                "label": f"{mention.get('source')} {mention.get('entity')}",
            }
        )
    return sorted(spans, key=lambda span: (span["start"], span["end"]))


def family_counts(mentions: list[dict[str, Any]]) -> dict[str, int]:
    counts = {family: 0 for family in FAMILIES}
    for mention in mentions:
        entity = str(mention.get("entity") or "")
        if entity in counts:
            counts[entity] += 1
    return counts


def metrics_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    headline = summary.get("score_ladder", {}).get("headline_target", {})
    overall = headline.get("overall", {})
    by_indicator = headline.get("by_indicator", {})
    return {
        "overall_f1": overall.get("f1"),
        "precision": overall.get("precision"),
        "recall": overall.get("recall"),
        "families": {
            family: {
                "f1": by_indicator.get(family, {}).get("f1"),
                "precision": by_indicator.get(family, {}).get("precision"),
                "recall": by_indicator.get(family, {}).get("recall"),
                "tp": by_indicator.get(family, {}).get("tp"),
                "fp": by_indicator.get(family, {}).get("fp"),
                "fn": by_indicator.get(family, {}).get("fn"),
            }
            for family in FAMILIES
        },
    }


def operational_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    diagnostics = summary.get("lane_diagnostics", {})
    exact_rates = [
        float(value.get("exact_evidence_rate", 0.0))
        for value in diagnostics.values()
        if isinstance(value, dict)
    ]
    return {
        "call_failures": max(
            [int(value.get("call_failures", 0)) for value in diagnostics.values() if isinstance(value, dict)]
            or [0]
        ),
        "parse_schema_failures": max(
            [
                int(value.get("parse_schema_failures", 0))
                for value in diagnostics.values()
                if isinstance(value, dict)
            ]
            or [0]
        ),
        "evidence_invalid_dropped": sum(
            int(value.get("evidence_invalid_dropped", 0))
            for value in diagnostics.values()
            if isinstance(value, dict)
        ),
        "exact_evidence_rate": min(exact_rates) if exact_rates else None,
        "by_family": diagnostics,
    }


def build_run(spec: dict[str, Any]) -> dict[str, Any]:
    summary = load_json(spec["summary_path"])
    rows = load_jsonl(spec["assembly_jsonl_path"])
    letter_texts = extract_letter_texts(spec["text_source_paths"])

    letters: list[dict[str, Any]] = []
    for row in rows:
        letter_id = str(row.get("letter_id") or "")
        gold_mentions = [
            simplify_mention(mention, f"{letter_id}:gold:{index}", "gold")
            for index, mention in enumerate(row.get("gold_mentions") or [])
        ]
        predicted_mentions = [
            simplify_mention(mention, f"{letter_id}:predicted:{index}", "predicted")
            for index, mention in enumerate(row.get("predicted_mentions") or [])
        ]
        letter_text = letter_texts.get(letter_id) or "\n\n".join(
            mention["evidence"]
            for mention in predicted_mentions
            if mention.get("evidence")
        )
        all_mentions = gold_mentions + predicted_mentions
        letters.append(
            {
                "letter_id": letter_id,
                "split": row.get("split", "dev"),
                "stage": row.get("stage", spec["split"]),
                "letter_text": letter_text,
                "gold_mentions": gold_mentions,
                "predicted_mentions": predicted_mentions,
                "family_counts": {
                    "gold": family_counts(gold_mentions),
                    "predicted": family_counts(predicted_mentions),
                },
                "evidence_spans": evidence_spans(letter_text, all_mentions),
            }
        )

    return {
        "run_id": spec["run_id"],
        "task": "exectv2",
        "label": spec["label"],
        "model": spec["model"],
        "architecture_family": spec["architecture_family"],
        "pipeline_family": spec["pipeline_family"],
        "split": spec["split"],
        "row_count": summary.get("row_count", len(rows)),
        "date": summary.get("generated_on", "2026-06-22"),
        "decision": spec["decision"],
        "promotion_decision": spec["promotion_decision"],
        "claim_boundary": spec["claim_boundary"],
        "scorer_view": spec["scorer_view"],
        "artifact_paths": [
            path
            for path in [
                spec.get("config_path"),
                spec.get("report_path"),
                spec.get("summary_path"),
                spec.get("assembly_jsonl_path"),
            ]
            if path
        ],
        "source_paths": spec["text_source_paths"],
        "metrics": metrics_from_summary(summary),
        "operational": operational_from_summary(summary),
        "letters": letters,
    }


def update_registry(runs: list[dict[str, Any]]) -> None:
    registry_path = MOCK_ROOT / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    existing_runs = [
        run for run in registry.get("runs", []) if run.get("task", "gan2026") != "exectv2"
    ]
    exectv2_entries = []
    for run in runs:
        exectv2_entries.append(
            {
                "task": "exectv2",
                "run_id": run["run_id"],
                "pipeline_family": run["pipeline_family"],
                "architecture_family": run["architecture_family"],
                "date": run["date"],
                "row_count": run["row_count"],
                "artifact_paths": run["artifact_paths"],
                "mode": run["label"],
                "model": run["model"],
                "model_role": run["promotion_decision"],
                "split": run["split"],
                "decision": run["decision"],
                "claim_boundary": run["claim_boundary"],
                "scorer_view": run["scorer_view"],
            }
        )
    registry["runs"] = existing_runs + exectv2_entries
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    EXECTV2_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    runs = [build_run(spec) for spec in RUN_SPECS]

    public_runs = []
    for run in runs:
        (ARTIFACT_ROOT / f"{run['run_id']}.json").write_text(
            json.dumps(
                {
                    "run_id": run["run_id"],
                    "artifact_path": run["artifact_paths"][-1],
                    "artifact_type": "exectv2_frontend_letters",
                    "content": run["letters"],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        public_runs.append(run)

    payload = {
        "generated_on": "2026-06-22",
        "source_index": "docs/experiments/final_artifact_index_2026-06-22.md",
        "runs": public_runs,
    }
    (EXECTV2_ROOT / "runs.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    update_registry(public_runs)

    print(f"Wrote {len(public_runs)} ExECTv2 frontend runs to {EXECTV2_ROOT / 'runs.json'}")


if __name__ == "__main__":
    main()
