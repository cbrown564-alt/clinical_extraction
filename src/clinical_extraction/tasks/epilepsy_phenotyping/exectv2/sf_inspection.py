"""Build the ExECT-V2 SeizureFrequency inspection payload.

This module is the single source of truth for the SeizureFrequency inspection
surface served by the Observatory (``GET /exectv2/sf-inspection``) and rendered by
the frontend ``/exectv2-sf-inspection`` route. It is the importable, JSON-emitting
twin of ``scripts/render_exectv2_sf_inspection_html.py``: every TP/FP/FN, every
projected state, every canonicalization is computed by the same code path so the
served payload can never drift from what the offline HTML reported.

Purpose (see ``docs/experiments/exectv2/seizure_frequency/``): give a human a way
to inspect *every* letter in detail, per schema attribute and per scoring
component, and see the prediction-transformation chain (closed-vocab validation,
format canonicalization, state projection, key construction) the scorer applies
before deciding right/wrong -- so it is legible where the model gets it right and
where it gets it wrong.

Data lineage (the strongest LLM-based SF surface on dev140):
  predictions  -> exectv2_sf_magnitude_complement_dev140_20260708.jsonl
                  (gpt-4.1-mini magnitude complement; directional F1 0.8602,
                   magnitude F1 0.9244 -- the top LLM arm, both beating the
                   closed-option selector).
  gold         -> load_letters_for_split('dev') (the canonical gold; the
                  artifact's ``gold_mentions`` field is NOT SF-filtered, so gold
                  comes from the loader).
  override ref -> exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl
                  to flag the SF mentions whose ``FrequencyChange`` the LLM
                  magnitude selector overwrote.

Faithfulness contract: :func:`build_sf_inspection_payload` re-scores all 140
letters with the real ``score_frequency_state`` and the payload's scorecard is
guaranteed to reproduce the published summary within 1e-4. The builder raises if
it would drift, so a 500 (not a silent bad payload) reaches the frontend.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import multiset_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    POINT_RANGE_TRIPLES,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _keys,
    _match_gold_to_predictions,
    benchmark_config_for,
    semantic_config_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    resolve_point_range,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _count_based_state,
    _frequency_active_rate_keys,
    _frequency_state_keys,
    _frequency_state_profile_direction_deconf_keys,
    _frequency_state_profile_directional_keys,
    _frequency_state_profile_keys,
    _frequency_state_profile_magnitude_keys,
    frequency_state_direction_deconf,
    frequency_state_directional,
    frequency_state_faithful,
    frequency_state_magnitude,
    score_frequency_state,
)


def _find_repo_root() -> Path:
    """Walk up from this module to the directory holding ``pyproject.toml``."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/<file>
    return here.parents[5]


REPO_ROOT = _find_repo_root()
EXPERIMENTS = REPO_ROOT / "experiments"
DATESTR = "20260708"

COMPLEMENT_ARTIFACT = EXPERIMENTS / f"exectv2_sf_magnitude_complement_dev140_{DATESTR}.jsonl"
BASELINE_ARTIFACT = EXPERIMENTS / "exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl"
LEDGER_ARTIFACT = EXPERIMENTS / f"exectv2_sf_magnitude_complement_ledger_{DATESTR}.jsonl"

# Gold-quality disclosure sources (the same files ``/gold-noise`` reads -- see
# ``observatory/routers/gold_noise.py``). Read-only, best-effort: the SF
# canonical-adjudication ledger is keyed to a different run
# (``exectv2_gepa_sf_verify_gpt41mini_20260628``) than the one this module
# scores, so a hit is "a prior adjudication for this letter/state", not a
# guaranteed match to the exact mention shown.
GOLD_DATA_ISSUES_ARTIFACT = EXPERIMENTS / "gold_data_issues.jsonl"
GOLD_CASE_LEDGER_ARTIFACT = EXPERIMENTS / "gold_case_ledger_seizurefrequency.jsonl"

SF_ENTITY = "SeizureFrequency"
SPLIT = "dev"

# Published anchor numbers for the faithfulness gate (dev140 complement run).
EXPECTED_F1 = {
    "state_profile": 0.9338,
    "state_profile_directional": 0.8602,
    "state_profile_magnitude": 0.9244,
}
ANCHOR_TOLERANCE = 1e-4

# Attribute display order (SF-specific grouping: burden -> cadence -> change ->
# timing -> dates -> ages -> shared provenance).
SF_ATTR_ORDER = [
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "TimePeriod",
    "FrequencyChange",
    "TimeSince_or_TimeOfEvent",
    "PointInTime",
    "DayDate",
    "MonthDate",
    "YearDate",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
    "CUI",
    "CUIPhrase",
    "Certainty",
    "Negation",
]

