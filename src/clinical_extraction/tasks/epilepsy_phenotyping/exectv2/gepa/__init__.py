"""DSPy-native GEPA optimization for the ExECTv2 de-dup clinical-fact task.

This package keeps the optimizable surface (the clinical instruction the model
reads) inside a ``dspy.Signature`` so ``dspy.GEPA`` can evolve it, while the
proven de-dup post-stack (JSON parse, evidence gate, attribution-clean
representation adapter, and the canonical ``clinical_headline`` clinical-recovery
scorers) is reused unchanged from the key-entities generation-selection pipeline.

The research question (plan 13): every prior single-prompt de-dup attempt was
hand-tuned and plateaued at ~0.71-0.75 clinical_headline F1 on dev140, below the
v08 hybrid's 0.9155. Can an auto-evolved, length-penalized lean prompt do better?

Modules:

``program``  GEPA-native ``dspy.Module`` whose instruction is the evolved prompt.
``metric``   Length-penalized feedback metric (per-letter clinical_headline F1 minus
             prompt-bloat penalty, with clinical natural-language reflection feedback).
``data``     Build ``dspy.Example`` train/val sets from a seeded dev sub-split.
``run_gepa`` Single-experiment driver: compile, evaluate, register, resumable.
"""
