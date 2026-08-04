#!/usr/bin/env python3
"""Build the explainer pages from live repository data.

One front door, plus the prototype archive it grew out of:

* ``explainer.html`` - the whole system on one page, in three depths
                       (glance / mechanism / machinery)
* ``index.html``     - the prototype archive and directory
* ``journey.html``, ``xray.html``, ``custody.html`` - wave-2 mechanism prototypes
* ``map.html``, ``ladder.html``, ``console.html``   - wave-1 orientation prototypes

Everything except the ``CLI_MAP`` block below is derived from the repository:
stage manifests, executed teaching cases, and a walk of ``src``. The CLI map
is hand-authored from the argument parsers and is labelled as such in the UI.

    .venv\\Scripts\\python.exe scratch\\explainer\\build.py          # rebuild all pages
    .venv\\Scripts\\python.exe scratch\\explainer\\build.py --check  # fail if any page is stale
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from clinical_extraction.architecture.stage_manifest import (
    METHOD_IDS,
    load_manifest,
    repo_root,
)
from clinical_extraction.architecture.teaching_case import build_all_cases

HERE = Path(__file__).resolve().parent
ROOT = repo_root()


# ---------------------------------------------------------------------------
# 1. Stage manifests (derived)
# ---------------------------------------------------------------------------


def collect_manifests() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for method_id in METHOD_IDS:
        path = (
            ROOT
            / "src/clinical_extraction/architecture/manifests"
            / f"{method_id}.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        load_manifest(method_id)  # validates the manifest actually loads
        payload["manifest_path"] = path.relative_to(ROOT).as_posix()
        out.append(payload)
    return out


# ---------------------------------------------------------------------------
# 2. Executed teaching cases (derived; no model calls, no locked rows)
# ---------------------------------------------------------------------------


def collect_cases() -> list[dict[str, Any]]:
    return [case.to_dict() for case in build_all_cases()]


# ---------------------------------------------------------------------------
# 3. Codebase map (derived walk + declared roles)
# ---------------------------------------------------------------------------

# Why a directory exists. "sediment" is not an insult: it is retained research
# that is deliberately not on a selected path, and a newcomer needs to know
# that before reading 20k lines of it.
DIRECTORY_ROLES: dict[str, tuple[str, str]] = {
    "agentic": ("sediment", "Retained agentic experiments. Not a selected path."),
    "gepa": ("sediment", "Closed GEPA prompt-optimization workstream. Historical comparison only."),
    "experiments": (
        "sediment",
        "Ablation and experiment controls, switched off in the selected configuration.",
    ),
    "artifact_analysis": ("sediment", "Post-hoc analysis over saved run artifacts."),
    "reports": ("support", "Report rendering over saved runs."),
    "runners": ("support", "Split runners and CLI wrappers. Add no clinical stage."),
    "cli": ("support", "Argument parsing and run bookkeeping."),
    "contract": ("support", "Label and schema contracts shared across methods."),
    "data": ("support", "Split loading and record types."),
    "state_graph": ("sediment", "Retained state-graph exploration."),
    "selected_evidence": ("support", "Evidence records for the selected runs."),
    "components": ("support", "Reusable pipeline components."),
    "pipeline": ("support", "Pipeline assembly helpers."),
}

LAYERS = [
    (
        "src/clinical_extraction/tasks",
        "Tasks",
        "The two research pipelines. Almost all of the code, and all of the clinical stages.",
    ),
    (
        "src/clinical_extraction/core",
        "Core",
        "Shared machinery: model calls, caching, resumable runs, scoring helpers.",
    ),
    (
        "src/clinical_extraction/architecture",
        "Architecture",
        "The stage manifests and the teaching case. This directory is the source of "
        "truth these prototypes read.",
    ),
    (
        "src/clinical_extraction/operational",
        "Operational",
        "The thin wrapper behind `clinical-extract`: notes in, JSONL out.",
    ),
    (
        "src/clinical_extraction/trace_explorer",
        "Trace explorer",
        "The local API the Next.js frontend talks to.",
    ),
    (
        "src/clinical_extraction/observatory",
        "Observatory",
        "Additional routers over saved runs.",
    ),
    (
        "src/clinical_extraction_local",
        "Readable wrappers",
        "A short public surface over the operational wrapper.",
    ),
]


def _measure(directory: Path) -> tuple[int, int]:
    files = [
        p
        for p in directory.rglob("*.py")
        if "__pycache__" not in p.parts
    ]
    loc = 0
    for path in files:
        loc += len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    return len(files), loc


def _selected_path_dirs(manifests: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Directory -> method ids whose stages are implemented in it."""

    hits: dict[str, set[str]] = {}
    for manifest in manifests:
        paths = [manifest["entry_point"]["path"]]
        paths += [stage["implementation"]["path"] for stage in manifest["stages"]]
        for raw in paths:
            directory = Path(raw).parent.as_posix()
            hits.setdefault(directory, set()).add(manifest["method_id"])
    return {key: sorted(value) for key, value in sorted(hits.items())}


