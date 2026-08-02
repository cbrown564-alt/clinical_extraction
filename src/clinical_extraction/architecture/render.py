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
    lines.append(f"Stages: {len(manifest.stages)}  ")
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
            "These paths exist and are easy to mistake for the selected "
            "method. They are named here so they cannot be read as it."
        )
        lines.append("")
        lines.extend(
            _table(
                ["Path", "Role", "Why it is not the selected method"],
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
        f"See the [{manifest.task_label} teaching case]"
        f"(../teaching_cases/{task_slug}.md), which runs this method over one "
        "letter and records what every stage above actually did."
    )
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Diagrams (Phase 4)
# --------------------------------------------------------------------------


def render_overview_diagram() -> str:
    manifests = load_manifests()
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Overview: two tasks x three methods")
    lines.append("")
    lines.append(
        "One diagram, six cells. Each cell names who first proposes the "
        "clinical answer, which is the fact most often lost when these "
        "methods are described informally."
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
        "Every stage of every selected method, counted by what it is allowed "
        "to change. A method is only as explainable as this row."
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


def render_teaching_case(case: TeachingCase) -> str:
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append(f"# Teaching case: {case.task_label}")
    lines.append("")
    lines.append(f"Case id: `{case.case_id}`  ")
    lines.append(f"Letter: `{case.letter_id}`")
    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    lines.append(case.fixture_note)
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
            ["Method", "Final answer", "Correct?"],
            [
                [
                    run.manifest.method_label,
                    run.final_answer,
                    (
                        "not scored"
                        if run.correct is None
                        else ("yes" if run.correct else "no")
                    ),
                ]
                for run in case.runs
            ],
        )
    )
    lines.append("")

    for run in case.runs:
        lines.extend(_render_run(run))
    return "\n".join(lines)


def _render_run(run: MethodRun) -> list[str]:
    lines: list[str] = []
    lines.append(f"## {run.manifest.method_label}")
    lines.append("")
    lines.append(f"> {run.manifest.one_sentence}")
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


def _case_slug(case: TeachingCase) -> str:
    return "gan2026" if case.task == "gan2026" else "exectv2"


def _method_anchor(run: MethodRun) -> str:
    return run.manifest.method_label.lower().replace(" ", "-")


