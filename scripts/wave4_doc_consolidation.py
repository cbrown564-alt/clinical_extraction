#!/usr/bin/env python3
"""Wave 4 documentation consolidation helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REDIRECT_TEMPLATE = """# {title}

> **Relocated (Wave 4)** — canonical document: [`{new_path}`]({new_rel}).

This legacy path is retained for backward-compatible links. Update bookmarks to the
numbered canon under [`docs/canon/`](../../canon/README.md).
"""

ARCHIVE_REDIRECT = """> **Archived (Wave 4)** — full narrative: [`{archive_rel}`]({archive_rel}). Canonical summary: [`{canon_name}`]({canon_rel}).
"""


def write_redirect(old_path: Path, new_path: Path, title: str) -> None:
    rel = Path("..") / Path(*Path("../" * (len(old_path.parent.parts) - 1)).parts)
    # compute relative from old_path.parent to new_path
    rel = Path(
        *[
            ".."
            for _ in range(len(old_path.parent.relative_to(ROOT).parts))
        ]
    )
    # simpler: use path from repo root in link
    new_rel = "/" + str(new_path.relative_to(ROOT)).replace("\\", "/")
    # use relative path properly
    import os

    new_rel = os.path.relpath(new_path, old_path.parent)
    content = REDIRECT_TEMPLATE.format(title=title, new_path=str(new_path.relative_to(ROOT)), new_rel=new_rel)
    old_path.write_text(content, encoding="utf-8")


def fix_moved_canon_links() -> None:
    replacements = [
        # 10_paper_provenance
        ("docs/canon/10_paper_provenance.md", "paper_manuscript_2026-06-26.md", "../research/paper_manuscript_2026-06-26.md"),
        ("docs/canon/10_paper_provenance.md", "paper_claims_evidence_review_2026-07-01.md", "../research/paper_claims_evidence_review_2026-07-01.md"),
        ("docs/canon/10_paper_provenance.md", "exectv2_evaluation_canon.md", "04_scoring.md"),
        ("docs/canon/10_paper_provenance.md", "gan2026/GAN2026_RESEARCH_CANON.md", "06_gan_clinical_policy.md"),
        ("docs/canon/10_paper_provenance.md", "exectv2_gepa_canon.md", "08_gepa.md"),
        ("docs/canon/10_paper_provenance.md", "../experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md", "07_exect_plan11.md"),
        ("docs/canon/10_paper_provenance.md", "GAN2026_RESEARCH_CANON.md", "06_gan_clinical_policy.md"),
        ("docs/canon/10_paper_provenance.md", "contribution_thesis.md", "../research/contribution_thesis.md"),
        ("docs/canon/10_paper_provenance.md", "closing_stage_research_critique_2026-06-27.md", "../research/closing_stage_research_critique_2026-06-27.md"),
        ("docs/canon/10_paper_provenance.md", "supervisor_brief_conformance_audit_2026-07-01.md", "../research/supervisor_brief_conformance_audit_2026-07-01.md"),
        # 04_scoring
        ("docs/canon/04_scoring.md", "exectv2_gold_representation_and_scoring_principles_2026-06-17.md", "../research/exectv2_gold_representation_and_scoring_principles_2026-06-17.md"),
        ("docs/canon/04_scoring.md", "exectv2_benchmark_surface_overall_2026-06-18.md", "../research/exectv2_benchmark_surface_overall_2026-06-18.md"),
        ("docs/canon/04_scoring.md", "exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md", "../research/exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md"),
        ("docs/canon/04_scoring.md", "paper_drafts/", "../research/paper_drafts/"),
        ("docs/canon/04_scoring.md", "exectv2_cost_quality_matched_split_table_2026-07-01.md", "../research/exectv2_cost_quality_matched_split_table_2026-07-01.md"),
        ("docs/canon/04_scoring.md", "PAPER_CANON.md", "10_paper_provenance.md"),
        ("docs/canon/04_scoring.md", "exectv2_final_key_family_architecture_synthesis_2026-06-18.md", "../research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md"),
        ("docs/canon/04_scoring.md", "exectv2_data_discoveries_log.md", "../research/exectv2_data_discoveries_log.md"),
        ("docs/canon/04_scoring.md", "../experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md", "07_exect_plan11.md"),
        ("docs/canon/04_scoring.md", "exectv2_gepa_canon.md", "08_gepa.md"),
        # 06_gan
        ("docs/canon/06_gan_clinical_policy.md", "retrospectives/", "../research/gan2026/retrospectives/"),
        ("docs/canon/06_gan_clinical_policy.md", "syntheses/", "../research/gan2026/syntheses/"),
        ("docs/canon/06_gan_clinical_policy.md", "error_analysis/", "../research/gan2026/error_analysis/"),
        ("docs/canon/06_gan_clinical_policy.md", "../wall_transfer_forward_observable_feature_inventory_2026-06-27.md", "../research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md"),
        ("docs/canon/06_gan_clinical_policy.md", "../PAPER_CANON.md", "10_paper_provenance.md"),
        ("docs/canon/06_gan_clinical_policy.md", "PAPER_CANON.md", "10_paper_provenance.md"),
        ("docs/canon/06_gan_clinical_policy.md", "../experiments/gan2026/", "../experiments/gan2026/"),
        ("docs/canon/06_gan_clinical_policy.md", "contribution_thesis.md", "../research/contribution_thesis.md"),
        ("docs/canon/06_gan_clinical_policy.md", "../exectv2_evaluation_canon.md", "04_scoring.md"),
        ("docs/canon/06_gan_clinical_policy.md", "exectv2_evaluation_canon.md", "04_scoring.md"),
        # 07_exect
        ("docs/canon/07_exect_plan11.md", "key_entities/", "../experiments/exectv2/key_entities/"),
        ("docs/canon/07_exect_plan11.md", "reliability/", "../experiments/exectv2/reliability/"),
        ("docs/canon/07_exect_plan11.md", "../final_artifact_index_2026-06-22.md", "../experiments/final_artifact_index_2026-06-22.md"),
        ("docs/canon/07_exect_plan11.md", "../../research/exectv2_evaluation_canon.md", "04_scoring.md"),
        ("docs/canon/07_exect_plan11.md", "../../research/PAPER_CANON.md", "10_paper_provenance.md"),
        ("docs/canon/07_exect_plan11.md", "key_entities/exectv2_cross_model_closeout_2026-06-22.md", "../experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md"),
        # 08_gepa
        ("docs/canon/08_gepa.md", "exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md", "../research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md"),
        ("docs/canon/08_gepa.md", "PAPER_CANON.md", "10_paper_provenance.md"),
        ("docs/canon/08_gepa.md", "exectv2_evaluation_canon.md", "04_scoring.md"),
        ("docs/canon/08_gepa.md", "../experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md", "07_exect_plan11.md"),
    ]
    for rel_path, old, new in replacements:
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")


def create_redirect_stubs() -> None:
    stubs = [
        ("docs/research/PAPER_CANON.md", "docs/canon/10_paper_provenance.md", "Paper Canon"),
        ("docs/research/exectv2_evaluation_canon.md", "docs/canon/04_scoring.md", "ExECTv2 Evaluation Canon"),
        ("docs/research/gan2026/GAN2026_RESEARCH_CANON.md", "docs/canon/06_gan_clinical_policy.md", "Gan 2026 Research Canon"),
        ("docs/experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md", "docs/canon/07_exect_plan11.md", "ExECTv2 Closeout Evidence Canon"),
        ("docs/research/exectv2_gepa_canon.md", "docs/canon/08_gepa.md", "ExECTv2 GEPA Canon"),
    ]
    for old_rel, new_rel, title in stubs:
        old_path = ROOT / old_rel
        new_path = ROOT / new_rel
        import os

        new_link = os.path.relpath(new_path, old_path.parent)
        old_path.write_text(
            REDIRECT_TEMPLATE.format(title=title, new_path=new_rel, new_rel=new_link),
            encoding="utf-8",
        )


def archive_stubbed_files() -> list[str]:
    """Move Wave 3 stubbed files to docs/archive and leave redirect stubs."""
    moved: list[str] = []
    buckets = [
        (
            ROOT / "docs/experiments/gan2026/validation750",
            ROOT / "docs/archive/experiments/gan2026/validation750",
            "../VALIDATION750_CANON.md",
            "VALIDATION750_CANON",
        ),
        (
            ROOT / "docs/experiments/gan2026/rq_series",
            ROOT / "docs/archive/experiments/gan2026/rq_series",
            "../COMPONENT_MECHANICS_CANON.md",
            "COMPONENT_MECHANICS_CANON",
        ),
        (
            ROOT / "docs/experiments/exectv2/key_entities",
            ROOT / "docs/archive/experiments/exectv2/key_entities",
            "../HOLISTIC_ASSEMBLY_LADDER_CANON.md",
            "HOLISTIC_ASSEMBLY_LADDER_CANON",
        ),
    ]
    import os

    for src_dir, archive_dir, canon_rel, canon_name in buckets:
        archive_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(src_dir.glob("*.md")):
            if path.name.endswith("_CANON.md"):
                continue
            if path.name.startswith("exectv2_holistic_finding_assembly_v08"):
                continue
            text = path.read_text(encoding="utf-8")
            if "Superseded for navigation" not in text:
                continue
            dest = archive_dir / path.name
            subprocess.run(["git", "mv", str(path), str(dest)], check=True, cwd=ROOT)
            archive_rel = os.path.relpath(dest, path.parent)
            stub = ARCHIVE_REDIRECT.format(
                archive_rel=archive_rel,
                canon_name=canon_name + ".md",
                canon_rel=canon_rel,
            )
            path.write_text(stub, encoding="utf-8")
            moved.append(str(path.relative_to(ROOT)))
    return moved


def stub_workstream_sources(canon_path: Path, glob_pattern: str, exclude: set[str] | None = None) -> int:
    exclude = exclude or set()
    count = 0
    import os

    canon_rel = os.path.relpath(canon_path, ROOT)
    for path in sorted(ROOT.glob(glob_pattern)):
        if path.name in exclude or path.name.endswith("_CANON.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if "Superseded for navigation" in text:
            continue
        rel_canon = os.path.relpath(canon_path, path.parent)
        banner = f"> **Superseded for navigation —** canonical summary: [`{canon_path.name}`]({rel_canon}). Full detail retained below.\n\n"
        path.write_text(banner + text, encoding="utf-8")
        count += 1
    return count


def main() -> None:
    fix_moved_canon_links()
    create_redirect_stubs()
    moved = archive_stubbed_files()
    print(f"Archived {len(moved)} files")
    n = stub_workstream_sources(
        ROOT / "docs/canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md",
        "docs/experiments/exectv2/diagnosis/*.md",
    )
    n += stub_workstream_sources(
        ROOT / "docs/canon/workstreams/SF_ADJUDICATOR_LADDER_CANON.md",
        "docs/experiments/exectv2/seizure_frequency/exectv2_sf_state_adjudicator_v*.md",
    )
    n += stub_workstream_sources(
        ROOT / "docs/canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md",
        "docs/experiments/exectv2/reliability/exectv2_2call_no_sf_self_consistency*.md",
    )
    print(f"Stubbed {n} workstream source files")


if __name__ == "__main__":
    main()