def collect_codebase(manifests: list[dict[str, Any]]) -> dict[str, Any]:
    on_path = _selected_path_dirs(manifests)

    def _role(directory: Path, relative: str) -> dict[str, Any]:
        methods = sorted(
            {
                method
                for hit_dir, hit_methods in on_path.items()
                if hit_dir == relative or hit_dir.startswith(relative + "/")
                for method in hit_methods
            }
        )
        declared = DIRECTORY_ROLES.get(directory.name)
        if methods:
            role, note = "selected", "Contains stages of a selected method."
        elif declared:
            role, note = declared
        else:
            role, note = "support", "Supporting code."
        files, loc = _measure(directory)
        return {
            "name": directory.name,
            "path": relative,
            "files": files,
            "loc": loc,
            "role": role,
            "note": note,
            "methods": methods,
        }

    layers = []
    for relative, label, blurb in LAYERS:
        directory = ROOT / relative
        if not directory.exists():
            continue
        files, loc = _measure(directory)
        children: list[dict[str, Any]] = []
        if relative.endswith("tasks"):
            for task_dir, task_label in (
                ("seizure_frequency/gan2026", "Gan 2026"),
                ("epilepsy_phenotyping/exectv2", "ExECTv2"),
                ("shared", "Shared"),
            ):
                task_path = directory / task_dir
                if not task_path.exists():
                    continue
                task_files, task_loc = _measure(task_path)
                grandchildren = [
                    _role(child, (task_path / child.name).relative_to(ROOT).as_posix())
                    for child in sorted(task_path.iterdir())
                    if child.is_dir() and child.name != "__pycache__"
                ]
                children.append(
                    {
                        "name": task_label,
                        "path": (task_path).relative_to(ROOT).as_posix(),
                        "files": task_files,
                        "loc": task_loc,
                        "role": "task",
                        "note": "",
                        "children": grandchildren,
                    }
                )
        layers.append(
            {
                "name": label,
                "path": relative,
                "blurb": blurb,
                "files": files,
                "loc": loc,
                "children": children,
            }
        )

    total_files, total_loc = 0, 0
    for layer in layers:
        total_files += layer["files"]
        total_loc += layer["loc"]
    return {
        "layers": layers,
        "total_files": total_files,
        "total_loc": total_loc,
        "on_path_dirs": on_path,
    }


# ---------------------------------------------------------------------------
# 4. CLI map (hand-authored from the argument parsers; labelled in the UI)
# ---------------------------------------------------------------------------

