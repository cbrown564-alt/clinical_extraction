# Clinical extraction trace explorer specification

Status: implemented local application; not part of the retained evidence deliverables  
Implementation: [`frontend`](../../frontend/) and
[`clinical_extraction.trace_explorer`](../../src/clinical_extraction/trace_explorer/)  
Demonstration: run the API and Next.js frontend per
[`frontend/README.md`](../../frontend/README.md) (`/workbench`, `/clinical-review`,
and related routes); architecture teaching paths live in
[`docs/architecture/`](../../docs/architecture/)  
Last updated: 2026-08-02

## Purpose

Build a local research application that lets a collaborator inspect how one
permitted clinical record moves through an ExECTv2 or Gan 2026 pipeline. The
application must show source evidence, model output, deterministic changes,
component ownership, and score projections without changing the pipeline or
weakening split restrictions.

The first release is a read-only projection of existing artifacts. A later,
bounded review feature may collect independent judgments for the frozen ExECT
semantic-support sample. That feature is not a general annotation tool: it
must preserve the source substrate, write a separate review artifact, and obey
the review protocol below. The application is not a new experiment runner,
model playground, or replacement for the retained evidence reports.

## Product boundary

### Primary user

A researcher or technical reviewer who needs to answer:

- What entered this stage and what left it?
- Which component made a clinically meaningful change?
- Which exact source text supports the selected result?
- Was a change format-only, deterministic clinical logic, model-owned, or a
  benchmark projection?
- How did the rich clinical representation become the reported score?
- Is this record available for inspection under the dataset split policy?

### Complete user loop

1. Open the run catalog and select a task, run, and permitted record.
2. Read the immutable source beside the ordered pipeline stages.
3. Select a stage and inspect its complete saved output, before-and-after
   change, evidence, component owner, and run provenance.
4. Follow a highlighted evidence span back to the source text.
5. Switch to the pipeline map or transformation ledger without losing the
   selected run, record, or stage.
6. When working from the governed semantic-support sample, assess whether the
   cited text supports the conclusion and save or export the bounded review.
7. Copy a stable trace link or trace identifier for another local collaborator.
8. If a row is not inspectable, see an aggregate-only explanation rather than
   an empty or partially redacted record.

### Explicit exclusions from version 1

- live model calls or provider credentials;
- prompt editing or prompt comparison;
- general annotation, gold-label editing, or review outside an explicitly
  indexed and frozen review sample;
- record-level access to Gan `test450`, ExECT `test60`, or the test portion of
  `full200`;
- broad filesystem discovery or automatic ingestion of every experiment file;
- MLflow, a generic experiment registry, or a generic workflow engine;
- clinical-validity claims or adjudication workflows;
- remote or multi-user deployment.

If remote deployment or live execution becomes necessary, it requires a new
decision record covering authentication, authorization, clinical-data
handling, secrets, audit retention, and operational ownership.

## Governing rules

The explorer is subordinate to these owners:

- [`data_contract.md`](data_contract.md) owns dataset and split behavior.
- [`03_evidence_claims_frozen.md`](../canon/03_evidence_claims_frozen.md) owns
  row-inspection limits.
- [`04_scoring.md`](../canon/04_scoring.md) owns score names and meanings.
- [`component_evidence_attribution_architecture.md`](component_evidence_attribution_architecture.md)
  owns component credit and required comparison records.
- [Decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md)
  owns ExECT family-level model and deterministic responsibilities.
- [Decision 0041](../decisions/0041-single-call-exect-model-comparison.md)
  owns the selected one-call ExECT graph.
- [`evidence_groundedness_metric.md`](../reference/evidence_groundedness_metric.md)
  owns evidence grades.
- [`exectv2_semantic_support_review_substrate_protocol_2026-07-18.md`](../experiments/exectv2/reliability/exectv2_semantic_support_review_substrate_protocol_2026-07-18.md)
  owns the 48-item sample, review question, required fields, and claim boundary.

The UI must use the score and evidence names from these documents. It must not
collapse `clinical_headline`, entity-specific scores, phrase, CUI, attributes,
state profile, evidence groundedness, Purist, or Pragmatic into one generic
accuracy value.

## Decisions taken from the prototype

