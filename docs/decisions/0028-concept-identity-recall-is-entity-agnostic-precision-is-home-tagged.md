# Concept-Identity Recall Is Entity-Agnostic; Precision Is Home-Tagged

Date: 2026-06-18

The `Concept-Identity Headline` (ADR 0027) scores recall source-entity-agnostically: a Class-B gold concept (e.g. a Diagnosis seizure type) is recovered if *any* extraction pass surfaced that concept, regardless of which entity the pass was tagged as. This is deliberate — the ExECTv2 gold itself dual-files concepts (a named seizure type is annotated under both Diagnosis and PatientHistory), so penalizing the model for the same convention measures annotation phrasing, not clinical understanding.

Precision, however, is home-tagged: a prediction counts against an entity's false-positive denominator only if the model (or deterministic normalization) actually assigned it to that entity. A concept surfaced only under the PatientHistory pass and never normalized to Diagnosis earns Diagnosis recall credit but cannot inflate Diagnosis precision.

This asymmetry is surprising — a reader will expect recall and precision to share one matcher and may "fix" it back to strict per-entity matching (the old `score_entity` behavior), which re-introduces exactly the entity-confusion penalty ADR 0027 pushed into the projection layer. Rejected alternatives: fully entity-agnostic (pool all concepts letter-wide for both recall and precision — over-credits, erases the clinical diagnosis-vs-history distinction) and strict-home for both (the discarded per-entity scorer).