# component_name -> human description of its projection / key rule.
COMPONENT_INFO = {
    "clinical_headline": (
        "Convention-strict 3-way state (count-only; FrequencyChange-blind). "
        "Key = (seizure-type CUI-or-phrase, state). Deduped per letter."
    ),
    "state_profile": (
        "Type-agnostic presence set of change-aware 4-way state "
        "(seizure-free / active-rate / changed / unknown). Deduped."
    ),
    "state_profile_directional": (
        "Like state_profile, but the 'changed' bucket is split into gold's "
        "5-way FrequencyChange vocab (increased/decreased/frequent/infrequent/same)."
    ),
    "state_profile_direction_deconf": (
        "SF-3 direction-only: Frequent/Infrequent project to direction-neutral "
        "'same'; only increased/decreased/same carry direction."
    ),
    "state_profile_magnitude": (
        "SF-3 magnitude-only: only Frequent/Infrequent populate this axis; "
        "everything else -> 'none'."
    ),
    "active_rate": "clinical_headline key filtered to state == active-rate.",
    "active_rate_fidelity": (
        "Among active-rate mentions, key = (seizure-type, sorted rate-bearing "
        "attributes: counts + cadence, excluding dates/point-in-time)."
    ),
    "seizure_free": "clinical_headline key filtered to state == seizure-free.",
    "unknown": "clinical_headline key filtered to state == unknown.",
    "exact_semantic": (
        "Full (entity, normalized phrase, sorted non-ignored attributes) match; "
        "CUI DROPPED. Benchmark ignores {CUIPhrase, Certainty, Negation}."
    ),
    "benchmark_with_cui": ("Same as exact_semantic but CUI RETAINED (benchmark-comparable)."),
}

# component_name -> (key_builder, uses_state_column)
# uses_state_column: whether to render the projected-state column (the
# attribute-level exact_semantic / benchmark_with_cui keys have no single state).
_STATE_KEY_BUILDERS = {
    "clinical_headline": lambda anns: _frequency_state_keys(anns, "clinical_headline"),
    "state_profile": _frequency_state_profile_keys,
    "state_profile_directional": _frequency_state_profile_directional_keys,
    "state_profile_direction_deconf": _frequency_state_profile_direction_deconf_keys,
    "state_profile_magnitude": _frequency_state_profile_magnitude_keys,
    "active_rate": lambda anns: _frequency_state_keys(anns, "active-rate"),
    "active_rate_fidelity": _frequency_active_rate_keys,
    "seizure_free": lambda anns: _frequency_state_keys(anns, "seizure-free"),
    "unknown": lambda anns: _frequency_state_keys(anns, "unknown"),
}

COMPONENT_ORDER = [
    "clinical_headline",
    "state_profile",
    "state_profile_directional",
    "state_profile_direction_deconf",
    "state_profile_magnitude",
    "active_rate",
    "active_rate_fidelity",
    "seizure_free",
    "unknown",
    "exact_semantic",
    "benchmark_with_cui",
]


class SfInspectionFaithfulnessError(RuntimeError):
    """Raised when the rebuilt scorecard drifts from the published anchors."""


# ---------------------------------------------------------------------------
# Data loading (same construction the magnitude-complement runner uses).
# ---------------------------------------------------------------------------
def _pred_letters_from_artifact(
    jsonl_path: Path, gold_by_id: dict[str, ExectLetter]
) -> tuple[list[ExectLetter], dict[str, dict[str, Any]]]:
    """Build predicted ExectLetters from an SF artifact, preserving the raw rows.

    Returns (pred_letters, rows_by_id) so the builder can read candidate_spans,
    draft_mentions, provenance, etc. straight from the source record.
    """

    pred: list[ExectLetter] = []
    rows_by_id: dict[str, dict[str, Any]] = {}
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        gold = gold_by_id.get(lid)
        if gold is None:
            continue
        rows_by_id[lid] = row
        anns_list: list[ExectAnnotation] = []
        for m in row.get("predicted_mentions", []):
            if m.get("entity") != SF_ENTITY:
                continue
            attrs = {str(k): str(v) for k, v in dict(m.get("attributes", {})).items()}
            anns_list.append(
                ExectAnnotation(
                    entity=SF_ENTITY,
                    text=str(m.get("text", "")),
                    attributes=attrs,
                )
            )
        pred.append(
            ExectLetter(letter_id=lid, note_text=gold.note_text, annotations=tuple(anns_list))
        )
    return pred, rows_by_id


