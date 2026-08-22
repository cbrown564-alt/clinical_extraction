"""Declarative lookup tables for ExECTv2 deterministic Select rules.

Each table is owned by one catalogue rule id; the rule body in
``select_rules.py`` is the engine that consults it.
"""

from __future__ import annotations

# selection.sf_to_diagnosis_explicit_type — always-project named SF types.
DIRECT_SF_DIAGNOSIS_TEXT_BY_CUI: dict[str, str] = {
    "C0877017": "focal to bilateral convulsive seizures",
    "C0270834": "focal seizures with altered awareness",
    "C0016399": "focal motor seizures",
    "C0234533": "generalised seizures",
    "C0751495": "focal seizures",
    "C4316903": "absence seizures",
}

# selection.sf_to_diagnosis_explicit_type — heading-only Diagnosis-view aliases.
HEADING_ONLY_SF_DIAGNOSIS_TEXT_BY_CUI: dict[str, str] = {
    "C0494475": "generalised tonic clonic seizures",
    "C0270838": "secondary generalised seizures",
}

# selection.sf_to_diagnosis_explicit_type — absence-family CUIs for named refinement.
ABSENCE_FAMILY_CUIS = frozenset({"C0563606", "C4316903"})

# selection.sf_to_diagnosis_explicit_type — surfaces that project as absence seizures.
NAMED_ABSENCE_SURFACES = frozenset({"typical absence", "typical absences"})

# selection.sf_named_type_identity — parent CUI for allowed named-type refinements.
SF_TYPE_PARENT_CUI: dict[str, str] = {
    "C4316903": "C0563606",
    "C0270834": "C0751495",
}

# selection.sf_to_diagnosis_explicit_type — embedded Diagnosis aliases blocking projection.
EMBEDDED_DIAGNOSIS_ALIASES_BY_CUI: dict[str, tuple[str, ...]] = {
    "C0016399": ("focal motor seizure", "partial motor seizure"),
}

# selection.diagnosis_explicit_heading_phenotype — phenotype names under a type heading.
HEADING_PHENOTYPE_NAMES = frozenset(
    {
        "absence",
        "absence like seizures",
        "absence seizure",
        "absence seizures",
        "absences",
        "typical absence",
        "typical absences",
        "myoclonic jerk",
        "myoclonic jerks",
        "myoclonus",
    }
)
