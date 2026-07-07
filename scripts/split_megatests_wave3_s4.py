"""One-off splitter for Wave 3 Sprint 4 megatest decomposition."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def extract_blocks(source: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (preamble, [(name, block), ...]) including decorators on each function."""
    lines = source.splitlines(keepends=True)
    module = ast.parse(source)
    function_nodes = [
        node for node in module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if not function_nodes:
        raise ValueError("No function definitions found")

    first_start = (
        function_nodes[0].decorator_list[0].lineno
        if function_nodes[0].decorator_list
        else function_nodes[0].lineno
    )
    preamble = "".join(lines[: first_start - 1])
    blocks: list[tuple[str, str]] = []

    for index, node in enumerate(function_nodes):
        start_line = node.decorator_list[0].lineno if node.decorator_list else node.lineno
        if index + 1 < len(function_nodes):
            next_node = function_nodes[index + 1]
            end_line = (
                next_node.decorator_list[0].lineno if next_node.decorator_list else next_node.lineno
            )
        else:
            end_line = len(lines) + 1
        block = "".join(lines[start_line - 1 : end_line - 1]).rstrip() + "\n"
        blocks.append((node.name, block))

    return preamble, blocks


def compose_file(docstring: str, preamble: str, blocks: list[str]) -> str:
    body = "\n\n".join(blocks)
    if docstring:
        return f'"""{docstring}"""\n\n{preamble.rstrip()}\n\n{body}\n'
    return f"{preamble.rstrip()}\n\n{body}\n"


def exectv2_cluster(name: str) -> str:
    diagnosis_markers = (
        "diagnosis",
        "epileptic_events",
        "nonepileptic_events",
        "inferred_only_from_seizures",
        "context_parent_epilepsy",
        "temporal_lobe",
        "generalised_epilepsy",
        "gtc_diagnosis",
        "secondary_gtc",
        "complex_partial",
        "syndrome_to_gtc",
        "syndrome_without_alone",
        "dropped_general_complex_sf_to_diagnosis",
        "report_scores_projected_diagnosis",
    )
    if any(marker in name for marker in diagnosis_markers):
        return "diagnosis"
    return "seizure_frequency"


def projection_render_cluster(name: str) -> str:
    if name.startswith("test_project_and_render"):
        return "routing"
    instrumentation_markers = (
        "instruments_",
        "instrumented",
        "prior_encounter",
        "since_then",
        "antecedent",
        "event_month",
        "last_event_full_year",
        "approximate_season",
        "approximate_year",
        "hyphenated_mid_month",
        "relative_since_anchor",
        "uses_prior_encounter",
        "traces_renderable_prior",
        "can_disable_seizure_free_date",
        "numeric_since_date",
        "seizure_free_since_date",
        "last_event_day_month",
        "resolves_since_then",
        "keeps_since_then",
        "does_not_use_antecedent_for_duration",
    )
    if any(marker in name for marker in instrumentation_markers):
        return "instrumentation"
    return "repairs"


def split_exectv2() -> dict[str, list[str]]:
    path = TESTS / "test_exectv2_target_indicators_single_call.py"
    source = read_text(path)
    preamble, blocks = extract_blocks(source)

    core_names = {
        "test_target_single_call_prompt_is_limited_to_adr0030_indicators",
        "test_target_single_call_parser_salvages_malformed_rationale_mentions",
        "test_target_single_call_parser_accepts_python_literal_payload",
        "test_target_single_call_parser_salvages_complete_objects_from_truncated_array",
    }
    core_blocks: list[str] = []
    diagnosis_blocks: list[str] = []
    sf_blocks: list[str] = []
    moved: dict[str, list[str]] = {"core": [], "diagnosis": [], "seizure_frequency": []}

    for name, block in blocks:
        if name.startswith("_"):
            continue
        if name in core_names or any(
            token in name
            for token in (
                "prescription",
                "investigation",
                "cross_modal",
                "ecg",
                "drops_planned",
                "drops_requesting",
                "drops_useful_to_get",
                "drops_non_target_and_invalid",
                "repairs_case_only",
                "repairs_whitespace",
                "repairs_no_further_since",
                "repairs_ellipsis",
                "normalizes_format_only",
                "repairs_trailing_punctuation",
                "drops_non_target_ecg",
            )
        ):
            core_blocks.append(block)
            moved["core"].append(name)
        elif exectv2_cluster(name) == "diagnosis":
            diagnosis_blocks.append(block)
            moved["diagnosis"].append(name)
        else:
            sf_blocks.append(block)
            moved["seizure_frequency"].append(name)

    write_text(
        path,
        compose_file(
            "Parser, prescription, and investigation adapter tests for ExECTv2 target single-call.",
            preamble,
            core_blocks,
        ),
    )
    write_text(
        TESTS / "test_exectv2_target_indicators_single_call_diagnosis.py",
        compose_file(
            "Diagnosis projection and normalization tests for ExECTv2 target single-call.\n\n"
            "Split from test_exectv2_target_indicators_single_call.py.",
            preamble,
            diagnosis_blocks,
        ),
    )
    write_text(
        TESTS / "test_exectv2_target_indicators_single_call_seizure_frequency.py",
        compose_file(
            "Seizure-frequency projection, quarantine, and drop tests for ExECTv2 target single-call.\n\n"
            "Split from test_exectv2_target_indicators_single_call.py.",
            preamble,
            sf_blocks,
        ),
    )
    return moved


def split_projection_render() -> dict[str, list[str]]:
    path = TESTS / "test_gan2026_clinical_assessment_projection_render.py"
    source = read_text(path)
    preamble, blocks = extract_blocks(source)

    helper_blocks = [
        block.replace("def _candidate_set(", "def candidate_set(")
        .replace("def _row_context(", "def row_context(")
        .replace("def _unknown_candidate(", "def unknown_candidate(")
        .replace("def _seizure_free_candidate(", "def seizure_free_candidate(")
        for name, block in blocks
        if name.startswith("_")
    ]
    test_blocks = [(name, block) for name, block in blocks if name.startswith("test_")]

    fixtures_path = TESTS / "helpers" / "gan2026_projection_render_fixtures.py"
    write_text(
        fixtures_path,
        compose_file(
            "Shared fixtures for Gan2026 clinical assessment projection/render tests.",
            preamble,
            helper_blocks,
        ),
    )

    import_line = (
        "from tests.helpers.gan2026_projection_render_fixtures import (\n"
        "    candidate_set as _candidate_set,\n"
        "    row_context as _row_context,\n"
        "    seizure_free_candidate as _seizure_free_candidate,\n"
        "    unknown_candidate as _unknown_candidate,\n"
        ")\n"
    )
    slim_preamble = preamble.rstrip() + "\n\n" + import_line

    routing_blocks: list[str] = []
    repair_blocks: list[str] = []
    instrumentation_blocks: list[str] = []
    moved: dict[str, list[str]] = {"routing": [], "repairs": [], "instrumentation": []}

    for name, block in test_blocks:
        cluster = projection_render_cluster(name)
        if cluster == "routing":
            routing_blocks.append(block)
            moved["routing"].append(name)
        elif cluster == "instrumentation":
            instrumentation_blocks.append(block)
            moved["instrumentation"].append(name)
        else:
            repair_blocks.append(block)
            moved["repairs"].append(name)

    write_text(
        path,
        compose_file(
            "Routing and direct project_and_render tests for Gan2026 clinical assessment.",
            slim_preamble,
            routing_blocks,
        ),
    )
    write_text(
        TESTS / "test_gan2026_clinical_assessment_projection_render_repairs.py",
        compose_file(
            "Frequency repair and policy tests for Gan2026 clinical assessment projection/render.\n\n"
            "Split from test_gan2026_clinical_assessment_projection_render.py.",
            slim_preamble,
            repair_blocks,
        ),
    )
    write_text(
        TESTS / "test_gan2026_clinical_assessment_projection_render_instrumentation.py",
        compose_file(
            "Seizure-free date instrumentation and prior-encounter tests for Gan2026 projection/render.\n\n"
            "Split from test_gan2026_clinical_assessment_projection_render.py.",
            slim_preamble,
            instrumentation_blocks,
        ),
    )
    return moved


def split_pipeline_v1() -> dict[str, list[str]]:
    path = TESTS / "test_gan2026_pipeline_v1.py"
    source = read_text(path)
    preamble, blocks = extract_blocks(source)

    extraction_start = "test_pipeline_extracts_simple_current_frequency_rates"
    extraction_end = (
        "test_pipeline_prefers_convulsive_event_count_over_nonprogressive_myoclonic_jerks"
    )

    core_blocks: list[str] = []
    extraction_blocks: list[str] = []
    helper_blocks: list[str] = []
    in_extraction = False
    moved: dict[str, list[str]] = {"core": [], "extraction": []}

    for name, block in blocks:
        if name.startswith("_") and not name.startswith("test_"):
            helper_blocks.append(block)
            continue
        if name == extraction_start:
            in_extraction = True
        if in_extraction:
            extraction_blocks.append(block)
            moved["extraction"].append(name)
            if name == extraction_end:
                in_extraction = False
            continue
        core_blocks.append(block)
        moved["core"].append(name)

    core_body = helper_blocks + core_blocks
    extraction_body = helper_blocks + extraction_blocks

    write_text(
        path,
        compose_file(
            "Pipeline v1 infrastructure, ablation, metadata, and selection tests.",
            preamble,
            core_body,
        ),
    )
    write_text(
        TESTS / "test_gan2026_pipeline_v1_extraction.py",
        compose_file(
            "Parametrized frequency extraction patterns for Gan2026 pipeline v1.\n\n"
            "Split from test_gan2026_pipeline_v1.py.",
            preamble,
            extraction_body,
        ),
    )
    return moved


def main() -> None:
    print("Splitting exectv2 target indicators...")
    exectv2 = split_exectv2()
    print("Splitting clinical assessment projection render...")
    projection = split_projection_render()
    print("Splitting gan2026 pipeline v1 extraction cluster...")
    pipeline = split_pipeline_v1()

    print("\n=== ExECTv2 ===")
    for cluster, names in exectv2.items():
        print(f"  {cluster}: {len(names)} tests")

    print("\n=== Projection render ===")
    for cluster, names in projection.items():
        print(f"  {cluster}: {len(names)} tests")

    print("\n=== Pipeline v1 ===")
    for cluster, names in pipeline.items():
        print(f"  {cluster}: {len(names)} tests")


if __name__ == "__main__":
    main()