def _baseline_freqchange_by_letter() -> dict[str, list[str]]:
    """{letter_id: [FrequencyChange values across SF predicted_mentions]} from the
    v08 baseline, used to flag where the LLM magnitude selector overwrote values."""

    out: dict[str, list[str]] = {}
    if not BASELINE_ARTIFACT.exists():
        return out
    for line in BASELINE_ARTIFACT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        vals: list[str] = []
        for m in row.get("predicted_mentions", []):
            if m.get("entity") != SF_ENTITY:
                continue
            attrs = m.get("attributes") or {}
            if "FrequencyChange" in attrs:
                vals.append(str(attrs["FrequencyChange"]))
        out[lid] = vals
    return out


def _ledger_overrides_by_letter() -> dict[str, list[dict[str, Any]]]:
    """{letter_id: [ledger rows]} for the magnitude-complement run, when present."""

    out: dict[str, list[dict[str, Any]]] = {}
    if not LEDGER_ARTIFACT.exists():
        return out
    for line in LEDGER_ARTIFACT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        out.setdefault(row["letter_id"], []).append(row)
    return out


def _read_jsonl_tolerant(path: Path) -> list[dict[str, Any]]:
    """Newline-delimited JSON, tolerant of a missing file or a bad line.

    Mirrors ``observatory/routers/gold_noise.py:_read_jsonl`` -- a missing file
    is an empty list, not an error, and one malformed row can't blank the
    surface.
    """

    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _gold_data_issues_by_letter() -> dict[str, list[dict[str, Any]]]:
    """{letter_id: [gold_data_issues.jsonl rows]}, SeizureFrequency only."""

    out: dict[str, list[dict[str, Any]]] = {}
    for row in _read_jsonl_tolerant(GOLD_DATA_ISSUES_ARTIFACT):
        if row.get("entity") != SF_ENTITY:
            continue
        out.setdefault(row["letter_id"], []).append(row)
    return out


def _gold_case_ledger_by_letter() -> dict[str, list[dict[str, Any]]]:
    """{letter_id: [gold_case_ledger_seizurefrequency.jsonl rows]}.

    Best-effort, disclosed as such: this ledger was adjudicated against a
    *different* run than the one this module scores (see
    ``GOLD_CASE_LEDGER_ARTIFACT``'s module comment), so it is surfaced at the
    letter level -- "a prior adjudication exists for this letter" -- not
    matched to one exact mention.
    """

    out: dict[str, list[dict[str, Any]]] = {}
    for row in _read_jsonl_tolerant(GOLD_CASE_LEDGER_ARTIFACT):
        out.setdefault(row["letter_id"], []).append(row)
    return out


def _gold_issue_for_mention(
    issues: list[dict[str, Any]], attributes: Mapping[str, str]
) -> dict[str, Any] | None:
    """The first ``gold_data_issues`` row whose disputed field(s) this mention
    actually populates, or ``None``. Precise (curated per-fact), unlike the
    ledger's letter-level, cross-run best-effort join."""

    populated = {key for key, value in attributes.items() if value}
    for issue in issues:
        fields = {f.strip() for f in str(issue.get("field", "")).split(",")}
        if populated & fields:
            return issue
    return None


# ---------------------------------------------------------------------------
# Per-attribute validation (mirrors contract/validate.py:22-41 exactly, applied
# per attribute so the report can flag individual illegal values).
# ---------------------------------------------------------------------------
def _attr_validation(spec_value: tuple[str, str]) -> str:
    key, value = spec_value
    if key in SEIZURE_FREQUENCY.noise_attributes:
        return "noise"
    if key not in SEIZURE_FREQUENCY.legal_attributes:
        return "illegal_attr"
    if key in SEIZURE_FREQUENCY.closed_vocab and value not in SEIZURE_FREQUENCY.closed_vocab[key]:
        return "illegal_value"
    return "ok"


# ---------------------------------------------------------------------------
# Key / value formatting for the payload.
# ---------------------------------------------------------------------------
def _type_key_str(annotation: ExectAnnotation) -> str:
    cui = annotation.attributes.get("CUI")
    if cui:
        return f"CUI:{canonicalize_attribute_value('CUI', cui)}"
    return f"phrase:{normalize_phrase(annotation.text)}"


def _type_key_str_from_tuple(type_key: Any) -> str:
    kind, val = type_key
    return f"{kind}:{val}"