| Question | Decision | Evidence | Consequence | Owner |
| --- | --- | --- | --- | --- |
| What is the core product? | A trace inspector, not an experiment dashboard. | The prototype centers one source record, ordered stages, evidence, and before/after payloads. | Run creation and fleet monitoring are excluded. | This specification |
| How should ExECT and Gan relate? | Share navigation and trace contracts while retaining task-specific stages and scores. | The prototype shows the same record through two materially different pipelines. | Adapters normalize transport shape, not clinical meaning. | Architecture and scoring documents |
| May held-out rows appear? | No. The backend returns aggregate-only run metadata and never creates a record resource for locked rows. | Canonical split rules prohibit row review. | Enforcement occurs before storage and again before every record response. | Data and evidence canon |
| Are schema repair and semantic repair the same stage? | Never. | Gan rules require raw model selection, format repair, semantic deterministic repair, and scoring to remain separable. | Each operation gets its own category and trace event. | Gan contracts and scoring canon |
| Is the application a new retained deliverable? | Not yet. | The active roadmap removed the prior frontend and Observatory because no required workflow justified them. | This document is proposed; promotion requires an explicit scope decision. | Active roadmap |
| What deployment is assumed? | Single-user, local-only, bound to loopback. | It avoids inventing a security model before a remote user need exists. | No authentication in v1; remote binding must fail closed. | This specification |
| Is semantic-support review part of ordinary trace inspection? | No. It is a protocol-bound queue over the frozen 48-item ExECT sample. | Exact evidence is only an eligibility condition; semantic support requires independent review. | The explorer may collect judgments but cannot alter findings, gold, sample membership, or claim status. | Review protocol and this specification |

## Information architecture

### Persistent application state

The URL owns the current selection:

```text
/runs/{run_id}/records/{source_id}/workbench?stage={stage_id}&detail=output
/runs/{run_id}/records/{source_id}/map?stage={stage_id}
/compare?left={trace_id}&right={trace_id}&stage={stage_id}
/runs/{run_id}/records/{source_id}/ledger?category={category}
/reviews/{review_set_id}/items/{review_item_id}
```

Refreshing or sharing a local URL must restore the same run, record, stage, and
detail tab. Invalid or inaccessible identifiers return a clear not-found or
aggregate-only state without selecting a nearby record.

### Global header

The header contains:

- product name: **Clinical extraction trace**;
- task selector: ExECTv2 or Gan 2026;
- run selector with model, method, split, prompt/program version, and run state;
- record search by permitted source identifier;
- an access label: `ROW INSPECTION ALLOWED`, `SYNTHETIC EXAMPLE`, or
  `AGGREGATE ONLY`;
- primary views: **Evidence workbench**, **Pipeline map**, **Compare**, and
  **Transformation ledger**;
- **Semantic support review** appears only when a governed review set is
  indexed and the current item is permitted for review.

The run and record selection stays fixed when changing views. The pipeline
selector in the prototype becomes part of the run selector so the UI cannot
display an ExECT label over Gan data.

## Frontend specification

### 1. Run catalog and selection

The initial screen lists only explicitly indexed runs. Each row shows:

- task and method (`rules`, `llm`, or `llm_with_rules`);
- dataset and exact split name;
- row access policy;
- model and route, or `no model` for rules-only runs;
- prompt or program version;
- repair-policy identifier;
- scorer identifier and available score views;
- artifact hash and ingestion state;
- complete, partial, contaminated, rejected, or illustrative status.

Defaults:

- synthetic example if no index exists;
- most recently indexed inspectable development run otherwise;
- never a held-out run and never an arbitrary first row.

Filters include task, method, split, model, run state, and inspectability. Search
matches identifiers and metadata only. Source-note text is never put in the
search index.

### 2. Evidence workbench

At desktop widths the workbench uses three coordinated areas:

1. **Stage list** — ordered stage name, operation category, owner, and status.
2. **Source and findings** — immutable note text with evidence highlights and
   the current stage's finding or event snapshots.
3. **Trace detail** — status, summary, and tabs for complete output, change,
   evidence, and provenance.

Selecting a stage updates all three areas and the URL. It must not refetch the
source note. Keyboard Up/Down moves through stages; Enter selects; Home/End
moves to the first or last stage.

#### Stage states

Supported states are:

| State | Meaning |
| --- | --- |
| `not_run` | No operation was attempted. |
| `running` | Reserved for future replay jobs; not emitted by static imports. |
| `passed` | Operation completed without repair or blocking diagnostics. |
| `repaired` | A recorded repair changed the transport or representation. |
| `warning` | Output exists but non-blocking diagnostics remain. |
| `failed` | The stage could not produce its required output. |
| `skipped` | A declared condition made the stage inapplicable. |

Color is secondary to text and icon. `repaired` must name whether the change is
format-only or semantic. A repaired stage must never use the same visual label
as an ordinary pass.

#### Complete output tab

- Render structured JSON as a collapsible tree with a plain-text fallback.
- Preserve the saved field names; do not rewrite payload values for display.
- Show truncation explicitly. Never silently omit fields.
- Collapse raw provider output by default and label it as untrusted model text.
- Provide copy for one field or one JSON pointer, not a one-click copy of the
  entire clinical record.

#### Change tab

Show the operation followed by a structural before/after diff:

- additions, removals, replacements, selections, and suppressions have
  separate labels;
