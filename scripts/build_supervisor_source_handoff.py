"""Build the readable supervisor handoff from an explicit source allowlist."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "true")
os.environ.setdefault("DSPY_CACHEDIR", str(ROOT / ".tmp" / "dspy-handoff-build-cache"))

TEMPLATE = ROOT / "handoff" / "source"
PUBLIC_PACKAGE = ROOT / "src" / "clinical_extraction_local"
SOURCE_PACKAGE = ROOT / "src" / "clinical_extraction"
HANDOFF = ROOT / "handoff" / "supervisor"
ARCHIVE = ROOT / "handoff" / "clinical_extraction_supervisor_handoff.zip"
PACKAGE_TESTS = (
    "test_clinical_extraction_local.py",
    "test_clinical_extraction_local_batch.py",
    "test_clinical_extraction_local_parity.py",
)

# Runtime tracing proves imports; these prefixes decide what may be shipped.
# Anything outside this list fails the build instead of entering the archive.
ALLOWED_RUNTIME_PREFIXES = (
    "__init__.py",
    "core/",
    "operational/__init__.py",
    "operational/exect.py",
    "operational/io.py",
    "operational/runtime.py",
    "tasks/__init__.py",
    "tasks/epilepsy_phenotyping/__init__.py",
    "tasks/epilepsy_phenotyping/exectv2/",
    "tasks/seizure_frequency/__init__.py",
    "tasks/seizure_frequency/gan2026/",
    "tasks/shared/",
)
FORBIDDEN_PARTS = {
    "__pycache__",
    "artifact_analysis",
    "cli",
    "gepa",
    "reports",
}
TEMPLATE_EXCLUSIONS = {".env", ".venv", "__pycache__", ".pytest_cache"}


def main() -> None:
    _check_sources()
    runtime_files, runtime_assets = _trace_runtime_closure()
    _replace_destination()
    _copy_template()
    for name in PACKAGE_TESTS:
        shutil.copy2(ROOT / "tests" / name, HANDOFF / "tests" / name)
    shutil.copytree(PUBLIC_PACKAGE, HANDOFF / "clinical_extraction_local")
    for source in sorted(runtime_files | runtime_assets):
        relative = source.relative_to(SOURCE_PACKAGE)
        target = HANDOFF / "clinical_extraction" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    _remove_generated_junk()
    _write_source_manifest()
    _build_archive()
    _verify_clean_copy()
    print(
        f"Built readable handoff with {len(runtime_files)} internal modules and "
        f"{len(runtime_assets)} runtime assets: {ARCHIVE}"
    )


def _check_sources() -> None:
    if not TEMPLATE.is_dir() or not PUBLIC_PACKAGE.is_dir():
        raise RuntimeError("handoff template or public package is missing")


def _trace_runtime_closure() -> tuple[set[Path], set[Path]]:
    read_assets: set[Path] = set()
    original_read_text = Path.read_text

    def traced_read_text(path: Path, *args: object, **kwargs: object) -> str:
        resolved = path.resolve()
        if resolved.is_relative_to(SOURCE_PACKAGE) and resolved.suffix != ".py":
            read_assets.add(resolved)
        return original_read_text(path, *args, **kwargs)  # type: ignore[arg-type]

    Path.read_text = traced_read_text  # type: ignore[method-assign]
    try:
        _exercise_runtime_paths()
    finally:
        Path.read_text = original_read_text  # type: ignore[method-assign]
    modules = _loaded_source_modules()
    for source in modules | read_assets:
        _assert_allowed_runtime_file(source)
    return modules, read_assets


def _exercise_runtime_paths() -> None:
    from clinical_extraction.operational.exect import _assemble
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_builders import (  # noqa: E501
        build_prompt_input as build_exect_prompt,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
    from clinical_extraction_local import ClinicalExtractor  # noqa: F401

    build_exect_prompt(ExectLetter("synthetic", "Focal epilepsy."), prompt_profile="full")
    empty = label_to_frequency_record("unknown")
    record = GanFrequencyRecord(
        source_row_index=0,
        note_text="Two seizures per month.",
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
    hybrid_structured_events.build_prompt_input(
        record, prompt_version=hybrid_structured_events.PROMPT_VERSION_V0_5
    )
    # Keep the conditional assembly path in the explicit import closure.
    assert callable(_assemble)


def _loaded_source_modules() -> set[Path]:
    files: set[Path] = set()
    for module in tuple(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if not filename:
            continue
        path = Path(filename).resolve()
        if path.suffix == ".py" and path.is_relative_to(SOURCE_PACKAGE):
            files.add(path)
    required = {
        SOURCE_PACKAGE / "operational" / "exect.py",
        SOURCE_PACKAGE
        / "tasks"
        / "seizure_frequency"
        / "gan2026"
        / "llm"
        / "hybrid_structured_events.py",
    }
    if missing := required - files:
        raise RuntimeError(f"runtime trace missed required files: {sorted(missing)}")
    return files


def _assert_allowed_runtime_file(source: Path) -> None:
    relative = source.relative_to(SOURCE_PACKAGE).as_posix()
    allowed = any(
        relative == prefix or relative.startswith(prefix)
        for prefix in ALLOWED_RUNTIME_PREFIXES
    )
    if not allowed:
        raise RuntimeError(f"runtime import is outside the allowlist: {relative}")
    if any(part in FORBIDDEN_PARTS for part in Path(relative).parts):
        raise RuntimeError(f"forbidden research/runtime path entered the handoff: {relative}")


def _replace_destination() -> None:
    expected = (ROOT / "handoff" / "supervisor").resolve()
    if HANDOFF.resolve() != expected or HANDOFF.name != "supervisor":
        raise RuntimeError(f"refusing unexpected destination: {HANDOFF}")
    if HANDOFF.exists():
        shutil.rmtree(HANDOFF)
    HANDOFF.mkdir(parents=True)


def _copy_template() -> None:
    for source in TEMPLATE.rglob("*"):
        relative = source.relative_to(TEMPLATE)
        if any(part in TEMPLATE_EXCLUSIONS for part in relative.parts):
            continue
        target = HANDOFF / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _remove_generated_junk() -> None:
    for path in HANDOFF.rglob("*"):
        if path.is_file() and (path.suffix in {".pyc", ".pyz"} or path.name == ".env"):
            path.unlink()
    for path in sorted(HANDOFF.rglob("__pycache__"), reverse=True):
        shutil.rmtree(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_source_manifest() -> None:
    entries = []
    for path in sorted(HANDOFF.rglob("*")):
        if path.is_file() and path.name != "SOURCE_MANIFEST.json":
            entries.append(
                {
                    "path": path.relative_to(HANDOFF).as_posix(),
                    "sha256": _sha256(path),
                    "bytes": path.stat().st_size,
                }
            )
    payload = {
        "manifest_version": 1,
        "source_first": True,
        "generated_from": "scripts/build_supervisor_source_handoff.py explicit allowlist",
        "files": entries,
    }
    (HANDOFF / "SOURCE_MANIFEST.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )


def _build_archive() -> None:
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="supervisor-source-handoff-", suffix=".zip", dir=ARCHIVE.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(HANDOFF.rglob("*")):
                if source.is_file():
                    relative = source.relative_to(HANDOFF).as_posix()
                    info = zipfile.ZipInfo.from_file(source, arcname=relative)
                    info.create_system = 3
                    mode = 0o100755 if relative == "setup.sh" else 0o100644
                    info.external_attr = mode << 16
                    archive.writestr(
                        info,
                        source.read_bytes(),
                        compress_type=zipfile.ZIP_DEFLATED,
                    )
        os.replace(temporary, ARCHIVE)
    finally:
        temporary.unlink(missing_ok=True)


def _verify_clean_copy() -> None:
    with tempfile.TemporaryDirectory(prefix="supervisor-handoff-check-", dir=ROOT / ".tmp") as raw:
        clean = Path(raw)
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(clean)
        command = [
            sys.executable,
            "run.py",
            "validate-input",
            "--input",
            "examples/seizure_frequency/notes.jsonl",
        ]
        result = subprocess.run(command, cwd=clean, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"clean-copy validation failed: {result.stderr}")
        tests = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests",
                "-q",
                "-p",
                "no:cacheprovider",
                "--basetemp",
                ".test-tmp",
            ],
            cwd=clean,
            capture_output=True,
            text=True,
            check=False,
        )
        if tests.returncode != 0:
            raise RuntimeError(f"clean-copy tests failed: {tests.stdout}\n{tests.stderr}")


if __name__ == "__main__":
    main()
