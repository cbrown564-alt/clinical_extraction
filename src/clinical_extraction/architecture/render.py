"""Render method cards, diagrams, and teaching-case documents from manifests.

Everything this module emits is derived from the stage manifests or from an
executed teaching case. Nothing is hand-authored prose about pipeline
behaviour, so a diagram cannot disagree with runtime ownership: if the code
moves, the manifest fails validation or the teaching case fails to build, and
the documents are regenerated from the corrected source.

``scripts/build_architecture_docs.py --check`` re-renders and compares, so
drift between the code and the published explanation fails CI.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from clinical_extraction.architecture.stage_manifest import (
    EFFECT_CLASSES,
    METHOD_IDS,
    MethodManifest,
    Stage,
    load_manifest,
    load_manifests,
)
from clinical_extraction.architecture.teaching_case import MethodRun, TeachingCase

GENERATED_BANNER = (
    "<!-- GENERATED FILE. Do not edit by hand.\n"
    "     Source: src/clinical_extraction/architecture/ (stage manifests +\n"
    "     executed teaching cases). Regenerate with\n"
    "     python scripts/build_architecture_docs.py -->"
)

_EFFECT_LABEL = {
    "transport_or_schema": "transport/schema only",
    "representation": "representation",
    "clinical_meaning": "CLINICAL MEANING",
    "benchmark_projection": "benchmark projection",
    "validation_gate": "gate",
}

_OWNER_LABEL = {
    "model": "model",
    "deterministic": "rules",
    "scorer": "scorer",
}


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _mermaid_label(text: str) -> str:
    """Mermaid node labels cannot carry quotes, brackets, or parentheses."""

    cleaned = text.replace('"', "'")
    for char in "()[]{}":
        cleaned = cleaned.replace(char, "")
    return cleaned


def _table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_escape(str(cell)) for cell in row) + " |")
    return lines


# --------------------------------------------------------------------------
# Method cards (Phase 3)
# --------------------------------------------------------------------------


def render_method_card(manifest: MethodManifest) -> str:
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append(f"# {manifest.task_label} - {manifest.method_label}")
    lines.append("")
    lines.append(f"Method id: `{manifest.method_id}`  ")
    lines.append(f"Role: **{manifest.role}**  ")
    lines.append(f"Stages: {len(manifest.stages)}")
    lines.append(
        f"Stages that may change clinical meaning: "
        f"{len(manifest.clinical_meaning_stages)}"
    )
    lines.append("")

    lines.append("## One sentence")
    lines.append("")
    lines.append(f"> {manifest.one_sentence}")
    lines.append("")

    lines.append("## Sixty seconds")
    lines.append("")
    lines.append(manifest.sixty_second)
    lines.append("")

    lines.append("## The five recall questions")
    lines.append("")
    entry = manifest.stages[0]
    lines.extend(
        _table(
            ["Question", "Answer"],
            [
                ["What enters?", f"{entry.input_type} - see `{entry.stage_id}`"],
                ["Who first proposes the clinical answer?", manifest.prediction_owner],
                [
                    "Which later stages may change clinical meaning?",
                    ", ".join(
                        f"`{stage.stage_id}`"
                        for stage in manifest.clinical_meaning_stages[1:]
                    )
                    or "none - the first proposer is the only one",
                ],
                ["What final representation is scored?", manifest.scored_representation],
                [
                    "What evidence shows whether each component helped or harmed?",
                    ", ".join(f"`{owner}`" for owner in manifest.evidence_owners)
                    or "no evidence owner recorded",
                ],
            ],
        )
    )
    lines.append("")

    lines.append("## Stages")
    lines.append("")
    lines.append(
        "Read the `Effect` column first. `CLINICAL MEANING` marks every stage "
        "that can change the answer."
    )
    lines.append("")
    lines.extend(
        _table(
            ["#", "Stage", "Owner", "Effect", "What it does"],
            [
                [
                    str(index),
                    f"`{stage.stage_id}`<br>{stage.name}",
                    _OWNER_LABEL[stage.owner],
                    _EFFECT_LABEL[stage.effect_class],
                    stage.operation,
                ]
                for index, stage in enumerate(manifest.stages, start=1)
            ],
        )
    )
    lines.append("")

    lines.append("## Stage walkthrough")
    lines.append("")
    for index, stage in enumerate(manifest.stages, start=1):
        lines.append(f"### {index}. {stage.name}")
        lines.append("")
        lines.append(f"`{stage.stage_id}` - {_OWNER_LABEL[stage.owner]}-owned, "
                     f"{_EFFECT_LABEL[stage.effect_class]}"
                     + (f", rule category `{stage.rule_category}`" if stage.rule_category else ""))
        lines.append("")
        lines.append(stage.operation)
        lines.append("")
        lines.extend(
            _table(
                ["", "Type", "Example"],
                [
                    ["In", stage.input_type, stage.input_example],
                    ["Out", stage.output_type, stage.output_example],
                ],
            )
        )
        lines.append("")
        if stage.notes:
            lines.append(f"> {stage.notes}")
            lines.append("")
        code_path = stage.implementation.path
        lines.append(
            f"- Code: [`{code_path}`](../../../{code_path}) "
            f"(`{stage.implementation.symbol}`)"
        )
        lines.append(f"- Test: [`{stage.governing_test.split('::')[0]}`]"
                     f"(../../../{stage.governing_test.split('::')[0]})")
        lines.append("- Proven in a trace by: "
                     + ", ".join(f"`{field}`" for field in stage.trace_fields))
        lines.append(f"- Paper wording: {stage.paper_wording}")
        lines.append("")

    lines.append("## Code map")
    lines.append("")
    lines.append(f"Entry point: [`{manifest.entry_point.path}`]"
                 f"(../../../{manifest.entry_point.path}) "
                 f"(`{manifest.entry_point.symbol}`)")
    lines.append("")
    lines.extend(
        _table(
            ["Stage", "Implementation", "Governing test"],
            [
                [
                    f"`{stage.stage_id}`",
                    f"`{stage.implementation.symbol}`",
                    f"`{stage.governing_test}`",
                ]
                for stage in manifest.stages
            ],
        )
    )
    lines.append("")

    if manifest.related_paths:
        lines.append("## Not this method")
        lines.append("")
        lines.append(
            "These paths exist and are easy to mistake for this "
            "runner. They are named here so they cannot be read as it."
        )
        lines.append("")
        lines.extend(
            _table(
                ["Path", "Role", "Why it is not this runner"],
                [
                    [f"`{related.path}`", related.role, related.note]
                    for related in manifest.related_paths
                ],
            )
        )
        lines.append("")

    lines.append("## Executable trace")
    lines.append("")
    task_slug = "gan2026" if manifest.task == "gan2026" else "exectv2"
    lines.append(
        f"See the [{manifest.task_label} teaching letters]"
        f"(../teaching_cases/{task_slug}.md), which run this method over the "
        "paper flagship letters and record what every stage above actually did."
    )
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Diagrams (Phase 4)
# --------------------------------------------------------------------------


def render_overview_diagram() -> str:
    manifests = load_manifests()
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Overview: two tasks x three implemented runners")
    lines.append("")
    lines.append(
        "Six implemented runners on one page. Each cell names who first "
        "proposes the clinical answer, which is the fact most often lost "
        "when these pipelines are described informally. These runners are "
        "not the paper's five-cell headline table; for cited methods, "
        "scores, and claims see "
        "[docs/paper/methods.md](../../../docs/paper/methods.md)."
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TB")
    for task, label in (("gan2026", "Gan 2026"), ("exectv2", "ExECTv2")):
        lines.append(f"  subgraph {task}[{label}]")
        lines.append("    direction TB")
        for manifest in manifests:
            if manifest.task != task:
                continue
            node = manifest.method_id
            owner = "model" if any(
                stage.owner == "model" for stage in manifest.stages
            ) else "rules"
            changing = len(manifest.clinical_meaning_stages)
            lines.append(
                f"    {node}[\"{_mermaid_label(manifest.method_label)}"
                f"<br/>first proposer: {owner}"
                f"<br/>{changing} stage(s) can change the answer\"]"
            )
        lines.append("  end")
    lines.append("")
    for manifest in manifests:
        lines.append(f"  class {manifest.method_id} {manifest.method};")
    lines.append("  classDef rules fill:#eef4ea,stroke:#5a7d4f;")
    lines.append("  classDef rules_only fill:#eef4ea,stroke:#5a7d4f;")
    lines.append("  classDef llm_only fill:#eaf0f7,stroke:#4a6f9c;")
    lines.append("  classDef llm fill:#eaf0f7,stroke:#4a6f9c;")
    lines.append("  classDef llm_with_rules fill:#f7f0e6,stroke:#a07b3c;")
    lines.append("```")
    lines.append("")
    lines.extend(
        _table(
            ["Task", "Method", "One sentence"],
            [
                [manifest.task_label, manifest.method_label, manifest.one_sentence]
                for manifest in manifests
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def render_stage_diagram(method_id: str) -> str:
    manifest = load_manifest(method_id)
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append(f"# {manifest.task_label} {manifest.method_label}: stage diagram")
    lines.append("")
    lines.append(f"> {manifest.one_sentence}")
    lines.append("")
    lines.append(
        "Node shape carries the ownership. Rounded nodes are model-owned. "
        "Rectangles are deterministic. Hexagons are gates. Stages that may "
        "change clinical meaning are highlighted."
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append("  letter([source letter])")
    previous = "letter"
    for stage in manifest.stages:
        node = stage.stage_id.replace(".", "_")
        label = _mermaid_label(stage.name)
        if stage.owner == "model":
            shape = f'{node}("{label}")'
        elif stage.effect_class == "validation_gate":
            shape = f'{node}{{{{"{label}"}}}}'
        else:
            shape = f'{node}["{label}"]'
        lines.append(f"  {shape}")
        lines.append(f"  {previous} --> {node}")
        previous = node
    lines.append("")
    for stage in manifest.stages:
        node = stage.stage_id.replace(".", "_")
        lines.append(f"  class {node} {stage.effect_class};")
    lines.append("  classDef clinical_meaning fill:#fbe9e7,stroke:#c0392b,stroke-width:2px;")
    lines.append("  classDef representation fill:#f4f6f8,stroke:#7f8c8d;")
    lines.append("  classDef transport_or_schema fill:#fbfbfb,stroke:#bdc3c7;")
    lines.append("  classDef validation_gate fill:#eef7ee,stroke:#27ae60;")
    lines.append("  classDef benchmark_projection fill:#eef0fb,stroke:#5b6abf;")
    lines.append("```")
    lines.append("")
    lines.append("## Stages that can change the clinical answer")
    lines.append("")
    lines.extend(
        _table(
            ["Stage", "Owner", "What it may change"],
            [
                [f"`{stage.stage_id}`", _OWNER_LABEL[stage.owner], stage.operation]
                for stage in manifest.clinical_meaning_stages
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def render_ownership_matrix() -> str:
    manifests = load_manifests()
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Ownership matrix")
    lines.append("")
    lines.append(
        "Every stage of every implemented runner, counted by what it is "
        "allowed to change. A runner is only as explainable as this row."
    )
    lines.append("")
    lines.append("## Effect classes")
    lines.append("")
    lines.extend(
        _table(
            ["Class", "Meaning"],
            [[f"`{name}`", description] for name, description in EFFECT_CLASSES.items()],
        )
    )
    lines.append("")
    lines.append("## Counts by method")
    lines.append("")
    effect_order = list(EFFECT_CLASSES)
    rows = []
    for manifest in manifests:
        counts = {effect: 0 for effect in effect_order}
        for stage in manifest.stages:
            counts[stage.effect_class] += 1
        rows.append(
            [
                manifest.task_label,
                manifest.method_label,
                str(len(manifest.stages)),
                *[str(counts[effect]) for effect in effect_order],
            ]
        )
    lines.extend(
        _table(
            ["Task", "Method", "Stages", *[f"`{effect}`" for effect in effect_order]],
            rows,
        )
    )
    lines.append("")
    lines.append("## Who owns the first clinical answer")
    lines.append("")
    lines.extend(
        _table(
            ["Task", "Method", "Prediction owner", "Scored representation"],
            [
                [
                    manifest.task_label,
                    manifest.method_label,
                    manifest.prediction_owner,
                    manifest.scored_representation,
                ]
                for manifest in manifests
            ],
        )
    )
    lines.append("")
    lines.append("## Every clinical-meaning stage in the system")
    lines.append("")
    rows = []
    for manifest in manifests:
        for stage in manifest.clinical_meaning_stages:
            rows.append(
                [
                    manifest.task_label,
                    manifest.method_label,
                    f"`{stage.stage_id}`",
                    _OWNER_LABEL[stage.owner],
                    stage.rule_category or "-",
                ]
            )
    lines.extend(
        _table(["Task", "Method", "Stage", "Owner", "Rule category"], rows)
    )
    lines.append("")
    return "\n".join(lines)


def render_attribution_view() -> str:
    """Where a rescue or a regression can come from, per method.

    This diagram shows possible origins, derived from the manifests. It does
    not carry counts: the measured rescue and regression numbers live in the
    retained attribution artifacts, which this file deliberately does not
    restate.
    """

    manifests = load_manifests()
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Result attribution: where a rescue or regression can originate")
    lines.append("")
    lines.append(
        "If a letter's answer changed for the better or the worse, one of the "
        "stages below did it. This is the candidate list, derived from the "
        "stage manifests - it is structural, not a measurement."
    )
    lines.append("")
    lines.append(
        "**Counts belong elsewhere.** Measured rescues and regressions live in "
        "the retained attribution artifacts named in each method card's "
        "evidence owners. This page deliberately does not restate them."
    )
    lines.append("")
    for manifest in manifests:
        lines.append(f"## {manifest.task_label} - {manifest.method_label}")
        lines.append("")
        lines.append(f"First proposer: {manifest.prediction_owner}")
        lines.append("")
        lines.append("```mermaid")
        lines.append("flowchart LR")
        lines.append(f'  origin_{manifest.method_id}["answer changed"]')
        for stage in manifest.clinical_meaning_stages:
            node = stage.stage_id.replace(".", "_")
            lines.append(f'  {node}["{_mermaid_label(stage.name)}"]')
            lines.append(f"  origin_{manifest.method_id} --> {node}")
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Teaching case documents (Phase 2 output)
# --------------------------------------------------------------------------


def _card_why(case: TeachingCase, run: MethodRun) -> str:
    if run.method_id.endswith("rules_only"):
        return case.card_why.get("rules", "")
    if run.method_id.endswith("llm_only"):
        return case.card_why.get("llm", "")
    return case.card_why.get("llm_with_rules", "")


def _verdict_label(run: MethodRun) -> str:
    if run.correct is None:
        return "not scored"
    return "yes" if run.correct else "no"


def _verdict_phrase(run: MethodRun) -> str:
    if run.correct is None:
        return "no correctness verdict is claimed for this trace"
    return "correct" if run.correct else "incorrect"


def render_teaching_case(case: TeachingCase) -> str:
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append(f"# Teaching case: {case.task_label} — `{case.letter_id}`")
    lines.append("")
    lines.append(f"Case id: `{case.case_id}`  ")
    lines.append(f"Letter: `{case.letter_id}`")
    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    lines.append(case.fixture_note)
    lines.append("")
    if case.mechanism_title or case.mechanism or case.story:
        lines.append("## Why this letter")
        lines.append("")
        if case.mechanism_title:
            lines.append(f"**{case.mechanism_title}**")
            lines.append("")
        if case.story:
            lines.append(case.story)
            lines.append("")
        if case.mechanism:
            lines.append(case.mechanism)
            lines.append("")
    lines.append("## The letter")
    lines.append("")
    lines.append("```text")
    lines.append(case.note_text)
    lines.append("```")
    lines.append("")
    lines.append(f"**Expected answer:** {case.gold}")
    lines.append("")
    lines.append(case.gold_note)
    lines.append("")

    lines.append("## Outcome by method")
    lines.append("")
    lines.extend(
        _table(
            ["Method", "Final answer", "Correct?", "On this letter"],
            [
                [
                    run.manifest.method_label,
                    run.final_answer,
                    _verdict_label(run),
                    _card_why(case, run),
                ]
                for run in case.runs
            ],
        )
    )
    lines.append("")

    for run in case.runs:
        lines.extend(_render_run(run, case))
    return "\n".join(lines)


def _render_run(run: MethodRun, case: TeachingCase | None = None) -> list[str]:
    lines: list[str] = []
    lines.append(f"## {run.manifest.method_label}")
    lines.append("")
    lines.append(f"> {run.manifest.one_sentence}")
    lines.append("")
    if case is not None and _card_why(case, run):
        lines.append(_card_why(case, run))
        lines.append("")
    lines.append(f"**Prediction owner:** {run.manifest.prediction_owner}")
    lines.append("")
    lines.append(f"**Final answer:** {run.final_answer}")
    lines.append("")
    if run.correctness_note:
        lines.append(run.correctness_note)
        lines.append("")

    changed = [obs for obs in run.observations if obs.changed]
    lines.append(
        f"{len(changed)} of {len(run.observations)} stages changed something "
        "on this letter."
    )
    lines.append("")

    for index, obs in enumerate(run.observations, start=1):
        marker = "**changed**" if obs.changed else "no change"
        lines.append(
            f"### {index}. {obs.stage_name} <sub>`{obs.stage_id}`</sub>"
        )
        lines.append("")
        lines.append(
            f"{_OWNER_LABEL[obs.owner]}-owned, "
            f"{_EFFECT_LABEL[obs.effect_class]} - {marker}"
        )
        lines.append("")
        lines.append("```text")
        lines.append(f"in : {_clip(str(obs.input_value))}")
        lines.append(f"out: {_clip(str(obs.output_value))}")
        lines.append("```")
        lines.append("")
        if obs.note:
            lines.append(f"> {obs.note}")
            lines.append("")
    return lines


def _letter_slug(case: TeachingCase) -> str:
    return case.letter_id.lower()


def _method_anchor(run: MethodRun) -> str:
    return run.manifest.method_label.lower().replace(" ", "-")


def _changed_repairs(run: MethodRun) -> list[str]:
    return [
        observation.stage_name
        for observation in run.observations
        if ".repair." in observation.stage_id and observation.changed
    ]


def render_task_letter_index(cases: Sequence[TeachingCase], task: str) -> str:
    selected = [case for case in cases if case.task == task]
    label = selected[0].task_label if selected else task
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append(f"# {label} teaching letters")
    lines.append("")
    lines.append(
        "Each letter below is a development-split paper flagship case. "
        "Open a letter for the full stage trace through all three methods."
    )
    lines.append("")
    lines.extend(
        _table(
            ["Letter", "What it teaches", "Gold"],
            [
                [
                    f"[{case.letter_id}]({_letter_slug(case)}.md)",
                    case.story or case.mechanism_title,
                    case.gold,
                ]
                for case in selected
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def render_six_path_walkthrough(cases: Sequence[TeachingCase]) -> str:
    """One reading order across the paper letters and their three methods.

    Result language is taken from the executed cases. This page does not
    invent a rescue that the implemented pipeline did not produce.
    """

    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Four-letter teaching walkthrough")
    lines.append("")
    lines.append(
        "Read this page as one continuous tour of the six implemented "
        "runners. The tour uses four development-split paper letters: two "
        "Gan 2026 rows and two ExECTv2 letters. Model outputs are replay "
        "fixtures; no live model call is made. Prediction-bearing stages "
        "and post-model gates use the real implemented pipelines. ExECT "
        "Score lists the four-family units that left the line; gold "
        "comparison lives on Workbench."
    )
    lines.append("")
    lines.append(
        "The five-stage diagram in the [repository README](../../../README.md) "
        "is the short orientation. Each letter page is the full in/out trace."
    )
    lines.append("")

    lines.append("## The four letters")
    lines.append("")
    lines.extend(
        _table(
            ["Letter", "Task", "Gold", "What it teaches"],
            [
                [f"`{case.letter_id}`", case.task_label, case.gold, case.story]
                for case in cases
            ],
        )
    )
    lines.append("")

    for case in cases:
        lines.append(f"## `{case.letter_id}` — {case.mechanism_title or case.story}")
        lines.append("")
        if case.mechanism:
            lines.append(case.mechanism)
            lines.append("")
        lines.append(
            f"**Gold:** {case.gold}  "
        )
        lines.append("")
        lines.append(case.gold_note)
        lines.append("")
        for run in case.runs:
            manifest = run.manifest
            repairs = _changed_repairs(run)
            repair_note = (
                f" Changed repair stages: {', '.join(f'`{name}`' for name in repairs)}."
                if repairs
                else ""
            )
            why = _card_why(case, run)
            lines.append(f"### {case.task_label} — {manifest.method_label}")
            lines.append("")
            lines.append(
                f"**Letter:** `{case.letter_id}` · **Final output:** "
                f"`{run.final_answer}` · **Status:** {_verdict_phrase(run)}"
            )
            lines.append("")
            if why:
                lines.append(why)
                lines.append("")
            if repair_note:
                lines.append(repair_note.strip())
                lines.append("")
            lines.append(
                f"The first clinical proposer is {manifest.prediction_owner}. "
                f"Open the [method card](../method_cards/{manifest.method_id}.md) "
                f"for the contract, then the [full stage trace]"
                f"({_letter_slug(case)}.md#{_method_anchor(run)}) for the "
                "observed inputs, outputs, and ownership at each stage."
            )
            lines.append("")

        gan_runs = {run.method_id: run for run in case.runs}
        if "gan2026_llm_only" in gan_runs and "gan2026_llm_with_rules" in gan_runs:
            llm_only = gan_runs["gan2026_llm_only"]
            hybrid = gan_runs["gan2026_llm_with_rules"]
            lines.append("### What the three Gan answers show")
            lines.append("")
            lines.append(
                f"Rules-only returns `{(gan_runs.get('gan2026_rules_only') or gan_runs['gan_rules']).final_answer}`. "
                f"LLM-only returns `{llm_only.final_answer}` "
                f"({_verdict_phrase(llm_only)}) against gold `{case.gold}`. "
                f"LLM-with-rules returns `{hybrid.final_answer}` "
                f"({_verdict_phrase(hybrid)})."
            )
            lines.append("")
            if hybrid.correct is True and llm_only.correct is False:
                repairs = _changed_repairs(hybrid)
                credited = repairs[0] if repairs else "a named deterministic repair"
                lines.append(
                    f"On this letter the hybrid path is a rescue, credited to "
                    f"`{credited}`."
                )
                lines.append("")
            elif hybrid.correct is False:
                lines.append(
                    "On this letter the hybrid path is not a rescue. The "
                    "trace keeps the wrong answer visible."
                )
                lines.append("")
        lines.append(
            "This is a mechanism example from a development letter and a "
            "replayed model output, not a holdout result."
        )
        lines.append("")
    return "\n".join(lines)


def _clip(text: str, limit: int = 600) -> str:
    single = text.replace("\n", " ")
    if len(single) <= limit:
        return single
    return single[:limit] + " ... (truncated)"


# --------------------------------------------------------------------------
# Index
# --------------------------------------------------------------------------


def render_index(cases: Sequence[TeachingCase] | None = None) -> str:
    manifests = load_manifests()
    cases = list(cases or ())
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Architecture: how a record moves through each method")
    lines.append("")
    lines.append(
        "This directory answers one question: what happens to a letter, "
        "stage by stage, in each of the six implemented task-method "
        "runners, and who owns each change. These runners explain "
        "mechanism only; they are not the paper's five-cell headline "
        "table. For cited methods, scores, and claims see "
        "[docs/paper/methods.md](../paper/methods.md)."
    )
    lines.append("")
    lines.append(
        "Everything here is generated from the stage manifests in "
        "`src/clinical_extraction/architecture/manifests/` and from teaching "
        "cases that execute the real pipelines. Do not edit these files by "
        "hand - change the manifest or the code, then run "
        "`python scripts/build_architecture_docs.py`."
    )
    lines.append("")
    lines.append("## Start here")
    lines.append("")
    lines.append(
        "1. [Two tasks x three implemented runners](diagrams/overview.md) - "
        "the whole system on one page."
    )
    lines.append(
        "2. [Four-letter teaching walkthrough](teaching_cases/six_paths.md) - "
        "one continuous reading order across the paper flagship letters."
    )
    lines.append(
        "3. [Ownership matrix](diagrams/ownership_matrix.md) - who may change "
        "a clinical answer, everywhere."
    )
    lines.append("4. A method card below, for the method you need.")
    lines.append(
        "5. A teaching letter for that task, to see a development letter "
        "move through it."
    )
    lines.append("")
    lines.append("## Method cards")
    lines.append("")
    lines.extend(
        _table(
            ["Task", "Method", "One sentence", "Card"],
            [
                [
                    manifest.task_label,
                    manifest.method_label,
                    manifest.one_sentence,
                    f"[card](method_cards/{manifest.method_id}.md)",
                ]
                for manifest in manifests
            ],
        )
    )
    lines.append("")
    lines.append("## Teaching cases")
    lines.append("")
    lines.append(
        "- [Four-letter walkthrough](teaching_cases/six_paths.md) - the "
        "supervisor reading order for G1, G3, E1, and E2."
    )
    lines.append(
        "- [Gan 2026 letters](teaching_cases/gan2026.md) - quiet-interval "
        "versus cluster grammar, and qualitative frequent versus unknown."
    )
    lines.append(
        "- [ExECTv2 letters](teaching_cases/exectv2.md) - four-family named "
        "windows, and epileptic versus dissociative rates."
    )
    if cases:
        lines.append("")
        for case in cases:
            lines.append(
                f"- [`{case.letter_id}`](teaching_cases/{_letter_slug(case)}.md) "
                f"- {case.story}"
            )
    lines.append("")
    lines.append("## Diagrams")
    lines.append("")
    lines.append("- [Overview](diagrams/overview.md)")
    lines.append("- [Ownership matrix](diagrams/ownership_matrix.md)")
    lines.append("- [Gan LLM-with-rules stages](diagrams/gan2026_llm_with_rules_stages.md)")
    lines.append("- [ExECT LLM pre-post stages](diagrams/exectv2_llm_pre_post_stages.md)")
    lines.append("- [Result attribution origins](diagrams/attribution_origins.md)")
    lines.append("")
    lines.append("## What this layer does not own")
    lines.append("")
    lines.append(
        "Scores, claim strength, and evidence freshness are owned elsewhere: "
        "`PROJECT_STATUS.md` for current evidence and `docs/paper/` for "
        "methods and claims. This layer explains mechanism only, and links "
        "to those owners rather than restating them."
    )
    lines.append("")
    return "\n".join(lines)


def all_documents(cases: Sequence[TeachingCase]) -> dict[str, str]:
    """Relative path -> rendered content, for every generated document."""

    documents: dict[str, str] = {
        "README.md": render_index(cases),
        "diagrams/overview.md": render_overview_diagram(),
        "diagrams/ownership_matrix.md": render_ownership_matrix(),
        "diagrams/attribution_origins.md": render_attribution_view(),
        "diagrams/gan2026_llm_with_rules_stages.md": render_stage_diagram(
            "gan2026_llm_with_rules"
        ),
        "diagrams/exectv2_llm_pre_post_stages.md": render_stage_diagram(
            "exectv2_llm_pre_post"
        ),
    }
    for method_id in METHOD_IDS:
        documents[f"method_cards/{method_id}.md"] = render_method_card(
            load_manifest(method_id)
        )
    for case in cases:
        documents[f"teaching_cases/{_letter_slug(case)}.md"] = render_teaching_case(
            case
        )
    documents["teaching_cases/gan2026.md"] = render_task_letter_index(
        cases, "gan2026"
    )
    documents["teaching_cases/exectv2.md"] = render_task_letter_index(
        cases, "exectv2"
    )
    documents["teaching_cases/six_paths.md"] = render_six_path_walkthrough(cases)
    return documents


def _unused(stage: Stage) -> None:  # pragma: no cover - keeps Stage imported
    del stage