- a deterministic change that alters clinical meaning names the deterministic
  rule and rule category; a model-owned change that alters clinical meaning
  declares `owner_kind: model` instead, because it has no deterministic rule to
  name and must not claim one;
- format-only repair states `clinical meaning unchanged by this operation`;
- unchanged fields are collapsed by default;
- every finding transition retains its stable finding or event identifier.

#### Evidence tab

Each evidence item shows:

- quoted text;
- start and end offsets when available;
- evidence grade: exact, repaired artifact, repaired case, repaired whitespace,
  repaired ellipsis, repaired section, absent, or empty;
- the finding/event and operation that selected it;
- whether it is selected evidence, supporting evidence, rejected evidence, or
  merely source-near diagnostic text.

Activating an evidence item scrolls the source panel to the span and briefly
emphasizes it. Exact spans use offsets. Repaired spans show the repaired match
and the original citation without pretending the original was exact. Absent or
empty evidence never highlights unrelated source text.

#### Provenance tab

Required fields:

- run ID, trace ID, source ID, dataset, split, row policy;
- method, pipeline family, model, model route, and mode;
- prompt/program version and profile;
- stage ID, sequence, operation category, operation owner, and portability
  category;
- input artifact path relative to an allowed root, artifact SHA-256, and schema
  version;
- repair policy, scorer, replay/cache mode, and timestamp from the artifact;
- predecessor and successor stage IDs;
- parse, schema, call, evidence, and policy diagnostics.

Provider secrets, environment variables, absolute user paths, and raw request
headers must never be returned.

#### Source and finding panel

- Source text is immutable and uses stable character offsets.
- Overlapping evidence spans use a stacked underline/highlight treatment and a
  small selector, not merged offsets.
- The selected evidence receives the strongest emphasis; other trace evidence
  remains visible but quiet.
- ExECT findings show entity, text, normalized concept, assertion, attributes,
  producer, fact origin, evidence status, and selected/suppressed state.
- Gan shows every extracted event, the selected event IDs, final clinical kind,
  normalized label, evidence, and benchmark label separately.
- Gold is hidden by default and available only for splits whose policy permits
  row-level development review. Its presence is explicit; predictions and gold
  must not share one unlabeled style.

### 3. Pipeline map

The map is derived from trace stages and edges; it is not a separately edited
diagram. Nodes show operation category, owner, status, input/output summary,
and evidence count. Selecting a node opens the same stage in the workbench.

ExECT must show independent producer origin before family-specific assembly.
Gan must keep source, structured events, format repair, semantic normalization,
selection, and scoring visibly separate.

The visual map has a parallel ordered-list representation with the same nodes
and links for keyboard and screen-reader users. Horizontal scrolling is allowed
on small screens; zoom is optional and cannot be the only way to read labels.

### 4. Compare

Compare supports two modes:

- **Same-record run comparison:** two permitted traces with the same dataset
  and source ID, such as rules versus LLM-with-rules or two model conditions.
- **Task explanation:** the bundled `SYN-014` illustrative fixture comparing
  broad ExECT phenotyping with deep Gan frequency reconstruction.

The application refuses a comparison when either trace is aggregate-only or
when source identity cannot be established. The screen aligns stages by
semantic role rather than list position and shows unmatched stages explicitly.
It compares component owner, evidence, clinical output, deterministic changes,
diagnostics, and score views. It does not declare a winner from one record.

### 5. Transformation ledger

One row represents one operation, not one screen stage if a stage contains
multiple attributable operations. Columns are:

- sequence and stage;
- category and owner;
- input reference;
- operation;
- output reference;
- change type;
- selected evidence and grade;
- status and diagnostics.

Filters: category, owner, status, change type, evidence grade, entity/family,
and text match within displayed operation metadata. Expand a row to show its
payload and provenance. The table preserves source order unless the user
explicitly sorts it; an active sort is always visible.

### 6. Clinical review

This ExECTv2 workspace contains two distinct, blinded tasks in one shared
review layout:

- **Correctness review:** is the complete stored attribute value clinically
  correct? Allowed values are `correct` and `incorrect`.
- **Semantic support:** is the complete extracted finding clinically supported
  by the cited text and supplied letter context? Allowed values are
  `supported`, `unsupported`, and `unclear`.

Both tasks collect optional notes and revisioned reviewer identity. They share
the queue, extraction-to-source comparison, full-letter context, judgment
panel, shortcuts, and save-and-advance behavior. They do not share decisions
or collapse correctness into semantic support.

#### Review-set admission

The importer accepts a review set only when it:

- matches the retained substrate hash and contains exactly the 24 expected
  model-family strata with two distinct `dev140` letters per stratum;
- contains no `test60` or mixed-split identifiers;
- preserves all substrate review fields as null;
- names a frozen review schema with allowed values, reviewer instructions, and
  an adjudication rule; and
