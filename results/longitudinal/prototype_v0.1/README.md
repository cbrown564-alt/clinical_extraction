# Phase 4 longitudinal prototype

Implemented and verified on 2026-09-11 in the working tree. The twelve authored
patients have a complete local loop: permitted letters → saved extraction or
provisional reference facts → inferred links → retained source accounts → five
cohort answers with evidence. The frontend is at `/longitudinal`. No new model
calls, clinical validation, corpus freeze or deployment occurred.

The [evaluation protocol](../../../docs/longitudinal/evaluation_protocol.md) owns
the study procedure. Existing Phase 2/3 references, diagnostic programs and saved
outputs are unchanged. This is a development fit to inspected synthetic examples,
not a generalization estimate. The two packs have 24 patients and 480 requests;
only the original twelve authored patients have independent saved extractions.

## Run the demonstration

From the repository root:

```bash
source .venv/bin/activate
python scripts/longitudinal/run_prototype.py
python scripts/longitudinal/verify_prototype.py
cd frontend
npm run dev
```

Open `http://localhost:3000/longitudinal`. The existing frontend requires no Python
API server for this route. Its server reads the versioned local frame files and
returns only the selected patient's permitted letters plus cohort statuses. This
is local repository operation; a standalone deployment would need explicit
artifact packaging. The original model attempts saw the query context. The
adapter verifies their exact input and source text, discards their query answers
and links, repairs unique exact-quotation offsets, and runs the new linker/query
policy. Unseen or changed inputs fail; no reference facts substitute for missing
predictions. A fresh extraction provider is outside this saved-output prototype.

Start with Patient 001, first visit, Q2, provisional reference facts. The visit
account is eligible using L1 alone at 15 January 2025. The retrospective cutoff
of 14 July admits L2 (available 10 July): the same staring spells are reclassified
as non-epileptic, leaving one active epileptic pattern. Q2 becomes ineligible.
The 20 June decision is not backdated for Q5. Switching back reproduces the earlier
answer. Evidence buttons focus the exact passage in its source letter.

Select saved model predictions to inspect actual extracted facts. Patient 005 at
the first visit has an original failed capture. Retry preserves that failure;
selecting provisional reference facts explicitly recovers an inspectable history.
Indeterminate and failed results remain outside eligible cohorts and have separate
counts. All five questions, two index schedules and both temporal views work.

## Component comparison

| Input / linking condition | Agreement | Failed requests | Unsupported definitive answers |
| --- | ---: | ---: | ---: |
| Reference facts + reference links | 480/480 | 0 | 0 |
| Reference facts + inferred links | 480/480 | 0 | 0 |
| Reference facts without links | 440/480 | 0 | 8 |
| Saved predicted facts + inferred links | 190/240 | 20 | 1 |

All eleven Phase 2 gaps and 33 Phase 3 mismatches are resolved in both reference-
fact linking conditions. The 40-query difference versus removing links measures
downstream dependence in these examples. It does not establish clinical benefit.
The predicted condition retains 44 usable captures and four failures (five
requests each). Thirty additional requests disagree after successful extraction.
Successful captures agree on 190/220 requests; the primary denominator stays 240.

The remaining unsupported definitive answer is Patient 012, T1 retrospective Q1.
The saved model labels “I cannot establish a definitive diagnosis of epilepsy
today” as asserted, negated epilepsy. The query policy consumes that erroneous
clinical field and returns ineligible; the provisional reference is indeterminate.
The raw output is preserved. This is a named input-semantics limitation, not a
silent repair or accepted clinical conclusion.

Patient 006 exposed a separate linker issue: narrow extracted quotations omitted
the surrounding explicit reporter-disagreement sentence. The final linker selects
that same source paragraph as additional link evidence, retains both reports and
abstains. It does not alter the extraction. The regression test checks this case.

`comparison.json` records every condition/request, evidence, rules, and the first
condition that disagrees. `predicted_input_or_linking` deliberately leaves causal
attribution unresolved: changing extracted facts, names or quotation boundaries
can also change linking. A successful reference-fact condition alone cannot prove
that every predicted-condition error is an extraction error.

| Linking input | Reference-supported edge precision | Reference-edge recall | Exact annotated edges | Fact alignment |
| --- | ---: | ---: | ---: | ---: |
| Reference facts, 96 frames | 391/511 | 142/221 | 135 | Identical input assertions |
| Predicted facts, 44 successful frames | 20/118 | 19/97 | 19 | 204/506 predicted assertions |

These are repeated view/frame instances, not independent patients. Support uses
provisional reference relations, identity paths and same-letter, same-name,
overlapping-evidence accounts to allow equivalent endpoints. Exact edge agreement
is also retained. Unaligned predicted edges (72/118) remain in the precision
denominator. Alignment requires unique same-letter content, polarity/certainty
and overlapping evidence, and is intentionally strict. Extra edges may be valid
but unannotated; these measures are neither adjudicated clinical precision nor an
unrestricted estimate of reconstruction quality. The low linkage agreement remains
a Phase 5 review concern despite complete reference-fact query agreement.

## Evidence and verification

- `frames/`: 96 view/source files, including original predicted facts, offset
  repairs, source hashes, inferred links, histories and query traces.
- `comparison.json`, `summary.json`: all 1,680 condition/request rows, denominators,
  per-patient/query/view/status summaries and source/program hashes.
- `link_alignment.json`: endpoint mappings, missing/additional edges and support
  definitions. Failed captures do not enter successful-input link denominators.
- `failures.json`: original capture metadata and four explicit failures.
- `rule_catalog.json`: owners and categories for format normalization, source
  selection, semantic linking and query policy. No semantic extraction repair or
  treatment-causality rule is implemented.
- `browser_qa.json`, `verification.json`: interaction and automated-check evidence.

The semantic rules live in `src/clinical_extraction/longitudinal/`. `evidence.py`
only handles source validation, exact offsets and quoted context. `history.py`
owns inferred relationships; `temporal.py` and `queries.py` own scope, uncertainty
and clinical selection. Original assertions are never overwritten. Negative
coverage unions preserve one-day gaps; qualitative Christmas inclusion never
writes an invented date into an assertion. Past-year/autumn/month-scope and
explicit medication-continuity rules are bounded synthetic-development rules.

The post-change review checked source boundaries, raw/repair separation, future-
evidence exclusion, failure denominators, rule ownership and file size. No change
was made to Gan/ExECT scoring or locked data. Residual concerns are the one harmful
predicted answer, limited link alignment, source-specific semantic rules and
unmeasured expert/human agreement. Those constrain promotion and Phase 5 decisions;
they do not conceal unfinished prototype behavior.

Final checks: 30 longitudinal tests pass; Ruff, mypy (406 source files), TypeScript,
changed-frontend ESLint, production build, 167 frontend tests, documentation hygiene
and exact replay verification pass. Full pytest has 809 passes and three unrelated
failures: the two existing benchmark documentation/inventory expectations and an
intermittent random request-ID substring collision in the holdout-denial test
(the denial remained HTTP 403). The existing five-cell-grid route emits a non-fatal
filesystem-tracing build warning. No deep-tier tests or model calls were required.
