from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
    hybrid_rules_candidates_llm_adjudicator as hybrid,
)

JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_"
    "cluster_diary_candidate_recall_live_2026-06-02.jsonl"
)
MARKDOWN_PATH = JSONL_PATH.with_suffix(".md")


def main() -> None:
    records = load_records_for_split("test", DEFAULT_DATA_PATH, DEFAULT_SPLIT_MANIFEST_PATH)
    manifest = load_split_manifest(DEFAULT_SPLIT_MANIFEST_PATH)
    split_manifest = str(
        manifest.get("manifest_version")
        or manifest.get("version")
        or DEFAULT_SPLIT_MANIFEST_PATH.stem
    )
    rows, metadata = hybrid.run_hybrid_rules_candidates_llm_adjudicator_split(
        records,
        split="test",
        split_manifest=split_manifest,
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1100,
        mode="live",
        dspy_cache=True,
        escalation_reason=(
            "frozen locked-test generalization audit for hybrid v0.2 "
            "cluster_diary_candidate_recall; no test-row failure inspection or tuning"
        ),
        progress_every=25,
        checkpoint_jsonl_path=JSONL_PATH,
        checkpoint_report_path=MARKDOWN_PATH,
        candidate_revision="cluster_diary_candidate_recall",
    )
    hybrid.write_hybrid_rules_candidates_llm_adjudicator_jsonl(rows, JSONL_PATH)
    hybrid.write_hybrid_rules_candidates_llm_adjudicator_report(
        rows,
        metadata,
        MARKDOWN_PATH,
        jsonl_path=JSONL_PATH,
    )
    print(
        json.dumps(
            {
                "jsonl": str(JSONL_PATH),
                "markdown": str(MARKDOWN_PATH),
                "summary": metadata["summary"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
