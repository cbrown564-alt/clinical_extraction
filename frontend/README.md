# Clinical Extraction Explorer

This is the established Next.js interface for inspecting the Gan 2026 and ExECTv2
research pipelines. The browser talks to the local Python service through Next.js at
`/api/*`; `next.config.ts` forwards those requests to `http://127.0.0.1:8000`.

## Run locally on Windows

From the repository root, start the API with the repository environment:

```powershell
.venv\Scripts\python.exe -m clinical_extraction.trace_explorer.api.app
```

In another terminal, start the frontend:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Open [http://127.0.0.1:3000/workbench](http://127.0.0.1:3000/workbench).

For ExECTv2 clinical review, open
[http://127.0.0.1:3000/clinical-review](http://127.0.0.1:3000/clinical-review).
Each reviewer uses one assigned ID and switches inside the workspace between
Correctness review and Semantic support. Both tasks use the same queue,
extraction-to-source comparison, full-letter context, optional notes, and
reviewer-separated revision history. The semantic task's governing allowed
values and adjudication rule are in the
[review protocol](../../docs/experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md).

The API builds its disposable local trace index on first start. Reviewer decisions and
their immutable revisions are stored separately in `.trace_explorer/reviews.sqlite3`;
the evidence substrate is never mutated. The fixture files under `public` are an
allowlisted backend input and are blocked as browser routes; the frontend always uses
the live local API.

## Verify

```powershell
npm test -- --runInBand
npm run lint
npm run build
```
