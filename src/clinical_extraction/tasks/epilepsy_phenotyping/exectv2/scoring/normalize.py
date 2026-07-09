from __future__ import annotations

import re
from collections.abc import Mapping

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)

_LOWERCASE_ATTRIBUTE_VALUES: frozenset[str] = frozenset({"DrugName", "DoseUnit"})
_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")

PointRangeTriple = tuple[str, str, str]


def canonicalize_attribute_value(key: str, value: str) -> str:
    """Apply format-only canonicalization before attribute matching.

    This deliberately cannot create a missing attribute or infer a clinical
    category. It only removes quote/whitespace noise and normalizes attributes
    where case is a spelling artifact under the ExECTv2 contract.
    """

    normalized = _WHITESPACE.sub(" ", str(value).translate(_QUOTES)).strip()
    if key in _LOWERCASE_ATTRIBUTE_VALUES:
        normalized = normalized.lower()
    return normalized


def resolve_point_range(
    attributes: Mapping[str, str], triple: PointRangeTriple
) -> tuple[str, ...] | None:
    """Collapse a ``(bare, lower, upper)`` attribute triple to one canonical value.

    Several ExECTv2 entities (SeizureFrequency's seizure/period counts, Onset and
    PatientHistory's ages) let an annotator express the same quantity two ways: a
    bare value, or a ``Lower*``/``Upper*`` pair. A degenerate range (``lower ==
    upper``) denotes the identical point value as the bare attribute -- but a
    plain per-key comparison sees three unrelated attribute names and never
    recognizes the equivalence. This resolves the triple to one of:

    - ``None`` -- nothing in the triple is populated.
    - ``("point", value)`` -- one unambiguous value, whether stated as the bare
      key, a degenerate range, or one of lower/upper alone.
    - ``("range", lower, upper)`` -- a genuine range (``lower != upper``). This
      never equals a point from the other side: a stated range is a strictly
      looser claim than a definite count, not the same fact.
    - ``("conflict", bare, lower, upper)`` -- the bare value disagrees with the
      lower/upper bound(s). Left unresolved on purpose: a real annotation
      inconsistency should surface as a mismatch, not be silently merged.
    """

    bare_key, lower_key, upper_key = triple
    bare_raw = attributes.get(bare_key) or None
    lower_raw = attributes.get(lower_key) or None
    upper_raw = attributes.get(upper_key) or None
    if bare_raw is None and lower_raw is None and upper_raw is None:
        return None

    bare = canonicalize_attribute_value(bare_key, bare_raw) if bare_raw is not None else None
    lower = canonicalize_attribute_value(lower_key, lower_raw) if lower_raw is not None else None
    upper = canonicalize_attribute_value(upper_key, upper_raw) if upper_raw is not None else None

    if lower is not None and upper is not None:
        if lower != upper:
            return ("conflict", bare, lower, upper) if bare is not None else ("range", lower, upper)
        bound = lower
    elif lower is not None or upper is not None:
        bound = lower if lower is not None else upper
    else:
        bound = None

    if bound is None:
        return ("point", bare)
    if bare is not None and bare != bound:
        return ("conflict", bare, lower, upper)
    return ("point", bound)


def canonicalize_point_range_attributes(
    attributes: Mapping[str, str], triples: tuple[PointRangeTriple, ...]
) -> dict[str, str]:
    """Rewrite a degenerate ``Lower*``/``Upper*`` range onto its bare key.

    For every triple that :func:`resolve_point_range` reduces to a single point,
    the returned copy drops the ``Lower*``/``Upper*`` entries and sets the bare
    key to that value -- so a bare count and an equal-bounds range project to the
    identical ``(key, value)`` pair wherever attribute tuples are built for
    matching. Genuine ranges and conflicts are left untouched: they should not
    match a point from the other side.
    """

    if not triples:
        return dict(attributes)
    result = dict(attributes)
    for triple in triples:
        bare_key, lower_key, upper_key = triple
        resolved = resolve_point_range(attributes, triple)
        if resolved is not None and resolved[0] == "point":
            result.pop(lower_key, None)
            result.pop(upper_key, None)
            result[bare_key] = resolved[1]
    return result


__all__ = [
    "canonicalize_attribute_value",
    "canonicalize_point_range_attributes",
    "normalize_phrase",
    "resolve_point_range",
]
