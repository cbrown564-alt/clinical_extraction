"""Published ExECTv2 benchmark references and promotion freeze targets."""

from __future__ import annotations

FREEZE_TARGET_PER_ITEM = 0.87
FREEZE_TARGET_PER_LETTER = 0.90

PAPER_PER_ITEM_F1: dict[str, float] = {
    "BirthHistory": 0.97,
    "Diagnosis": 0.85,
    "EpilepsyCause": 0.90,
    "Investigations": 0.95,
    "Onset": 0.96,
    "PatientHistory": 0.78,
    "Prescription": 0.87,
    "SeizureFrequency": 0.66,
    "WhenDiagnosed": 0.91,
}
PAPER_OVERALL_PER_ITEM = 0.87
PAPER_OVERALL_PER_LETTER = 0.90

PUBLISHED_PER_ENTITY_ITEM_F1 = PAPER_PER_ITEM_F1
