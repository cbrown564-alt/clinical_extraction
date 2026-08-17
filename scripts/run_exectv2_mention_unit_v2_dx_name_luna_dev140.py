"""No-call Diagnosis name/concept leftover catalog after febrile v14."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from collections.abc import Hashable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    concepts_hierarchically_related,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitEncoder,
    _fold_span,
    _span_in_letter,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_stack_error_analysis_luna_dev140 import (
    _family_gaps,
    _family_keys,
)
from scripts.run_exectv2_mention_unit_v2_leftover_form_v3_luna_dev140 import (
    _form_census,
    _score_method,
)
from scripts.run_exectv2_mention_unit_v2_luna import DEV20_IDS

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/"
    "mention_unit_v2_dx_name_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / (
    "docs/research/exectv2/mention_unit_v2_dx_name_luna_dev140_2026-08-17.md"
)
SOURCE_ROWS = ROOT / "experiments/exectv2_mention_unit_v2_luna_dev140_20260816" / "rows.jsonl"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v2_dx_name_luna_dev140_20260817"
CONTROL: MentionUnitEncoder = "leftover_form_span_fold_febrile_v14"
STACK_V10: MentionUnitEncoder = "leftover_form_span_fold_fortnight_v10"
FORM: MentionUnitEncoder = "leftover_form_intervening_v3"
ENCODERS: tuple[MentionUnitEncoder, ...] = ("landed", FORM, STACK_V10, CONTROL)
DEV20 = frozenset(DEV20_IDS)
V14_EXTRAS = {"all140": 54, "rest120": 51}


def main() -> None:
    if not SOURCE_ROWS.exists():
        raise SystemExit(f"missing saved raws: {SOURCE_ROWS}")
    letters = list(load_letters_for_split("dev"))
    if len(letters) != 140:
        raise SystemExit(f"expected 140 development letters, found {len(letters)}")
    by_id = {letter.letter_id: letter for letter in letters}
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()

    rows: list[dict[str, Any]] = []
    gold_in_order: list[ExectLetter] = []
    predictions: dict[str, list[PredictedLetter]] = {
        name: [] for name in ("llm", *ENCODERS)
    }
    with SOURCE_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            saved = json.loads(line)
            letter = by_id[str(saved["letter_id"])]
            gold_in_order.append(letter)
            row = _rematerialize_row(letter, saved)
            rows.append(row)
            predictions["llm"].append(
                PredictedLetter.model_validate(saved["methods"][LLM_METHOD]["prediction"])
            )
            for encoder in ENCODERS:
                predictions[encoder].append(
                    PredictedLetter.model_validate(row["hybrid"][encoder]["prediction"])
                )
    slices = {
        "all140": [letter.letter_id for letter in gold_in_order],
        "dev20": [letter.letter_id for letter in gold_in_order if letter.letter_id in DEV20],
        "rest120": [
            letter.letter_id for letter in gold_in_order if letter.letter_id not in DEV20
        ],
    }
    scored: dict[str, dict[str, Any]] = {}
    for slice_name, letter_ids in slices.items():
        gold, preds = _slice(gold_in_order, predictions, letter_ids)
        scored[slice_name] = {
            "methods": {name: _score_method(gold, preds[name]) for name in preds},
            "form_census": {name: _form_census(preds[name]) for name in preds},
        }
    family_gaps = {
        encoder: _family_gaps(gold_in_order, predictions[encoder])
        for encoder in ("llm", *ENCODERS)
    }
    miss_catalog = _diagnosis_miss_catalog(
        gold_in_order, rows, predictions[CONTROL], encoder=CONTROL
    )
    next_rules = _rank_next_rules(miss_catalog, family_gaps[CONTROL]["Diagnosis"])
    decision = _decision(scored, family_gaps, miss_catalog, next_rules)
    artifact = {
        "schema_version": "exectv2.mention_unit_v2_dx_name.dev140.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev140",
        "row_count": len(rows),
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "control": CONTROL,
        "form_context": FORM,
        "stack_context": STACK_V10,
        "candidate": None,
        "slices": {
            name: {
                "letter_count": len(letter_ids),
                "methods": scored[name]["methods"],
                "form_census": scored[name]["form_census"],
            }
            for name, letter_ids in slices.items()
        },
        "family_gaps": {
            encoder: {"Diagnosis": family_gaps[encoder]["Diagnosis"]}
            for encoder in ("llm", *ENCODERS)
        },
        "decision": decision,
        "next_rules": next_rules,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "provenance": _provenance(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT Diagnosis name leftover catalog on frozen "
            "mention-unit v2 dev140 hybrid raws after febrile v14. Not holdout, "
            "not a Decision 0050 change, and not selected-stack parity."
        ),
    }
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "diagnosis_miss_catalog.json").write_text(
        json.dumps(miss_catalog, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    with (STUDY_DIR / "rows.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    REPORT.write_text(_render_report(artifact, miss_catalog), encoding="utf-8")
    print(
        json.dumps(
            {
                "model_calls": 0,
                "decision": decision,
                "diagnosis": {
                    encoder: {
                        "miss": family_gaps[encoder]["Diagnosis"]["miss_count"],
                        "extra": family_gaps[encoder]["Diagnosis"]["extra_count"],
                        "f1": family_gaps[encoder]["Diagnosis"]["f1"],
                    }
                    for encoder in (STACK_V10, CONTROL)
                },
                "mechanism_counts": miss_catalog["mechanism_counts"],
                "next_rules": next_rules,
            },
            indent=2,
            default=_json_default,
        )
    )


def _rematerialize_row(letter: ExectLetter, saved: dict[str, Any]) -> dict[str, Any]:
    raw = str(saved["methods"][HYBRID_METHOD]["raw_output"])
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    hybrid: dict[str, Any] = {}
    for encoder in ENCODERS:
        if parsed.record is None:
            prediction = PredictedLetter(letter_id=letter.letter_id, mentions=())
            payload = {
                "semantic_facts": [],
                "rule_trace": [],
                "warnings": [],
                "evidence_invalid": 0,
                "prediction": prediction.model_dump(mode="json"),
            }
        else:
            materialized = materialize_mention_unit(
                letter,
                parsed.record,
                method=HYBRID_METHOD,
                encoder=encoder,
            )
            payload = {
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        hybrid[encoder] = payload
    return {
        "letter_id": letter.letter_id,
        "split": "dev140",
        "model_calls": 0,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "raw_output": raw,
        "parse_errors": parsed.errors,
        "hybrid": hybrid,
        "llm_prediction": saved["methods"][LLM_METHOD]["prediction"],
    }


def _slice(
    gold: list[ExectLetter],
    predictions: dict[str, list[PredictedLetter]],
    letter_ids: list[str],
) -> tuple[list[ExectLetter], dict[str, list[PredictedLetter]]]:
    wanted = set(letter_ids)
    keep = [index for index, letter in enumerate(gold) if letter.letter_id in wanted]
    return (
        [gold[index] for index in keep],
        {name: [rows[index] for index in keep] for name, rows in predictions.items()},
    )


def _diagnosis_miss_catalog(
    gold: list[ExectLetter],
    rows: list[dict[str, Any]],
    predictions: list[PredictedLetter],
    *,
    encoder: str,
) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    by_row = {row["letter_id"]: row for row in rows}
    items: list[dict[str, Any]] = []
    for letter, pred in zip(gold, pred_letters, strict=True):
        g_keys = _family_keys("Diagnosis", letter.entities("Diagnosis"), letter.note_text)
        p_keys = _family_keys("Diagnosis", pred.entities("Diagnosis"), letter.note_text)
        g_count = Counter(g_keys)
        p_count = Counter(p_keys)
        extras = [
            _concept_from_key(key)
            for key, count in (p_count - g_count).items()
            for _ in range(count)
        ]
        hierarchy_pairs = _hierarchy_pairs(g_count - p_count, p_count - g_count)
        gold_texts = [ann.text for ann in letter.entities("Diagnosis")]
        pred_dx = [
            mention
            for mention in pred.annotations
            if mention.entity == "Diagnosis"
        ]
        pred_sf = [
            mention
            for mention in pred.annotations
            if mention.entity == "SeizureFrequency"
        ]
        facts = [
            fact
            for fact in by_row[letter.letter_id]["hybrid"][encoder].get("semantic_facts")
            or []
            if fact.get("family") == "Diagnosis"
        ]
        warnings = by_row[letter.letter_id]["hybrid"][encoder].get("warnings") or []
        for key, count in (g_count - p_count).items():
            concept = _concept_from_key(key)
            items.append(
                _classify_miss(
                    letter=letter,
                    concept=concept,
                    count=count,
                    extras=extras,
                    hierarchy_pairs=hierarchy_pairs,
                    gold_texts=gold_texts,
                    pred_dx=pred_dx,
                    pred_sf=pred_sf,
                    facts=facts,
                    warnings=warnings,
                )
            )
    mechanism_counts = dict(Counter(item["mechanism"] for item in items))
    class_counts = _key_counts(items)
    hierarchy_credited = [
        item for item in items if item.get("hierarchy_credited")
    ]
    return {
        "encoder": encoder,
        "miss_count": sum(item["count"] for item in items),
        "mechanism_counts": mechanism_counts,
        "hierarchy_credited_count": sum(item["count"] for item in hierarchy_credited),
        "true_fn_count": sum(
            item["count"] for item in items if not item.get("hierarchy_credited")
        ),
        "miss_key_counts": class_counts,
        "items": items,
    }


def _classify_miss(
    *,
    letter: ExectLetter,
    concept: str,
    count: int,
    extras: list[str],
    hierarchy_pairs: list[dict[str, str]],
    gold_texts: list[str],
    pred_dx: list[Any],
    pred_sf: list[Any],
    facts: list[dict[str, Any]],
    warnings: list[str],
) -> dict[str, Any]:
    gold_surfaces = [
        text
        for text in gold_texts
        if canonicalize_diagnosis_concept(text) == concept
        or concepts_hierarchically_related(canonicalize_diagnosis_concept(text), concept)
    ]
    if not gold_surfaces:
        gold_surfaces = [concept]
    letter_fold = _fold_span(letter.note_text)
    in_letter_exact = any(
        _span_in_letter(letter.note_text, surface, mode="exact") for surface in gold_surfaces
    )
    in_letter_fold = any(
        _span_in_letter(letter.note_text, surface, mode="span_fold")
        for surface in gold_surfaces
    ) or _fold_span(concept) in letter_fold
    emitted = [
        fact
        for fact in facts
        if _name_targets_concept(str(fact.get("clinical_name") or fact.get("text") or ""), concept)
    ]
    dropped = [
        fact
        for fact in emitted
        if not fact.get("text_valid")
        or any(
            f"item[{fact.get('fact_index')}]: text_not_substring" in warning
            for warning in warnings
        )
    ]
    kept_wrong = [
        mention
        for mention in pred_dx
        if _related_name(mention.text, concept)
        and canonicalize_diagnosis_concept(mention.text) != concept
        and not concepts_hierarchically_related(
            canonicalize_diagnosis_concept(mention.text), concept
        )
    ]
    sf_near = [
        mention
        for mention in pred_sf
        if _related_name(mention.text, concept)
    ]
    paired_extras = [
        extra
        for extra in extras
        if _related_name(extra, concept)
        or concepts_hierarchically_related(extra, concept)
    ]
    hierarchy_credited = [
        pair for pair in hierarchy_pairs if pair["gold"] == concept
    ]
    if dropped:
        mechanism = "span_fold_miss"
    elif kept_wrong:
        mechanism = "cui_name_mismatch"
    elif paired_extras:
        mechanism = "extra_as_substitution"
    elif in_letter_fold and not emitted:
        mechanism = "unread_span"
    elif not in_letter_fold:
        mechanism = "gold_phrase_absent"
    else:
        mechanism = "cui_name_mismatch"
    return {
        "letter_id": letter.letter_id,
        "key": ["Diagnosis", concept],
        "count": count,
        "slice": "dev20" if letter.letter_id in DEV20 else "rest120",
        "mechanism": mechanism,
        "gold_surfaces": gold_surfaces,
        "in_letter_exact": in_letter_exact,
        "in_letter_fold": in_letter_fold,
        "emitted_names": [
            str(fact.get("clinical_name") or fact.get("text") or "") for fact in emitted
        ],
        "dropped_names": [
            str(fact.get("clinical_name") or fact.get("text") or "") for fact in dropped
        ],
        "kept_wrong_names": [mention.text for mention in kept_wrong],
        "sf_near_names": [mention.text for mention in sf_near],
        "paired_extras": paired_extras,
        "hierarchy_credited": hierarchy_credited,
        "pred_dx_names": [mention.text for mention in pred_dx],
        "letter_extras": extras,
    }


def _hierarchy_pairs(
    misses: Counter[Hashable], extras: Counter[Hashable]
) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    pred_items = list(extras.items())
    for gold_key, gold_count in misses.items():
        needed = gold_count
        gold_concept = _concept_from_key(gold_key)
        for index, (pred_key, pred_count) in enumerate(pred_items):
            if needed == 0:
                break
            if pred_count <= 0:
                continue
            pred_concept = _concept_from_key(pred_key)
            if concepts_hierarchically_related(gold_concept, pred_concept):
                take = min(needed, pred_count)
                pairs.append(
                    {
                        "gold": gold_concept,
                        "pred": pred_concept,
                        "count": str(take),
                    }
                )
                needed -= take
                pred_items[index] = (pred_key, pred_count - take)
    return pairs


def _name_targets_concept(name: str, concept: str) -> bool:
    canonical = canonicalize_diagnosis_concept(name)
    folded = _fold_span(name)
    concept_fold = _fold_span(concept)
    return (
        canonical == concept
        or concepts_hierarchically_related(canonical, concept)
        or folded == concept_fold
        or concept_fold in folded
        or folded in concept_fold
    )


def _related_name(name: str, concept: str) -> bool:
    folded = _fold_span(name)
    concept_fold = _fold_span(concept)
    tokens = set(concept_fold.split())
    name_tokens = set(folded.split())
    shared = tokens & name_tokens
    return bool(
        shared
        and (
            "epilep" in folded
            or "seizure" in folded
            or "epilep" in concept_fold
            or "seizure" in concept_fold
        )
    )


def _concept_from_key(key: Hashable) -> str:
    if isinstance(key, tuple) and len(key) > 1:
        return str(key[1])
    if isinstance(key, list) and len(key) > 1:
        return str(key[1])
    return str(key)


def _key_counts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(
        tuple(item["key"]) if isinstance(item["key"], list) else item["key"]
        for item in items
        for _ in range(int(item.get("count") or 1))
    )
    return [
        {"key": list(key) if isinstance(key, tuple) else key, "count": count}
        for key, count in counts.most_common()
    ]


def _rank_next_rules(
    catalog: dict[str, Any], diagnosis: dict[str, Any]
) -> list[dict[str, Any]]:
    by_mechanism: dict[str, list[dict[str, Any]]] = {}
    for item in catalog["items"]:
        by_mechanism.setdefault(item["mechanism"], []).append(item)
    unread = by_mechanism.get("unread_span", [])
    unread_keys = Counter(
        item["key"][1] for item in unread for _ in range(item["count"])
    )
    mismatch = by_mechanism.get("cui_name_mismatch", [])
    mismatch_keys = Counter(
        item["key"][1] for item in mismatch for _ in range(item["count"])
    )
    rules: list[dict[str, Any]] = []
    if unread_keys:
        top = unread_keys.most_common(3)
        rules.append(
            {
                "rank": 1,
                "action": "do_not_test",
                "rule": "unread_span_prompt_or_selection",
                "reason": (
                    "Unread Diagnosis names are selection leftovers. Recovering "
                    "them needs a new model row, not a gold-free name rewrite "
                    "of an already-emitted phrase."
                ),
                "count": sum(unread_keys.values()),
                "top_keys": [{"key": key, "count": count} for key, count in top],
            }
        )
    if mismatch_keys:
        top = mismatch_keys.most_common(3)
        rules.append(
            {
                "rank": 2,
                "action": "do_not_test",
                "rule": "keep_emitted_over_longest_surface",
                "reason": (
                    "Several misses keep a shorter surface after the model "
                    "already copied a longer name. Recovering them is not one "
                    "named class: temporal-lobe onset, GTCS-alone, and "
                    "complex-partial compounds would each need a different "
                    "rewrite, and replacing the short name can drop a gold "
                    "generic that hierarchy does not cover."
                ),
                "count": sum(mismatch_keys.values()),
                "top_keys": [{"key": key, "count": count} for key, count in top],
            }
        )
        rules.append(
            {
                "rank": 3,
                "action": "do_not_test",
                "rule": "closed_rewrite_keep_lobe",
                "reason": (
                    "Closed rewrite maps symptomatic-structural lobe names to "
                    "focal epilepsy on many letters. EA0167 temporal is already "
                    "hierarchy-credited. EA0054 frontal is a true miss, but "
                    "skipping the rewrite would swap away the gold focal "
                    "epilepsy match. Do not retune the convention table."
                ),
                "count": 2,
            }
        )
    span_fold = by_mechanism.get("span_fold_miss", [])
    if span_fold:
        rules.append(
            {
                "rank": 4,
                "action": "do_not_test",
                "rule": "span_fold_retune",
                "reason": (
                    "Do not retune span-fold from EA0021 / EA0045 / EA0185 or "
                    "from Diagnosis drops."
                ),
                "count": sum(item["count"] for item in span_fold),
            }
        )
    extras = by_mechanism.get("extra_as_substitution", [])
    if extras:
        rules.append(
            {
                "rank": 5,
                "action": "do_not_test",
                "rule": "extra_as_substitution_rewrite",
                "reason": (
                    "Paired extras are a different concept, not a leftover "
                    "phrase already in evidence. Rewriting them would invent "
                    "or replace a name."
                ),
                "count": sum(item["count"] for item in extras),
            }
        )
    absent = by_mechanism.get("gold_phrase_absent", [])
    if absent:
        rules.append(
            {
                "rank": 6,
                "action": "do_not_test",
                "rule": "paraphrase_or_singular_gold",
                "reason": (
                    "Gold concept wording is absent after span-fold. Do not "
                    "singularize, stem, or invent a name that is not in the "
                    "letter."
                ),
                "count": sum(item["count"] for item in absent),
            }
        )
    fragments = [
        item
        for item in catalog["items"]
        if item["key"][1]
        in {
            "generalised",
            "focal",
            "secondary",
            "drug",
            "occipital",
            "epileptic",
            "symptomatic",
            "temporal",
        }
    ]
    if fragments:
        rules.append(
            {
                "rank": 7,
                "action": "do_not_test",
                "rule": "gold_heading_fragments",
                "reason": (
                    "Some gold Diagnosis units are heading tokens "
                    "(generalised, focal, drug, occipital). Those are not a "
                    "named recovery class."
                ),
                "count": sum(item["count"] for item in fragments),
            }
        )
    if not rules:
        rules.append(
            {
                "rank": 1,
                "action": "do_not_test",
                "rule": "no_gold_free_dx_name_class",
                "reason": "No remaining Diagnosis miss class is a gold-free phrase contract.",
                "count": diagnosis["miss_count"],
            }
        )
    return rules


def _decision(
    scored: dict[str, dict[str, Any]],
    family_gaps: dict[str, dict[str, Any]],
    catalog: dict[str, Any],
    next_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    all140 = scored["all140"]["methods"]
    rest = scored["rest120"]["methods"]
    extras = all140[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    rest_extras = rest[CONTROL]["empty_gold_sf_extras"]["mention_count"]
    extras_rose = extras > V14_EXTRAS["all140"] or rest_extras > V14_EXTRAS["rest120"]
    dx = family_gaps[CONTROL]["Diagnosis"]
    v10 = family_gaps[STACK_V10]["Diagnosis"]
    diagnosis_unchanged = (
        dx["miss_count"] == v10["miss_count"]
        and dx["extra_count"] == v10["extra_count"]
        and dx["f1"] == v10["f1"]
    )
    implementable = any(rule["action"] == "test" for rule in next_rules)
    if extras_rose:
        status = "revise"
        mechanism = "dx_name_catalog_extras_rose"
    elif implementable:
        status = "revise"
        mechanism = "dx_name_rule_not_remeasured"
    else:
        status = "answer"
        mechanism = "remaining_dx_is_unread_or_banned_name"
    return {
        "status": status,
        "mechanism": mechanism,
        "rule_implemented": False,
        "candidate": None,
        "diagnosis_miss": dx["miss_count"],
        "diagnosis_extra": dx["extra_count"],
        "diagnosis_f1": dx["f1"],
        "v10_diagnosis_miss": v10["miss_count"],
        "v10_diagnosis_extra": v10["extra_count"],
        "v10_diagnosis_f1": v10["f1"],
        "diagnosis_unchanged_from_v10": diagnosis_unchanged,
        "empty_gold_sf_extras": extras,
        "rest120_empty_gold_sf_extras": rest_extras,
        "extras_rose": extras_rose,
        "candidate_headline_140": all140[CONTROL]["clinical_headline_f1"],
        "candidate_sf_140": all140[CONTROL]["clinical_headline_family_f1"][
            "SeizureFrequency"
        ],
        "implementable_rule": implementable,
        "hierarchy_credited_count": catalog["hierarchy_credited_count"],
        "true_fn_count": catalog["true_fn_count"],
        "mechanism_counts": catalog["mechanism_counts"],
    }


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    return {"git_head": commit, "dirty_tree": dirty}


def _json_default(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"unserializable {type(value)!r}")


def _render_report(artifact: dict[str, Any], catalog: dict[str, Any]) -> str:
    decision = artifact["decision"]
    return (
        "# ExECT leftover-form Diagnosis name leftovers after febrile v14, "
        "mention-unit v2 `dev140`\n\n"
        f"Date: 2026-08-17  \n"
        f"Status: complete; **{decision['status']}**  \n"
        f"Protocol: [dx name `dev140`]({Path(PROTOCOL).name})  \n"
        "Parent: [febrile widen `dev140`]"
        "(mention_unit_v2_febrile_widen_luna_dev140_2026-08-17.md)\n\n"
        "`model_calls`: 0. Draft rendered by the remasure script. "
        "Replace with the inspected report.\n"
    )


if __name__ == "__main__":
    main()
