"""Merged hybrid -> benchmark-overall runner for ExECTv2."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.benchmark_constants import (
    PAPER_OVERALL_PER_ITEM,
    PAPER_OVERALL_PER_LETTER,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.hybrid_benchmark_overall import (
    EXPERIMENTS_DIR,
    KEY_FAMILIES,
    KEY_FAMILY_DEFAULTS,
    write_scorecard_artifacts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.registry_sync import (
    DEFAULT_RUN_INDEX_PATH,
)

DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merged hybrid key-family + deterministic all-9 benchmark-overall scorer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev", help="Data split; test is locked.")
    parser.add_argument("--prescription-jsonl", type=Path, default=None)
    parser.add_argument("--investigations-jsonl", type=Path, default=None)
    parser.add_argument("--diagnosis-jsonl", type=Path, default=None)
    parser.add_argument("--seizure-frequency-jsonl", type=Path, default=None)
    parser.add_argument(
        "--deterministic-for",
        nargs="*",
        default=(),
        choices=KEY_FAMILIES,
        help="Key families to leave on the deterministic substrate instead of the hybrid verifier.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--register", action="store_true", help="Register the run (default off).")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    return parser


def _resolve_sources(args: argparse.Namespace) -> dict[str, tuple[Path, str]]:
    overrides = {
        "Prescription": args.prescription_jsonl,
        "Investigations": args.investigations_jsonl,
        "Diagnosis": args.diagnosis_jsonl,
        "SeizureFrequency": args.seizure_frequency_jsonl,
    }
    deterministic_for = set(args.deterministic_for)
    sources: dict[str, tuple[Path, str]] = {}
    for entity, (default_path, entity_filter) in KEY_FAMILY_DEFAULTS.items():
        if entity in deterministic_for:
            continue
        path = overrides[entity] or default_path
        sources[entity] = (path, entity_filter)
    return sources


def main() -> None:
    args = _build_parser().parse_args()
    if args.split == "test":
        raise SystemExit("ERROR: test split is locked; only dev is permitted.")
    family_sources = _resolve_sources(args)
    for entity, (path, _filter) in family_sources.items():
        if not path.exists():
            raise SystemExit(f"ERROR: missing {entity} artifact: {path}")

    today = date.today().isoformat().replace("-", "")
    base = f"exectv2_hybrid_benchmark_overall_{args.split}_{today}"
    out_json = args.out_json or EXPERIMENTS_DIR / f"{base}.json"
    out_md = args.out_md or EXPERIMENTS_DIR / f"{base}.md"

    scorecard = write_scorecard_artifacts(
        out_json=out_json,
        out_md=out_md,
        split=args.split,
        family_sources=family_sources,
        generated_on=None,
        registry_path=args.registry if args.register else None,
        run_index_path=args.run_index,
    )

    benchmark = scorecard["scores"]["benchmark"]
    delta = scorecard["benchmark_overall_delta_vs_paper"]
    print(f"\nDone. JSON: {out_json}  MD: {out_md}", flush=True)
    print(
        f"Benchmark overall: per-item F1 {benchmark['per_item']['f1']:.4f} "
        f"(paper {PAPER_OVERALL_PER_ITEM}, {delta['per_item']:+.4f}) | "
        f"per-letter F1 {benchmark['per_letter']['f1']:.4f} "
        f"(paper {PAPER_OVERALL_PER_LETTER}, {delta['per_letter']:+.4f})",
        flush=True,
    )
    print(
        f"Semantic overall per-item F1 {scorecard['scores']['semantic']['per_item']['f1']:.4f} | "
        f"phrase-only per-item F1 {scorecard['scores']['phrase_only']['per_item']['f1']:.4f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