def _state_key_str(raw_key: Any, component: str) -> str:
    """Render a scorer key (often nested tuples) as a readable string.

    Key shapes vary by component family:
      - state_profile / state_profile_directional / state_profile_direction_deconf
        / state_profile_magnitude -> bare state STRING (e.g. 'active-rate').
      - clinical_headline / active_rate / seizure_free / unknown ->
        ((type_kind, type_val), state).
      - active_rate_fidelity -> ((type_kind, type_val), rate_tuple).
      - exact_semantic / benchmark_with_cui ->
        (entity, phrase, attr_tuple)."""

    if component == "active_rate_fidelity":
        type_key, rate = raw_key
        head = _type_key_str_from_tuple(type_key)
        rate_s = ", ".join(f"{k}={v}" for k, v in rate) or "(no rate attrs)"
        return f"{head} | rate[{rate_s}]"
    if component in {
        "state_profile",
        "state_profile_directional",
        "state_profile_direction_deconf",
        "state_profile_magnitude",
    }:
        # Bare state string, type-agnostic.
        return str(raw_key)
    if component in {"clinical_headline", "active_rate", "seizure_free", "unknown"}:
        type_key, state = raw_key
        head = _type_key_str_from_tuple(type_key)
        return f"{head} | {state}"
    # exact_semantic / benchmark_with_cui: (entity, phrase, attr_tuple)
    entity, phrase, attr_tuple = raw_key
    attrs_s = ", ".join(f"{k}={v}" for k, v in attr_tuple) or "(no attrs)"
    return f"{phrase} | {attrs_s}"


def _fmt_attr_value(value: str | None) -> str:
    return "" if value in (None, "") else value  # empty string = absent for JSON


# ---------------------------------------------------------------------------
# Per-letter, per-component computation.
# ---------------------------------------------------------------------------
def _component_keys(component: str, anns: tuple[ExectAnnotation, ...]) -> list[Any]:
    if component in _STATE_KEY_BUILDERS:
        return _STATE_KEY_BUILDERS[component](anns)
    if component == "exact_semantic":
        return _keys(anns, semantic_config_for(SF_ENTITY))
    if component == "benchmark_with_cui":
        return _keys(anns, benchmark_config_for(SF_ENTITY))
    raise KeyError(component)


def _letter_component_errors(
    gold_anns: tuple[ExectAnnotation, ...],
    pred_anns: tuple[ExectAnnotation, ...],
    component: str,
) -> int:
    """FP+FN count for one component in one letter (what the nav badges sum)."""

    _g, _p, _t, fp, fn = _per_mention_status(gold_anns, pred_anns, component)
    return fp + fn


def _per_mention_key(component: str, ann: ExectAnnotation) -> Any:
    """The key ONE mention projects to under ``component`` (no per-letter dedup).

    The deduping builders above collapse repeated keys within a letter via
    ``dict.fromkeys``; for the per-mention rows we want a 1:1 mention->key map
    (same key value, just not collapsed), so we recompute each mention's key
    individually. The multiset counts still use the deduped builders via
    :func:`_component_keys` so TP/FP/FN match the scorer exactly."""

    a = (ann,)
    keys = _component_keys(component, a)
    return keys[0] if keys else None


def _per_mention_status(
    gold_anns: tuple[ExectAnnotation, ...],
    pred_anns: tuple[ExectAnnotation, ...],
    component: str,
) -> tuple[
    list[tuple[ExectAnnotation, Any, str]],
    list[tuple[ExectAnnotation, Any, str]],
    int,
    int,
    int,
]:
    """Return (gold_rows, pred_rows, tp, fp, fn) for one component in one letter.

    Each row is (annotation, key, status) where status is tp/fn/fp. TP/FP/FN use
    the deduped key builders (matching the scorer exactly); the per-mention key
    shown for each row is computed individually (same value, not collapsed)."""

    # Deduped key multisets -- what the scorer actually compares.
    gold_keys = _component_keys(component, gold_anns)
    pred_keys = _component_keys(component, pred_anns)
    s = multiset_prf1(gold_keys, pred_keys)

    # Per-mention keys (1:1 with mentions) for the display rows.
    g_pm = [_per_mention_key(component, ann) for ann in gold_anns]
    p_pm = [_per_mention_key(component, ann) for ann in pred_anns]

    tp_budget = Counter(gold_keys) & Counter(pred_keys)
    gold_rows: list[tuple[ExectAnnotation, Any, str]] = []
    for ann, key in zip(gold_anns, g_pm, strict=True):
        if key is None:
            gold_rows.append((ann, key, "skip"))  # filtered out of this component
        elif tp_budget.get(key, 0) > 0:
            tp_budget[key] -= 1
            gold_rows.append((ann, key, "tp"))
        else:
            gold_rows.append((ann, key, "fn"))

    tp_budget2 = Counter(gold_keys) & Counter(pred_keys)
    pred_rows: list[tuple[ExectAnnotation, Any, str]] = []
    for ann, key in zip(pred_anns, p_pm, strict=True):
        if key is None:
            pred_rows.append((ann, key, "skip"))
        elif tp_budget2.get(key, 0) > 0:
            tp_budget2[key] -= 1
            pred_rows.append((ann, key, "tp"))
        else:
            pred_rows.append((ann, key, "fp"))

    return gold_rows, pred_rows, s.tp, s.fp, s.fn


