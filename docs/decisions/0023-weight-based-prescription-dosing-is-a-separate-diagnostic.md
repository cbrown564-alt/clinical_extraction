# Weight-Based Prescription Dosing Is a Separate Diagnostic

Date: 2026-06-17

For ExECTv2 Prescription, weight-based dosing statements such as `mg/kg/day` must be reported in a separate diagnostic rather than scored as absolute current-regimen `DrugDose + DoseUnit` tuples. This preserves clinically meaningful dosing evidence while keeping absolute-dose component F1 tied to the measurement object expected by the Prescription regimen score.
