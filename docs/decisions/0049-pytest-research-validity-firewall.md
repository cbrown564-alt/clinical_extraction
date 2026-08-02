# 0049: Shrink pytest to a research-validity firewall

Date: 2026-08-02
Status: accepted; Waves 1–2 landed; Waves 3–4 not started

## Decision

Dramatically reduce the Python test base. The default suite is a
**research-validity firewall**, not a scrapbook of every TDD edge case.

Terms live in [`CONTEXT.md`](../../CONTEXT.md) under Verification. This decision
records the trade-off and operating rules.

## Why

The repository collected on the order of 1,500 pytest cases. Most weight is dense
rule and pipeline tables plus historical candidate coverage. That bulk slows
agents, obscures the contracts that protect claims, and fights Decision 0048's
comprehension goal. Aggregate “more tests” is not more research safety when the
suite no longer names what must not silently change.

## Tier model

- **Always-on test tier** — default `pytest` and CI (`-m "not deep"`). Protects
  split barriers, scoring and claim contracts, locked-row policy, and
  selected-method behavior whose silent change would falsify a paper-facing
  claim.
- **Deep test tier** — explicit opt-in (`pytest -m deep`). Short allowlist only;
  capped at about five files or about 100 tests. Growth past the cap is fixed by
  deletion or folding into a thinner always-on contract, not by demoting more
  bulk.

Rejected alternatives: one undifferentiated suite; demoting everything that
fails admission; requiring deep coverage for the default gate; one-test-per-
module coverage as the success criterion.

## Always-on admission

A test enters always-on only if:

1. a silent failure could falsify a paper-facing claim, split barrier,
   locked-row policy, or selected-method clinical meaning; or
2. a living canon page, decision, or method card still names it as the
   **governing test owner** for that obligation.

Method-card stage breadcrumbs are not automatic admission. Prefer one governing
always-on contract (or small vertical-slice file) per real obligation.

## Disposition and thinning

- Non-admitted tests are **deleted by default**.
- Demotion to deep is rare and only for dense tables that still help debug a
  **living** selected-method mechanism under the deep cap.
- Fat files keep a few **exemplars** for living mechanisms; retired or redundant
  encyclopedias are deleted whole.
- Filename heuristics alone do not delete `*candidate*` coverage when that
  behavior still runs in a selected active method.

## Owner rebinds

Deleting or demoting a test updates living owner links in the same change.
Demoted deep tests are not owners. Do not rebind one-for-one every old stage
“Test:” pin.

## Exit band and growth

- Always-on exit band: about **200–300** collected tests; about **100–150** is an
  aspirational floor if governing owners stay honest.
- New tests must pass always-on admission or fit the deep cap. New always-on
  coverage should **replace or narrow** an existing case for the same obligation
  rather than stacking another edge.

## Scope and landing

- **Pytest-first.** Frontend Jest (~73 tests) is out of this campaign unless a
  file clearly pins a retired surface; a light Jest pass may follow later.
- Land **wave-by-risk**:
  1. policy, markers, and default-gate mechanics;
  2. Wave 2 delete class — non-selected surfaces and redundant wrappers once one
     governing owner remains;
  3. fat-table thinning with exemplars and owner rebinds;
  4. scoreboard against the always-on exit band.

## Consequences

- Plain `pytest` no longer means “everything under `tests/`.”
- Clinical-extraction TDD guidance must prefer the smallest lasting always-on
  case over unbounded regression encyclopedias.
- Closed-candidate evidence stays in artifacts and decisions, not in pytest.
- Decision 0048 cleanup may delete tests under these rules without treating
  suite size as a quality metric.
- To collect always-on and deep together after demotions exist, override the
  default gate explicitly (for example
  `pytest --override-ini addopts=` or `pytest -m "deep or not deep"`).

## Wave status

1. **Wave 1 landed:** `pyproject.toml` registers `deep` and defaults to
   `-m "not deep"`; `tests/test_pytest_tier_gate.py` owns the gate contract;
   AGENTS, README, TDD skill, navigation, roadmap, and project status point here.
2. **Wave 2 landed:** deleted 46 non-selected or redundant pytest files (~730
   cases), including GEPA/v09/closed-candidate surfaces and fat
   pipeline_v1 / normalize / SF-split encyclopedias whose living owners remain.
   Rebinds: retained-evidence manifest GEPA and Gan LLM-only test lists;
   ExECT candidate-config retention slice example command. Kept
   `tests/test_clinical_extraction_local_parity.py` because the supervisor
   handoff source allowlist still traces it.
3. **Waves 3–4:** not started (fat-table exemplar thinning + scoreboard).
