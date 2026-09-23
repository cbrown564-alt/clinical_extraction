# Clinical Extraction Explorer

This is the established Next.js interface for inspecting the Gan 2026 and ExECTv2
research pipelines. On Vercel, the Next.js API routes at `/api/*` serve the bundled
demonstration fixtures. Local development forwards those routes to the Python API
when it is running.

The public demonstration is `/demo`. The workbench at `/workbench` is the
deeper inspection view. Both run from the bundled fixtures in
`public/mock-data/`. A public clone does not need the local letter corpus.

## Viva demo

Application introductions are designed for narrated presentation: short headlines,
visual examples and working interactions carry the main story. Keep qualifications
and literature context in **Presenter notes & sources**. Cohort uses a patient
population, longitudinal analysis a selectable visit history, and prediction a
time boundary and adjustable review capacity. Preserve this distinction when extending
the pages; avoid repeating prose cards or definition tables.

Run `npm run dev` from `frontend`, then open
[http://localhost:3000/demo](http://localhost:3000/demo). The guided pipeline,
batch browser and method details use bundled development records and work without
the Python API or model access.

Suggested walkthrough:

1. Start on **Introduction** (`/demo`). Switch between Time, Arithmetic and
   Context, compare the three past approaches side by side and use **Trace a letter**,
   then choose **Follow the evidence** in the research diagram. Select quotations
   or evidence rows to see their source link; expand the Hybrid calculation to
   inspect the three-month denominator. Stages can also be selected manually;
   reduced motion shows the complete diagram. The workbench's **About the research** link opens this
   same introduction.
2. Open **The pipeline**, starting with letter 16021. Start at **Extract** with the source letter alongside the evidence, then move
   to **Decide** for the final decision. Run the rules locally to reproduce the saved answer.
3. Use the other four cases to show an unchanged answer, a difference between
   executors, and two disagreements with the reference label. Open the optional
   executor comparison and decision trace when useful.
4. **Zoom out to the results** compares models, prompt ablations, and the
   external 300-letter evaluation. Values are transcribed
   at the submitted PDFs' precision in `lib/demoResults.ts`, with table/section
   attribution in each panel. These are aggregate results, never holdout rows.
5. **Applications → Find a cohort** starts with a guided research-cohort workflow:
   define criteria, gather evidence, check matches and missing information, and
   inspect the output. The example opens the explorer with focal epilepsy,
   4+ seizures/month and month 6 selected. The overview separately counts unknown
   frequency; it does not claim adjudicated membership. This teaching page draws
   on the supplied Cohort Identification Literature Review (7 September 2026,
   pp. 3, 7–8). The explorer uses 72 fictional patients and 360 co-generated notes
   and records. Filter a cohort, follow the same patients across five visits, and
   select visits to read their source notes. Unknown frequency stays distinct
   from seizure freedom. Cohort JSON exports preserve the simulation provenance.
   **Follow over time** now opens with a guided longitudinal workflow: define the
   outcome, distinguish event and documentation time, reconcile history, and
   compare a fixed cohort. A clickable five-visit example links observations to
   their notes; a cohort summary preserves unknown states. The explorer opens
   with all 72 patients and offers a return to the workflow. Background: supplied
   Longitudinal Clinical Data Literature Review (7 September 2026, pp. 3, 7–8).

6. **Risk stratification** uses seizure history as an input to a separate
   emergency-care outcome: seizure-related ED attendance or admission during
   months 6–18, using information available through month 6. The introduction
   compares two fictional histories; the explorer compares structured-only and
   note-enhanced logistic regressions on the same patients. Adjust review capacity,
   inspect ranking changes, and read the supporting notes. Counts show subsequent
   events captured, events outside the list, and reviews without an event; these
   are not estimates of events prevented. AUC, Brier score and a limited aggregate
   calibration comparison are available in the model details.
   Emergency simulation v1 (lib/emergencyRisk.ts, seed 91026) extends the existing
   profiles without changing cohort/timeline fixtures. Its arbitrary outcome
   formula intentionally uses note features. Missing emergency follow-up excludes
   patients from both model comparisons; missing predictors remain visible with
   model-only placeholders and missingness indicators. Patient partitions and
   training-only standardisation preserve the prediction cutoff. No extraction
   model was run and no clinical performance or validation is claimed.
   The [2025 emergency-care/death prediction protocol](https://pubmed.ncbi.nlm.nih.gov/41212874/)
   motivates the use case, not the simulation's coefficients. Links to SUDEP and
   medication-withdrawal recurrence studies describe separate applications.
7. Choose **A batch of letters** from the pipeline toolbar, filter a category, and inspect a source letter.
   Returning to the batch preserves the filters. Export the selected records as
   JSON with source text, evidence, provenance and an explicit review status.
8. Open **Under the hood** at any pipeline stage. Its four views show the saved Extract
   prompt, normalise/encode rules, Decide rules and saved Decide prompt. Rule
   entries include the actual Python entry-point function and source fingerprint;
   prompt views include the exact payload for the current letter.

The batch contains 25 evenly spaced saved synthetic dev750 records, selected
without looking at outcomes. It demonstrates evidence inspection and preparation
for review; it is not a population estimate, longitudinal patient dataset or
accuracy evaluation. The five guided cases are selected teaching examples.

The separate application simulation is deterministic (`lib/syntheticPatients.ts`,
seed 8056, version 1); its distributions are arbitrary teaching assumptions.
The cohort and longitudinal views are inspired by EpiDEA, Chang et al. (2026)
and Xie et al. (2023). CLINES and Wang et al.'s SNOW motivate structuring and
predictive feature workflows. Source links and limitations live in expandable
context within the demo. These are application illustrations, not replications
of those studies or extensions to the dissertation's measured extraction scope.

Chapter URLs use `#introduction`, `#pipeline`, `#results`, `#applications` and
`#batch`; browser back/forward navigation works between chapters.

**Run rules locally** invokes the repository `.venv/bin/python` through the local
Next.js server and applies the existing rules to the saved extraction record.
It makes no model call. The response must match the bundled selection and trace
before the UI reports a verified replay. If Python is unavailable, the saved
decision remains available and the UI offers a retry. Hosted deployments use the
saved decisions.

To regenerate the bundle from the original saved development artifacts, run from
the repository root:

```sh
source .venv/bin/activate
python scripts/publications/viva_demo.py --build 16021 10 14187 11254 743
```

This checks extraction and decision provenance, exact source quotes, shared prompt
versions and replay agreement before writing `lib/viva-data.json` and
`lib/viva-method.json`. The original experiment artifacts are needed only for
regeneration, not for presenting the bundled demo.

Before the viva, build and rehearse using `npm run build` followed by
`npm run start`. Check the actual projector, browser zoom, all five cases, one
batch drill-down and local replay. Keep the bundled decisions available for
recovery. Device/projection checks and presenter rehearsal still need to happen
on the presentation setup.

## Local R8 comparison

During local development, select **Gan R8 review** from the workbench dataset
switcher, or open [R8 versus reviewed gold](http://localhost:3000/workbench?dataset=ganR8).
The v0.8.1 view also shows source-aligned measurement and event-label credit
separately. A partial match remains in the whole-finding missed/extra lists so
the original endpoint is still visible.
It shows each synthetic dev750 letter with its existing gold
answer and reviewed v0.7 findings beside the saved R8 answer and findings.
The ExECT-style inspector shows matched findings, field differences, missed gold
findings and extra predictions. Click a quotation to locate it in the source
letter. Matched states use the frozen Finding Purist score. This view makes no model calls and
is unavailable in the public deployment.

If the local bundle is absent or the saved scores change, rebuild it from the
repository root with `.venv/bin/python scripts/benchmarks/build_r8_review.py`.
The generated bundle stays under ignored `runs/`; never put the notes in
`frontend/public`.

The **Labels** selector also offers v0.8 simplified and v0.8.1 one-year timing
references against the same saved R8 responses. Build their local bundles with
`.venv/bin/python scripts/benchmarks/score_findings_v08.py` and
`.venv/bin/python scripts/benchmarks/retime_findings_v081.py`, respectively.
The original v0.7 and v0.8 comparisons remain available for audit.

## Run locally

From the repository root, start the API with the repository environment, then run
the frontend in another terminal:

```sh
.venv/bin/python run.py inspect
```

```sh
cd frontend
npm ci
npm run dev
```

Open [http://127.0.0.1:3000/demo](http://127.0.0.1:3000/demo). The workbench is at `/workbench`.

On Vercel, the fixture files under `public/mock-data` are read by the static API
routes at build/runtime and are not exposed as direct browser file routes.

## Verify

```sh
npm test -- --runInBand
npm run lint
npm run build
```
