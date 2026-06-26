# Gan 2026 H1 Hidden-Family Slice Aggregates v0

H1 aggregate-only predeclared hidden-family slice readout. The script may read frozen test rows to compute aggregate family membership and correctness, but it writes no test row ids, clinical text, raw outputs, or row-level failure records.

## Decision

h1_inconclusive_gap_not_strongly_concentrated

## Interpretation

H1 remains inconclusive: family slices show gaps, but concentration is not strong enough to explain the aggregate gap alone.

## Surface Summary

| Split | Rows | Correct | Proxy | Families |
| --- | ---: | ---: | ---: | ---: |
| validation750 | 750 | 708 | 0.9440 | 10 |
| test450 | 450 | 351 | 0.7800 | 10 |

## Family Gaps

| Family | Validation rows | Validation proxy | Test rows | Test proxy | Gap | Contribution | Action shift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `diary_or_log_aggregation` | 727 | 0.9477 | 436 | 0.7775 | 0.1702 | 0.1649 | -0.0037 |
| `current_vs_historical` | 739 | 0.9432 | 444 | 0.7770 | 0.1661 | 0.1639 | 0.0031 |
| `competing_semiologies` | 640 | 0.9406 | 386 | 0.7720 | 0.1686 | 0.1446 | -0.0053 |
| `rate_bucket_or_denominator` | 595 | 0.9395 | 347 | 0.7752 | 0.1643 | 0.1267 | 0.0048 |
| `cluster_burden` | 420 | 0.9333 | 264 | 0.7765 | 0.1568 | 0.0920 | 0.0165 |
| `uncertainty_or_ambiguity` | 282 | 0.9255 | 178 | 0.7247 | 0.2008 | 0.0794 | -0.0139 |
| `seizure_free_duration` | 202 | 0.8960 | 121 | 0.6529 | 0.2431 | 0.0654 | -0.0082 |
| `benchmark_format_convention` | 83 | 0.9036 | 48 | 0.6667 | 0.2369 | 0.0253 | 0.0351 |
| `unknown_boundary` | 95 | 0.8737 | 57 | 0.7368 | 0.1368 | 0.0173 | -0.0421 |
| `unclassified` | 1 | 1.0000 | 1 | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

## Next Step

Do not accept hidden-family mix as the primary explanation yet; move to H3 candidate-exposure instrumentation and H7 template-brittleness panels.

## Inspection Boundary

This artifact writes aggregate family rows only. It does not write test row ids, clinical text, raw model outputs, or row-level failures.
