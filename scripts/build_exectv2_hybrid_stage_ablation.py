#!/usr/bin/env python3
"""ExECTv2 llm_with_rules band + first-changer stage ablation.

True ordered no-call replay from retained structured JSONL. See
docs/research/exectv2/hybrid_stage_ablation_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses import (
    LensPolicy,
    lens_from_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    manifest_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.producers import (
    SavedJsonlProducer,
    findings_from_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection,
    sf_unknown_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as kes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (
    TARGET_ENTITIES,
    _direct_sf_row,
    _manifest_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    headline_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_KEY = 2

_CATALOG_PATH = REPO_ROOT / "scripts/build_exectv2_family_error_catalog.py"
_SPEC = importlib.util.spec_from_file_location("exect_family_error_catalog", _CATALOG_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_CATALOG_PATH}")
cat = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cat)
hs = cat.hs

MODEL_PREFERENCE = cat.MODEL_PREFERENCE
FAMILIES = cat.FAMILIES

BAND_ORDER = (
    "post_flatten",
    "producer_gate",
    "sf_clinical",
    "diagnosis_lens",
    "prescription_lens",
    "investigations_lens",
    "evidence_gate",
)

BAND_LABELS = {
    "post_flatten": "After flatten (pre-gate)",
    "producer_gate": "After producer gate",
    "sf_clinical": "After SF clinical",
    "diagnosis_lens": "After Diagnosis lens",
    "prescription_lens": "After Prescription lens",
    "investigations_lens": "After Investigations lens",
    "evidence_gate": "After evidence gate / final",
}

STAGE_ORDER = (
    "project_and_gate",
    "sf_state_projection",
    "sf_unknown_suppression",
    "lens.diagnosis",
    "lens.seizure_frequency",
    "lens.prescription",
    "lens.investigations",
    "evidence_requirement",
)

STAGE_BAND = {
    "project_and_gate": "producer_gate",
    "sf_state_projection": "sf_clinical",
    "sf_unknown_suppression": "sf_clinical",
    "lens.diagnosis": "diagnosis_lens",
    "lens.seizure_frequency": "sf_clinical",
    "lens.prescription": "prescription_lens",
    "lens.investigations": "investigations_lens",
    "evidence_requirement": "evidence_gate",
}

LENS_STAGE = {
    "Diagnosis": "lens.diagnosis",
    "SeizureFrequency": "lens.seizure_frequency",
    "Prescription": "lens.prescription",
    "Investigations": "lens.investigations",
}

CONFIG = StructuredMethodConfig.selected()


def _structured_path(main_jsonl: Path) -> Path:
    return main_jsonl.with_name(main_jsonl.name.replace(".jsonl", "_structured.jsonl"))


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _mention_to_row(mention: Any) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _keys(mentions: list[dict[str, Any]], gold: list[dict[str, Any]], family: str) -> list[str]:
    return headline_keys(
        {"predicted_mentions": mentions, "gold_mentions": gold},
        family,
        field="predicted_mentions",
    )


def _mode(gold_keys: list[str], pred_keys: list[str]) -> str:
    return cat._mode(gold_keys, pred_keys)


def _exact(mode: str) -> bool:
    return mode.startswith("correct_")


def _key_sig(keys: list[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(keys).items()))


def _bundle_non_sf(
    gate_mentions: list[dict[str, Any]], sf_mentions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    out = [
        mention
        for mention in gate_mentions
        if str(mention.get("entity")) != "SeizureFrequency"
    ]
    out.extend(sf_mentions)
    return out


def _all_family_mentions(family_mentions: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for entity in TARGET_ENTITIES:
        out.extend(family_mentions[entity])
    return out


def _family_keys(
    mentions: list[dict[str, Any]], gold: list[dict[str, Any]]
) -> dict[str, list[str]]:
    return {family: _keys(mentions, gold, family) for family in FAMILIES}


def replay_letter(
    structured_row: dict[str, Any],
    letter: ExectLetter,
    *,
    gold_mentions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replay deterministic stages; record per-family keys after each hop."""

    events = structured_row.get("structured_events") or []
    if not events:
        empty = {family: [] for family in FAMILIES}
        return {
            "replayable": False,
            "reason": "empty_structured_events",
            "band_keys": {band: empty for band in BAND_ORDER},
            "stage_keys": {},
            "changes": [],
            "final_mentions": [],
            "evidence_ok": False,
        }

    record = kes.records.StructuredExtractionRecord.model_validate(
        {"clinical_events": events}
    )
    flattened = kes.parsing.mentions_from_events(record)
    flat_rows = [_mention_to_row(mention) for mention in flattened]
    projected, _gate_warnings = kes.projection.to_predicted_letter(
        letter.letter_id,
        flattened,
        note_text=letter.note_text,
        prompt_version=str(structured_row.get("prompt_version") or ""),
    )
    gate_rows = [_mention_to_row(mention) for mention in projected.mentions]

    structured_for_sf = dict(structured_row)
    structured_for_sf["predicted_mentions"] = gate_rows
    sf_direct = _direct_sf_row(structured_for_sf)
    sf_projected = sf_state_projection.project_row(
        sf_direct, ablation=CONFIG.sf_projection_ablation
    )
    sf_suppressed = sf_unknown_suppression.suppress_row(sf_projected)

    stage_mentions: dict[str, list[dict[str, Any]]] = {
        "flatten_events": flat_rows,
        "project_and_gate": gate_rows,
        "sf_state_projection": _bundle_non_sf(
            gate_rows, list(sf_projected.get("predicted_mentions") or [])
        ),
        "sf_unknown_suppression": _bundle_non_sf(
            gate_rows, list(sf_suppressed.get("predicted_mentions") or [])
        ),
    }

    manifest = manifest_from_mapping(
        _manifest_payload(
            Path("structured.jsonl"),
            Path("sf.jsonl"),
            row_count=1,
            config=CONFIG,
        )
    )
    producers = {
        producer_id: SavedJsonlProducer.from_manifest(producer_manifest)
        for producer_id, producer_manifest in manifest.producers.items()
    }
    source_rows = {
        "structured_key_family_event_ledger": {letter.letter_id: structured_for_sf},
        "sf_model_projection_suppression": {letter.letter_id: sf_suppressed},
    }

    store = ClinicalFindingStore(letter.letter_id, letter.note_text)
    family_mentions: dict[str, list[dict[str, Any]]] = {}
    for entity in TARGET_ENTITIES:
        lens_config = manifest.lenses[entity]
        producer = producers[lens_config.producer]
        row = source_rows[lens_config.producer][letter.letter_id]
        source = producer.source_for_row(
            row, source_lane=lens_config.source_lane or producer.source_lane
        )
        store.register_source(source)
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=entity,
                note_text=letter.note_text,
                source=source,
                raw_surface=True,
            )
        )
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=entity,
                note_text=letter.note_text,
                source=source,
                raw_surface=False,
            )
        )
        family_mentions[entity] = [
            finding.to_row()
            for finding in store.findings(
                entity=entity,
                producer_id=lens_config.producer,
                raw_surface=False,
            )
        ]

    current = {entity: list(rows) for entity, rows in family_mentions.items()}
    for entity in TARGET_ENTITIES:
        lens_config = manifest.lenses[entity]
        producer = producers[lens_config.producer]
        source_lane = lens_config.source_lane or producer.source_lane or lens_config.producer
        result = lens_from_manifest(lens_config).reconcile(
            store,
            policy=LensPolicy(
                producer_id=lens_config.producer,
                source_lane=source_lane,
                ownership_label=lens_config.ownership_label or producer.ownership_label,
                portability=lens_config.portability,
                diagnosis_policy_variant=CONFIG.diagnosis_policy_variant,
                prescription_policy_variant=CONFIG.prescription_policy_variant,
            ),
        )
        current[entity] = [finding.to_row() for finding in result.findings]
        stage_mentions[LENS_STAGE[entity]] = _all_family_mentions(current)

    final_mentions = _all_family_mentions(current)
    invalid = [
        mention
        for mention in final_mentions
        if not str(mention.get("evidence", ""))
        or str(mention.get("evidence", "")) not in letter.note_text
    ]
    evidence_ok = not invalid
    if evidence_ok:
        stage_mentions["evidence_requirement"] = final_mentions
    else:
        stage_mentions["evidence_requirement"] = []

    band_keys = {
        "post_flatten": _family_keys(stage_mentions["flatten_events"], gold_mentions),
        "producer_gate": _family_keys(stage_mentions["project_and_gate"], gold_mentions),
        "sf_clinical": _family_keys(
            stage_mentions["sf_unknown_suppression"], gold_mentions
        ),
        "diagnosis_lens": _family_keys(stage_mentions["lens.diagnosis"], gold_mentions),
        "prescription_lens": _family_keys(
            stage_mentions["lens.prescription"], gold_mentions
        ),
        "investigations_lens": _family_keys(
            stage_mentions["lens.investigations"], gold_mentions
        ),
        "evidence_gate": _family_keys(
            stage_mentions["evidence_requirement"], gold_mentions
        ),
    }

    # First-changer hops: compare consecutive prediction-bearing stages.
    prior_stage = "flatten_events"
    prior_keys = _family_keys(stage_mentions[prior_stage], gold_mentions)
    changes: list[dict[str, Any]] = []
    for stage in STAGE_ORDER:
        after_keys = _family_keys(stage_mentions[stage], gold_mentions)
        for family in FAMILIES:
            before = prior_keys[family]
            after = after_keys[family]
            if _key_sig(before) == _key_sig(after):
                continue
            gold_keys = headline_keys(
                {"gold_mentions": gold_mentions, "predicted_mentions": []},
                family,
                field="gold_mentions",
            )
            before_mode = _mode(gold_keys, before)
            after_mode = _mode(gold_keys, after)
            effect = "neutral"
            if _exact(after_mode) and not _exact(before_mode):
                effect = "rescue"
            elif _exact(before_mode) and not _exact(after_mode):
                effect = "harm"
            changes.append(
                {
                    "stage": stage,
                    "band": STAGE_BAND[stage],
                    "family": family,
                    "before_keys": before,
                    "after_keys": after,
                    "before_mode": before_mode,
                    "after_mode": after_mode,
                    "effect": effect,
                }
            )
        prior_keys = after_keys

    stage_keys = {
        stage: _family_keys(mentions, gold_mentions)
        for stage, mentions in stage_mentions.items()
        if stage in {"flatten_events", *STAGE_ORDER}
    }

    return {
        "replayable": True,
        "band_keys": band_keys,
        "stage_keys": stage_keys,
        "changes": changes,
        "final_mentions": final_mentions if evidence_ok else [],
        "evidence_ok": evidence_ok,
        "n_invalid_evidence": len(invalid),
    }