def _projection_state_for(component: str, ann: ExectAnnotation) -> str:
    """The projected state label a component would assign (for the state column)."""

    if component in {"exact_semantic", "benchmark_with_cui"}:
        return "(attribute key)"
    if component == "state_profile":
        return frequency_state_faithful(ann.attributes)
    if component == "state_profile_directional":
        return frequency_state_directional(ann.attributes)
    if component == "state_profile_direction_deconf":
        return frequency_state_direction_deconf(ann.attributes)
    if component == "state_profile_magnitude":
        return frequency_state_magnitude(ann.attributes)
    # clinical_headline / active_rate / seizure_free / unknown all key on the
    # count-only _frequency_state.
    return _count_based_state(ann.attributes) or "unknown"


# ---------------------------------------------------------------------------
# Payload construction.
# ---------------------------------------------------------------------------
def _scorecard_dict(scores: Any) -> dict[str, dict[str, float | int]]:
    out: dict[str, dict[str, float | int]] = {}
    for name in COMPONENT_ORDER:
        s = getattr(scores, name)
        out[name] = {
            "f1": round(s.f1, 4),
            "precision": round(s.precision, 4),
            "recall": round(s.recall, 4),
            "tp": s.tp,
            "fp": s.fp,
            "fn": s.fn,
        }
    return out


def _point_range_match_overrides(
    gold_attrs: Mapping[str, str],
    pred_attrs: Mapping[str, str],
    triples: tuple[tuple[str, str, str], ...],
) -> dict[str, str]:
    """Per-key ``ok``/``bad`` verdict for a bare/Lower/Upper triple, non-destructively.

    Unlike :func:`canonicalize_point_range_attributes` (which the scorer uses),
    this does not rewrite the displayed gold/pred values -- it only decides
    whether the triple, as a whole, denotes the same fact
    (:func:`resolve_point_range` equal on both sides), and applies that single
    verdict to every key in the triple that is populated on either side.
    """

    overrides: dict[str, str] = {}
    for triple in triples:
        gold_resolved = resolve_point_range(gold_attrs, triple)
        pred_resolved = resolve_point_range(pred_attrs, triple)
        if gold_resolved is None and pred_resolved is None:
            continue
        verdict = "ok" if gold_resolved == pred_resolved else "bad"
        for key in triple:
            if gold_attrs.get(key) or pred_attrs.get(key):
                overrides[key] = verdict
    return overrides


