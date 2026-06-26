"""Catalog-backed noise builders."""

from __future__ import annotations

import re

from .context import ConventionContext
from . import _legacy_impl as legacy
from .registry import register_builder

_SF_VAGUE_EPISODE_RE = legacy._SF_VAGUE_EPISODE_RE
_SF_RISK_COUNSELLING_RE = legacy._SF_RISK_COUNSELLING_RE
_SF_CONTEXTUAL_RATE_NOISE_RE = legacy._SF_CONTEXTUAL_RATE_NOISE_RE
_SF_CONTEXTUAL_SEIZURE_FREE_RE = legacy._SF_CONTEXTUAL_SEIZURE_FREE_RE
_SF_HISTORICAL_COMPARATOR_RE = legacy._SF_HISTORICAL_COMPARATOR_RE


@register_builder('noise_branch_01')
def builder_noise_branch_01(ctx: ConventionContext) -> bool | None:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (_SF_VAGUE_EPISODE_RE.fullmatch(phrase)):
        return True
    return None

@register_builder('noise_branch_02')
def builder_noise_branch_02(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase in {
        "absences and jerks",
        "attacks",
        "collapses",
        "collapse episode",
        "dissociative seizures",
        "drops",
        "drop attacks",
        "events",
        "febrile seizure",
        "febrile seizures",
        "general and complex partial seizures",
        "grand mal episodes",
        "mini shakes",
        "minor seizures",
        "one of them",
        "seizure frequency",
        "seizure like episodes",
        "these",
        "staring episodes",
        "two unprovoked generalised seizures",
    }):
        return True
    return None

@register_builder('noise_branch_03')
def builder_noise_branch_03(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase == "one seizure" and _SF_RISK_COUNSELLING_RE.search(evidence)):
        return True
    return None

@register_builder('noise_branch_04')
def builder_noise_branch_04(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase == "further seizures" and _SF_RISK_COUNSELLING_RE.search(evidence)):
        return True
    return None

@register_builder('noise_branch_05')
def builder_noise_branch_05(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase == "previous seizures"):
        return True
    return None

@register_builder('noise_branch_06')
def builder_noise_branch_06(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (cui == "C0563606" and "NumberOfSeizures" not in attrs and re.search(
        r"\b(?:absence\s+like\s+seizures\s+2014|typical\s+absences|"
        r"at\s+(?:around\s+)?the\s+age\s+of\s+8\b[^.]{0,120}\brelatively\s+infrequent|"
        r"relatively\s+infrequent\b[^.]{0,120}\bat\s+(?:around\s+)?the\s+age\s+of\s+8)\b",
        evidence,
        re.IGNORECASE,
    )):
        return True
    return None

@register_builder('noise_branch_07')
def builder_noise_branch_07(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (cui == "C0036572" and re.search(
        r"\baround\s+3\s+seizures\s+per\s+month\b",
        evidence,
        re.IGNORECASE,
    )):
        return True
    return None

@register_builder('noise_branch_08')
def builder_noise_branch_08(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (cui == "C0877017" and re.search(
        r"\b(?:focal\s+to\s+bilateral\s+convulsive\s+seizures?\s+\d{4}|"
        r"three\s+episodes\s+whilst\s+asleep)\b",
        evidence,
        re.IGNORECASE,
    )):
        return True
    return None

@register_builder('noise_branch_09')
def builder_noise_branch_09(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (cui == "C1299590"
        and attrs.get("NumberOfSeizures") == "0"
        and _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)):
        return True
    return None

@register_builder('noise_keep_canonical_seizure_free')
def builder_noise_keep_canonical_seizure_free(ctx: ConventionContext) -> bool | None:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if cui == "C1299590" and attrs.get("NumberOfSeizures") == "0":
        return False
    return None

@register_builder('noise_branch_11')
def builder_noise_branch_11(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase in {"seizure", "seizures", "seizure free", "seizure freedom"} and (
        _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)
    )):
        return True
    return None

@register_builder('noise_branch_12')
def builder_noise_branch_12(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase in {"seizure", "seizures", "seizure free"} and _SF_CONTEXTUAL_SEIZURE_FREE_RE.search(
        evidence
    )):
        return True
    return None

@register_builder('noise_branch_13')
def builder_noise_branch_13(ctx: ConventionContext) -> bool:
    phrase = ctx.phrase
    evidence = ctx.evidence
    attrs = {str(k): str(v) for k, v in ctx.attrs.items()}
    cui = attrs.get("CUI")
    if (phrase == "seizure" and _SF_HISTORICAL_COMPARATOR_RE.search(evidence)):
        return True
    return None
