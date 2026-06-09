from __future__ import annotations

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.core.validation import ValidationIssue, ValidationResult
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    EntitySpec,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)


def validate_mention(
    mention: PredictedMention,
    source_text: str,
    spec: EntitySpec,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for key in mention.attributes:
        if key in spec.noise_attributes:
            continue
        if key not in spec.legal_attributes:
            issues.append(
                ValidationIssue(
                    code="illegal_attribute",
                    message=f"{spec.name}: unexpected attribute {key!r}",
                )
            )
        elif key in spec.closed_vocab and mention.attributes[key] not in spec.closed_vocab[key]:
            issues.append(
                ValidationIssue(
                    code="illegal_attribute_value",
                    message=(
                        f"{spec.name}.{key}: value {mention.attributes[key]!r} not in "
                        f"{sorted(spec.closed_vocab[key])}"
                    ),
                )
            )

    if not mention.evidence:
        issues.append(
            ValidationIssue(
                code="missing_evidence",
                message=f"{spec.name}: evidence field is empty",
                severity="warning",
            )
        )
    elif source_text and not evidence_is_substring(source_text, mention.evidence):
        issues.append(
            ValidationIssue(
                code="evidence_not_substring",
                message=f"{spec.name}: evidence not found verbatim in source text",
                severity="warning",
            )
        )

    return issues


def validate_letter(prediction: PredictedLetter, source_text: str = "") -> ValidationResult:
    """Validate all mentions in a predicted letter against the entity registry.

    ``source_text`` enables evidence-is-substring checking; omit (or pass empty
    string) to skip that check (e.g. when the source is unavailable at score time).
    """
    issues: list[ValidationIssue] = []

    for mention in prediction.mentions:
        spec = ENTITY_REGISTRY.get(mention.entity)
        if spec is None:
            issues.append(
                ValidationIssue(
                    code="unknown_entity",
                    message=f"entity {mention.entity!r} not in registry",
                )
            )
            continue
        issues.extend(validate_mention(mention, source_text, spec))

    return ValidationResult(
        ok=not any(i.severity == "error" for i in issues),
        issues=issues,
    )