- has a server-derived `development_row_level` policy for every source.

Until the allowed values and adjudication rule are frozen, the catalog may show
the sample as `prepared`, but the review controls remain disabled and explain
the missing prerequisite. The UI never invents those values.

#### Reviewer loop

1. Enter the reviewer identity used for both task queues.
2. Choose Correctness review or Semantic support without leaving the clinical
   review workspace.
3. Open the next unreviewed item and compare the complete extraction with the
   cited source and permitted full `dev140` letter context.
4. Record the task's single required judgment and optional notes.
5. Save and advance with Enter.
6. Move to the next item without revealing automated correctness, confidence,
   another reviewer's judgment, aggregate model performance, or future
   adjudication outcome.
7. Review completion counts by family and model, validate the set, and export a
   separate machine-readable review artifact.

The layout reuses one evidence-review structure rather than maintaining a
second source viewer. On desktop, the extraction and source comparison occupy
the main area and the single judgment plus optional notes occupy a stable side
panel. On narrow screens, source, conclusion, and evidence precede the form.

#### Bias controls and review states

- Item order is the frozen sample order or a deterministic blinded order
  declared in the review schema; users cannot sort by model score or outcome.
- Model identity and family remain available for provenance, but the default
  review presentation may mask model identity when the frozen instructions
  require blinding.
- Evidence exactness is shown as an eligibility fact, never as a positive
  semantic-support cue.
- Required item states are `unreviewed`, `draft`, `complete`, `skipped`, and
  `conflict`. Only an adjudication import may resolve `conflict`.
- Completion progress is descriptive. It must not display a semantic-support
  rate, model comparison, or clinical-validity claim before the governed
  analysis is separately defined and run.

#### Review persistence and export

Review responses are stored in a separate local SQLite database beneath
`.trace_explorer/reviews/`; they never modify the content-addressed trace
projection or frozen substrate. Every save records review-set ID, review-item
ID, reviewer identity, schema version, response revision, timestamp, and a hash
of the source substrate item. Edits append a revision rather than overwriting
history.

Export produces a new JSON artifact containing the frozen item identifiers,
review fields, reviewer metadata, revision history, completion state, substrate
hash, review-schema hash, and export hash. It excludes full source text. The
export validator refuses incomplete required fields, changed sample membership,
source-hash mismatch, or an item whose current response does not match the
frozen schema. Importing another reviewer's artifact is explicit and preserves
reviewer separation; it never silently merges or adjudicates disagreements.

### Responsive behavior

- `>= 1280px`: three-area workbench.
- `768–1279px`: stage list becomes a horizontal strip; source and trace stack in
  two columns or vertically according to available width.
- `< 768px`: read-only single-column layout; stage selector is a standard
  disclosure list, detail tabs scroll horizontally, and the map defaults to its
  ordered-list representation.
- No feature that changes or reveals data is desktop-only.

### Visual system

Preserve the prototype's restrained research-tool register:

- one UI sans-serif family and one monospace family for identifiers and JSON;
- neutral content surfaces with blue for model-owned operations, amber for
  deterministic or repair operations, and green for verified evidence;
- semantic colors are tokens and always paired with text/icon labels;
- 4.5:1 minimum contrast for body and placeholder text;
- 6–8 px control radius and 12–16 px panel radius;
- no decorative gradients, glass effects, oversized metrics, or animation.

Motion is limited to 150–200 ms state transitions, source-span emphasis, and
panel disclosure. `prefers-reduced-motion` makes these instant or crossfades.

### Loading, empty, error, and access states

| Situation | Required behavior |
| --- | --- |
| Catalog loading | Skeleton rows that preserve the final layout. |
| No indexed runs | Explain how the maintainer builds an index; offer the synthetic example. |
| No records match | Keep filters visible and state which filters removed results. |
| Aggregate-only run | Show safe aggregate metadata and why row inspection is unavailable; render no record selector. |
| Missing artifact | Name the missing relative path and expected hash without exposing an absolute path. |
| Hash mismatch | Block the run, mark it `integrity_failed`, and render no row data. |
| Adapter failure | Show the source artifact and diagnostic code; do not partially guess stages. |
| Evidence absent | Keep the finding visible, label evidence absent, and do not highlight source text. |
| Oversized payload | Show the retained summary and explicit truncation metadata. |
| Unknown schema | Quarantine the import; never apply a nearest-version parser silently. |

### Accessibility

- Meet WCAG 2.2 AA for the implemented application.
- Use landmarks, real buttons, tabs with linked tab panels, table headers, and a
  logical heading order.
- Maintain visible focus and never rely on color alone.
- Announce stage and view changes in a concise live region; do not announce the
  entire JSON payload.
- JSON trees, diffs, source highlights, and map nodes all have text equivalents.
- Target size is at least 24 by 24 CSS pixels; primary controls use 40 pixels.
- A keyboard user can select a run, select a record, inspect every stage, follow
  evidence, change views, and return without a pointer.

