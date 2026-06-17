# Prescription Medication Identity and CUI Projection Are Separate Layers

Date: 2026-06-17

For ExECTv2 Prescription, clinical medication identity should canonicalize brand names, generic names, and common spelling variants for component scoring, while a separate benchmark projection layer emits the ExECT-facing `DrugName` and CUI convention. This keeps clinically correct regimen recovery distinct from ontology and benchmark-format alignment, so CUI or brand/generic projection gains are reported as projection gains rather than hidden extraction improvements.
