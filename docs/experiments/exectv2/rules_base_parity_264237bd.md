# ExECTv2 rules base parity fingerprint

This artifact governs no-call parity for the active `rules` runner. The
reference was generated from the independently verified Sol base checkout at
commit `264237bd`, over the 140 permitted `dev` letters only. It does not load
or inspect test60, full200, or any locked row.

The fixture is
[`tests/fixtures/exectv2_rules_base_264237bd_fingerprint.json`](../../../tests/fixtures/exectv2_rules_base_264237bd_fingerprint.json).
It hashes complete per-letter records in manifest order, rather than aggregate
counts:

- extraction: the full all-nine prediction, including mention order, text,
  attributes, evidence, diagnostics, and provenance;
- prediction/projection/trace: that prediction, the Decision 0046 primary
  comparison projection, and every trace event with its owner, action, inputs,
  outputs, rule category, and changed flag.

The source-side abbreviated anchors supplied in the review are retained in the
fixture as `0bba18...96ebf` and `6af972...aa420`. The full governed SHA-256
values are the fixture's `extraction_sha256` and
`prediction_projection_trace_sha256`; the parity test recomputes both from the
current active runner.

This is implementation parity evidence, not a clinical performance or holdout
claim.