def _layer_a_pairs(
    gold_anns: tuple[ExectAnnotation, ...],
    pred_anns: tuple[ExectAnnotation, ...],
    gold_issues: list[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Layer A — schema attributes. Returns the list of pair dicts.

    Gold<->prediction pairs use the scorer's max-cardinality phrase-overlap
    matcher. For each predicted attribute the chain shown is:
    raw -> closed-vocab validity -> canonicalized -> compared to gold's
    canonicalized value. Out-of-vocab or unexpected attributes are flagged.
    """

    pairing = _match_gold_to_predictions(list(gold_anns), list(pred_anns))
    pred_used = set(pairing.values())

    pairs: list[dict[str, Any]] = []
    for gi, gold_ann in enumerate(gold_anns):
        pi = pairing.get(gi)
        pred_ann = pred_anns[pi] if pi is not None else None
        pairs.append(
            _attr_pair(gi, gold_ann, pred_ann, paired=pi is not None, gold_issues=gold_issues)
        )
    # Unpaired predictions = false positives.
    for pi, pred_ann in enumerate(pred_anns):
        if pi not in pred_used:
            pairs.append(
                _attr_pair(
                    None, None, pred_ann, paired=False, fp_only=True, gold_issues=gold_issues
                )
            )
    return pairs


def _attr_pair(
    index: int | None,
    gold_ann: ExectAnnotation | None,
    pred_ann: ExectAnnotation | None,
    *,
    paired: bool,
    fp_only: bool = False,
    gold_issues: list[dict[str, Any]] = (),
) -> dict[str, Any]:
    if fp_only:
        label = "PREDICTION (no matching gold — FALSE POSITIVE)"
        side = "fp"
    elif not paired:
        label = "GOLD (no matching prediction — FALSE NEGATIVE)"
        side = "fn"
    else:
        label = f"PAIR #{index + 1}" if index is not None else "PAIR"
        side = "pair"

    gold_phrase = gold_ann.text if gold_ann else None
    pred_phrase = pred_ann.text if pred_ann else None
    gold_attrs = gold_ann.attributes if gold_ann else {}
    pred_attrs = pred_ann.attributes if pred_ann else {}

    # Point/range shape-equivalence: a bare count/cadence and an equal-bounds
    # Lower/Upper range denote the same fact (see
    # scoring/normalize.py:resolve_point_range). This overrides the per-key
    # match verdict for whichever keys are populated on either side of such a
    # triple, WITHOUT rewriting the displayed raw values -- so the table still
    # shows gold said a bare count while pred said a range, but no longer
    # marks that shape difference itself as an error.
    triple_overrides = _point_range_match_overrides(
        gold_attrs, pred_attrs, POINT_RANGE_TRIPLES.get(SF_ENTITY, ())
    )

    attributes: list[dict[str, Any]] = []
    for key in SF_ATTR_ORDER:
        gval = gold_attrs.get(key)
        pval = pred_attrs.get(key)
        validity = _attr_validation((key, pval)) if pval is not None else "absent"
        canon = canonicalize_attribute_value(key, pval) if pval is not None else ""
        gcanon = canonicalize_attribute_value(key, gval) if gval is not None else ""
        if pval is None and gval is None:
            match = "absent"
        elif key in triple_overrides:
            match = triple_overrides[key]
        else:
            match = "ok" if canon == gcanon else "bad"
        attributes.append(
            {
                "key": key,
                "gold": _fmt_attr_value(gval),
                "pred": _fmt_attr_value(pval),
                "validity": validity,
                "canonical": canon,
                "match": match,
            }
        )

    gold_norm = normalize_phrase(gold_phrase) if gold_phrase else ""
    pred_norm = normalize_phrase(pred_phrase) if pred_phrase else ""
    if gold_phrase is None and pred_phrase is None:
        phrase_match = "absent"
    elif gold_phrase is None or pred_phrase is None:
        phrase_match = "bad"
    else:
        phrase_match = "ok" if gold_norm == pred_norm else "bad"

    gold_advisory = None
    if gold_issues:
        # Fires for a "fp"/"fn" (no counterpart at all) as much as a "pair" row
        # whose disagreement is a mismatched value rather than a missing
        # mention (EA0079: gold and pred phrase-pair, but gold's own
        # TimePeriod/NumberOfTimePeriods disagree with the source text).
        disputed_keys = {a["key"] for a in attributes if a["match"] == "bad"}
        issue = _gold_issue_for_mention(list(gold_issues), {k: "1" for k in disputed_keys})
        if issue is not None:
            gold_advisory = {
                "source": "gold_data_issues",
                "gold_value": issue.get("gold_value", ""),
                "conflicting_evidence": issue.get("conflicting_evidence", ""),
                "resolution_status": issue.get("resolution_status", ""),
            }

    return {
        "label": label,
        "side": side,
        "gold_phrase": gold_phrase or "",
        "gold_normalized": gold_norm,
        "pred_phrase": pred_phrase or "",
        "pred_normalized": pred_norm,
        "phrase_match": phrase_match,
        "attributes": attributes,
        "gold_advisory": gold_advisory,
    }


def _layer_b_components(
    gold_anns: tuple[ExectAnnotation, ...],
    pred_anns: tuple[ExectAnnotation, ...],
) -> list[dict[str, Any]]:
    """Layer B — scoring components. Returns the list of component dicts.

    Each of the 11 FrequencyStateScores projects every mention through a
    different rule into a hashable key; letters are scored by multiset
    (order-independent) match. For each component the table shows each mention's
    attribute inputs -> count-based state -> the component's projected state ->
    final key, with TP / FP / FN status for THIS letter."""

    components: list[dict[str, Any]] = []
    for component in COMPONENT_ORDER:
        components.append(_component_block(gold_anns, pred_anns, component))
    return components


def _component_block(
    gold_anns: tuple[ExectAnnotation, ...],
    pred_anns: tuple[ExectAnnotation, ...],
    component: str,
) -> dict[str, Any]:
    gold_rows, pred_rows, tp, fp, fn = _per_mention_status(gold_anns, pred_anns, component)
    info = COMPONENT_INFO[component]
    has_error = bool(fp or fn)
    verdict = "clean" if not has_error else "err"

    rows: list[dict[str, Any]] = []
    for ann, key, status in gold_rows:
        rows.append(_mention_row(ann, key, status, "gold", component))
    for ann, key, status in pred_rows:
        rows.append(_mention_row(ann, key, status, "pred", component))

    if not gold_anns and not pred_anns:
        rows = []

    return {
        "name": component,
        "info": info,
        "has_error": has_error,
        "verdict": verdict,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "rows": rows,
    }


def _counts_str(attrs: dict[str, str]) -> str:
    counts = (
        f"NS={attrs.get('NumberOfSeizures', '')}/"
        f"L={attrs.get('LowerNumberOfSeizures', '')}/"
        f"U={attrs.get('UpperNumberOfSeizures', '')}"
    ).replace("NS=/L=/U=", "(no counts)")
    return counts


def _mention_row(
    ann: ExectAnnotation,
    key: Any,
    status: str,
    side: str,
    component: str,
) -> dict[str, Any]:
    attrs = ann.attributes
    counts = _counts_str(dict(attrs))
    fchange = attrs.get("FrequencyChange", "")
    count_state = _count_based_state(attrs) or ""
    proj_state = _projection_state_for(component, ann)
    if status == "skip":
        return {
            "side": side,
            "phrase": ann.text,
            "counts": counts,
            "frequency_change": fchange,
            "count_state": count_state,
            "projected_state": "",
            "key": "",
            "status": "skip",
        }
    key_str = _state_key_str(key, component)
    return {
        "side": side,
        "phrase": ann.text,
        "counts": counts,
        "frequency_change": fchange,
        "count_state": count_state,
        "projected_state": proj_state,
        "key": key_str,
        "status": status,
    }


def _lineage_dict(
    row: dict[str, Any],
    gold_anns: tuple[ExectAnnotation, ...],
    pred_anns: tuple[ExectAnnotation, ...],
    baseline_fc: dict[str, list[str]],
    ledger_rows: list[dict[str, Any]],
    lid: str,
) -> dict[str, Any]:
    spans = [
        {
            "text_hint": c.get("text_hint", ""),
            "candidate_type": c.get("candidate_type", ""),
            "source": c.get("source", ""),
            "evidence": (c.get("evidence", "") or "")[:140],
        }
        for c in row.get("candidate_spans", [])
        if c.get("decision_lane") == "active_rate"
    ]

    override: dict[str, Any] | None = None
    if ledger_rows:
        items = [
            {
                "applies_to": lr.get("applies_to", ""),
                "prior_frequency_change": lr.get("prior_frequency_change", ""),
                "assembled_magnitude": lr.get("assembled_magnitude", ""),
                "selection_mode": lr.get("selection_mode", ""),
                "selected_candidate_id": lr.get("selected_candidate_id", ""),
            }
            for lr in ledger_rows
        ]
        override = {"applied": True, "items": items}
    else:
        base_vals = baseline_fc.get(lid, [])
        comp_vals = [
            a.attributes.get("FrequencyChange")
            for a in pred_anns
            if a.attributes.get("FrequencyChange")
        ]
        if base_vals and base_vals != comp_vals:
            override = {
                "applied": False,
                "baseline": base_vals,
                "complement": comp_vals,
            }

    return {"candidate_spans": spans, "override": override}


def _letter_dict(
    letter: ExectLetter,
    pred_anns: tuple[ExectAnnotation, ...],
    row: dict[str, Any],
    baseline_fc: dict[str, list[str]],
    ledger_rows: list[dict[str, Any]],
    gold_issues: list[dict[str, Any]] = (),
    gold_case_ledger_rows: list[dict[str, Any]] = (),
) -> dict[str, Any]:
    lid = letter.letter_id
    gold_anns = letter.entities(SF_ENTITY)

    # Per-letter directional + magnitude error counts for the nav badges.
    _, _, _d_tp, d_fp, d_fn = _per_mention_status(gold_anns, pred_anns, "state_profile_directional")
    _, _, _m_tp, m_fp, m_fn = _per_mention_status(gold_anns, pred_anns, "state_profile_magnitude")
    total_errors = sum(_letter_component_errors(gold_anns, pred_anns, c) for c in COMPONENT_ORDER)
    has_activity = bool(gold_anns or pred_anns)

    return {
        "letter_id": lid,
        "has_activity": has_activity,
        "gold_count": len(gold_anns),
        "pred_count": len(pred_anns),
        "total_errors": total_errors,
        "direction_errors": {"fp": d_fp, "fn": d_fn},
        "magnitude_errors": {"fp": m_fp, "fn": m_fn},
        "layer_a": {"pairs": _layer_a_pairs(gold_anns, pred_anns, gold_issues)},
        "layer_b": {"components": _layer_b_components(gold_anns, pred_anns)},
        "lineage": _lineage_dict(row, gold_anns, pred_anns, baseline_fc, ledger_rows, lid),
        # Read-only, best-effort disclosure surface (see GOLD_CASE_LEDGER_ARTIFACT's
        # module comment): a prior canonical adjudication exists for this
        # letter, possibly against a different run/mention than shown above.
        "gold_case_ledger": [
            {
                "disagreement_type": r.get("disagreement_type", ""),
                "match_key": r.get("match_key", ""),
                "mechanism": r.get("mechanism", ""),
                "verdict": r.get("verdict", "unadjudicated"),
                "reason": (r.get("provenance") or {}).get("reason", ""),
                "run_id": r.get("run_id", ""),
            }
            for r in gold_case_ledger_rows
        ],
    }


# ---------------------------------------------------------------------------
# Public entry points.
# ---------------------------------------------------------------------------
def build_sf_inspection_payload(*, artifact: Path | None = None) -> dict[str, Any]:
    """Build the SeizureFrequency inspection payload.

    Re-scores all dev letters with the real ``score_frequency_state`` and raises
    :class:`SfInspectionFaithfulnessError` if the scorecard drifts from the
    published anchors -- so a 500 reaches the caller instead of a silent bad
    payload.
    """

    dev_gold = load_letters_for_split(SPLIT)
    gold_by_id = {le.letter_id: le for le in dev_gold}
    complement = artifact or COMPLEMENT_ARTIFACT
    pred_letters, rows_by_id = _pred_letters_from_artifact(complement, gold_by_id)
    pred_by_id = {le.letter_id: le for le in pred_letters}
    baseline_fc = _baseline_freqchange_by_letter()
    ledger = _ledger_overrides_by_letter()
    gold_issues = _gold_data_issues_by_letter()
    gold_case_ledger = _gold_case_ledger_by_letter()

    # ---- Faithfulness gate: reproduce the published F1s exactly. ----
    scores = score_frequency_state(dev_gold, pred_letters)
    failures: list[str] = []
    for name, expected in EXPECTED_F1.items():
        got = getattr(scores, name).f1
        if abs(got - expected) > ANCHOR_TOLERANCE:
            failures.append(f"{name}: got {got:.4f}, expected {expected:.4f}")
    if failures:
        detail = "; ".join(failures)
        raise SfInspectionFaithfulnessError(
            f"SF inspection payload would drift from scorer ({detail})"
        )

    scorecard = _scorecard_dict(scores)
    components_meta = [{"name": name, "info": COMPONENT_INFO[name]} for name in COMPONENT_ORDER]

    all_ids = sorted(set(gold_by_id) | set(pred_by_id))
    letters: list[dict[str, Any]] = []
    for lid in all_ids:
        letter = gold_by_id.get(lid) or pred_by_id.get(lid)
        pred_anns = pred_by_id[lid].entities(SF_ENTITY) if lid in pred_by_id else ()
        row = rows_by_id.get(lid, {})
        letters.append(
            _letter_dict(
                letter,
                pred_anns,
                row,
                baseline_fc,
                ledger.get(lid, []),
                gold_issues.get(lid, []),
                gold_case_ledger.get(lid, []),
            )
        )

    n_letters = len(all_ids)
    n_with_errors = sum(1 for d in letters if d["total_errors"])

    return {
        "generated_on": date.today().isoformat(),
        "split": SPLIT,
        "artifact": complement.name,
        "scorecard": scorecard,
        "components": components_meta,
        "n_letters": n_letters,
        "n_with_errors": n_with_errors,
        "letters": letters,
    }


@lru_cache(maxsize=1)
def cached_sf_inspection_json() -> str:
    """Process-cached, pre-serialized JSON for ``GET /exectv2/sf-inspection``.

    Mirrors :func:`cached_exectv2_runs_json`: the (heavy) payload is built once
    per process and re-serialized, so repeated requests cost only the Response
    write. The faithfulness gate runs inside :func:`build_sf_inspection_payload`,
    so a drift surfaces as a 500 on first hit rather than a stale cache.
    """

    return json.dumps(build_sf_inspection_payload(), ensure_ascii=False)
