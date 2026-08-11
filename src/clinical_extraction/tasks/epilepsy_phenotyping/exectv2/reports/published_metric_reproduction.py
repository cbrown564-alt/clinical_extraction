"""Produce a no-call ExECTv2 published-metric reproduction artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from importlib.metadata import version
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.benchmark_constants import (
    PAPER_OVERALL_PER_ITEM,
    PAPER_OVERALL_PER_LETTER,
    PAPER_PER_ITEM_F1,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    sha256_file,
    write_artifact_bundle,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_overall,
    semantic_config_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.published import (
    evaluated_attributes,
    score_published_metrics,
)

HYPOTHESIS_ID = "exectv2_published_metric_reproduction_2026-07-14"
SCORER_VERSION = "exectv2_published_metrics_v1"
PAPER_DOI = "10.1186/s13326-024-00316-z"
PUBLISHED_ENTITIES = tuple(PAPER_PER_ITEM_F1)


def build_published_metric_report(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    *,
    entities: Sequence[str],
    candidate_name: str,
    split: str,
    generated_on: str,
    source_revision: str,
    dirty_tree: bool,
    python_version: str,
    dependency_versions: Mapping[str, str],
    split_manifest: str,
    split_manifest_sha256: str,
) -> dict[str, Any]:
    """Build the machine-readable evidence object without reading or writing files."""

    entity_names = tuple(dict.fromkeys(entities))
    published = score_published_metrics(gold_letters, pred_letters, entity_names)
    existing_scores = {
        "phrase_only_micro": score_overall(
            gold_letters,
            pred_letters,
            entity_names,
            lambda _entity: PHRASE_ONLY,
        ),
        "semantic_micro": score_overall(
            gold_letters,
            pred_letters,
            entity_names,
            semantic_config_for,
        ),
        "benchmark_micro": score_overall(
            gold_letters,
            pred_letters,
            entity_names,
            benchmark_config_for,
        ),
    }
    complete_coverage = len(entity_names) == len(PUBLISHED_ENTITIES) and set(entity_names) == set(
        PUBLISHED_ENTITIES
    )
    scores = published.model_dump(mode="json")
    mechanism = _mechanism_analysis(gold_letters, pred_letters, entity_names)
    return {
        "schema_version": 1,
        "scorer_version": SCORER_VERSION,
        "hypothesis_id": HYPOTHESIS_ID,
        "generated_on": generated_on,
        "source": {
            "revision": source_revision,
            "dirty_tree": dirty_tree,
            "python": python_version,
            "dependencies": dict(dependency_versions),
        },
        "dataset": "ExECTv2 synthetic clinic letters",
        "split": split,
        "split_manifest": split_manifest,
        "split_manifest_sha256": split_manifest_sha256,
        "row_count": len(gold_letters),
        "row_policy": "all rows in the named development split; no test60 inspection",
        "candidate": candidate_name,
        "model": "none",
        "prompt_program": "none",
        "call_mode": "no_call_deterministic_replay",
        "repair_policy": (
            "candidate output fixed before scoring; scorer performs format-only canonicalization"
        ),
        "entities": list(entity_names),
        "metric_definitions": {
            "normalized_phrase": "entity plus normalized selected text",
            "cui": "entity plus non-empty UMLS CUI; missing CUIs never match",
            "all_features": (
                "entity plus non-empty CUI and all evaluated attributes; CUIPhrase excluded; "
                "Certainty evaluated only for Diagnosis and PatientHistory; Negation evaluated "
                "only for PatientHistory"
            ),
            "per_item": "multiset mention matching within letter, micro-aggregated per entity",
            "per_letter": "entity is correct when at least one feature-complete mention matches",
            "overall": "unweighted macro mean across entity scores, matching paper Table 1",
        },
        "paper_reference": {
            "doi": PAPER_DOI,
            "scope": "original ExECTv2 validation on full200 with all nine entities",
            "overall_per_item_f1": PAPER_OVERALL_PER_ITEM,
            "overall_per_letter_f1": PAPER_OVERALL_PER_LETTER,
            "per_entity_item_f1": dict(PAPER_PER_ITEM_F1),
        },
        "development_result": {
            "entity_coverage": f"{len(entity_names)}/{len(PUBLISHED_ENTITIES)}",
            "paper_comparable_nine_entity_overall": complete_coverage,
            "scores": {
                key: value
                for key, value in scores.items()
                if key in {"normalized_phrase", "cui", "all_features"}
            },
            "missing_cui": scores["missing_cui"],
            "representation_deltas": _representation_deltas(scores, entity_names),
            "mechanism_counts": mechanism["counts"],
            "mechanism_examples": mechanism["examples"],
        },
        "existing_score_regression": {
            name: score.model_dump(mode="json") for name, score in existing_scores.items()
        },
        "claim_boundary": (
            "Development evidence that the repository implements the paper-derived metric family. "
            "This is not a reproduction of the original ExECTv2 system's score, independent "
            "clinical validation, or holdout evidence."
        ),
    }


def render_published_metric_report(report: Mapping[str, Any], *, json_path: str) -> str:
    result = report["development_result"]
    scores = result["scores"]
    lines = [
        "# ExECTv2 published-metric reproduction",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- JSON: `{json_path}`",
        f"- Candidate: `{report['candidate']}`",
        f"- Split: `{report['split']}` ({report['row_count']} rows)",
        f"- Entity coverage: `{result['entity_coverage']}`",
        f"- Scorer: `{report['scorer_version']}`",
        f"- Mode: `{report['call_mode']}`",
        "",
        "## Result",
        "",
        "| View | Macro per-item F1 | Macro per-letter F1 |",
        "| --- | ---: | ---: |",
    ]
    for view in ("normalized_phrase", "cui", "all_features"):
        lines.append(
            f"| {view} | {scores[view]['macro_per_item']['f1']:.4f} "
            f"| {scores[view]['macro_per_letter']['f1']:.4f} |"
        )
    lines.extend(
        [
            "",
            "The paper's original ExECTv2 reference is 0.87 per item and 0.90 per letter "
            "across nine entities. This development replay is not a reproduction of the original "
            "ExECTv2 system; it reproduces the documented measurement family on the named "
            "candidate.",
            "",
            "## Per-entity representation layers",
            "",
            "| Entity | Phrase F1 | CUI F1 | All-features F1 | Phrase→CUI | "
            "CUI→features | Missing CUI gold/pred |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    deltas = result["representation_deltas"]
    missing = result["missing_cui"]["by_entity"]
    for entity in report["entities"]:
        phrase = scores["normalized_phrase"]["per_entity"][entity]["per_item"]["f1"]
        cui = scores["cui"]["per_entity"][entity]["per_item"]["f1"]
        features = scores["all_features"]["per_entity"][entity]["per_item"]["f1"]
        lines.append(
            f"| {entity} | {phrase:.4f} | {cui:.4f} | {features:.4f} "
            f"| {deltas[entity]['phrase_to_cui']:+.4f} "
            f"| {deltas[entity]['cui_to_all_features']:+.4f} "
            f"| {missing[entity]['gold']}/{missing[entity]['predicted']} |"
        )
    lines.extend(
        [
            "",
            "## Permitted development-row mechanism examples",
            "",
            "Counts: "
            + ", ".join(
                f"`{category}`={count}"
                for category, count in result["mechanism_counts"].items()
            ),
            "",
            "| Entity | Category | Letter | Gold → predicted phrase | CUI | Differing features |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for example in result["mechanism_examples"]:
        phrase_change = f"{example['gold_phrase']} → {example['predicted_phrase']}"
        differing = ", ".join(example["differing_attribute_names"]) or "—"
        cui = example["cui"] or f"{example['gold_cui']} → {example['predicted_cui']}"
        lines.append(
            f"| {example['entity']} | {example['category']} | {example['letter_id']} "
            f"| {phrase_change} | {cui} | {differing} |"
        )
    lines.extend(
        [
            "",
            "## Existing-score regression",
            "",
            "| Existing view | Micro per-item F1 | Micro per-letter F1 |",
            "| --- | ---: | ---: |",
        ]
    )
    for name, score in report["existing_score_regression"].items():
        lines.append(
            f"| {name} | {score['per_item']['f1']:.4f} | {score['per_letter']['f1']:.4f} |"
        )
    lines.extend(["", "## Claim boundary", "", str(report["claim_boundary"]), ""])
    return "\n".join(lines)


def write_deterministic_dev140_reproduction(
    *,
    out_json: Path,
    out_md: Path,
    generated_on: str,
) -> dict[str, Any]:
    """Run the all-nine deterministic reference on dev140 and write both artifacts."""

    gold_letters = load_letters_for_split("dev")
    predictions = run_all9_on_letters(gold_letters)
    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predictions, gold_letters, strict=True)
    ]
    report = build_published_metric_report(
        gold_letters,
        pred_letters,
        entities=PUBLISHED_ENTITIES,
        candidate_name="exectv2_deterministic_all9",
        split="dev140",
        generated_on=generated_on,
        source_revision=_git_revision(),
        dirty_tree=_git_dirty(),
        python_version=sys.version.split()[0],
        dependency_versions={
            "pydantic": version("pydantic"),
            "pyyaml": version("pyyaml"),
        },
        split_manifest=DEFAULT_SPLIT_MANIFEST.as_posix(),
        split_manifest_sha256=sha256_file(DEFAULT_SPLIT_MANIFEST),
    )
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    markdown = render_published_metric_report(report, json_path=out_json.as_posix())
    write_artifact_bundle({out_json: json_text, out_md: markdown})
    return report


def _representation_deltas(
    scores: Mapping[str, Any],
    entities: Sequence[str],
) -> dict[str, dict[str, float]]:
    return {
        entity: {
            "phrase_to_cui": (
                scores["cui"]["per_entity"][entity]["per_item"]["f1"]
                - scores["normalized_phrase"]["per_entity"][entity]["per_item"]["f1"]
            ),
            "cui_to_all_features": (
                scores["all_features"]["per_entity"][entity]["per_item"]["f1"]
                - scores["cui"]["per_entity"][entity]["per_item"]["f1"]
            ),
        }
        for entity in entities
    }


def _mechanism_analysis(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> dict[str, Any]:
    """Summarize representation-layer transitions on permitted development rows."""

    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    counts: Counter[str] = Counter()
    examples: dict[tuple[str, str], dict[str, Any]] = {}
    for letter_id in sorted(gold_by_id.keys() | pred_by_id.keys()):
        gold_letter = gold_by_id.get(letter_id)
        pred_letter = pred_by_id.get(letter_id)
        for entity in entities:
            gold = gold_letter.entities(entity) if gold_letter is not None else ()
            pred = pred_letter.entities(entity) if pred_letter is not None else ()
            gold_by_cui = _group_by_cui(gold)
            pred_by_cui = _group_by_cui(pred)
            for cui in sorted(gold_by_cui.keys() & pred_by_cui.keys()):
                gold_group = gold_by_cui[cui]
                pred_group = pred_by_cui[cui]
                if _phrases(gold_group).isdisjoint(_phrases(pred_group)):
                    _record_mechanism(
                        counts,
                        examples,
                        category="phrase_miss_cui_match",
                        letter_id=letter_id,
                        entity=entity,
                        cui=cui,
                        gold=gold_group[0],
                        pred=pred_group[0],
                    )
                if _feature_bundles(gold_group).isdisjoint(_feature_bundles(pred_group)):
                    _record_mechanism(
                        counts,
                        examples,
                        category="cui_match_feature_miss",
                        letter_id=letter_id,
                        entity=entity,
                        cui=cui,
                        gold=gold_group[0],
                        pred=pred_group[0],
                    )
            gold_by_phrase = _group_by_phrase(gold)
            pred_by_phrase = _group_by_phrase(pred)
            for phrase in sorted(gold_by_phrase.keys() & pred_by_phrase.keys()):
                gold_group = gold_by_phrase[phrase]
                pred_group = pred_by_phrase[phrase]
                if _cuis(gold_group).isdisjoint(_cuis(pred_group)):
                    _record_mechanism(
                        counts,
                        examples,
                        category="phrase_match_cui_miss",
                        letter_id=letter_id,
                        entity=entity,
                        cui="",
                        gold=gold_group[0],
                        pred=pred_group[0],
                    )
    return {
        "counts": dict(sorted(counts.items())),
        "examples": list(examples.values()),
    }


def _record_mechanism(
    counts: Counter[str],
    examples: dict[tuple[str, str], dict[str, Any]],
    *,
    category: str,
    letter_id: str,
    entity: str,
    cui: str,
    gold: Any,
    pred: Any,
) -> None:
    counts[category] += 1
    gold_attributes = dict(evaluated_attributes(gold))
    pred_attributes = dict(evaluated_attributes(pred))
    differing = sorted(
        key
        for key in gold_attributes.keys() | pred_attributes.keys()
        if key != "CUI" and gold_attributes.get(key) != pred_attributes.get(key)
    )
    examples.setdefault(
        (entity, category),
        {
            "category": category,
            "letter_id": letter_id,
            "entity": entity,
            "cui": cui,
            "gold_phrase": _phrase(gold),
            "predicted_phrase": _phrase(pred),
            "gold_cui": str(gold.attributes.get("CUI", "")),
            "predicted_cui": str(pred.attributes.get("CUI", "")),
            "differing_attribute_names": differing,
        },
    )


def _group_by_cui(annotations: Sequence[Any]) -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = {}
    for annotation in annotations:
        cui = str(annotation.attributes.get("CUI", "")).strip()
        if cui:
            grouped.setdefault(cui, []).append(annotation)
    return grouped


def _group_by_phrase(annotations: Sequence[Any]) -> dict[str, list[Any]]:
    grouped: dict[str, list[Any]] = {}
    for annotation in annotations:
        grouped.setdefault(_phrase(annotation), []).append(annotation)
    return grouped


def _phrase(annotation: Any) -> str:
    source = annotation.raw_text if annotation.raw_text is not None else annotation.text
    return normalize_phrase(source)


def _phrases(annotations: Sequence[Any]) -> set[str]:
    return {_phrase(annotation) for annotation in annotations}


def _cuis(annotations: Sequence[Any]) -> set[str]:
    return {
        str(annotation.attributes.get("CUI", "")).strip()
        for annotation in annotations
        if str(annotation.attributes.get("CUI", "")).strip()
    }


def _feature_bundles(annotations: Sequence[Any]) -> set[tuple[tuple[str, str], ...]]:
    return {tuple(sorted(evaluated_attributes(annotation).items())) for annotation in annotations}



def _git_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


__all__ = [
    "HYPOTHESIS_ID",
    "PUBLISHED_ENTITIES",
    "SCORER_VERSION",
    "build_published_metric_report",
    "render_published_metric_report",
    "write_deterministic_dev140_reproduction",
]