def _pathway_key(changes: list[dict[str, Any]], family: str) -> str:
    stages = [
        item["stage"].removeprefix("lens.").removeprefix("sf_")
        for item in changes
        if item["family"] == family
    ]
    if not stages:
        return "no_stage_change"
    return " → ".join(stages)


def _pick_examples(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(MODEL_PREFERENCE)
        effect_rank = 0 if row.get("effect") in {"rescue", "harm"} else 1
        return effect_rank, model_rank, str(row["letter_id"])

    picked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in sorted(candidates, key=sort_key):
        letter_id = str(row["letter_id"])
        if letter_id in seen:
            continue
        picked.append(row)
        seen.add(letter_id)
        if len(picked) >= EXAMPLES_PER_KEY:
            break
    return picked


def _count_modes(modes: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(modes).items(), key=lambda item: (-item[1], item[0])))


def _compact_keys(keys: list[str], *, limit: int = 6) -> list[str]:
    out = []
    for key in keys[:limit]:
        text = " ".join(str(key).split())
        if len(text) > 72:
            text = text[:71].rstrip() + "…"
        out.append(text)
    if len(keys) > limit:
        out.append(f"…(+{len(keys) - limit})")
    return out


def build_artifact() -> dict[str, Any]:
    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}

    band_mode_lists: dict[str, dict[str, list[str]]] = {
        family: {band: [] for band in BAND_ORDER} for family in FAMILIES
    }
    band_exact: dict[str, dict[str, int]] = {
        family: Counter() for family in FAMILIES
    }
    family_n: dict[str, int] = Counter()

    stage_stats: dict[str, dict[str, dict[str, Any]]] = {
        family: {
            stage: {
                "fires": 0,
                "first_changer": 0,
                "first_rescue": 0,
                "first_harm": 0,
                "any_rescue": 0,
                "any_harm": 0,
                "examples_rescue": [],
                "examples_harm": [],
            }
            for stage in STAGE_ORDER
        }
        for family in FAMILIES
    }
    band_first_changer: dict[str, Counter[str]] = {
        family: Counter() for family in FAMILIES
    }
    pathway_counter: dict[str, Counter[str]] = {family: Counter() for family in FAMILIES}
    pathway_examples: dict[str, dict[str, list[dict[str, Any]]]] = {
        family: defaultdict(list) for family in FAMILIES
    }
    residual: dict[str, Counter[str]] = {family: Counter() for family in FAMILIES}

    fidelity = {
        "replayable_rows": 0,
        "unreplayable_rows": 0,
        "evidence_gate_pass": 0,
        "evidence_gate_fail": 0,
        "key_exact_all_families": 0,
        "key_exact_by_family": Counter(),
        "letter_model_cells": 0,
    }

    for slug, display in hs.MODEL_SPECS:
        main_path = hs.EXECT_JSONL[slug]
        structured_path = _structured_path(main_path)
        main_rows = {
            str(row["letter_id"]): row for row in hs._read_jsonl(main_path)
        }
        structured_rows = hs._read_jsonl(structured_path)
        for structured_row in structured_rows:
            letter_id = str(structured_row["letter_id"])
            letter = letters[letter_id]
            main_row = main_rows[letter_id]
            gold = list(main_row.get("gold_mentions") or [])
            fidelity["letter_model_cells"] += 1
            replay = replay_letter(structured_row, letter, gold_mentions=gold)
            if not replay["replayable"]:
                fidelity["unreplayable_rows"] += 1
                continue
            fidelity["replayable_rows"] += 1
            if replay["evidence_ok"]:
                fidelity["evidence_gate_pass"] += 1
            else:
                fidelity["evidence_gate_fail"] += 1

            retained_keys = {
                family: headline_keys(main_row, family, field="predicted_mentions")
                for family in FAMILIES
            }
            final_keys = replay["band_keys"]["evidence_gate"]
            all_match = True
            for family in FAMILIES:
                if _key_sig(retained_keys[family]) == _key_sig(final_keys[family]):
                    fidelity["key_exact_by_family"][family] += 1
                else:
                    all_match = False
            fidelity["key_exact_all_families"] += int(all_match)

            for family in FAMILIES:
                family_n[family] += 1
                gold_keys = headline_keys(
                    {"gold_mentions": gold, "predicted_mentions": []},
                    family,
                    field="gold_mentions",
                )
                for band in BAND_ORDER:
                    pred_keys = replay["band_keys"][band][family]
                    mode = _mode(gold_keys, pred_keys)
                    band_mode_lists[family][band].append(mode)
                    if _exact(mode):
                        band_exact[family][band] += 1

                family_changes = [
                    item for item in replay["changes"] if item["family"] == family
                ]
                pathway = _pathway_key(replay["changes"], family)
                pathway_counter[family][pathway] += 1
                final_mode = _mode(gold_keys, final_keys[family])
                gate_mode = _mode(
                    gold_keys, replay["band_keys"]["producer_gate"][family]
                )
                if not family_changes:
                    residual[family][
                        "final_wrong_no_stage_change"
                        if not _exact(final_mode)
                        else "final_correct_no_stage_change"
                    ] += 1
                else:
                    residual[family][
                        "final_wrong_after_stage_change"
                        if not _exact(final_mode)
                        else "final_correct_after_stage_change"
                    ] += 1

                first_attributed = False
                for change in family_changes:
                    stage = change["stage"]
                    stats = stage_stats[family][stage]
                    stats["fires"] += 1
                    effect = change["effect"]
                    if effect == "rescue":
                        stats["any_rescue"] += 1
                    elif effect == "harm":
                        stats["any_harm"] += 1
                    example = {
                        "model_slug": slug,
                        "model_display": display,
                        "letter_id": letter_id,
                        "family": family,
                        "stage": stage,
                        "band": change["band"],
                        "before_keys": _compact_keys(change["before_keys"]),
                        "after_keys": _compact_keys(change["after_keys"]),
                        "before_mode": change["before_mode"],
                        "after_mode": change["after_mode"],
                        "final_mode": final_mode,
                        "effect": effect,
                        "pathway": pathway,
                        "gold_keys": _compact_keys(gold_keys),
                    }
                    if effect == "rescue":
                        stats["examples_rescue"].append(example)
                    elif effect == "harm":
                        stats["examples_harm"].append(example)
                    if not first_attributed:
                        first_attributed = True
                        stats["first_changer"] += 1
                        band_first_changer[family][change["band"]] += 1
                        if effect == "rescue":
                            stats["first_rescue"] += 1
                        elif effect == "harm":
                            stats["first_harm"] += 1

                if family_changes:
                    pathway_examples[family][pathway].append(
                        {
                            "model_slug": slug,
                            "model_display": display,
                            "letter_id": letter_id,
                            "family": family,
                            "pathway": pathway,
                            "stages": [item["stage"] for item in family_changes],
                            "before_keys": _compact_keys(
                                family_changes[0]["before_keys"]
                            ),
                            "after_keys": _compact_keys(
                                family_changes[-1]["after_keys"]
                            ),
                            "producer_gate_mode": gate_mode,
                            "final_mode": final_mode,
                            "effect": (
                                "rescue"
                                if _exact(final_mode) and not _exact(gate_mode)
                                else "harm"
                                if _exact(gate_mode) and not _exact(final_mode)
                                else "reshape"
                            ),
                            "gold_keys": _compact_keys(gold_keys),
                        }
                    )

    clinical_families: dict[str, Any] = {}
    for family in FAMILIES:
        n = family_n[family]
        bands_out: dict[str, Any] = {}
        prev_modes: dict[str, int] | None = None
        for band in BAND_ORDER:
            modes = _count_modes(band_mode_lists[family][band])
            exact = int(band_exact[family][band])
            delta = None
            if prev_modes is not None:
                keys = sorted(set(prev_modes) | set(modes))
                delta = {
                    key: int(modes.get(key, 0) - prev_modes.get(key, 0))
                    for key in keys
                    if modes.get(key, 0) != prev_modes.get(key, 0)
                }
            bands_out[band] = {
                "n_exact": exact,
                "n_imperfect": n - exact,
                "exact_rate": round(exact / n, 4) if n else None,
                "mode_counts": modes,
                "mode_delta_from_previous_band": delta,
            }
            prev_modes = modes

        stages_out: dict[str, Any] = {}
        for stage in STAGE_ORDER:
            stats = stage_stats[family][stage]
            stages_out[stage] = {
                "band": STAGE_BAND[stage],
                "fires": stats["fires"],
                "first_changer": stats["first_changer"],
                "first_rescue": stats["first_rescue"],
                "first_harm": stats["first_harm"],
                "any_rescue": stats["any_rescue"],
                "any_harm": stats["any_harm"],
                "examples_rescue": _pick_examples(stats["examples_rescue"]),
                "examples_harm": _pick_examples(stats["examples_harm"]),
            }

        top_pathways = [
            {
                "pathway": pathway,
                "count": count,
                "examples": _pick_examples(pathway_examples[family][pathway]),
            }
            for pathway, count in pathway_counter[family].most_common(12)
        ]
        clinical_families[family] = {
            "n_letter_model_cells": n,
            "bands": bands_out,
            "stages": stages_out,
            "band_first_changer_counts": dict(
                band_first_changer[family].most_common()
            ),
            "residual_ownership": dict(residual[family].most_common()),
            "top_pathways": top_pathways,
        }

    replayable = max(int(fidelity["replayable_rows"]), 1)
    fidelity_out = {
        "replayable_rows": fidelity["replayable_rows"],
        "unreplayable_rows": fidelity["unreplayable_rows"],
        "letter_model_cells": fidelity["letter_model_cells"],
        "evidence_gate_pass": fidelity["evidence_gate_pass"],
        "evidence_gate_fail": fidelity["evidence_gate_fail"],
        "key_exact_all_families": fidelity["key_exact_all_families"],
        "key_exact_all_families_rate": round(
            fidelity["key_exact_all_families"] / replayable, 4
        ),
        "key_exact_by_family": {
            family: int(fidelity["key_exact_by_family"][family]) for family in FAMILIES
        },
        "key_exact_by_family_rate": {
            family: round(fidelity["key_exact_by_family"][family] / replayable, 4)
            for family in FAMILIES
        },
        "evidence_gate_pass_rate": round(
            fidelity["evidence_gate_pass"] / replayable, 4
        ),
    }

    return {
        "schema_version": "exectv2.hybrid_stage_ablation.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/exectv2/hybrid_stage_ablation_protocol_2026-08-06.md"
        ),
        "parent_catalog": (
            "docs/research/exectv2/family_error_catalog_2026-08-06.md"
        ),
        "git": _git_note(),
        "dataset": "ExECTv2",
        "split": "dev140",
        "surface": "llm_with_rules",
        "policy": {
            "diagnosis_policy_variant": CONFIG.diagnosis_policy_variant,
            "prescription_policy_variant": CONFIG.prescription_policy_variant,
            "sf_projection_ablation": CONFIG.sf_projection_ablation,
        },
        "models": [
            {"slug": slug, "display": display} for slug, display in hs.MODEL_SPECS
        ],
        "band_order": list(BAND_ORDER),
        "stage_order": list(STAGE_ORDER),
        "fidelity": fidelity_out,
        "clinical_families": clinical_families,
        "claim_boundary": (
            "Development llm_with_rules stage ablation on ExECT dev140 under "
            "true ordered no-call replay of selected default/default policy. "
            "First-changer attribution by family; not leave-one-stage-out; "
            "not holdout; not a Decision 0046 rewrite."
        ),
    }