## Backend specification

### Technology and process model

Use the repository's Python 3.11 environment and Pydantic v2 contracts. Add a
small FastAPI application behind an optional `trace-ui` dependency group and
serve it with Uvicorn on `127.0.0.1` only. The process must reject a non-loopback
bind unless a future remote-deployment decision explicitly enables it.

Use a separate React and TypeScript frontend built with Vite. Generate
TypeScript API types from the backend OpenAPI document. Pin exact frontend and
backend dependency versions in their lockfiles when implementation begins.

Do not add an ORM or service framework. Use the standard `sqlite3` module for a
disposable read index and content-addressed JSON objects for normalized trace
projections.

### Proposed source layout

```text
src/clinical_extraction/trace_explorer/
  contracts.py              # transport-neutral trace models
  policy.py                 # split and row-access decisions
  projector.py              # stage, ledger, and graph derivation
  index.py                  # SQLite read-index creation and queries
  object_store.py           # content-addressed projection storage
  adapters/
    exectv2.py              # current ExECT artifact adapter
    gan2026.py              # current Gan artifact adapter
    illustrative.py         # SYN-014 fixture only
    semantic_review.py      # frozen substrate and review-schema adapter
  api/
    app.py
    dependencies.py
    errors.py
    routes_catalog.py
    routes_runs.py
    routes_traces.py
    routes_reviews.py
frontend/trace-explorer/
  src/
    api/
    components/
    features/catalog/
    features/workbench/
    features/map/
    features/compare/
    features/ledger/
    features/semantic-review/
    routes/
```

The adapters depend on current task code. Current pipeline code must not import
the trace explorer.

### Storage

The explorer directory defaults to `.trace_explorer/` and remains untracked:

```text
.trace_explorer/
  index.sqlite3
  objects/{sha256}.json
  reviews/reviews.sqlite3
  reviews/exports/{sha256}.json
  build-manifest.json
```

The index is derived and replaceable. It stores catalog metadata, allowed
source identifiers, trace/object hashes, and filter fields. It does not store
source-note text, raw prompts, raw model output, gold rows, or provider
credentials. Those live only in access-controlled projection objects and are
loaded after policy evaluation.

Index construction is an explicit command over named inputs:

```powershell
.venv\Scripts\python.exe -m clinical_extraction.trace_explorer.index build `
  --artifact <relative-path> `
  --output .trace_explorer
```

The command must not recursively discover experiments. Each artifact is
checked against the retained evidence index or an explicitly supplied
development-artifact allowlist, hashed before parsing, and assigned one schema
version. Imports are atomic: build a temporary index, validate it, then replace
the previous index.

Review responses are the only mutable application data. They use the separate
review database and export directory described above and never modify a trace
projection or the frozen substrate. Rebuilding the trace index must neither
delete nor rewrite them.

### Access policy

Every run receives one server-derived policy:

| Policy | Catalog | Aggregates | Record IDs | Source and trace rows |
| --- | :---: | :---: | :---: | :---: |
| `illustrative` | Yes | Yes | Fixture only | Yes |
| `development_row_level` | Yes | Yes | Yes | Yes |
| `aggregate_only` | Yes | Yes | No | No |
| `denied` | Minimal diagnostic metadata | No | No | No |

Current mappings:

- ExECT `dev140` -> `development_row_level`;
- ExECT `test60` -> `aggregate_only`;
- ExECT `full200` -> `aggregate_only` unless a new projection contains only
  manifest-proven dev140 identifiers;
- Gan validation/development split -> `development_row_level`;
- Gan `test450` -> `aggregate_only`;
- synthetic `SYN-014` -> `illustrative`.

Policy is calculated from canonical dataset and split identifiers, never from a
client flag or artifact filename. An unknown dataset, split, or mixed identifier
set is `denied`. The importer must prove that every row ID belongs to the stated
inspectable split before it creates record index entries.

All record routes repeat the policy check and query by both run ID and source
ID. A forbidden or unknown row returns a non-enumerating `404`; an explicitly
selected aggregate-only run returns `403 aggregate_only` before a source ID is
accepted.

### Trace contract

The normalized projection preserves task-specific payloads while sharing the
following envelope.

```json
{
  "schema_version": "trace.v1",
  "trace_id": "sha256:...",
  "run": {
    "run_id": "...",
    "task": "exectv2",
    "dataset": "ExECTv2",
    "split": "dev140",
    "row_policy": "development_row_level",
    "method": "llm_with_rules",
    "model": "...",
    "model_route": "...",
    "prompt_version": "...",
    "program_version": "...",
    "repair_policy": "...",
    "scorer": "...",
    "replay_mode": "saved_output",
    "artifact_sha256": "..."
  },
  "source": {
    "source_id": "...",
    "text": "...",
    "character_count": 286,
    "text_sha256": "..."
  },
  "stages": [],
  "findings": [],
  "score_views": [],
  "diagnostics": []
}
```

