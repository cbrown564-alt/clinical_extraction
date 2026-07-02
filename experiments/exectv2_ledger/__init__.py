"""Gold case ledger: one shared schema + taxonomy for "is this gold or model?"

Replaces four independently-reimplemented mechanism taxonomies
(``exectv2_{dx,sf,rx_inv}_evidence_recall_consolidation_check.py``, plus the
separate ``exectv2_{dx,sf}_canonical_row_analysis.py`` pair) with one ledger
every future family investigation reads and writes.

See ``docs/canon/workstreams/*_CANONICAL_LEDGER_CANON.md`` for the generated,
human-facing output; ``experiments/hypothesis_registry.jsonl`` for the
predeclaration -> verdict lifecycle.
"""
