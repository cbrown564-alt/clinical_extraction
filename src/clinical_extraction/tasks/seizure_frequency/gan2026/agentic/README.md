# Gan V12 efficiency ceiling

This package retains only the multi-model fresh-evidence reasoner used as the
quality ceiling in the Gan comparison. It is not the operational hybrid.

`fresh_evidence_reasoner.py` combines saved GPT, Qwen, and DeepSeek
structured-event traces with one GPT-4.1 judgment. Its direct imports are
implementation stages of that one retained pipeline, not separately supported
candidate families.

Run it through the single Gan CLI:

```sh
gan2026-llm-experiment --pipeline fresh_evidence_reasoner --split validation
```

The locked test result is aggregate-only. Development must not inspect or tune
from locked test rows. The retained evidence manifest records the exact result
and claim boundary.
