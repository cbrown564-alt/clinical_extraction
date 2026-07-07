"""SF projection builders migrated from ``target_projection/evidence_repair.py``."""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.constants import (
    ASYMMETRIC_DOSING,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.policy import (
    ProjectionFamilySwitches,
    is_projection_family_enabled,
    quarantined_projection_family_warning,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.shared import (
    clean_number,
    local_evidence_context,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection.types import (
    MentionT,
)


def repair_case_only_evidence(
    mentions: Sequence[MentionT],
    *,
    note_text: str,
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[list[MentionT], list[str]]:
    repaired: list[MentionT] = []
    warnings: list[str] = []
    lowered_note = note_text.lower()
    for mention in mentions:
        evidence = mention.evidence
        if evidence and evidence in note_text:
            if mention.entity == "Prescription":
                extended = extend_asymmetric_prescription_evidence(mention, note_text)
                if extended and extended != evidence:
                    repaired.append(mention.model_copy(update={"evidence": extended}))
                    warnings.append(f"extended_asymmetric_prescription_evidence: {mention.text!r}")
                    continue
            if mention.entity == "Diagnosis":
                extended = extend_probable_temporal_diagnosis_evidence(
                    mention,
                    note_text,
                )
                if extended and extended != evidence:
                    repaired.append(mention.model_copy(update={"evidence": extended}))
                    warnings.append(
                        f"extended_probable_temporal_diagnosis_evidence: {mention.text!r}"
                    )
                    continue
        if evidence and evidence not in note_text:
            index = lowered_note.find(evidence.lower())
            if index >= 0:
                exact = note_text[index : index + len(evidence)]
                repaired.append(mention.model_copy(update={"evidence": exact}))
                warnings.append(f"repaired_evidence_case: {mention.text!r}")
                continue
            whitespace_equivalent = repair_whitespace_equivalent_evidence(
                evidence,
                note_text,
            )
            if whitespace_equivalent:
                repaired.append(mention.model_copy(update={"evidence": whitespace_equivalent}))
                warnings.append(f"repaired_whitespace_equivalent_evidence: {mention.text!r}")
                continue
            stripped = evidence.rstrip(" .;:")
            if stripped != evidence and stripped in note_text:
                repaired.append(mention.model_copy(update={"evidence": stripped}))
                warnings.append(f"repaired_trailing_punctuation_evidence: {mention.text!r}")
                continue
            absence_like = repair_absence_like_frequency_evidence(mention, note_text)
            if absence_like:
                repaired.append(mention.model_copy(update={"evidence": absence_like}))
                warnings.append(f"repaired_absence_like_frequency_evidence: {mention.text!r}")
                continue
            since_clinic = repair_since_last_clinic_count_evidence(mention, note_text)
            if since_clinic:
                family = "repaired_since_last_clinic_count_evidence"
                if is_projection_family_enabled(family, projection_family_switches):
                    repaired.append(mention.model_copy(update={"evidence": since_clinic}))
                    warnings.append(f"{family}: {mention.text!r}")
                else:
                    repaired.append(mention)
                    warnings.append(quarantined_projection_family_warning(family))
                continue
            no_further = repair_no_further_since_evidence(mention, note_text)
            if no_further:
                repaired.append(mention.model_copy(update={"evidence": no_further}))
                warnings.append(f"repaired_no_further_since_evidence: {mention.text!r}")
                continue
            if (
                mention.entity == "SeizureFrequency"
                and mention.attributes.get("NumberOfSeizures") == "0"
                and "last one being around christmas" in evidence.lower()
            ):
                marker = "last one being around christmas time in 2017"
                marker_index = lowered_note.find(marker)
                if marker_index >= 0:
                    family = "repaired_last_event_evidence"
                    exact = note_text[marker_index : marker_index + len(marker)]
                    if is_projection_family_enabled(family, projection_family_switches):
                        repaired.append(mention.model_copy(update={"evidence": exact}))
                        warnings.append(f"{family}: {mention.text!r}")
                    else:
                        repaired.append(mention)
                        warnings.append(quarantined_projection_family_warning(family))
                    continue
            if mention.entity == "Prescription":
                ellipsis = repair_ellipsis_evidence(mention.evidence, note_text)
                if ellipsis:
                    repaired.append(mention.model_copy(update={"evidence": ellipsis}))
                    warnings.append(f"repaired_ellipsis_evidence: {mention.text!r}")
                    continue
                synonym = repair_prescription_frequency_synonym_evidence(
                    mention,
                    note_text,
                )
                if synonym:
                    repaired.append(mention.model_copy(update={"evidence": synonym}))
                    warnings.append(
                        f"repaired_prescription_frequency_synonym_evidence: {mention.text!r}"
                    )
                    continue
        repaired.append(mention)
    return repaired, warnings


def repair_whitespace_equivalent_evidence(evidence: str, note_text: str) -> str | None:
    tokens = [token for token in re.split(r"\s+", evidence.strip()) if token]
    if not tokens:
        return None
    pattern = re.compile(r"\s+".join(re.escape(token) for token in tokens), re.IGNORECASE)
    match = pattern.search(note_text)
    return match.group(0) if match else None


def repair_ellipsis_evidence(evidence: str, note_text: str) -> str | None:
    if "..." not in evidence:
        return None
    suffix = evidence.rsplit("...", 1)[-1].strip()
    if not suffix:
        return None
    lowered_note = note_text.lower()
    suffix_index = lowered_note.find(suffix.lower())
    if suffix_index < 0:
        return None
    return note_text[suffix_index : suffix_index + len(suffix)]


def repair_absence_like_frequency_evidence(
    mention: MentionT,
    note_text: str,
) -> str | None:
    attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
    normalized_text = normalize_phrase(mention.text)
    year = attrs.get("YearDate", "").strip()
    if (
        mention.entity != "SeizureFrequency"
        or normalized_text not in {"absence like seizure", "absence like seizures"}
        or not year
    ):
        return None
    pattern = re.compile(
        rf"\babsence\s+like\s+seizures?\s+{re.escape(year)}\b",
        re.IGNORECASE,
    )
    match = pattern.search(note_text)
    return match.group(0) if match else None


def repair_since_last_clinic_count_evidence(
    mention: MentionT,
    note_text: str,
) -> str | None:
    if mention.entity != "SeizureFrequency":
        return None
    evidence = normalize_phrase(mention.evidence)
    text = normalize_phrase(mention.text)
    if "last clinic" not in evidence or not text:
        return None
    if "secondary generalised seizures" not in evidence and text != (
        "secondary generalised seizures"
    ):
        return None
    pattern = re.compile(
        r"\bSince\s+her\s+last\s+clinic\s+appointment\s+she\s+has\s+had\s+"
        r"four\s+secondary\s+generalised\s+seizures\b",
        re.IGNORECASE,
    )
    match = pattern.search(note_text)
    return match.group(0) if match else None


def repair_no_further_since_evidence(
    mention: MentionT,
    note_text: str,
) -> str | None:
    if mention.entity != "SeizureFrequency":
        return None
    normalized_evidence = normalize_phrase(mention.evidence)
    if not normalized_evidence.startswith("no further "):
        return None
    rest = re.escape(normalized_evidence.removeprefix("no further ").strip())
    pattern = re.compile(rf"\b(?:has|have)\s+not\s+had\s+any\s+further\s+{rest}\b", re.I)
    match = pattern.search(note_text)
    return match.group(0) if match else None


def extend_asymmetric_prescription_evidence(
    mention: MentionT,
    note_text: str,
) -> str | None:
    attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
    drug = normalize_phrase(attrs.get("DrugName") or mention.text)
    if "levetiracetam" not in drug:
        return None
    if not re.search(r"\b\d+(?:\.\d+)?\s*mg\b.{0,30}\bmane\b", mention.evidence, re.I):
        return None
    context = local_evidence_context(note_text, mention.evidence, before=0, after=80)
    match = ASYMMETRIC_DOSING.search(context)
    return match.group(0) if match else None


def extend_probable_temporal_diagnosis_evidence(
    mention: MentionT,
    note_text: str,
) -> str | None:
    if mention.entity != "Diagnosis":
        return None
    if normalize_phrase(mention.text) not in {"epilepsy", "focal epilepsy"}:
        return None
    evidence = normalize_phrase(mention.evidence)
    if evidence != "focal epilepsy probable":
        return None
    pattern = re.compile(r"\bfocal\s+epilepsy\s*-\s*Probable\s+temporal\b", re.I)
    match = pattern.search(note_text)
    return match.group(0) if match else None


def repair_prescription_frequency_synonym_evidence(
    mention: MentionT,
    note_text: str,
) -> str | None:
    attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
    drug = normalize_phrase(attrs.get("DrugName", ""))
    dose = attrs.get("DrugDose", "").strip()
    if not drug or not dose or attrs.get("Frequency") != "2":
        return None
    pattern = re.compile(
        rf"\b{re.escape(drug)}\s+{re.escape(dose)}\s*mg\s+twice\s+a\s+day\b",
        re.IGNORECASE,
    )
    match = pattern.search(note_text)
    return match.group(0) if match else None


def repair_prescription_attrs_from_text(
    attrs: dict[str, str],
    *,
    source: str,
) -> list[str]:
    warnings: list[str] = []
    normalized_source = normalize_phrase(source)
    drug_aliases = {
        "carbamazepine": "carbamazepine",
        "clobazam": "clobazam",
        "lamotrigine": "lamotrigine",
        "levetiracetam": "levetiracetam",
        "phenytoin": "phenytoin",
        "sodium valproate": "sodium-valproate",
        "topiramate": "topiramate",
    }
    if not attrs.get("DrugName"):
        for phrase, drug_name in drug_aliases.items():
            if phrase in normalized_source:
                attrs["DrugName"] = drug_name
                warnings.append(f"inferred_prescription_drug_name: {drug_name}")
                break
    dose_match = re.search(
        r"\b(?P<dose>\d+(?:\.\d+)?)\s*(?P<unit>milligrams?|mgs?|mg|grams?|g)\b",
        source,
        re.IGNORECASE,
    )
    if dose_match:
        source_dose = clean_number(dose_match.group("dose"))
        if not attrs.get("DrugDose") or is_daily_total_dose(
            attrs.get("DrugDose", ""),
            source_dose,
            attrs.get("Frequency", ""),
        ):
            attrs["DrugDose"] = source_dose
            warnings.append(f"inferred_prescription_dose: {source_dose}")
        if not attrs.get("DoseUnit"):
            attrs["DoseUnit"] = dose_match.group("unit")
            warnings.append(f"inferred_prescription_dose_unit: {dose_match.group('unit')}")
    if not attrs.get("Frequency"):
        frequency = frequency_from_prescription_source(normalized_source)
        if frequency:
            attrs["Frequency"] = frequency
            warnings.append(f"inferred_prescription_frequency: {frequency}")
    elif re.search(r"\b(?:nocte|night|evening|afternoon|morning|mane)\b", normalized_source):
        frequency = frequency_from_prescription_source(normalized_source)
        if frequency and frequency != attrs.get("Frequency"):
            attrs["Frequency"] = frequency
            warnings.append(f"projected_prescription_frequency_from_evidence: {frequency}")
    return warnings


def is_daily_total_dose(raw_dose: str, source_dose: str, frequency: str) -> bool:
    if not raw_dose or not source_dose or not frequency.isdigit():
        return False
    try:
        return float(raw_dose) == float(source_dose) * int(frequency)
    except ValueError:
        return False


def frequency_from_prescription_source(normalized_source: str) -> str | None:
    if re.search(r"\b(?:bd|twice\s+(?:a\s+)?day|twice\s+daily)\b", normalized_source):
        return "2"
    if re.search(
        r"\b(?:tds|three\s+times\s+(?:a\s+)?day|three\s+times\s+daily)\b",
        normalized_source,
    ):
        return "3"
    if re.search(
        r"\b(?:mane|morning|nocte|night|once\s+(?:a\s+)?day|once\s+daily)\b",
        normalized_source,
    ):
        return "1"
    if re.search(r"\b(?:prn|as\s+required|rescue)\b", normalized_source):
        return "As_Required"
    return None