#### `TraceStage`

Required fields:

- `stage_id`, `sequence`, `name`, and `summary`;
- `category`: `source`, `model`, `format_repair`, `deterministic_semantic`,
  `evidence_validation`, `assembly`, `projection`, or `scoring`;
- `owner`: stable component identifier and display name;
- `rule_category` when deterministic: `general`, `clinical_epilepsy`,
  `seizure_frequency`, `gan2026_specific`, or `benchmark_format`;
- `status` and structured diagnostics;
- `input_refs`, `output_ref`, and optional bounded inline summary;
- ordered `changes`;
- evidence references;
- predecessor and successor stage IDs;
- elapsed time and provider usage only when measured in the source artifact.

Do not estimate missing latency, cost, token, energy, or hardware fields.

#### `TraceChange`

Required fields:

- `change_id`, `stage_id`, and operation owner, including the owner's
  `owner_kind`: model, deterministic, or scorer;
- `kind`: add, remove, replace, select, suppress, split, merge, normalize,
  validate, format_repair, or project;
- JSON pointers or finding/event IDs for before and after values;
- `clinical_meaning_changed`: true, false, or unknown;
- deterministic rule and rule category when applicable;
- evidence references and reason;
- first component that made a later incorrect result unrecoverable when that
  information exists in a comparison artifact.

#### `EvidenceReference`

Required fields:

- stable evidence ID and source ID;
- original citation;
- start/end offsets when exact;
- grade from the canonical evidence-groundedness metric;
- selected, supporting, rejected, or diagnostic role;
- linked finding/event and stage IDs;
- optional repaired citation and repair kind.

The backend verifies offsets and evidence grades during import. Client-provided
grades are never trusted.

#### Task-specific projections

ExECT adapters preserve `ClinicalFinding`, `FindingSource`, and
`ProvenanceEvent` fields including finding ID, entity, text, attributes,
normalized concept, assertion, confidence, producer, fact origin, raw surface,
evidence status, and every deterministic provenance event.

Gan adapters preserve the raw structured events, selected event IDs, selected
clinical state, format-repair diagnostics, semantic repair steps, selected
evidence, normalized label, and separate Purist and Pragmatic projections.

The shared contract may add transport metadata but must not rename task fields
inside saved payloads or map Gan frequency kinds to broader terms without the
open schema decision in `data_contract.md` being resolved.

### API

Base path: `/api/v1`. JSON responses use the trace schema version and an error
envelope with `code`, `message`, `request_id`, and safe details.

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Process and index readiness; no artifact details. |
| `GET /catalog` | Tasks, filter values, index build ID, and policy counts. |
| `GET /runs` | Cursor-paginated run catalog. |
| `GET /runs/{run_id}` | Safe metadata, aggregates, integrity, and row policy. |
| `GET /runs/{run_id}/records` | Cursor-paginated permitted source IDs and small summaries. |
| `GET /runs/{run_id}/records/{source_id}/trace` | Complete normalized trace envelope. |
| `GET /runs/{run_id}/records/{source_id}/stages/{stage_id}` | Lazily loaded stage payload and diff. |
| `GET /runs/{run_id}/records/{source_id}/ledger` | Flat operation rows with filters. |
| `GET /runs/{run_id}/records/{source_id}/graph` | Derived nodes and edges. |
| `GET /runs/{run_id}/aggregates` | Named score views and run diagnostics. |
| `POST /comparisons/resolve` | Validate and align two already permitted trace IDs. |
| `GET /review-sets` | Governed review sets, readiness, schema, and safe progress counts. |
| `GET /review-sets/{review_set_id}/items` | Permitted item identifiers and completion states. |
| `GET /review-sets/{review_set_id}/items/{review_item_id}` | Review item, evidence, conclusion, and optional permitted source context. |
| `PUT /review-sets/{review_set_id}/items/{review_item_id}/response` | Append a schema-valid draft or completed response revision. |
| `POST /review-sets/{review_set_id}/validate` | Check readiness, membership, hashes, and response completeness. |
| `POST /review-sets/{review_set_id}/export` | Write and return metadata for a validated review artifact. |

`POST /comparisons/resolve` is a read computation: it stores nothing and never
accepts source text or raw payloads from the client.

Review writes require an exact current response revision and substrate-item
hash. A stale revision returns `409 review_conflict` without discarding either
response. Review routes reject a set whose frozen schema, substrate hash, or
row policy no longer matches the indexed metadata.

Pagination uses opaque cursors and stable ordering by source identifier. API
responses set `Cache-Control: no-store`. ETags may use projection hashes for
local conditional requests without client persistence.

