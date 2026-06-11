"""ExECTv2 hybrid SeizureFrequency extractor (Phase 4).

Reset-native hybrid (mirrors Gan 2026's ``reset_clinical_assessment_pipeline``):

  raw letter text
    -> deterministic candidate extraction (high-recall anchors + attribute hints)
    -> LLM clinical assessment            (select/judge candidates; assign interpretation)
    -> deterministic normalize + render   (shared normalizer + CUI lexicon -> attributes)
    -> verify / route                     (evidence + plausibility gate; route the unresolved)
    -> adapter -> PredictedLetter

The LLM's job is *selection and assessment over a pre-extracted candidate set*,
not open-text parsing and not value formatting. Deterministic stages own
candidate recall, normalization, and format. See
``docs/plans/exectv2/04_hybrid_architecture.md``.
"""
