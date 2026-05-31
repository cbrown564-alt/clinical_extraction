# Gan 2026 Splits

`gan2026_split_v1.json` is the locked train/validation/test master manifest for
the local 1,500-row Gan 2026 synthetic seizure-frequency subset. The companion
`train_v1.json`, `validation_v1.json`, and `test_v1.json` files expose the same
row identifiers as one split per file for external scripts and manual inspection.

- `train`: 300 rows, reserved for DSPy GEPA or another optimizer.
- `validation`: 750 rows, primary development and error-analysis surface.
- `test`: 450 rows, locked final holdout only.

See `docs/design/gan2026_split_protocol.md` before using or changing these splits.
