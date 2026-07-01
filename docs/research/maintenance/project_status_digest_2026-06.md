# Project Status Digest — June 2026

Archived entries moved from `PROJECT_STATUS.md` "Done Recently" during the
2026-07-01 documentation consolidation pass. These remain discoverable here;
the live control board keeps a rolling ~30-day window only.

## 2026-06-26

- IEEE manuscript final consistency pass — verified every reported number,
  family score, and claim-boundary phrase end-to-end against the Appendix
  Table I source artifacts (Gan `test450` phase-4 audit; consensus/fresh Gate 4
  constrained `348/450 +19 0.5909` failed and exact `359/450 +16 0.6000`
  passed; ExECTv2 v08 full-200 `0.8502`; lean frontier `0.8356`/`0.7525`/`400`
  calls; calibration ECE `0.0432`/Brier `0.2245`/`0.2387`; robustness
  `0.8336` hard-slice across `414` cells vs `0.8503`; dev140 and full-200
  component-off ranges; same-core model swap). All numbers matched. Two
  consistency fixes applied: aligned the Results task descriptor to "broad
  multi-entity phenotyping", and restored the "(of rendered)" qualifier on the
  Gan Purist/Pragmatic table headers so the table's `364/448` (`0.812`)
  reconciles with the prose's `364/450` (`0.809`). Recompiled cleanly (`5`
  pages, no undefined refs or warnings).
- IEEE manuscript prose compression — tightened Introduction, Related Work,
  Methods (inspection-boundary paragraph folded), and Discussion prose without
  changing any number, table, or claim boundary; recompiled cleanly (5 pages,
  no undefined refs).
- IEEE manuscript provenance pass — added Appendix Table I linking result
  families to source artifacts and claim boundaries, added a Methods pointer,
  and recompiled
  `literature/IEEE/IEEE-conference-template-062824/IEEE-conference-template-062824.pdf`.
- Repo cleanup closed — pass 1 archived `438` superseded notes; pass 2 archived
  `1012` registry-filtered/unregistered iteration notes (`104` root `.md`
  remain active). Indexes: `experiments/README.md`,
  `experiments/archive/ARCHIVE_INDEX.md`, `docs/REGENERATION.md`,
  `docs/experiments/FROZEN_EVIDENCE_MANIFEST_2026-06-26.md`.
- Paper scaffold and Section 4 integration — IEEE TikZ figure, methods/results
  tables, appendix move, and manuscript Section 4 folded into LaTeX with
  compiled PDF.
- ExECTv2 component-off full200 replay (`9` rows; positive dictionary,
  semantic lens, headline projection deltas) and Qwen repair v02 same-core
  evidence (`0.8197` full-200; `0` call/parse failures).
- Gan consensus/fresh v0.9 gates and exact aggregate-only Gate 4 pass; holdout
  results remain frozen.
- 2026-06-25 to 2026-06-26: Same-core full-200 model-swap evidence, reliability
  validations, MLflow/registry indexing.