def _fmt_mode_delta(delta: dict[str, int] | None, *, limit: int = 6) -> str:
    if not delta:
        return "—"
    items = sorted(delta.items(), key=lambda item: (-abs(item[1]), item[0]))[:limit]
    return ", ".join(f"`{name}` {value:+d}" for name, value in items)


def _mermaid_keys(keys: list[str] | None, *, limit: int = 42) -> str:
    if not keys:
        return "(empty)"
    cleaned = " · ".join(str(key) for key in keys[:2])
    cleaned = " ".join(cleaned.split()).replace('"', "'")
    if len(keys) > 2:
        cleaned += f" (+{len(keys) - 2})"
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _rate(block: dict[str, Any] | None) -> str:
    if not block or block.get("exact_rate") is None:
        return "—"
    return f"{block['exact_rate']:.2f}"


def render_report(artifact: dict[str, Any]) -> str:
    fidelity = artifact["fidelity"]
    families = artifact["clinical_families"]
    lines: list[str] = [
        "# ExECTv2 llm_with_rules stage ablation",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development stage ablation inside hybrid only  ",
        "Protocol: [hybrid stage ablation protocol]"
        "(hybrid_stage_ablation_protocol_2026-08-06.md)  ",
        "Parent: [family error catalog](family_error_catalog_2026-08-06.md)  ",
        "Companions: [task-shape framework](task_shape_framework_2026-08-06.md), "
        "[architecture stage diagram]"
        "(../architecture/diagrams/exectv2_llm_with_rules_stages.md), "
        "[Gan peer](hybrid_stage_ablation_2026-08-06.md)  ",
        "Artifact: "
        f"[`experiments/exectv2_hybrid_stage_ablation_{DATE_STAMP}.json`]"
        f"(../../experiments/exectv2_hybrid_stage_ablation_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
    ]

    dx = families["Diagnosis"]["stages"]
    sf = families["SeizureFrequency"]["stages"]
    rx = families["Prescription"]["stages"]
    inv = families["Investigations"]["stages"]
    dx_bands = families["Diagnosis"]["bands"]
    sf_bands = families["SeizureFrequency"]["bands"]
    rx_bands = families["Prescription"]["bands"]

    lines.extend(
        [
            "Inside `llm_with_rules`, family rules are not one blob. On "
            f"{fidelity['replayable_rows']} replayable six-model letter cells "
            "under true ordered no-call replay:",
            "",
            "1. **Diagnosis** — `lens.diagnosis` is the mass first-changer "
            f"({dx['lens.diagnosis']['first_changer']} first; "
            f"{dx['lens.diagnosis']['first_rescue']} rescue / "
            f"{dx['lens.diagnosis']['first_harm']} harm). Exactness moves "
            f"{_rate(dx_bands['post_flatten'])} → "
            f"{_rate(dx_bands['diagnosis_lens'])} by the Diagnosis-lens band.",
            "2. **SeizureFrequency** — mass first-changer is "
            f"`project_and_gate` ({sf['project_and_gate']['first_changer']} first; "
            f"{sf['project_and_gate']['first_rescue']} rescue), mainly dropping or "
            "reshaping pre-state mentions; `sf_state_projection` adds a smaller "
            f"further lift ({sf['sf_state_projection']['first_changer']} first). "
            f"Thin SF lens fires {sf['lens.seizure_frequency']['fires']}. "
            f"Exactness {_rate(sf_bands['post_flatten'])} → "
            f"{_rate(sf_bands['producer_gate'])} after the gate, then "
            f"{_rate(sf_bands['sf_clinical'])} after SF clinical.",
            "3. **Prescription** — `lens.prescription` can hurt "
            f"({rx['lens.prescription']['any_harm']} any-harm vs "
            f"{rx['lens.prescription']['any_rescue']} any-rescue). Exactness "
            f"{_rate(rx_bands['diagnosis_lens'])} → "
            f"{_rate(rx_bands['prescription_lens'])} across the Rx lens band.",
            "4. **Investigations** — near no-op on lenses "
            f"(`lens.investigations` fires {inv['lens.investigations']['fires']}); "
            f"small `project_and_gate` movement only "
            f"({inv['project_and_gate']['fires']} fires).",
            "",
            "## Why this document exists",
            "",
            "The [family error catalog](family_error_catalog_2026-08-06.md) "
            "contrasts model lane vs after family rules. This sibling stays on "
            "hybrid only and splits the deterministic stack into bands and named "
            "stages under true ordered replay.",
            "",
            "## Observable bands",
            "",
            "No new calls. Saved `*_structured.jsonl` events are replayed through "
            "current selected-policy deterministic stages "
            "(`default` / `default`, SF `combined`).",
            "",
            "```mermaid",
            "flowchart LR",
            '  flat["0. Flatten"]',
            '  gate["1. Producer gate<br/>project_and_gate"]',
            '  sf["2. SF clinical<br/>project+suppress"]',
            '  dx["3. Diagnosis lens"]',
            '  rx["4. Prescription lens"]',
            '  inv["5. Investigations lens"]',
            '  ev["6. Evidence gate"]',
            "  flat --> gate --> sf --> dx --> rx --> inv --> ev",
            "```",
            "",
            "| Band | Stages | Role |",
            "| --- | --- | --- |",
            "| Post-flatten | `flatten_events` | Model events as mentions (pre-gate) |",
            "| Producer gate | `project_and_gate` | "
            "Enrich attributes; drop no-state SF / modality-only Inv |",
            "| SF clinical | `sf_state_projection`, `sf_unknown_suppression` "
            "(+ thin SF lens) | Project SF state; suppress unsupported unknown |",
            "| Diagnosis lens | `lens.diagnosis` | Heading/dictionary reconcile |",
            "| Prescription lens | `lens.prescription` | Bounded regimen correction |",
            "| Investigations lens | `lens.investigations` | Validate / de-dupe |",
            "| Evidence gate | `evidence_requirement` | Hard exact-evidence check |",
            "",
            "Attribute a rescue or harm to the **first** stage that changes that "
            "family's clinical-headline unit keys. Later fires count under "
            "any-rescue / any-harm.",
            "",
            "## Four pathways that explain the stack",
            "",
        ]
    )

    vignette_specs = [
        (
            "Diagnosis",
            "A. Diagnosis lens rewrites the concept set",
            "diagnosis",
            "Mass Diagnosis first-changer; inventory rescue from substitutions/extras.",
        ),
        (
            "SeizureFrequency",
            "B. Producer gate / SF projection trims state",
            "project_and_gate",
            "SF mass first-changer is often `project_and_gate`; projection adds a "
            "smaller further lift. Thin SF lens should barely fire.",
        ),
        (
            "Prescription",
            "C. Prescription lens drops or rewrites a drug",
            "prescription",
            "Known hurt surface under default policy.",
        ),
        (
            "Investigations",
            "D. Investigations with no stage change",
            "no_stage_change",
            "Rules leave Investigations alone on this roster.",
        ),
    ]
    for family, title, needle, lesson in vignette_specs:
        match = None
        if needle == "no_stage_change":
            match = next(
                (
                    item
                    for item in families[family]["top_pathways"]
                    if item["pathway"] == "no_stage_change"
                ),
                None,
            )
        else:
            for item in families[family]["top_pathways"]:
                if needle in item["pathway"]:
                    match = item
                    break
        lines.append(f"### {title}")
        lines.append("")
        lines.append(lesson)
        if match and match.get("examples"):
            example = match["examples"][0]
            lines.extend(
                [
                    "",
                    "```mermaid",
                    "flowchart LR",
                    f'  gold["Gold<br/>{_mermaid_keys(example.get("gold_keys"))}"]',
                    f'  before["Before pathway<br/>{_mermaid_keys(example.get("before_keys"))}"]',
                    f'  after["After pathway<br/>{_mermaid_keys(example.get("after_keys"))}"]',
                    "  gold -.-> before",
                    f'  before -->|{_mermaid_keys([example["pathway"]], limit=48)}| after',
                    "```",
                    "",
                    f"{example['letter_id']} / {example['model_display']}. "
                    f"Pathway effect `{example.get('effect')}`; final mode "
                    f"`{example.get('final_mode')}`.",
                ]
            )
        elif match:
            lines.append(f"Pooled count: {match['count']}.")
        lines.append("")

    lines.extend(
        [
            "## Band ablation by clinical family",
            "",
            "Pooled six-model letter×model cells. Exact rate is clinical-headline "
            "unit-key letter exactness at the band endpoint. Mode Δ is mode-count "
            "versus the previous band (negative means that shape shrank).",
            "",
        ]
    )

    for family in FAMILIES:
        block = families[family]
        lines.append(f"### `{family}` (n={block['n_letter_model_cells']})")
        lines.append("")
        lines.append("| Band | Exact | Top modes | Mode Δ from previous |")
        lines.append("| --- | ---: | --- | --- |")
        for band in BAND_ORDER:
            band_block = block["bands"][band]
            modes = band_block["mode_counts"]
            top = ", ".join(
                f"`{name}` ({count})" for name, count in list(modes.items())[:3]
            ) or "—"
            lines.append(
                f"| {BAND_LABELS[band]} | {_rate(band_block)} | {top} | "
                f"{_fmt_mode_delta(band_block.get('mode_delta_from_previous_band'))} |"
            )
        lines.append("")

    lines.extend(
        [
            "## First-changer stage ledger by family",
            "",
            "Counts are pooled six-model stage hops on replayable rows. "
            "**First-changer** = earliest stage that changed that family's keys. "
            "**Any-rescue / any-harm** count every hop.",
            "",
        ]
    )
    for family in FAMILIES:
        stages = families[family]["stages"]
        lines.append(f"### `{family}`")
        lines.append("")
        lines.append(
            "| Stage | Band | Fires | First | Rescue | Harm | Any+ | Any- |"
        )
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for stage in STAGE_ORDER:
            stats = stages[stage]
            if (
                stats["fires"] == 0
                and stats["first_changer"] == 0
                and stage
                not in {
                    "lens.diagnosis",
                    "lens.prescription",
                    "sf_state_projection",
                    "sf_unknown_suppression",
                    "lens.investigations",
                }
            ):
                continue
            lines.append(
                f"| `{stage}` | {stats['band']} | {stats['fires']} | "
                f"{stats['first_changer']} | {stats['first_rescue']} | "
                f"{stats['first_harm']} | {stats['any_rescue']} | "
                f"{stats['any_harm']} |"
            )
        lines.append("")
        lines.append("Band-level first-changer share:")
        lines.append("")
        lines.append("| Band | First-changer letters |")
        lines.append("| --- | ---: |")
        for band, count in families[family]["band_first_changer_counts"].items():
            lines.append(f"| `{band}` | {count} |")
        lines.append("")

        notable = [
            stage
            for stage in STAGE_ORDER
            if stages[stage]["fires"] or stages[stage]["any_harm"]
        ]
        for stage in notable:
            stats = stages[stage]
            if stats["fires"] == 0:
                continue
            lines.append(f"#### `{stage}`")
            lines.append("")
            lines.append(
                f"Fires {stats['fires']}; first-changer {stats['first_changer']} "
                f"(rescue {stats['first_rescue']}, harm {stats['first_harm']}); "
                f"any-rescue {stats['any_rescue']}, any-harm {stats['any_harm']}."
            )
            if stats["examples_rescue"]:
                ex = stats["examples_rescue"][0]
                lines.append(
                    f"- Rescue example: {ex['letter_id']} / {ex['model_display']}: "
                    f"{ex['before_mode']} → {ex['after_mode']} "
                    f"(`{ex['before_keys']}` → `{ex['after_keys']}`)."
                )
            if stats["examples_harm"]:
                ex = stats["examples_harm"][0]
                lines.append(
                    f"- Harm example: {ex['letter_id']} / {ex['model_display']}: "
                    f"{ex['before_mode']} → {ex['after_mode']} "
                    f"(`{ex['before_keys']}` → `{ex['after_keys']}`)."
                )
            lines.append("")

    lines.extend(
        [
            "## Residual ownership after the full stack",
            "",
        ]
    )
    for family in FAMILIES:
        lines.append(f"### `{family}`")
        lines.append("")
        lines.append("| Outcome | Count |")
        lines.append("| --- | ---: |")
        for key, count in families[family]["residual_ownership"].items():
            lines.append(f"| `{key}` | {count} |")
        lines.append("")

    lines.extend(
        [
            "## Top pathways by family",
            "",
        ]
    )
    for family in FAMILIES:
        lines.append(f"### `{family}`")
        lines.append("")
        lines.append("| Pathway | Count |")
        lines.append("| --- | ---: |")
        for item in families[family]["top_pathways"][:8]:
            lines.append(f"| `{item['pathway']}` | {item['count']} |")
        lines.append("")

    lines.extend(
        [
            "## How to explore further",
            "",
            "| Need | Where |",
            "| --- | --- |",
            "| Band mode tables and stage examples | JSON artifact |",
            "| llm vs hybrid mode catalog | "
            "[family error catalog](family_error_catalog_2026-08-06.md) |",
            "| Stage ownership definitions | "
            "[llm_with_rules stages]"
            "(../architecture/diagrams/exectv2_llm_with_rules_stages.md) |",
            "| Gan peer report | "
            "[Gan hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md) |",
            "| Regenerate | `python scripts/build_exectv2_hybrid_stage_ablation.py` |",
            "",
            "## Method",
            "",
            "- Split: ExECT `dev140`. Surface: `llm_with_rules` only.",
            "- Replay input: retained `*_structured.jsonl` `structured_events` + "
            "dev letter note text.",
            "- Policy: selected `default` / `default`, SF projection `combined`.",
            "- Baseline for hops: post-`flatten_events`; then "
            "`project_and_gate` → SF project/suppress → four lenses → evidence gate.",
            "- Wrongness: clinical-headline unit-key letter imperfect. Modes: same "
            "vocabulary as the parent catalog.",
            "- Attribution: first key-changing stage per family is the "
            "first-changer; any-rescue/harm count later hops too.",
            f"- Fidelity on replayable rows: all-family key exact "
            f"{fidelity['key_exact_all_families_rate']:.3f}; evidence-gate pass "
            f"{fidelity['evidence_gate_pass_rate']:.3f}; per-family "
            + ", ".join(
                f"{family} {fidelity['key_exact_by_family_rate'][family]:.3f}"
                for family in FAMILIES
            )
            + ".",
            "",
            "## Claim boundary",
            "",
            "- Development ExECT `llm_with_rules` stage ablation on `dev140`.",
            "- True ordered current-code replay of saved structured events, not a "
            "factorial leave-one-stage-out experiment.",
            "- Not a replacement for parent-catalog llm-vs-hybrid scores.",
            "- Not sealed holdout competence; not a Decision 0046 rewrite.",
            "- Do not treat post-rules exact-evidence rates near `1.00` as "
            "model-quality evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT / f"experiments/exectv2_hybrid_stage_ablation_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/exectv2/hybrid_stage_ablation_{REPORT_DATE}.md",
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    print(
        "fidelity all-family key exact "
        f"{artifact['fidelity']['key_exact_all_families_rate']:.3f} "
        f"({artifact['fidelity']['key_exact_all_families']}/"
        f"{artifact['fidelity']['replayable_rows']})"
    )


if __name__ == "__main__":
    main()
