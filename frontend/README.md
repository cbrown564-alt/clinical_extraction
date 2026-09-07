# Clinical Extraction Explorer

This is the established Next.js interface for inspecting the Gan 2026 and ExECTv2
research pipelines. On Vercel, the Next.js API routes at `/api/*` serve the bundled
demonstration fixtures. Local development forwards those routes to the Python API
when it is running.

The workbench demonstration runs from the bundled fixtures in `public/mock-data/`. A public
clone does not need the local letter corpus.

## Viva demo

Run `npm run dev` from `frontend`, then open
[http://localhost:3000/demo](http://localhost:3000/demo). The guided pipeline,
batch browser and method details use bundled development records and work without
the Python API or model access.

Suggested walkthrough:

1. Start with letter 16021. Step through the letter, extracted evidence and final
   decision. Run the rules locally to reproduce the saved answer.
2. Use the other four cases to show an unchanged answer, a difference between
   executors, and two disagreements with the reference label. Open the optional
   executor comparison and decision trace when useful.
3. Choose **A batch of letters**, filter a category, and inspect a source letter.
   Returning to the batch preserves the filters. Export the selected records as
   JSON with source text, evidence, provenance and an explicit review status.
4. Open **Under the hood** at any stage. Its four views show the saved Extract
   prompt, normalise/encode rules, Decide rules and saved Decide prompt. Rule
   entries include the actual Python entry-point function and source fingerprint;
   prompt views include the exact payload for the current letter.

The batch contains 25 evenly spaced saved synthetic dev750 records, selected
without looking at outcomes. It demonstrates evidence inspection and preparation
for review; it is not a population estimate, longitudinal patient dataset or
accuracy evaluation. The five guided cases are selected teaching examples.

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
python scripts/viva_demo.py --build 16021 10 14187 11254 743
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

## Run locally

From the repository root, start the API with the repository environment, then run
the frontend in another terminal:

```sh
.venv/bin/python -m clinical_extraction.trace_explorer.api.app
```

```sh
cd frontend
npm ci
npm run dev
```

Open [http://127.0.0.1:3000/workbench](http://127.0.0.1:3000/workbench).

On Vercel, the fixture files under `public/mock-data` are read by the static API
routes at build/runtime and are not exposed as direct browser file routes.

## Verify

```sh
npm test -- --runInBand
npm run lint
npm run build
```