CLI_MAP: list[dict[str, Any]] = [
    {
        "id": "clinical-extract-exect",
        "binary": "clinical-extract",
        "headline": "Run one ExECT method over your own notes",
        "entry": "src/clinical_extraction/operational/cli.py:main",
        "template": [
            {"token": "clinical-extract", "kind": "binary"},
            {"token": "exect", "kind": "subcommand"},
            {"token": "--method", "kind": "flag", "value": "llm_with_rules"},
            {"token": "--input", "kind": "flag", "value": "notes.jsonl"},
            {"token": "--output", "kind": "flag", "value": "facts.jsonl"},
            {"token": "--model", "kind": "flag", "value": "gpt-5.6-sol"},
        ],
        "tokens": {
            "clinical-extract": {
                "what": "The operational entry point declared in pyproject.toml.",
                "code": "src/clinical_extraction/operational/cli.py:main",
                "note": "Argument parsing and file IO only. It owns no clinical stage.",
            },
            "exect": {
                "what": "Selects the ExECTv2 task: four families of clinical facts per letter.",
                "code": "src/clinical_extraction/operational/exect.py:run_exect_notes",
                "note": "The sibling subcommand is `gan`. `probe` just checks the endpoint.",
            },
            "--method": {
                "what": (
                    "Selects which of the three methods runs, and therefore which "
                    "stage manifest describes it."
                ),
                "code": "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/runner.py",
                "choices": {
                    "rules": "exectv2_rules_only",
                    "llm": "exectv2_llm_only",
                    "llm_with_rules": "exectv2_llm_with_rules",
                },
                "note": "This is the single most important token: it picks the ladder.",
            },
            "--input": {
                "what": "JSONL of notes, one object per note with an id and text.",
                "code": "src/clinical_extraction/operational/io.py:read_notes",
                "note": "Your own notes. Locked benchmark splits are never read here.",
            },
            "--output": {
                "what": "JSONL of predicted facts, written atomically.",
                "code": "src/clinical_extraction/operational/io.py:write_jsonl_atomic",
                "note": "Refuses to overwrite unless you pass --overwrite.",
            },
            "--model": {
                "what": "Which model is called, with --base-url and --api-key.",
                "code": "src/clinical_extraction/operational/runtime.py:RuntimeConfig",
                "note": "Ignored by --method rules, which makes no model call.",
            },
        },
        "manifest_for": {
            "rules": "exectv2_rules_only",
            "llm": "exectv2_llm_only",
            "llm_with_rules": "exectv2_llm_with_rules",
        },
        "default_choice": "llm_with_rules",
        "choice_flag": "--method",
        "artifacts": [
            {
                "name": "facts JSONL (--output)",
                "what": "One object per input note: the predicted facts with their "
                "evidence spans. Written atomically; refuses to overwrite without --overwrite.",
            },
        ],
    },
    {
        "id": "clinical-extract-gan",
        "binary": "clinical-extract",
        "headline": "Answer the seizure-frequency question for your own notes",
        "entry": "src/clinical_extraction/operational/cli.py:main",
        "template": [
            {"token": "clinical-extract", "kind": "binary"},
            {"token": "gan", "kind": "subcommand"},
            {"token": "--input", "kind": "flag", "value": "notes.jsonl"},
            {"token": "--output", "kind": "flag", "value": "frequency.jsonl"},
            {"token": "--model", "kind": "flag", "value": "gpt-5.6-sol"},
        ],
        "tokens": {
            "clinical-extract": {
                "what": "The same operational entry point.",
                "code": "src/clinical_extraction/operational/cli.py:main",
                "note": "One binary, two tasks.",
            },
            "gan": {
                "what": (
                    "Selects the Gan 2026 task: one current seizure-frequency label "
                    "per letter."
                ),
                "code": "src/clinical_extraction/operational/gan.py:run_gan_notes",
                "note": (
                    "There is no --method here. The operational wrapper always runs "
                    "LLM with rules."
                ),
            },
            "--input": {
                "what": "JSONL of notes.",
                "code": "src/clinical_extraction/operational/io.py:read_notes",
                "note": "",
            },
            "--output": {
                "what": "JSONL, one frequency record per note.",
                "code": "src/clinical_extraction/operational/io.py:write_jsonl_atomic",
                "note": "",
            },
            "--model": {
                "what": "Which model is called.",
                "code": "src/clinical_extraction/operational/runtime.py:RuntimeConfig",
                "note": "Pinned to the hybrid_structured_events architecture, prompt v0.5.",
            },
        },
        "manifest_for": {"": "gan2026_llm_with_rules"},
        "default_choice": "",
        "choice_flag": "",
        "artifacts": [
            {
                "name": "frequency JSONL (--output)",
                "what": "One record per note: the frequency label and its evidence. "
                "Same atomic write and overwrite guard as the exect subcommand.",
            },
        ],
    },
    {
        "id": "gan2026-llm-experiment",
        "binary": "gan2026-llm-experiment",
        "headline": "Reproduce a Gan 2026 research run on a permitted split",
        "entry": (
            "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/"
            "llm_pipeline_cli.py:main"
        ),
        "template": [
            {"token": "gan2026-llm-experiment", "kind": "binary"},
            {"token": "--pipeline", "kind": "flag", "value": "llm_with_rules"},
            {"token": "--split", "kind": "flag", "value": "validation"},
            {"token": "--model", "kind": "flag", "value": "openai/gpt-4.1-mini"},
            {"token": "--mode", "kind": "flag", "value": "live"},
            {"token": "--jsonl", "kind": "flag", "value": "experiments/run.jsonl"},
        ],
        "tokens": {
            "gan2026-llm-experiment": {
                "what": (
                    "The research runner. Loads a split, runs a pipeline, writes "
                    "checkpoints and a report."
                ),
                "code": (
                    "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/"
                    "llm_pipeline_cli.py:main"
                ),
                "note": "Research entry point, not the operational one. It adds no clinical stage.",
            },
            "--pipeline": {
                "what": (
                    "Selects the method. The three choices are exactly the three "
                    "stage manifests."
                ),
                "code": (
                    "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/"
                    "llm_pipeline_cli.py:pipeline_specs"
                ),
                "choices": {
                    "rules": "gan2026_rules_only",
                    "llm": "gan2026_llm_only",
                    "llm_with_rules": "gan2026_llm_with_rules",
                },
                "note": "Required. There is no default method.",
            },
            "--split": {
                "what": "Which rows to run: train, validation, or test.",
                "code": (
                    "src/clinical_extraction/tasks/seizure_frequency/gan2026/"
                    "data.py:load_records_for_split"
                ),
                "note": "test is the locked test450 holdout and reports aggregate scores only.",
            },
            "--model": {
                "what": "Model id passed through to the model call.",
                "code": "src/clinical_extraction/core/",
                "note": "Rules-only ignores it.",
            },
            "--mode": {
                "what": "live makes model calls; prompt-only renders the prompts and stops.",
                "code": (
                    "src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/"
                    "llm_pipeline_cli.py"
                ),
                "note": (
                    "prompt-only is the cheap way to see exactly what the model "
                    "would be asked."
                ),
            },
            "--jsonl": {
                "what": "Per-row output path, written incrementally so a run can resume.",
                "code": "src/clinical_extraction/core/run_resume.py",
                "note": "",
            },
        },
        "manifest_for": {
            "rules": "gan2026_rules_only",
            "llm": "gan2026_llm_only",
            "llm_with_rules": "gan2026_llm_with_rules",
        },
        "default_choice": "llm_with_rules",
        "choice_flag": "--pipeline",
        "artifacts": [
            {
                "name": "row JSONL (--jsonl)",
                "what": "Per-row records written incrementally: prompt inputs, raw "
                "outputs, parse diagnostics, traces, and scores. Safe to inspect "
                "mid-run; a rerun resumes from it.",
            },
            {
                "name": "report (--markdown)",
                "what": "The aggregate report for the run: configuration, scores, "
                "and diagnostics summary.",
            },
            {
                "name": ".resume-part checkpoints",
                "what": "Progress checkpoints written every N rows. A rerun loads "
                "the durable target plus any newer interrupted-run checkpoint.",
            },
        ],
    },
    {
        "id": "trace-explorer",
        "binary": "trace-explorer",
        "headline": "Serve saved runs to the frontend",
        "entry": "src/clinical_extraction/trace_explorer/api/app.py:main",
        "template": [
            {"token": "trace-explorer", "kind": "binary"},
            {"token": "--host", "kind": "flag", "value": "127.0.0.1"},
            {"token": "--port", "kind": "flag", "value": "8000"},
            {"token": "--index", "kind": "flag", "value": ".trace_explorer"},
        ],
        "tokens": {
            "trace-explorer": {
                "what": "Local FastAPI service. The Next.js frontend proxies /api/* to it.",
                "code": "src/clinical_extraction/trace_explorer/api/app.py:main",
                "note": "Reads saved runs. Makes no model calls of its own.",
            },
            "--host": {
                "what": "Bind address, local by default.",
                "code": "src/clinical_extraction/trace_explorer/api/app.py",
                "note": "",
            },
            "--port": {
                "what": "Port the frontend expects at 127.0.0.1:8000.",
                "code": "frontend/next.config.ts",
                "note": "Change it here and you must change the frontend proxy too.",
            },
            "--index": {
                "what": "Where the disposable trace index is built on first start.",
                "code": "src/clinical_extraction/trace_explorer/index.py:build_index",
                "note": "Reviewer decisions live separately in .trace_explorer/reviews.sqlite3.",
            },
        },
        "manifest_for": {},
        "default_choice": "",
        "choice_flag": "",
        "artifacts": [
            {
                "name": ".trace_explorer/ trace index",
                "what": "Disposable index over saved runs, built on first start. "
                "Reviewer decisions live separately in reviews.sqlite3.",
            },
            {
                "name": "the workbench",
                "what": "The Next.js frontend proxies /api/* to this service. "
                "Open http://127.0.0.1:3000/workbench.",
            },
        ],
    },
    {
        "id": "build-architecture-docs",
        "binary": "python scripts/build_architecture_docs.py",
        "headline": "Regenerate the explanation from the code, or fail on drift",
        "entry": "scripts/build_architecture_docs.py:main",
        "template": [
            {"token": "python scripts/build_architecture_docs.py", "kind": "binary"},
            {"token": "--check", "kind": "flag", "value": ""},
        ],
        "tokens": {
            "python scripts/build_architecture_docs.py": {
                "what": (
                    "Renders the method cards, diagrams, and teaching cases from "
                    "the stage manifests."
                ),
                "code": "scripts/build_architecture_docs.py:main",
                "note": "This is the same data these prototypes read. Makes no model calls.",
            },
            "--check": {
                "what": "Do not write. Exit non-zero if any published document is stale.",
                "code": "src/clinical_extraction/architecture/render.py",
                "note": "The drift gate: if the code moves and the docs do not, CI fails.",
            },
        },
        "manifest_for": {},
        "default_choice": "",
        "choice_flag": "",
        "artifacts": [
            {
                "name": "docs/architecture/*",
                "what": "Regenerated method cards, diagrams, and teaching walks. "
                "--check fails on drift instead of writing.",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build_data() -> dict[str, Any]:
    manifests = collect_manifests()
    return {
        "manifests": manifests,
        "cases": collect_cases(),
        "codebase": collect_codebase(manifests),
        "cli": CLI_MAP,
        "scripts_count": len(
            [p for p in (ROOT / "scripts").glob("*.py")]
        ),
        "tests_count": len(
            [p for p in (ROOT / "tests").glob("test_*.py")]
        ),
    }


def render(data: dict[str, Any]) -> dict[Path, str]:
    """Return the content each generated file should have, keyed by path."""
    # `<\/` is valid JSON string escaping and keeps the payload from closing
    # the surrounding <script> element.
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    outputs: dict[Path, str] = {
        HERE / "explainer_data.json": json.dumps(data, ensure_ascii=False, indent=1)
    }
    for template in sorted(HERE.glob("*.template.html")):
        target = HERE / template.name.replace(".template.html", ".html")
        html = template.read_text(encoding="utf-8")
        if "__EXPLAINER_DATA__" not in html:
            raise SystemExit(f"{template.name} has no __EXPLAINER_DATA__ placeholder")
        outputs[target] = html.replace("__EXPLAINER_DATA__", payload)
    return outputs


def main() -> int:
    check = "--check" in sys.argv[1:]
    data = build_data()
    outputs = render(data)
    print(
        f"data: {len(data['manifests'])} manifests, "
        f"{sum(len(m['stages']) for m in data['manifests'])} stages, "
        f"{len(data['cases'])} teaching cases, "
        f"{data['codebase']['total_loc']:,} lines mapped"
    )
    if check:
        stale = []
        for target, content in sorted(outputs.items()):
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(target.relative_to(ROOT).as_posix())
        if stale:
            print("stale explainer pages (run scratch/explainer/build.py):")
            for name in stale:
                print(f"  {name}")
            return 1
        print(f"check: all {len(outputs)} generated files are current")
        return 0
    for target, content in sorted(outputs.items()):
        target.write_text(content, encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