### Validation and integrity

The importer must:

1. resolve every input beneath an approved repository or artifact root;
2. reject symlink or traversal escapes;
3. hash the source before parsing;
4. identify one exact adapter and schema version;
5. verify run metadata, split membership, row uniqueness, and completeness;
6. validate source offsets and evidence grades;
7. keep model output, format repair, semantic repair, evidence selection, and
   scoring as separate events;
8. verify that stage sequence and graph edges are acyclic and complete;
9. write content-addressed projections and the index atomically;
10. emit a machine-readable build manifest with counts and diagnostics.
11. validate review-set membership, null substrate labels, review-schema hash,
    and `dev140` source hashes before enabling review writes.

Hash mismatch, unknown schema, mixed split, duplicated source ID, invalid
offsets, or an adapter exception quarantines the affected run. No partial row
resources are exposed from a quarantined run.

### Privacy and local security

- Bind to loopback only and send no telemetry.
- Load no remote fonts, scripts, styles, analytics, or image assets.
- Set a restrictive Content Security Policy and deny framing.
- Never put source text, raw model output, gold rows, or prompts in application
  logs, SQLite search fields, error messages, URLs, or browser storage.
- Store only selection identifiers in the URL; source text stays in memory.
- Use `Cache-Control: no-store`; do not register a service worker.
- Sanitize all rendered strings as text. Raw model output is never interpreted
  as HTML or Markdown.
- Cap inline payloads and recursion depth to prevent a malformed artifact from
  exhausting the browser.
- Do not expose arbitrary file reads or user-supplied filesystem paths through
  HTTP.
- Treat reviewer identity and notes as sensitive local data. Do not place them
  in URLs, application logs, catalog search fields, or browser storage.

### Performance budgets

Measured on a typical local development machine with a warm index:

- catalog response: p95 under 200 ms for 1,000 indexed runs;
- record-list response: p95 under 200 ms for 100 rows per page;
- trace envelope: p95 under 500 ms for a 1 MB projection;
- stage detail: p95 under 300 ms for a 2 MB saved payload;
- initial usable workbench: under 1.5 s on a current desktop browser;
- stage switch after load: under 100 ms excluding lazy payload fetch.

Payloads over 2 MB are returned through the stage-detail route with explicit
truncation/size metadata in the envelope. The UI virtualizes only genuinely
long record lists or ledger tables; six-stage navigation must remain ordinary
DOM content.

## Failure and recovery paths

### Incomplete run

The catalog may show a partial development run, but its row list includes only
complete, schema-valid rows. The run page states expected, completed, failed,
and quarantined counts. Partial runs cannot be labeled final or compared as a
complete panel.

### Contaminated split

If any source ID falls outside the declared inspectable manifest, the entire
run is denied row-level indexing. The importer reports counts and safe IDs only
when those IDs are themselves permitted development identifiers. It must not
serve the permitted subset of a contaminated artifact as if the original run
were clean.

### Missing source text

The trace remains cataloged only if safe metadata and aggregates are valid. A
record trace requiring unavailable source text is not exposed. The UI explains
that evidence inspection requires the declared source artifact and matching
hash.

### Adapter upgrade

A new adapter version writes new projection objects and a new index build. It
never edits the old content-addressed object. Contract compatibility tests must
show that unchanged source artifacts retain stable trace and finding identities
or explicitly record the migration.

### Review substrate or schema mismatch

If the substrate, review schema, or source hash differs from the indexed value,
the review set becomes read-only and export is blocked. Existing response
revisions remain available for explicit recovery, but the application does not
reattach them to changed items. Re-enabling review requires a newly indexed,
versioned review set and an explicit migration whose output preserves both old
and new identifiers.

### Interrupted or conflicting review

Drafts are recoverable after restart. A stale browser write creates a conflict
rather than replacing the current revision. The reviewer can inspect both
revisions and save a new response; only a separately governed adjudication
artifact may resolve disagreement between independent reviewers.

## Testing and verification

### Backend

- policy tests for every dataset/split mapping and unknown/mixed inputs;
- path traversal, symlink escape, and non-loopback binding tests;
- adapter fixture tests for current ExECT and Gan saved-output shapes;
- golden contract snapshots using only synthetic or permitted development
  fixtures;
- evidence-offset and grade tests, including overlaps and every repair grade;
- separation tests proving format repair cannot be labeled semantic and vice
  versa;
- integrity tests for hash mismatch, duplicates, partial artifacts, and unknown
  schemas;
- API tests that aggregate-only runs have no enumerable record endpoint;
- OpenAPI compatibility test for the generated TypeScript client.
- review-set admission tests for all 24 strata, distinct-letter sampling, null
  substrate labels, frozen schema, `dev140` membership, and source hashes;
