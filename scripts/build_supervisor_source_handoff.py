"""Copy only the exercised Gan/ExECT operational import closure into the handoff."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKAGE = (ROOT / "src" / "clinical_extraction").resolve()
DESTINATION = (ROOT / "handoff" / "supervisor" / "clinical_extraction").resolve()


def main() -> None:
    read_assets: set[Path] = set()
    original_read_text = Path.read_text

    def traced_read_text(path: Path, *args: object, **kwargs: object) -> str:
        resolved = path.resolve()
        if resolved.is_relative_to(SOURCE_PACKAGE):
            read_assets.add(resolved)
        return original_read_text(path, *args, **kwargs)  # type: ignore[arg-type]

    Path.read_text = traced_read_text  # type: ignore[assignment,method-assign]
    try:
        _exercise_runtime_paths()
    finally:
        Path.read_text = original_read_text  # type: ignore[method-assign]

    module_files = _loaded_source_modules()
    files = module_files | read_assets
    _replace_destination(files)
    print(
        f"Copied {len(module_files)} Python modules and {len(read_assets)} runtime assets "
        f"to {DESTINATION}"
    )


def _exercise_runtime_paths() -> None:
    # Import the public CLI so `gan`, `exect`, and `probe` dependencies are all retained.
    from clinical_extraction.operational import (  # type: ignore[import-untyped]
        cli as _cli,  # noqa: F401
    )
    from clinical_extraction.operational.exect import _assemble  # type: ignore[import-untyped]
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (  # type: ignore[import-untyped]
        ExectLetter,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (  # type: ignore[import-untyped]
        key_entities_structured,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (  # type: ignore[import-untyped]
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import (  # type: ignore[import-untyped]
        GanFrequencyRecord,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (  # type: ignore[import-untyped]
        hybrid_structured_events as gan,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (  # type: ignore[import-untyped]
        hybrid_structured_events as _gan_runner,  # noqa: F401
    )

    key_entities_structured.build_prompt_input(
        ExectLetter(
            "trace",
            "She has two seizures per month and takes lamotrigine 100 mg twice daily.",
        ),
        prompt_profile="full",
    )
    empty = label_to_frequency_record("unknown")
    gan_record = GanFrequencyRecord(
        source_row_index=0,
        note_text="She has two seizures per month.",
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=False,
        quotes_ok_all_categories=False,
        row_ok=True,
        raw={},
        gold_normalized_label=empty.normalized_label,
        gold_label_kind=empty.kind,
        gold_yearly_bounds=empty.yearly_bounds,
        gold_monthly_frequency=empty.monthly_frequency,
    )
    gan.build_prompt_input(gan_record, prompt_version=gan.PROMPT_VERSION_V0_5)

    structured_row: dict[str, object] = {
        "letter_id": "trace",
        "split": "operational",
        "prompt_version": "trace",
        "prompt_profile": "full",
        "pipeline_family": "trace",
        "model": "trace",
        "mode": "live",
        "prompt_input_json": "{}",
        "raw_output": "{}",
        "call_error": None,
        "initial_parse_errors": [],
        "parse_errors": [],
        "structured_output_failure_codes": [],
        "format_retry_output": "",
        "format_retry_notes": [],
        "gate_warnings": [],
        "n_events_raw": 0,
        "n_mentions_raw": 0,
        "n_mentions_scored": 0,
        "n_evidence_invalid": 0,
        "structured_events": [],
        "predicted_mentions": [],
        "gold_mentions": [],
    }
    _assemble([ExectLetter("trace", "No relevant findings.")], [structured_row])


def _loaded_source_modules() -> set[Path]:
    files: set[Path] = set()
    for module in tuple(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename is None:
            continue
        path = Path(filename).resolve()
        if path.suffix == ".py" and path.is_relative_to(SOURCE_PACKAGE):
            files.add(path)
    required = {
        SOURCE_PACKAGE / "operational" / name
        for name in ("cli.py", "provider.py", "gan.py", "exect.py", "io.py", "runtime.py")
    }
    missing = required - files
    if missing:
        raise RuntimeError(f"operational trace missed required modules: {sorted(missing)}")
    return files


def _replace_destination(files: set[Path]) -> None:
    expected_parent = (ROOT / "handoff" / "supervisor").resolve()
    if DESTINATION.parent != expected_parent or DESTINATION.name != "clinical_extraction":
        raise RuntimeError(f"refusing unexpected destination: {DESTINATION}")
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    for source in sorted(files):
        relative = source.relative_to(SOURCE_PACKAGE)
        target = DESTINATION / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


if __name__ == "__main__":
    main()
