#!/usr/bin/env python3
"""Build gold-label-only task taxonomy inventories for Gan 2026 and ExECTv2.

No model predictions. Counts are recomputed from the frozen corpora and split
manifests. Report owners live under docs/research/.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.evaluation import (
    ENTITY_CLINICAL_RECOVERY_CLASSES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    classify_boundary_families,
    map_pragmatic,
    map_purist,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
KEY_FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)

_MULTIPLE_WORD_RE = re.compile(r"\bmultiple\b", re.IGNORECASE)


def _gan_shape_flags(label: str) -> dict[str, bool]:
    text = label.lower().strip()
    return {
        "is_range": " to " in text,
        "is_cluster": "cluster" in text,
        "is_multiple_word": bool(_MULTIPLE_WORD_RE.search(text)),
        "is_seizure_free": text.startswith("seizure free"),
        "is_unknown_exact": text == "unknown",
        "is_no_reference": text == "no seizure frequency reference",
        "has_per": " per " in text,
    }


def _gan_bucket(kind: str, flags: dict[str, bool]) -> str:
    if kind == "frequency" and flags["is_cluster"]:
        return "cluster_burden"
    if kind == "frequency" and flags["is_range"]:
        return "range_rate"
    if kind == "frequency" and flags["is_multiple_word"]:
        return "multiple_word_frequency"
    if kind == "frequency":
        return "ordinary_point_rate"
    if kind == "seizure_free":
        return "seizure_free"
    if kind == "unknown":
        return "unknown_sentinel"
    if kind == "no_reference":
        return "no_reference_sentinel"
    if kind == "unresolved_multiple":
        return "unresolved_multiple"
    return "other"


def _gan_inventory(records: list) -> dict:
    kind_c: Counter[str] = Counter()
    band_c: Counter[str] = Counter()
    purist_c: Counter[str] = Counter()
    pragmatic_c: Counter[str] = Counter()
    shape_c: Counter[str] = Counter()
    family_c: Counter[str] = Counter()
    combo: Counter[str] = Counter()
    label_c: Counter[str] = Counter()
    row_ok_false = 0
    for record in records:
        kind = record.gold_label_kind.value
        kind_c[kind] += 1
        monthly = record.gold_monthly_frequency
        band_c[boundary_band(monthly)] += 1
        purist_c[map_purist(monthly)] += 1
        pragmatic_c[map_pragmatic(monthly)] += 1
        flags = _gan_shape_flags(record.gold_label)
        for key, value in flags.items():
            if value:
                shape_c[key] += 1
        for family in classify_boundary_families(
            note_text=record.note_text,
            gold_per_month=monthly,
        ):
            family_c[family] += 1
        combo[_gan_bucket(kind, flags)] += 1
        label_c[record.gold_label] += 1
        if not record.row_ok:
            row_ok_false += 1
    return {
        "n": len(records),
        "row_ok_false": row_ok_false,
        "gold_label_kind": dict(kind_c.most_common()),
        "boundary_band": dict(band_c.most_common()),
        "purist": dict(purist_c.most_common()),
        "pragmatic": dict(pragmatic_c.most_common()),
        "shape_flags": dict(shape_c.most_common()),
        "boundary_families": dict(family_c.most_common()),
        "a_priori_buckets": dict(combo.most_common()),
        "unique_labels": len(label_c),
        "top_labels": [{"label": key, "n": value} for key, value in label_c.most_common(15)],
    }


def build_gan_artifact() -> dict:
    artifact = {
        "artifact_id": "gan2026.gold_task_taxonomy.v1",
        "date": REPORT_DATE,
        "dataset": "synthetic_data_subset_1500",
        "claim_boundary": (
            "Gold-label inventory only. No model predictions. "
            "Not performance or generalization evidence."
        ),
        "split_prose_aliases": {
            "train": "train300",
            "validation": "dev750",
            "test": "test450",
        },
        "full1500": _gan_inventory(load_records_with_monthly_frequency()),
    }
    for split in ("train", "validation", "test"):
        artifact[split] = _gan_inventory(load_records_for_split(split))
    return artifact


def _exect_letter_bucket(dx: int, sf: int, rx: int, inv: int) -> str:
    counts = (dx, sf, rx, inv)
    n_families = sum(1 for count in counts if count)
    multi_any = any(count >= 2 for count in counts)
    if n_families == 0:
        return "no_four_family_gold"
    if sf == 0 and n_families >= 1:
        if multi_any:
            return "present_families_multi_mention_empty_sf"
        return "present_families_single_mention_empty_sf"
    if multi_any:
        return "multi_mention_with_sf"
    if n_families >= 3:
        return "broad_single_mention_with_sf"
    if n_families == 1:
        return "single_family_single_mention_with_sf"
    return "sparse_multi_family_single_mention_with_sf"


def _sf_mention_bucket(attributes: dict[str, str]) -> str:
    count_values = [
        attributes[key]
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
        if key in attributes
    ]
    has_count = bool(count_values)
    has_cadence = "TimePeriod" in attributes or any(
        "TimePeriod" in key for key in attributes
    )
    has_change = "FrequencyChange" in attributes
    has_anchor = any(
        key in attributes
        for key in (
            "PointInTime",
            "TimeSince_or_TimeOfEvent",
            "YearDate",
            "MonthDate",
            "DayDate",
        )
    )
    if has_count and all(value in {"", "0"} for value in count_values):
        return "seizure_free"
    if has_count and has_cadence:
        return "numeric_cadence_rate"
    if has_count and has_anchor and not has_cadence:
        return "count_in_named_window"
    if has_change and not has_count:
        return "qualitative_frequency_change"
    if has_change and has_count:
        return "numeric_plus_frequency_change"
    if has_anchor and not has_count:
        return "temporal_anchor_without_count"
    if has_count:
        return "count_without_cadence_or_anchor"
    return "sparse_or_other"


def _exect_inventory(letters: list) -> dict:
    nine = [entity.name for entity in ALL_ENTITIES]
    four = list(KEY_FAMILIES)
    entity_mentions: Counter[str] = Counter()
    letters_with: Counter[str] = Counter()
    multi: Counter[str] = Counter()
    absent: Counter[str] = Counter()
    diag_cat: Counter[str] = Counter()
    sf_freq_change: Counter[str] = Counter()
    sf_time_period: Counter[str] = Counter()
    rx_freq: Counter[str] = Counter()
    inv_modalities: Counter[str] = Counter()
    letter_profiles: Counter[str] = Counter()
    four_family_counts: list[int] = []
    buckets: Counter[str] = Counter()
    sf_mention_buckets: Counter[str] = Counter()
    dx_multiplicity: Counter[str] = Counter()
    rx_completeness: Counter[str] = Counter()

    for letter in letters:
        present_four: list[str] = []
        counts = {entity: len(letter.entities(entity)) for entity in nine}
        for entity in nine:
            n = counts[entity]
            entity_mentions[entity] += n
            if n:
                letters_with[entity] += 1
            if n >= 2:
                multi[entity] += 1
            if n == 0:
                absent[entity] += 1
            if entity in four and n:
                present_four.append(entity)
            if entity == "Diagnosis":
                for annotation in letter.entities(entity):
                    diag_cat[annotation.attributes.get("DiagCategory", "<missing>")] += 1
                if n == 0:
                    dx_multiplicity["absent"] += 1
                elif n == 1:
                    dx_multiplicity["single"] += 1
                else:
                    dx_multiplicity["multi"] += 1
            if entity == "SeizureFrequency":
                for annotation in letter.entities(entity):
                    frequency_change = annotation.attributes.get("FrequencyChange")
                    if frequency_change:
                        sf_freq_change[frequency_change] += 1
                    time_period = annotation.attributes.get("TimePeriod")
                    if time_period:
                        sf_time_period[time_period] += 1
                    sf_mention_buckets[_sf_mention_bucket(annotation.attributes)] += 1
            if entity == "Prescription":
                for annotation in letter.entities(entity):
                    frequency = annotation.attributes.get("Frequency")
                    if frequency:
                        rx_freq[frequency] += 1
                    has_drug = bool(annotation.attributes.get("DrugName") or annotation.text)
                    has_dose = bool(annotation.attributes.get("DrugDose"))
                    has_unit = bool(annotation.attributes.get("DoseUnit"))
                    has_freq = bool(frequency)
                    if has_drug and has_dose and has_unit and has_freq:
                        rx_completeness["complete_regimen_attrs"] += 1
                    elif frequency == "As_Required":
                        rx_completeness["rescue_as_required"] += 1
                    else:
                        rx_completeness["incomplete_or_partial"] += 1
            if entity == "Investigations":
                for annotation in letter.entities(entity):
                    for modality in ("MRI", "CT", "EEG"):
                        if annotation.attributes.get(f"{modality}_Performed"):
                            inv_modalities[modality] += 1
        profile = ",".join(present_four) if present_four else "none"
        letter_profiles[profile] += 1
        four_family_counts.append(len(present_four))
        buckets[
            _exect_letter_bucket(
                counts["Diagnosis"],
                counts["SeizureFrequency"],
                counts["Prescription"],
                counts["Investigations"],
            )
        ] += 1

    return {
        "n_letters": len(letters),
        "entity_mentions": dict(entity_mentions.most_common()),
        "letters_with_entity": dict(letters_with.most_common()),
        "letters_multi_mention": dict(multi.most_common()),
        "letters_absent": dict(absent.most_common()),
        "diag_category": dict(diag_cat.most_common()),
        "diag_letter_multiplicity": dict(dx_multiplicity.most_common()),
        "sf_frequency_change": dict(sf_freq_change.most_common()),
        "sf_time_period": dict(sf_time_period.most_common()),
        "sf_mention_buckets": dict(sf_mention_buckets.most_common()),
        "rx_frequency": dict(rx_freq.most_common()),
        "rx_completeness": dict(rx_completeness.most_common()),
        "inv_modality_mentions": dict(inv_modalities.most_common()),
        "four_family_presence_profiles_top": [
            {"profile": key, "n": value} for key, value in letter_profiles.most_common(20)
        ],
        "four_family_count_per_letter": dict(Counter(four_family_counts).most_common()),
        "a_priori_letter_buckets": dict(buckets.most_common()),
        "recovery_class_by_entity": dict(ENTITY_CLINICAL_RECOVERY_CLASSES),
        "key_families": four,
        "all_entities": nine,
    }


def build_exect_artifact() -> dict:
    return {
        "artifact_id": "exectv2.gold_task_taxonomy.v1",
        "date": REPORT_DATE,
        "dataset": "ExECTv2 Json EA0001-EA0200",
        "split_manifest": "exectv2_split_v2",
        "claim_boundary": (
            "Gold-label inventory only. No model predictions. "
            "Comparison surface is four-family clinical fact F1; "
            "nine-entity inventory is corpus context only."
        ),
        "split_prose_aliases": {
            "dev": "dev140",
            "test": "test60 (59 letters under exectv2_split_v2)",
        },
        "full200": _exect_inventory(load_letters()),
        "dev": _exect_inventory(load_letters_for_split("dev")),
        "test": _exect_inventory(load_letters_for_split("test")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "experiments",
        help="Directory for JSON artifacts",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    gan_path = args.output_dir / f"gan2026_gold_task_taxonomy_{DATE_STAMP}.json"
    exect_path = args.output_dir / f"exectv2_gold_task_taxonomy_{DATE_STAMP}.json"
    gan_path.write_text(json.dumps(build_gan_artifact(), indent=2) + "\n", encoding="utf-8")
    exect_path.write_text(json.dumps(build_exect_artifact(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {gan_path.relative_to(REPO_ROOT)}")
    print(f"wrote {exect_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
