"""Build the ExECTv2 Investigations aggregate rule/adjudicator ablation."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    investigations_rule_ablation,
)


def main() -> None:
    paths = investigations_rule_ablation.write_investigations_rule_ablation_artifacts()
    print(f"JSON: {paths['json']}")
    print(f"Markdown: {paths['markdown']}")
    print(f"Selective JSONL: {paths['selective_jsonl']}")


if __name__ == "__main__":
    main()
