# Clinical Extraction Explorer

This is the established Next.js interface for inspecting the Gan 2026 and ExECTv2
research pipelines. On Vercel, the Next.js API routes at `/api/*` serve the bundled
demonstration fixtures. Local development forwards those routes to the Python API
when it is running.

The Demo UI runs from the bundled fixtures in `public/mock-data/`. A public
clone does not need the local letter corpus.

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
