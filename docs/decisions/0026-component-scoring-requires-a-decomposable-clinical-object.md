# Component Scoring Requires a Decomposable Clinical Object

Date: 2026-06-17

For ExECTv2 reporting, component scores should be added only when an entity has a real decomposable clinical object, such as a medication regimen, an investigation performed/result/type fact, or seizure-frequency attribute families. Entities whose main errors are phrase scope, assertion, temporal anchoring, or ontology projection should receive diagnostics for those layers rather than artificial component scores created for symmetry across the scorecard.
