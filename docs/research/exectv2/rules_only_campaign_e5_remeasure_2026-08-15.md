# Rules-only Parity Campaign Phase E5 Remeasure Report

Date: 2026-08-15
Status: **complete; Phases E0–E5 executed, verified, and landed**
Track: ExECTv2 rules-only parity campaign
Parent: [G5 remasure](../gan2026/rules_only_campaign_g5_remeasure_2026-08-15.md)
Governing decision: [Decision 0046](../../decisions/0046-exect-primary-method-comparison-boundary.md)
Artifact: [`experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json`](../../../experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json)

## 1. Executive Summary

Phases E0 through E5 of the Rules-Only Parity Campaign on ExECTv2 are complete. With zero LLM calls and strict adherence to holdout row safeguards, we conducted exhaustive error partitioning across all 140 development letters in all four target families, developed and tested gold-free mechanisms, and confirmed them on locked `test60` via aggregate-only evaluation.

The four-family headline F1 improves:
- **`dev140`:** `0.8982 → 0.9042` ($\Delta$ **+0.0060**, surpassing the 0.90 four-family threshold)
- **`test60`:** `0.7918 → 0.7937` ($\Delta$ **+0.0019**, positive holdout generalization with 0 harms / 0 regressions)

## 2. Family-by-Family Progression

| Family | dev140 Baseline | dev140 Final | dev140 $\Delta$ | test60 Baseline | test60 Final | test60 $\Delta$ | Key Mechanism Landed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **Investigations** | 0.9579 | 0.9618 | +0.0039 | 0.8706 | 0.8706 | 0.0000 | PNES EEG confirmation (`EA0102` rescued) |
| **Prescription** | 0.9615 | 0.9780 | +0.0165 | 0.8395 | 0.8395 | 0.0000 | Future initiation / plan filtering (5 rescued) |
| **Diagnosis** | 0.8633 | 0.8633 | 0.0000 | 0.8550 | 0.8550 | 0.0000 | Closed at practical floor (173 gold representation ceiling) |
| **SeizureFrequency** | 0.8333 | 0.8402 | +0.0069 | 0.5797 | 0.5899 | **+0.0102** | Kept-associated filtering before statement dedup (2 rescued) |
| **Four-Family Total** | **0.8982** | **0.9042** | **+0.0060** | **0.7918** | **0.7937** | **+0.0019** | **All 4 families improved or preserved** |

## 3. Campaign Safeguards Confirmation

- **Python environment:** Repository `.venv` used exclusively.
- **Model calls:** Exactly 0 model calls throughout all phases.
- **Holdout integrity:** Aggregate-only evaluations on `test60`. Zero row text, letter identifiers, annotations, predictions, or error cases inspected.
- **Predeclared protocols:** Every development and holdout evaluation was preceded by its dedicated predeclared protocol file.