def render_six_path_walkthrough(cases: Sequence[TeachingCase]) -> str:
    """Render one compact reading order across all six selected paths.

    The detailed stage observations stay in the task-specific generated cases.
    This page is the single supervisor entry point: it sequences those
    observations and derives its result and failure language from the
    executable case output rather than duplicating pipeline facts by hand.
    """

    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Six-path teaching walkthrough")
    lines.append("")
    lines.append(
        "Read this page as one continuous tour of the selected system. The "
        "tour uses two synthetic letters because Gan 2026 and ExECTv2 have "
        "different output contracts: `TEACH-GAN-01` supplies the competing "
        "frequency example, and `TEACH-EXECT-01` supplies the four-family "
        "example. No model call is made; fixture model outputs are marked at "
        "the model boundary. Prediction-bearing stages and post-model gates "
        "use the real selected implementation; the final ExECT score entry is "
        "an unscored scorer-boundary illustration because the letter has no "
        "gold annotations."
    )
    lines.append("")
    lines.append(
        "The five-stage diagram in the [repository README](../../../README.md) "
        "is the short orientation. Each link below opens the generated method "
        "card and the full stage trace for that path."
    )
    lines.append("")

    lines.append("## Walk the six paths in order")
    lines.append("")
    path_runs = [
        (teaching_case, method_run)
        for teaching_case in cases
        for method_run in teaching_case.runs
    ]
    for index, (case, run) in enumerate(path_runs, start=1):
        manifest = run.manifest
        result = run.final_answer
        if run.correct is None:
            verdict = "no correctness verdict is claimed for this fixture"
        else:
            verdict = "correct" if run.correct else "incorrect"
        stage_names = " → ".join(stage.name for stage in manifest.stages)
        lines.append(f"### {index}. {case.task_label} — {manifest.method_label}")
        lines.append("")
        lines.append(
            f"**Letter:** `{case.letter_id}` · **Final output:** `{result}` · "
            f"**Status:** {verdict}"
        )
        lines.append("")
        lines.append(f"**Stages:** {stage_names}")
        lines.append("")
        lines.append(
            f"The first clinical proposer is {manifest.prediction_owner}. "
            f"Open the [method card](../method_cards/{manifest.method_id}.md) "
            f"for the contract, then the [full stage trace]({_case_slug(case)}.md"
            f"#{_method_anchor(run)}) for the observed inputs, outputs, and "
            "ownership at each stage."
        )
        lines.append("")

    gan = next(case for case in cases if case.task == "gan2026")
    gan_runs = {run.method_id: run for run in gan.runs}
    failed = gan_runs["gan2026_llm_only"]
    recovered = gan_runs["gan2026_llm_with_rules"]
    repairs = [
        observation
        for observation in recovered.observations
        if observation.stage_id.startswith("gan.llm_with_rules.repair.")
        and observation.changed
    ]
    repair_name = repairs[0].stage_name if repairs else "the named deterministic repair stage"

    lines.append("## Deliberate failure and recovery")
    lines.append("")
    lines.append(
        f"**Failure:** the Gan LLM-only path returns `{failed.final_answer}` "
        f"against the teaching answer `{gan.gold}`. Its full trace preserves "
        "the model label and quoted evidence, making the selection error "
        "visible rather than silently rewriting it."
    )
    lines.append("")
    lines.append(
        f"**Recovery:** the LLM-with-rules path starts from the same competing "
        f"model choice and reaches `{recovered.final_answer}`. The change is "
        f"credited to `{repair_name}`; the [Gan teaching trace]"
        f"(gan2026.md#{_method_anchor(recovered)}) shows the before/after "
        "values and the evidence check."
    )
    lines.append("")
    lines.append(
        "This is a mechanism example from a synthetic fixture, not a clinical "
        "validation result."
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


def render_index() -> str:
    manifests = load_manifests()
    lines: list[str] = [GENERATED_BANNER, ""]
    lines.append("# Architecture: how a record moves through each method")
    lines.append("")
    lines.append(
        "This directory answers one question: what happens to a letter, "
        "stage by stage, in each of the six selected task-method pairs, and "
        "who owns each change. It was built to close the gaps reported in the "
        "[pipeline understandability review]"
        "(../reviews/pipeline-understandability-review-2026-07-30.md)."
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
        "1. [Two tasks x three methods](diagrams/overview.md) - the whole "
        "system on one page."
    )
    lines.append(
        "2. [Six-path teaching walkthrough](teaching_cases/six_paths.md) - one "
        "continuous reading order across the selected methods."
    )
    lines.append(
        "3. [Ownership matrix](diagrams/ownership_matrix.md) - who may change "
        "a clinical answer, everywhere."
    )
    lines.append("4. A method card below, for the method you need.")
    lines.append("5. The teaching case for that task, to see a real letter move through it.")
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
        "- [Six-path walkthrough](teaching_cases/six_paths.md) - the supervisor "
        "reading order, including the deliberate failure and recovery."
    )
    lines.append(
        "- [Gan 2026](teaching_cases/gan2026.md) - one letter where the model "
        "selects the wrong competing rate and the deterministic layer rescues "
        "it."
    )
    lines.append(
        "- [ExECTv2](teaching_cases/exectv2.md) - one ordinary letter through "
        "all three methods, showing the four-family versus nine-entity "
        "comparison boundary."
    )
    lines.append("")
    lines.append("## Diagrams")
    lines.append("")
    lines.append("- [Overview](diagrams/overview.md)")
    lines.append("- [Ownership matrix](diagrams/ownership_matrix.md)")
    lines.append("- [Gan LLM-with-rules stages](diagrams/gan2026_llm_with_rules_stages.md)")
    lines.append("- [ExECT LLM-with-rules stages](diagrams/exectv2_llm_with_rules_stages.md)")
    lines.append("- [Result attribution origins](diagrams/attribution_origins.md)")
    lines.append("")
    lines.append("## What this layer does not own")
    lines.append("")
    lines.append(
        "Scores, claim strength, and evidence freshness are owned elsewhere: "
        "`PROJECT_STATUS.md` for current evidence, `docs/canon/` for governing "
        "claims, and `docs/plans/ACTIVE_ROADMAP.md` for sequence. This layer "
        "explains mechanism only, and links to those owners rather than "
        "restating them."
    )
    lines.append("")
    return "\n".join(lines)


def all_documents(cases: Sequence[TeachingCase]) -> dict[str, str]:
    """Relative path -> rendered content, for every generated document."""

    documents: dict[str, str] = {
        "README.md": render_index(),
        "diagrams/overview.md": render_overview_diagram(),
        "diagrams/ownership_matrix.md": render_ownership_matrix(),
        "diagrams/attribution_origins.md": render_attribution_view(),
        "diagrams/gan2026_llm_with_rules_stages.md": render_stage_diagram(
            "gan2026_llm_with_rules"
        ),
        "diagrams/exectv2_llm_with_rules_stages.md": render_stage_diagram(
            "exectv2_llm_with_rules"
        ),
    }
    for method_id in METHOD_IDS:
        documents[f"method_cards/{method_id}.md"] = render_method_card(
            load_manifest(method_id)
        )
    for case in cases:
        slug = "gan2026" if case.task == "gan2026" else "exectv2"
        documents[f"teaching_cases/{slug}.md"] = render_teaching_case(case)
    documents["teaching_cases/six_paths.md"] = render_six_path_walkthrough(cases)
    return documents


def _unused(stage: Stage) -> None:  # pragma: no cover - keeps Stage imported
    del stage
