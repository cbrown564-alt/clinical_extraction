# ExECTv2 `test60` split identity-fix (Phase 0)

Status: **DONE.** Date: 2026-07-01. Owner: ExECTv2 workstream.

Companions:
- `docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md` (Phase 0)
- `docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`
  (correction banner added 2026-07-01 — the original "actionable finding" this
  fix follows from misattributed the duplication as an undiscovered bug)
- `PROJECT_STATUS.md`

## Attribution

The source dataset paper (Fonferko-Shadrach et al. 2024, *Annotation of
epilepsy clinic letters for natural language processing*, J Biomed Semantics,
DOI 10.1186/s13326-024-00316-z) states directly: **"Four letters were
duplicated within the set to test for consistency in annotations."** This is a
disclosed, intentional annotation-QA design by the corpus's original authors,
confirmed against the `data/ExECTv2 (2025)/` directory, which maps 1:1 onto
the paper's Data Availability statement:

| Local directory | Zenodo record |
| --- | --- |
| `Gold1-200_corrected_spelling/` | `8381080` (file literally named `Gold1-200_corrected_spelling.zip`) |
| `Json/` | `8356494` |
| `ExECT V2 .1- What and How of annotating_v9.docx` | `8382589` |
| `MarkupOutput_200_SyntheticEpilepsyLetters/` | `12520180` |

## Audit (`experiments/exectv2_corpus_dedupe_audit.py`)

md5-hashing all 200 `.txt` letters in `Gold1-200_corrected_spelling/`
reproduces exactly 4 duplicate pairs (8/200 letters, 4%) — matching "four
letters duplicated" exactly:

| pair | dev/test (v1) | `.ann` diff |
| --- | --- | --- |
| EA0021 / EA0183 | dev / dev | 144 diff-lines — substantially different annotations |
| EA0149 / EA0185 | dev / dev | 88 diff-lines — substantially different annotations |
| **EA0159 / EA0160** | **test / dev** | **4 diff-lines — one trivial offset+hyphen typo** |
| EA0169 / EA0181 | dev / dev | 111 diff-lines — substantially different annotations |

**Refinement of the review doc's characterization:** the review's "the `.ann`
gold files are duplicated too (one pair differs by a single trivial offset
typo)" is imprecise read as a general statement — all 4 pairs' `.ann` files
differ in raw bytes, but by very different degrees. Three pairs (all
same-side, in dev) show large, structurally independent annotation content —
different entity/attribute ID numbering and, in places, different span
boundaries or categorizations (e.g. EA0169/EA0181's `SeizureFrequency` span
`focal-dyscognitive-seizures` vs `ocal-dyscognitive-seizures`) — consistent
with genuine independent re-annotation for the paper's disclosed consistency
check. Only the cross-split pair, EA0159/EA0160, is near-identical: a single
line, one character offset (`799 807` vs `800 807`) and a leading-hyphen
difference (`-anxiety` vs `anxiety`). This pair's near-perfect annotation
agreement — in contrast to the other three's substantial disagreement — is
noted here as a discrete observation, not further investigated (it does not
change the fix below).

## Citation check

- `EA0159`: not cited as a standalone example anywhere else in this repo
  (confirmed by repo-wide grep, markdown files only).
- `EA0160`: cited repeatedly in
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`
  (lines 127-129, 180-182, 254) as a worked example within the SF Phase 7
  canonical row-adjudication. That analysis is entirely dev140-internal and
  never crosses into `test`, so it is unaffected by this fix.

## Fix (user-confirmed 2026-07-01, Option A)

Dropped `EA0159` from `test` rather than relocating it into `dev` — its
content is already represented in `dev` via `EA0160`, and the other 3
duplicate pairs already land same-side (precedent for "same-side duplicates
are harmless"). `v1` is left untouched, since it is referenced by
`evidence_validity` language in existing registry rows and must remain a
stable historical record. `experiments/exectv2_split_v2_cut.py` derives
`data/ExECTv2 (2025)/splits/exectv2_split_v2.json` from `v1`:

- `dev`: 140 letters, unchanged.
- `test`: 59 letters (was 60; `EA0159` dropped). This is the corrected frozen
  holdout going forward — future "test60" claims should say "test59" or cite
  `exectv2_split_v2`.

`data.py`'s `DEFAULT_SPLIT_MANIFEST` still points at `v1` as of this doc; the
project is not yet cut over. Existing registry rows evaluated against `v1`
remain valid as historical record (the review already established this
scope is narrow — 1/60 test letters — and does not implicate existing
GEPA/hybrid/model-swap comparisons, which all score the same set equally).
Cut-over to `v2` as the default should happen the next time a fresh
`test`-split run is planned; until then, both manifests are valid and any run
using `v2` should say so explicitly.

## Status

Done. `PROJECT_STATUS.md`'s `Next` entry updated to reflect this fix.