- response revision, conflict, restart recovery, validation, and export tests;
- tests proving review writes cannot mutate traces, substrate rows, or gold.

### Frontend

- component tests for every control state, stage state, evidence grade, and
  access state;
- keyboard tests for run selection, stage navigation, tabs, evidence links,
  ledger expansion, and return focus;
- automated accessibility checks plus manual screen-reader checks of the
  workbench and map fallback;
- route restoration and forbidden-route tests;
- visual regression tests at desktop, tablet, and narrow widths using the
  illustrative fixture;
- tests that no note text or raw payload enters URL, local storage, logs, or
  client error reporting;
- production build, type check, lint, and bundle-size check.
- keyboard and screen-reader tests for the reviewer loop, required fields,
  draft recovery, skip reasons, conflicts, and export validation;
- tests that review screens do not expose performance summaries or another
  reviewer's judgments before the governing instructions allow it.

### End-to-end acceptance slice

The first implemented slice uses `SYN-014` only and must prove this complete
loop:

1. open the ExECT trace;
2. select candidate production, family assembly, normalization, evidence, and
   scoring stages;
3. follow the Prescription evidence to `lamotrigine 150 mg twice daily`;
4. inspect the `twice daily` to `BID` deterministic change and its owner;
5. switch to Gan without losing the source fixture;
6. distinguish schema repair from monthly rate normalization;
7. inspect the selected rate while retaining cluster and seizure-free events;
8. open the pipeline map and return to the same workbench stage;
9. inspect the equivalent ledger operation using only the keyboard;
10. attempt a synthetic aggregate-only run and verify that no record route or
    source text is available.

Only after this slice passes should adapters be connected to real permitted
development artifacts.

## Implementation sequence

1. **Contracts and policy:** implement Pydantic trace contracts, split policy,
   synthetic fixture, and policy/integrity tests.
2. **Representative backend slice:** index `SYN-014`, serve catalog, trace,
   stage, ledger, and graph routes, and generate OpenAPI types.
3. **Representative frontend slice:** complete the end-to-end acceptance loop
   above with responsive and accessible states.
4. **ExECT adapter:** project one permitted dev140 artifact, prove stable finding
   IDs, provenance, score views, and exact evidence.
5. **Gan adapter:** project one permitted validation artifact and prove the
   separation of event extraction, format repair, semantic repair, selection,
   and Purist/Pragmatic scoring.
6. **Semantic-support review slice:** after the review values and adjudication
   rule are frozen, index the 48-item substrate, complete one synthetic review
   set end to end, then verify the real `dev140` sample and export contract.
7. **Hardening:** add quarantine behavior, performance checks, contract
   compatibility, and production builds.
8. **Promotion decision:** decide whether the verified application becomes a
   retained deliverable. Only then update the active roadmap, CI, packaging,
   and maintenance ownership.

## Acceptance criteria

The application is implemented when:

- all four prototype views operate on one shared, URL-addressable trace state;
- the source, stage payloads, changes, evidence, provenance, graph, and ledger
  come from backend contracts rather than duplicated frontend fixture objects;
- ExECT and Gan preserve their different clinical objects, operation ownership,
  and score semantics;
- every prediction-changing deterministic operation is attributable;
- format-only and semantic changes are visibly and structurally distinct;
- aggregate-only runs cannot reveal source IDs, notes, gold, row failures, or
  row payloads through the UI, API, logs, index, or error messages;
- the frozen semantic-support sample can be reviewed without changing sample
  membership, traces, source artifacts, findings, or gold;
- review responses retain identity, schema, hashes, and revision history and
  export to a separately validated artifact without full source text;
- the review UI does not convert exact evidence, completion, or reviewer input
  into a clinical-validity or model-ranking claim;
- the representative backend and frontend test suites pass;
- the UI production build is visually checked at the three responsive widths;
- the repository's Python tests, Ruff, and mypy checks remain clean.

It is verified only after those checks pass. It is validated only after
representative researchers can complete the inspection loop and the resulting
feedback is recorded. It is promoted only after the roadmap and retained
deliverable boundary are changed explicitly.

## Deferred decisions

- Whether this application becomes a retained project deliverable. Unblock:
  explicit owner approval after the synthetic and one-artifact slices are
  verified.
- Whether a remote, multi-user deployment is needed. Unblock: a named user and
  deployment environment; then write a security and operations decision.
- Whether no-call deterministic replay should be triggerable from the UI.
  Unblock: a required reviewer workflow that cannot be met by explicit CLI
  indexing; keep model calls out of that decision.
- Whether future shared schemas rename Gan `FrequencyLabelKind`. Unblock: the
  existing open decision in `data_contract.md`.
- Semantic-support review controls remain disabled until allowed response
  values, reviewer instructions, and the adjudication rule are frozen in a
  dated protocol amendment. Preparing the current substrate does not clear
  this dependency.
