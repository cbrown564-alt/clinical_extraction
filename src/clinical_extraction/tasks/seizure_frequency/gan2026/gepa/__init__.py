"""DSPy-native GEPA optimization for the Gan 2026 seizure-frequency task.

This package keeps the optimizable surface (the clinical instruction the model
reads) inside a ``dspy.Signature`` so ``dspy.GEPA`` can evolve it, while the
proven deterministic post-stack (schema repair, label normalization, purist
scoring) is reused unchanged from the hybrid structured-events pipeline.

Modules:

``program``  GEPA-native ``dspy.Module`` whose instruction is the evolved prompt.
``metric``   Length-penalized feedback metric (purist quality minus prompt-bloat
             penalty, with clinical natural-language feedback for reflection).
``data``     Build ``dspy.Example`` train/val sets from the frozen split protocol.
``run_gepa`` Single-experiment driver: compile, evaluate, register, resumable.
"""
