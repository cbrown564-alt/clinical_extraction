# Longitudinal generation and quality-check protocol

Date: 2026-09-10. Version: execution v0.3. Mode: Explore.
Owner: Conor Brown for scope, spending and release decisions. This document owns
Phase 3 procedure and configuration; the [roadmap](../plans/ACTIVE_ROADMAP.md)
owns task order. The execution amendment below predeclares the seed-free batch.

## Next batch and source decision

Prepare one seed-free, development-only patient with three letters. Review that
patient before authoring five, then twelve. This sequence tests reproducibility,
text-supported annotation and failure recovery; it does not freeze a corpus.
Use the [configuration](../../configs/longitudinal/seed_free_pilot.json).

The proposed batch contains no ExECT/Gan input records. Therefore upstream
record matching and seed-family checks have an empty input set, rather than an
assumed clean source pool. Assign each new history an authoring-family ID. Any
reuse of a history, template or description adds its ancestor to that family;
all connected descendants stay development-only. Never claim source-independent
splits for rewrites of the same authored history.

The [source-use audit](../../results/longitudinal/pilot_v0.7/source_use_audit.json)
records release metadata and local split-manifest hashes. ExECT's official
[Zenodo API record](https://zenodo.org/api/records/8381080) lists version 1,
26 September 2023, CC BY 4.0 and its creators. The local copy has not been matched
to the release; no source-conditioned inputs are cleared by that licence finding
alone. Retain attribution and indicate changes for any later derivative batch.
The [Gan paper](https://arxiv.org/html/2603.11407v1) describes ten base letters and
shared descriptions. A matching public release and licence for the local subset
remain unidentified. Its paper licence is not a dataset licence.

Before a later source-conditioned batch, load only ExECT dev140/Gan dev750 through
their permitted development loaders; match actual source bytes to a documented
release; record source/record IDs and ancestry locally. Compute exact normalized
text duplicates and five-token-shingle Jaccard candidates at a predeclared 0.8
threshold within permitted inputs. Review candidates and union confirmed shared
ancestors before any split. This threshold is an inspection heuristic, not a
claim that lower similarity proves independence. Unknown ancestry stays a shared
conservative group or is excluded. Neither locked rows nor their failures are
available for choosing thresholds. Source-conditioned generation remains disabled.

## Generation stages and records

1. **Author the history.** Fix fictional adult outpatient eligibility, family ID,
   three visit/availability dates, the two index dates 180 days apart, query drug
   and modality. Separate intended clinical events from what each consultation
   actually documents. Include one ordinary follow-up and one named mechanism
   under review; do not pack every difficulty into every letter.
2. **Plan documentation and style independently.** Assign concise prose, detailed
   prose or shorthand without using the cohort-answer status. Record omissions,
   delayed documentation, copied content and uncertain dates explicitly in the
   authoring record. The authoring record never appears in extractor inputs.
3. **Write final letters.** Preserve raw draft, revision ID and a change log. If a
   provider is later enabled, save rendered instructions, model/version, generation
   parameters, seed when supported, token usage, failures and actual cost. A model
   name or random seed does not guarantee byte-identical regeneration; saved-output
   replay must reproduce exact bytes. Current configuration makes zero provider calls.
4. **Annotate the final text afresh.** Use schema/guide v0.3, final letter IDs and
   exact quotes. Derive offsets from final quotes. Annotate only what the finished
   letters support, even if it differs from the intended history. Filter letters
   physically for each information cutoff before a second pass.
5. **Review and retain failures.** Save each request and returned output before
   parsing. Give every planned patient an accepted, needs-revision or rejected
   status with reasons. Keep missing/uncertain outcomes; never reject solely
   because a teacher and extractor disagree. After a revision, retain old files,
   increment the version, rebuild inputs and rerun affected checks.

Run records belong under ignored `runs/longitudinal/<batch>/<patient>/<attempt>/`.
The reviewed public-safe summary belongs under `results/longitudinal/<version>/`.
Every record carries program/config hashes, exact source hashes, annotation and
query-definition versions, origin, lineage, author/reviewer identity, disposition
and repair policy. Do not place raw private source material in tracked results.

Resume only a missing stage whose recorded inputs and configuration hashes match.
Never overwrite a successful capture. Use a new attempt ID for a retry; a changed
input starts a new revision. Paid retries are disabled in this configuration.
The preparation configuration records the original decision. The execution
configuration additionally pins the program, authoring instructions and batch IDs.
The runner must reject provider-enabled or source-conditioned configurations.

## Execution amendment: small seed-free batch

Primary question: can a staged authoring and review procedure reproduce the same
finished letters and text-supported references while retaining failures, lineage
and information cutoffs? This is a generation/QC engineering probe, with no model
comparison or clinical-performance endpoint. The fixed comparison is byte equality
between the accepted capture and a clean saved-output regeneration.

Use twelve new fictional adult outpatient histories, three letters each, all in
development. Cross four scenario types with three styles (concise, detailed and
shorthand). The scenarios exercise ordinary follow-up, concurrent patterns with
a treatment plan, unresolved reporting conflict, and delayed documentation of a
reinterpretation and test result. Style is preassigned without reading query
answers. Shared scenario descendants are identified; a common authoring template
also keeps this entire probe in one conservative connected family. These are
twelve patient records, not twelve independent clinical histories. This probe
does not replace the broader Phase 2 coverage pack.

The current Codex assistant authors the history, consultation plan and letters,
then separately records annotations and query reasons from finished text. Record
the supplied model family and state that the hosted model snapshot, sampling
parameters and token billing are unavailable. No separate provider, independent
model or paid fallback is invoked. Preserve task instructions and every submitted
source revision. This same-assistant process is internal review, not independent
or expert annotation. Exact regeneration means replay of saved authoring outputs,
not a claim that fresh stochastic authoring will reproduce them.

Execute cumulative stages 1, 5 and 12. Before expanding, inspect every assertion,
relationship and query answer for the current stage and record a disposition and
reason bound to the exact case and QC hashes. A rejected case remains in the
planned denominator. Unresolved reporting and missing information are acceptable
when the reference preserves them. A structural defect needs a new attempt with
its previous failed capture retained; never overwrite one. Changed successful
inputs require a separate run/revision. Missing stages may resume only with
unchanged configuration, program and source hashes.

Record exact spans, temporal/burden bounds, linkage and contradiction evidence,
query cutoffs, status distributions and cross-letter references. Run the existing
incomplete query evaluator only as a diagnostic and disposition every mismatch;
agreement is not an acceptance filter. Compare normalized duplicate letters and
five-token-shingle Jaccard candidates at 0.8 within the batch. Also compare the
36 Phase 2 authored letters as declared development-only context; do not read
benchmark corpora. Record all candidate pairs and their lineage dispositions.

Local artifacts contain captured raw sources, failed attempts, final cases, QC,
review decisions, elapsed stage wall time and config/program/source hashes.
Reviewed results contain an explicit allowlist of fictional final cases and the
replay summary; hidden authoring history remains local. Keep query references
outside all filtered task inputs. Record additional API calls and costs as zero;
assistant account usage and human effort remain unmeasured. Stage elapsed time
includes generation/checking or review as labelled, not isolated annotation time.

Stop after twelve planned cases have dispositions, all accepted cases pass the
checks and every accepted artifact regenerates byte-for-byte. Stop expansion on
an undispositioned defect or stale review. The positive claim is reproducible,
internally reviewed synthetic development material only. No dataset freeze,
expert validation, release, outreach or 300-patient scaling follows automatically.

## Quality checks and acceptance

For each patient, run the existing case builder/verifier and annotation validator
in the repository environment. Checks must establish exact letter hashes, valid
spans, unique IDs, valid endpoints, date bounds, exact fixed query schedule and
physically filtered input bytes. Rebuilding derived files must change no bytes.

Review all assertions, relationships and 20 reference answers against final text:

- Separate clinical event, interpretation decision and document availability dates.
  An EEG performed date is not result availability. A proposal is not use.
- Keep reporter disagreement and identity uncertainty. A later account can settle
  an earlier dispute only when it explicitly addresses the earlier scope.
- Record exhaustive negative evidence explicitly; null bounds mean unknown, not
  lifelong coverage. Keep qualitative dates without invented precise bounds.
- Preserve seizure ranges, clusters and type-specific absence in the history.
- Check cross-letter evidence on requests that need it and each cutoff boundary.
  Zero unsupported definitive references and zero future-evidence leaks are required.

Use `evaluate_query_witnesses.py` as a diagnostic, recording all mismatches. It is
incomplete and cannot certify reference quality or drive agreement filtering.
The pilot now represents explicit complete prior non-use. The remaining qualitative
time, inventory and treatment-continuity cases are recorded in the pilot review
and must be handled before using a complete evaluator to filter generated references. Independent AI agreement remains distinct from expert review.

A one-patient authoring probe can proceed without a clinical partner. Advancing
1 → 5 → 12 requires a saved internal review of the previous stage, reproducible
checks, all defects dispositioned and actual workload recorded. Scaling toward
300 additionally requires Phase 2 effort evidence, source checks for any seeds,
a frozen generation version and protected family-level splits. No release or
outreach is authorized by this protocol.

## Cost and effort plan

| Item | Selected plan / cap | Evidence or limit |
| --- | --- | --- |
| New generation API calls | 0 paid calls; £0 total and per patient | Generation provider disabled; no fallback or retries. |
| Phase 2 AI timing probe | 18 agy annotation calls; £0 incremental charge | User confirmed agy has no per-call charge. This is annotation timing, not generation or human labor. |
| Local saved-output replay | £0 incremental API charge | Existing scripts; local electricity/hardware not measured. |
| New seed-free authoring | One patient first, then reviewed 5/12 stages | Current assistant/manual authoring; account usage is not asserted free. |
| Independent human timing probe | Three cases: 002, 006, 011; maximum 60 active minutes each | A prospective workload cap of 3 hours, not an estimated annotation duration. Reviewer not assigned. |
| Human fee | Unknown until reviewer rate is agreed | Maximum fee for the probe = 3 × agreed hourly rate; no procurement authorized. |
| Prospective provider alternative | Disabled | Requires model/version, verified rates, token/retry caps and explicit spending authorization. |

The previous 44 successful jobs took 22.9–102.2 seconds each (median 57.6), with
four failed calls reported separately. These are wall-clock observations, not
predicted annotation time. Provider cost was not returned. No extrapolated paid
price or human-effort estimate is supported by those records. The separate
[v0.8 timed probe](../../results/longitudinal/pilot_v0.8/timed_pass/analysis.json)
records wall time by focused activity; its shared work and three selected cases
cannot supply isolated field costs or a human workload estimate.

For a future paid configuration, reserve worst-case input + output + separately
billed reasoning tokens at the verified rate before each request, including retry
allowance. Stop before a request that could exceed the remaining cap. Do not add
reasoning tokens twice when the provider already includes them in output usage.
The account/provider terms and rates must be checked when selecting that option.

## Prospective effort measurement

Use the reference-free prepared inputs for cases 002 (ordinary), 006 (reporter
conflict) and 011 (clusters/reinterpretation). A reviewer who has not seen the
reference answers records active minutes separately for diagnosis, seizures,
medications, investigations, temporal normalization, relationship decisions and
query answering. Pause for interruptions and stop at the per-case cap while
retaining unfinished items. Record rejected/uncertain fields and the reason.

The [timing template](../../results/longitudinal/pilot_v0.7/effort_session_template.json)
is empty by design. Record identity, prior exposure, schema version, source/input
hashes, start/end timestamps, paused seconds, output path and remaining work.
Report actual active time by case/family and completion fractions; do not project
three selected cases into a population estimate. A reviewer with prior exposure
can measure correction work, but that session is not an independent annotation pass.
