# Dissertation Publication Materials

This directory contains the manuscript sources, supporting materials, submission rubrics, IEEE LaTeX templates, and historical draft archives for the MSc AI dissertation:
*Extract, then decide: a two-stage pipeline to identify seizure frequency patterns in epilepsy clinic letters* (Conor Brown, Queen's University Belfast, September 2026).

## Directory Structure

- `draft/`: Active dissertation manuscript files:
  - `Extract, then decide.tex`: Primary manuscript LaTeX source (IEEEtran format).
  - `Extract, then decide.pdf`: Preserved manuscript PDF (10 pages).
  - Figure assets: architecture diagrams (`pipeline_architecture.*`), method comparisons (`pipeline_methods_comparison.*`), confusion matrices (`confusion_matrix*`), model stage performance charts (`six_model_stage_performance.*`), and letter / frequency examples.
  - `archive/`: Historical preliminary draft stages (`FES.tex`, `RES...tex`, and prior diagrams).
- `supporting materials/`: Supplementary materials accompanying the dissertation:
  - `Supporting materials.tex`: Supplementary document LaTeX source.
  - `Supporting materials.pdf`: Preserved supplementary PDF (16 pages).
  - `gan_llm_extract_prompt_template.json`: Frozen extraction prompt template.
  - `gan_llm_select_prompt_template.json`: Frozen selection prompt template.
  - Detailed performance charts and inspection figures (`development_vs_test_generalization.*`, `healthcare_index_vs_purist_f1.*`, error mode crops).
  - `archive/`: Earlier supporting figures.
- `template/`: IEEE conference template files (`IEEEtran.cls`, `IEEE-conference-template-062824.*`, `Diagrams.pptx`).
- Top-level files:
  - `ECS8056_Project_Handbook_202526.pdf`: Academic module handbook.
  - `Rubric_ECS8056.pdf`: Dissertation grading rubric.
  - `ai_draft.tex`: Historical initial AI draft outline.

## Outputs: Current vs. Historical

- **Current preserved outputs**:
  - Primary manuscript: `draft/Extract, then decide.pdf` (10 pages, reflecting the two-stage extract-then-decide pipeline).
  - Supporting materials: `supporting materials/Supporting materials.pdf` (16 pages, supplementary results, prompt contracts, and extended reviews).
- **Historical draft outputs**:
  - `draft/archive/FES.pdf` (pre-simplification three-stage FES manuscript).
  - `draft/archive/RES - A modular pipeline to recognise, encode and select relevant facts from clinical notes.pdf` (earlier RES manuscript draft).

## Build Instructions

Building the LaTeX documents requires `pdflatex` (e.g. from TeX Live / MacTeX; on macOS typically located at `/Library/TeX/texbin/pdflatex`).

The following commands assume the current working directory is the repository root. Outputs are directed to isolated directories under `scratch/` so tracked PDFs are never modified.

### 1. Primary Manuscript (`Extract, then decide.tex`)

```bash
mkdir -p scratch/publication-build/manuscript
(cd "publications/dissertation/draft" && PATH="/Library/TeX/texbin:$PATH" pdflatex -interaction=nonstopmode -output-directory="$PWD/../../../scratch/publication-build/manuscript" "Extract, then decide.tex")
(cd "publications/dissertation/draft" && PATH="/Library/TeX/texbin:$PATH" pdflatex -interaction=nonstopmode -output-directory="$PWD/../../../scratch/publication-build/manuscript" "Extract, then decide.tex")
```

The document builds with exit code 0 producing a 10-page PDF with the same extracted text as the pre-move rebuild.

### 2. Supporting Materials (`Supporting materials.tex`)

```bash
mkdir -p scratch/publication-build/supporting
(cd "publications/dissertation/supporting materials" && PATH="/Library/TeX/texbin:$PATH" pdflatex -interaction=nonstopmode -output-directory="$PWD/../../../scratch/publication-build/supporting" "Supporting materials.tex")
(cd "publications/dissertation/supporting materials" && PATH="/Library/TeX/texbin:$PATH" pdflatex -interaction=nonstopmode -output-directory="$PWD/../../../scratch/publication-build/supporting" "Supporting materials.tex")
```

### Pre-Existing Build Limitation

The source file `Supporting materials.tex` references `\includegraphics[width=\linewidth]{inventory.png}` around line 950. The asset `inventory.png` is missing from this checkout. Because of this missing figure:
- The compilation fails with `! Package pdftex.def Error: File 'inventory.png' not found` and exits with a nonzero status (code 1).
- In nonstop mode, `pdftex` inserts a draft bounding box and produces a 15-page PDF.
- This rebuild is defective and does **NOT** match the preserved 16-page `Supporting materials.pdf`. Pre-move and post-move rebuilds exhibit identical failure behavior and identical 15-page streams, confirming the move itself introduced no build regressions.
- **Do not overwrite or replace the preserved 16-page `Supporting materials.pdf` with this rebuild output.**
