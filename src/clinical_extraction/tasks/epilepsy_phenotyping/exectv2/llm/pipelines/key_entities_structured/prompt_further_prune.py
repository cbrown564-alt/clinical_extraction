"""Further prunes of the cleaned cheap-stack prompt.

Study-only. Applied after the v0.9.40 structural drop and the language
pass. One-cut arms apply a single kind. The stacked arm applies all
three in order.
"""

from __future__ import annotations

from typing import Any

IX_PENDING = "ix_pending"
SCAFFOLD_REPRINT = "scaffold_reprint"
REFUSE_CHORUS = "refuse_chorus"
STACKED_PRUNES = (IX_PENDING, SCAFFOLD_REPRINT, REFUSE_CHORUS)

_IX_PENDING_DROP_PREFIXES = (
    "Completed historical tests and tests with results include Investigations",
    "Do not include future planned, requested, repeat, or follow-up investigations",
    "Never include an Investigations mention whose only support is pending-test",
)

_SCAFFOLD_DROP_PREFIXES = (
    "First classify each suggested-evidence row into a category:",
)

_SCAFFOLD_DECISION = [
    "Scan the whole letter. Do not stop at section headers.",
    (
        "Treat suggested-evidence rows as hints. Keep, reject, split, or "
        "merge only when the full sentence supports that family."
    ),
    (
        "Before returning JSON, remove duplicates and remove events whose "
        "evidence or mention text is not an exact copy from the letter."
    ),
]

_REFUSE_DROP_PREFIXES = (
    "Do not include vague symptoms, blackout/loss-of-consciousness",
    "Do not include isolated symptoms or aura features as Diagnosis",
    "A problem-list or Diagnosis header is not enough by itself",
    "Do not include SeizureFrequency for generic events, blackouts",
    "Reject vague words such as 'events', 'episodes'",
    "Do not include childhood febrile seizures, family-history seizures",
    "Do not include risk or counselling statements",
    "Do not include non-epileptic or diagnostically vague episode descriptions",
    "Do not include old or contextual minor-seizure episode phrases",
    "Do not include safety-advice, conditional, or instructional statements",
)

_COMBINED_REFUSE = (
    "Do not include blackouts, collapse, anxiety, dissociative or "
    "non-epileptic events, vague symptoms, isolated jerks or aura "
    "features, childhood febrile or family-history seizures, risk or "
    "counselling statements, safety advice, or vague words such as "
    "'events', 'episodes', or 'jerks' as Diagnosis or SeizureFrequency "
    "unless the letter explicitly states that phrase is an epileptic "
    "seizure, epilepsy diagnosis, or named seizure type. A Diagnosis or "
    "problem-list heading is not enough. Do not include old or contextual "
    "episode counts, or phrases such as 'if you have a seizure', as a "
    "current frequency."
)


def apply_further_prune(payload: dict[str, Any], kind: str) -> dict[str, Any]:
    """Return a copy of the cleaned cheap payload with one named chorus removed."""

    pruned = dict(payload)
    if kind == IX_PENDING:
        pruned["clinical_rules"] = _drop_prefixed(
            pruned["clinical_rules"], _IX_PENDING_DROP_PREFIXES
        )
        return pruned
    if kind == SCAFFOLD_REPRINT:
        pruned.pop("prompt_version", None)
        pruned.pop("letter_id", None)
        pruned["decision_procedure"] = list(_SCAFFOLD_DECISION)
        pruned["clinical_rules"] = _drop_prefixed(
            pruned["clinical_rules"], _SCAFFOLD_DROP_PREFIXES
        )
        return pruned
    if kind == REFUSE_CHORUS:
        rules = _drop_prefixed(pruned["clinical_rules"], _REFUSE_DROP_PREFIXES)
        insert_at = next(
            index
            for index, rule in enumerate(rules)
            if rule.startswith("Do not include negated resemblance")
        )
        rules.insert(insert_at, _COMBINED_REFUSE)
        pruned["clinical_rules"] = rules
        return pruned
    raise ValueError(f"unsupported further prune {kind!r}")


def _drop_prefixed(rules: list[str], prefixes: tuple[str, ...]) -> list[str]:
    return [
        rule
        for rule in rules
        if not any(rule.startswith(prefix) for prefix in prefixes)
    ]
