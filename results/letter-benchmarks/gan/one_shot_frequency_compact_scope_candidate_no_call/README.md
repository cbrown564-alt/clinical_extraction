# Compact primary-finding migration candidate

Gan 2026 **synthetic dev750** only. This is a no-call preparation for the
owner-selected narrower primary finding score. The frozen v0.8.5 gold, saved R8
outputs and their scores are unchanged. The [candidate annotation rule](../../../../docs/research/gan2026/seizure_finding_annotation_v08.md#candidate-compact-primary-finding-policy-23-september-2026)
owns clinical scope; the [schema decisions](../../../../docs/research/gan2026/one_shot_schema_decisions.md#candidate-compact-claim-record-2026-09-23)
own the new record shape.

Run `.venv/bin/python scripts/benchmarks/prepare_compact_annotation_batches.py`
from the repository root. It reads only the reviewed v0.8.5 dev750 reference and
its source-bearing review bundle. `migration_summary.json` records input and
schema hashes, row policy, counts and batch hashes. Source-bearing outputs stay
local under `runs/seizure_finding_annotation_compact_v0_1/dev750/`.

The deterministic pass preserved all 750 source IDs and hashes and all 1,524
legacy findings. It produced 1,510 schema-valid structural candidates. Fourteen
legacy `non_seizure` findings remain as review-only objects rather than being
silently recoded as seizures. Every candidate retains the complete original
finding and exact source evidence. Five disjoint files contain 150 rows each.

The code moves old number, range, bound and verbatim values without inventing
new values; makes counted units explicit where the old label or measurement
supports it; and carries period/occurrence wording into `time.source`. It sets
`time.phase` to `past_or_unclear` and `primary_scope` to `review_pending` for
**every** finding. The old current/historical field describes the prior
one-year recency rule and cannot establish whether a pattern is ongoing.
Conditions, period details, generic labels, affected-day/night wording, and
possible cluster days receive review flags. Flag counts overlap and are not
error estimates. The first batch should review the source plus legacy and
candidate claims; it should edit or exclude existing claims before seeking new
ones.

Batch 1 returned on 23 September 2026. Its saved review contains all 150 rows
and 271 preserved legacy claims: 229 provisional primary, 29 context, and 13
exclude. The local structural validator passed identity, original-record,
schema, and exact-evidence checks. Of the rows, 117 are marked complete and 33
need adjudication; three provisional primary claims have no compact candidate.
Nine possible omissions were recorded separately and have not been added to the
reference. The review and validation report are in the local batch directory.
Batch 2 also returned with 150 rows and 271 preserved claims. The local
structural validator passed. It marked 132 rows complete and 18 for
adjudication; seven provisional primary claims have no compact candidate.
Nine possible omissions remain separate from gold. Batch 3 returned with 150
rows and 260 legacy claims. The local structural validator passed after a
recorded format repair restored each full input claim under `original_record`;
the raw Pro file is retained and no clinical candidate changed in that repair.
It marked 139 rows complete and 11 for adjudication, with one provisional
primary claim lacking a compact candidate. Seven possible omissions remain
separate from gold. Batch 4 returned with 150 rows and 319 preserved claims;
the local structural validator passed. It marked 127 rows complete and 23 for
adjudication, with no null primary candidates. Nineteen possible omissions
remain separate from gold. Batch 5 returned with 150 rows and 403 preserved
claims; the local structural validator passed. It marked 119 rows complete and
31 for adjudication, with seven provisional primary claims lacking compact
candidates. Nine possible omissions remain separate from gold. Across all five
batches, 750 rows and 1,524 original claims have been structurally checked;
116 rows still need adjudication. The five-batch progress file records chat
URLs and batch status. These candidate reviews are not accepted gold.

The first cross-batch policy review is saved locally as
`compact_policy_adjudication_proposal.json`. Its input packet hash and 18
full-source row recommendations were checked before selecting candidate v0.2
rules in the guide and schema decisions. `rich.v0_2.schema.json` adds only
`status_episode` observed counts and `median_interval`; the v0.1 schema stays
available for replay. This is a prospective representation decision. The
policy proposal alone did not settle individual source rows. Subsequent source
and omission reviews are recorded below.

## Completed development review and current candidate

GPT-6 Pro reviewed three full-source packets covering the other 98 initially
flagged rows; the 18 policy-packet rows were then adjudicated from source notes
locally. The five original 150-row reviews and all three source-packet outputs
passed local identity, source-hash, legacy-order, exact-evidence, and schema
checks. Unresolved rows retain `needs_review` status.

The omission review used three sets of leads after the 750-row batch review:
53 batch suggestions, 46 source-text heuristic leads, and 25 leads from an
independent review of 88 rows originally without a primary claim. GPT-6 Pro
inspected the full notes and current inventories for each lead. Local
validators checked packet hashes, source identity and order, exact quotations
and evidence, v0.2 schema, and edit attribution. The reviews proposed 16, 8,
and 1 distinct primary findings, respectively. The final one adds the stated
occasional focal aura progression in source 3468. The app-log absence in source
8577 remains unresolved because its event population is not established as
seizures. Rejected suggestions were not copied into candidate claims.

The final provisional file is
`runs/seizure_finding_annotation_compact_v0_1/dev750/candidate_v0_2_zero_primary_audit_reviewed.json`
(SHA-256 `c9cf6790cbe7ffd7979589101f6448e34b396af7ceb862ac80fba6c9ec7985ca`).
It retains **750 source rows and all 1,524 legacy claims**, with 25 separately
attributed additions. **686 rows are complete for this source review and 64
remain `needs_review`**. Only the 1,037 primary records on complete rows are
eligible for a provisional compact score; this is not a scored benchmark or an
accepted 750-row gold reference. Ten primary slots with null compact records
occur only on unresolved rows. Complete rows have no material open question
from these review passes; this does not establish independent annotator
agreement or clinical validation. Further source clarification or owner
adjudication is needed for the 64 unresolved rows before a fully accepted
reference or prospective model evaluation. Local `batch_progress.json` owns
file hashes, review stages, and Browser conversation provenance.

Run `.venv/bin/python scripts/benchmarks/validate_compact_candidate_v0_2.py
--candidate runs/seizure_finding_annotation_compact_v0_1/dev750/candidate_v0_2_zero_primary_audit_reviewed.json`
to repeat provenance, schema, source-evidence and score-partition checks. These
checks do not prove the clinical decisions.

After a Pro batch returns, save its JSON under the local batch directory and
run `.venv/bin/python scripts/benchmarks/validate_compact_annotation_batch.py
--batch N --review PATH`. The validator requires exactly 150 rows, unchanged
source IDs/hashes and legacy claim order, dispositions and edit reasons, valid
compact records, and exact source evidence. Its report is a structural check;
an independent source review is still needed before accepting a reference.

The five fictional fixtures validate the response schema's basic structure.
Neither this mechanical pass nor those fixtures establish clinical correctness,
native selected-answer agreement, annotation reproducibility, or a new finding
score. No test450 row, model response or paid extraction call was used.

## Owner-approved v0.3 source review, 24 September 2026

Conor answered source-specific questions and approved one batch of recommended
decisions for the other 44 open rows. The owner choices retain separately
stated rates and since-visit absences without repairing contradictory source
histories, while treating less precise restatements as context. They also
settle the `bimonthly` convention, named count labels, selected windows,
possible-seizure clusters, and explicit maximum gaps. The [guide](../../../../docs/research/gan2026/seizure_finding_annotation_v08.md#owner-reviewed-compact-candidate-v03-24-september-2026)
owns the policy; the [schema decisions](../../../../docs/research/gan2026/one_shot_schema_decisions.md#owner-reviewed-compact-candidate-v03-2026-09-24)
record that the v0.2 response shape is reused.

The replayable overlay is
`scripts/benchmarks/apply_compact_owner_review_v0_3.py`. It reads the fixed
SHA-256 v0.2 candidate and writes the local-only
`runs/seizure_finding_annotation_compact_v0_1/dev750/candidate_v0_3_owner_adjudicated.json`.
The current output SHA-256 is
`25e1b63c71f4ddd29bee3f6cf9f40da360f840f4477c88e74d60f36387b46d06`.
It retains all **750 source rows, 1,524 unchanged original claim records**, and
the 25 prior attributed additions. The overlay changes 65 source rows (the 64
open rows plus previously complete source 10873), makes 14 further attributed
additions, and has **39 additions total**. All 750 rows are now marked complete
under the declared source-literal policy, with 1,219 primary claim records and
zero null primary slots. This is structural completion of development
annotations; independent annotator agreement and prospective model scoring
remain outstanding.

Run `.venv/bin/python scripts/benchmarks/validate_compact_owner_review_v0_3.py`
to check the v0.2 input hash, exactly 64 reviewed open rows, allowed change
scope, unchanged source notes and original records, prior additions, owner
attribution, schema and exact evidence. The validator reports 14 new additions
and 65 changed source rows. It does not establish clinical correctness. Frozen
v0.8.5 references, saved R8 outputs and test450 remain untouched.
