# Paper roadmap

Updated: 2026-09-24. Owner: Conor Brown.

## Current focus

Exclusive focus: the one-call seizure-frequency paper. Longitudinal work,
research-paper tables and optimiser experiments are postponed.

On 2026-09-24 Conor locked the study to stop iterating on the secondary
inventory. The core claim is that one call returns the established answer at
answer-only accuracy while also returning richer findings; every earlier rich
schema already held Purist at 86–88% on dev750. The locked set is:

- two prompts, `minimal` (r4, unchanged) and `expanded` (r4 plus the full
  seizure-frequency inventory);
- one [annotation guide](../research/gan2026/seizure_frequency_annotation_guide.md):
  full inventory with a phase tag, compact finding schema;
- one lenient, descriptive finding score;
- one dev750 reference derived from the owner-reviewed annotation.

The [evaluation protocol](../research/gan2026/one_shot_paper_protocol.md) owns
conditions, endpoints, execution and the run record. The
[paper outline](../../publications/jamia-one-shot/README.md) owns the argument.
Earlier revisions (v1, r3–r11, guide v0.1–v0.8.5, compact v0.1–v0.3, Jev) are
removed from the checkout and recoverable from Git tag
`archive/pre-lockdown-2026-09-24` and the archived runs tarball.

## Standing decisions

- One clinical model call per note returns findings, quotations and one declared
  answer. Examples inside the prompt are allowed; one-call is not zero-shot.
- Primary outcome: native Purist agreement with the existing expert label, with
  Pragmatic companion, over all scheduled letters; unusable output is wrong.
- Do not tune prompts, the schema, the guide or the scorer to the inventory
  score. Changes need an owner decision in the owning document's change log,
  not a new numbered revision.
- Develop on dev750 only. Evaluate the frozen conditions once on aggregate-only
  test450 after its source-only re-annotation, disclosing prior exposure.
- Main synthetic runs use the DeepSeek API from this computer within Conor's
  study cap. The collaborator owns local DeepSeek cluster runs on real data.
- Real Gan 300 use depends on written permission and exposure metadata.
- No semantic deterministic repair or extra clinical call in the primary method.
  The dissertation's two-stage results are context only.
- One compact ExECT configuration example on permitted dev140 letters still
  demonstrates configurability; it is not a model leaderboard.

## Work ahead

| Order | Work | Completion evidence |
| --- | --- | --- |
| 1 | Run the paired `minimal`/`expanded` dev750 comparison once. Needs Conor's authorisation and a budget decision (worst-case reservation exceeds the current cap; expected charge about US$10). | `results/letter-benchmarks/gan/one_call/dev750/score.json` with answer agreement, paired difference and descriptive finding score. |
| 2 | Re-annotate all 450 test letters from source only under the locked guide. | Reviewed test450 reference with source hashes; annotation exposure recorded. No predictions inspected. |
| 3 | Freeze both conditions, the scorer and the analysis; run test450 once. | Recorded freeze and aggregate-only result. |
| 4 | Extend the same approach to medications (the existing Prescription family), then diagnoses and investigations, keeping the native frequency answer as the common endpoint. | Family-specific guide sections and development references; a paired seizure-only versus multi-family comparison on the answer endpoint. |
| 5 | Conor shares the reviewed guide and data with Yujian Gan to explore annotation of real letters by the King's team. | Agreed scope, permissions and review procedure; nothing assumed in advance. |
| 6 | Freeze and run the authorised real-letter study; complete the manuscript. | Separate real and synthetic results with declared limitations. |

## Documentation

Keep at most 50 Markdown documents under `docs/`. Update existing owners
rather than adding status reports; current status is brief and local in
`PROJECT_STATUS.md`. For documentation changes, check links and hygiene; for
code changes, run the documented tests.
