"""External-signal feature construction for the calibration scoring-rule redesign.

These features replay saved dev140 artifacts — the same-core model-swap adjudicator
runs (GPT-4.1-mini / DeepSeek / Qwen 3.6) and the four-temperature self-consistency
runs — to derive per-(letter, family) signals that the original calibration rule never
consumed. They are part of the calibration strengthening plan
(`docs/plans/calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`).

Rule-family portability: ``gan2026_specific`` replay over saved dev140 artifacts. No
model calls are made and no full-200 or holdout rows are loaded.

The two signals:

* **Cross-model agreement** — the size of the largest identical-headline-keyset cluster
  across the three same-core models for a (letter, family), ported from the SF wall
  transfer probe's leg #1 and generalized to all four families via
  ``clinical_headline_unit_keys``. Agreement in {1, 2, 3}; risk = ``(3 - agreement) / 3``.
* **Self-consistency entropy** — normalized entropy of the headline-keyset distribution
  across the four temperature runs, per (letter, family). 0 when every run agrees,
  approaching 1 as the runs split evenly.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    FAMILIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.io import (
    REPO_ROOT,
    load_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)

# The three same-core model-swap adjudicator runs on dev140 (shared 140-letter space).
_CROSS_MODEL_CANDIDATES: tuple[str, ...] = ("gpt41mini", "deepseek", "qwen36")
_CROSS_MODEL_PATH_TEMPLATE = (
    "experiments/exectv2_2call_no_sf_adjudicator_{candidate}_dev140_20260625.jsonl"
)

# The four self-consistency temperature runs on dev140 (each 140 letters).
_SELF_CONSISTENCY_TEMPS: tuple[tuple[str, str], ...] = (
    ("r1", "temp0p3"),
    ("r2", "temp0p5"),
    ("r3", "temp0p7"),
    ("r4", "temp1p0"),
)
_SELF_CONSISTENCY_PATH_TEMPLATE = (
    "experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_"
    "{repeat}_{temp}_20260625_assembly.jsonl"
)


def cross_model_agreement_table(
    rows_by_candidate: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[tuple[str, str], dict[str, float]]:
    """Per-(letter, family) cross-model agreement risk from three same-core runs.

    ``rows_by_candidate`` maps each of the three candidate labels to its per-letter
    rows. Rows are inner-joined on ``letter_id``; only letters present in all three
    contribute. For each (letter, family) the agreement is the size of the largest
    identical-headline-keyset cluster across the three models (1..3), and ``risk``
    is ``(3 - agreement) / 3`` (0 = full agreement, ~0.67 = total disagreement).
    """

    indexed = {
        candidate: {str(row["letter_id"]): row for row in rows}
        for candidate, rows in rows_by_candidate.items()
    }
    candidates = list(rows_by_candidate)
    if not candidates:
        return {}
    shared: set[str] = set(indexed[candidates[0]])
    for candidate in candidates[1:]:
        shared &= set(indexed[candidate])

    table: dict[tuple[str, str], dict[str, float]] = {}
    for letter_id in sorted(shared):
        per_model_keysets: dict[str, dict[str, frozenset[Any]]] = {}
        for candidate in candidates:
            row = indexed[candidate][letter_id]
            for family in FAMILIES:
                keyset = _headline_keyset(row, family)
                per_model_keysets.setdefault(family, {})[candidate] = keyset
        for family in FAMILIES:
            keysets = list(per_model_keysets[family].values())
            agreement = max(Counter(keysets).values()) if keysets else 0
            table[(letter_id, family)] = {
                "agreement": float(agreement),
                "risk": round((3.0 - float(agreement)) / 3.0, 4),
            }
    return table


def self_consistency_entropy_table(
    runs: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str], float]:
    """Per-(letter, family) normalized self-consistency entropy across runs.

    ``runs`` is a sequence of per-letter row mappings (one per temperature run), each
    carrying ``letter_id`` and ``predicted_mentions``. For every (letter, family)
    present in any run, the headline keyset is reduced to a hashable fingerprint per
    run and the normalized Shannon entropy of the fingerprint distribution is returned
    (0 = every run agrees, approaching 1 as the runs split evenly).
    """

    by_letter: dict[str, list[Mapping[str, Any]]] = {}
    for row in runs:
        by_letter.setdefault(str(row["letter_id"]), []).append(row)

    table: dict[tuple[str, str], float] = {}
    for letter_id, letter_runs in by_letter.items():
        for family in FAMILIES:
            fingerprints = [_headline_keyset_fingerprint(row, family) for row in letter_runs]
            fingerprints = [fp for fp in fingerprints if fp is not None]
            table[(letter_id, family)] = round(_normalized_entropy(fingerprints), 4)
    return table


def load_dev140_cross_model_agreement(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[tuple[str, str], dict[str, float]]:
    """Load and score the three dev140 same-core model-swap runs."""

    rows_by_candidate = {
        candidate: load_jsonl(repo_root / _CROSS_MODEL_PATH_TEMPLATE.format(candidate=candidate))
        for candidate in _CROSS_MODEL_CANDIDATES
    }
    return cross_model_agreement_table(rows_by_candidate)


def load_dev140_self_consistency_entropy(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[tuple[str, str], float]:
    """Load and score the four dev140 self-consistency temperature runs."""

    runs: list[dict[str, Any]] = []
    for repeat, temp in _SELF_CONSISTENCY_TEMPS:
        path = repo_root / _SELF_CONSISTENCY_PATH_TEMPLATE.format(repeat=repeat, temp=temp)
        if path.exists():
            runs.extend(load_jsonl(path))
    return self_consistency_entropy_table(runs)


def auroc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    """AUROC via the Mann-Whitney U statistic (True label = positive class).

    Inlined here (rather than imported from the gan2026 ``artifact_analysis``
    research package) so the reliability reporting layer keeps a clean dependency
    boundary: production code must not import from the research layer (see
    ``scripts/check_artifact_analysis_imports.py``). The implementation matches the
    Mann-Whitney formulation used by the SF wall-transfer probe, so figures remain
    directly comparable.
    """

    pos = [s for s, y in zip(scores, labels, strict=True) if y]
    neg = [s for s, y in zip(scores, labels, strict=True) if not y]
    if not pos or not neg:
        return float("nan")
    ranked = sorted(zip(scores, labels, strict=True), key=lambda t: t[0])
    ranks: list[float] = [0.0] * len(ranked)
    i = 0
    while i < len(ranked):
        j = i
        while j + 1 < len(ranked) and ranked[j + 1][0] == ranked[i][0]:
            j += 1
        avg_rank = (i + j) / 2 + 1  # 1-based average rank
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    sum_ranks_pos = sum(r for r, (_, y) in zip(ranks, ranked, strict=True) if y)
    n_pos, n_neg = len(pos), len(neg)
    u = sum_ranks_pos - n_pos * (n_pos + 1) / 2
    return u / (n_pos * n_neg)


def _headline_keyset(row: Mapping[str, Any], family: str) -> frozenset[Any]:
    """The comparable per-model headline-unit fingerprint for one family in a row."""

    mentions = _family_mentions(row, family)
    keys = clinical_headline_unit_keys(family, _annotations(mentions))
    return frozenset(keys)


def _headline_keyset_fingerprint(row: Mapping[str, Any], family: str) -> frozenset[Any] | None:
    """Same as ``_headline_keyset`` but returns ``None`` when the family is absent.

    Used by self-consistency entropy so that a run emitting no mentions for a family
    is treated as a genuine (empty-frozenset) reading rather than dropped.
    """

    mentions = _family_mentions(row, family)
    keys = clinical_headline_unit_keys(family, _annotations(mentions))
    return frozenset(keys)


def _family_mentions(row: Mapping[str, Any], family: str) -> list[Mapping[str, Any]]:
    return [
        mention
        for mention in (row.get("predicted_mentions") or [])
        if str(mention.get("entity", "")) == family
    ]


def _annotations(mentions: Iterable[Mapping[str, Any]]) -> tuple[ExectAnnotation, ...]:
    return tuple(
        ExectAnnotation(
            entity=str(mention.get("entity", "")),
            text=str(mention.get("text", "")),
            attributes={
                str(key): str(value)
                for key, value in (mention.get("attributes") or {}).items()
                if value is not None
            },
        )
        for mention in mentions
    )


def _normalized_entropy(values: Sequence[Any]) -> float:
    """Normalized Shannon entropy over a discrete value distribution in [0, 1]."""

    vals = [v for v in values if v is not None]
    if len(vals) <= 1:
        return 0.0
    counts = Counter(vals)
    n = float(len(vals))
    h = -sum((count / n) * math.log(count / n) for count in counts.values())
    return h / math.log(n)
