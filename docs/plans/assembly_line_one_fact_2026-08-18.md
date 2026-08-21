# Assembly Line: one fact through the pipeline

Date: 2026-08-18
Status: built
Letters: paper flagship G1, G3, E1, E2 only
(`GAN-15431`, `GAN-2166`, `EA0186`, `EA0057`)

## The two lanes

| | Workbench | Assembly Line |
| --- | --- | --- |
| Job | The letter’s facts against gold | What changed along the way for **one** predicted fact |
| Question | Did we recover the right mentions? | What happened to this fact at each stage? |
| Highlight | Gold and predicted, family-coloured | Predicted spans only |
| Sidebar | Every mention in the active family, matched to gold | One fact, top to bottom, every transform |
| Gold | Throughout | Last row of the sidebar only |

Workbench stays as it is. Assembly Line is rebuilt. The current S-path
station map is retired for this surface. It taught method order. It did
not show a fact moving.

## What we are building

Same shell as Workbench: letter dominant on the left, inspector on the
right. Reuse the existing clinical letter view (`LetterRenderer` /
`ExplorerBody`). Do not invent a second letter widget.

The letter shows **model-predicted** (or rules-predicted) spans for the
active method. Click a highlighted span to select that fact. The
sidebar then shows that fact only, as a vertical list of the stages
that touched it.

Each sidebar row is one transform:

- stage name
- what entered
- what left
- idle if this stage did not change this fact

The last row is gold: the comparable gold unit for this fact, or a
clear “no gold counterpart” if the scorer has none. That is the only
gold on the page.

Chrome keeps **Case** (the four letters) and **Rules / Model / Hybrid**.

## What a “fact” is

Not a family. Not a station. One attributable extraction unit.

| Task | Selectable fact | Gold at the bottom |
| --- | --- | --- |
| Gan 2026 | One candidate event, or the one-call label plus its quoted span | The letter’s single gold frequency label |
| ExECTv2 | One predicted mention (one headline unit) | The aligned gold mention, if any |

Gan Workbench often shows extract → normalise → select over **many**
events. That inventory stays on Workbench. Assembly Line follows
**one** of those events (or the selected label’s lineage) from first
proposal to what left the line.

If the method never proposed a span (rules miss, model abstains), the
letter has nothing to click. The sidebar then shows the empty lineage
and gold at the bottom. Do not invent a clickable gold span to start
the tour.

## Why the current map is the wrong object

The S-path answers “which stations exist.” The teaching need is “what
changed on this fact.” Station catalogs, `on · n of m`, and
gold-versus-predicted scorecards belong to the wrong lane. Lenses
helped only when we summarised a rewrite. The rebuild makes that the
whole product: every rewrite, one fact, in order.

## Navbar strip (open, with a default)

It cannot list every fact. It cannot reuse ExECT’s four-family strip
(that is Workbench). It cannot reuse Gan’s five-stage debug strip
(that is a multi-event workbench).

**Default:** a strip of **pipeline bands** that jump in the sidebar.
Not a second inspector.

Proposed bands (same words on both tasks):

1. **Propose** — source span, prompt, model (or rules extract)
2. **Reshape** — parse / flatten / normalise / lenses / repair
3. **Gate** — evidence
4. **Leave** — what left the line, then gold

A band that never touched the selected fact is muted. Clicking a band
scrolls the sidebar to that group. It does not change which fact is
selected.

If the strip still feels like Gan’s five stages after the first letter
is wired, drop it and keep only Case + Method. Do not add family chips
to compensate.

## Data this surface needs

Today’s teaching observations are **stage-global**: one In → Out for
the whole letter. This view needs **fact-keyed** lineage:

- a stable fact id for the run
- the predicted span offsets used to highlight and to click
- the ordered transforms that applied to that id
- the gold unit used only in the last row

Build that lineage from the same executed teaching cases already used
for G1, G3, E1, and E2. Replay only. No live model calls. No locked
rows. Do not retune from these letters.

If a stage cannot be attributed to one fact, it does not appear in
that fact’s sidebar. It must not be faked as a no-op on every fact.

## Scope limits

In:

- `/schematic` only
- the four paper teaching letters
- three methods per letter
- shared letter view with Workbench
- predicted-only highlights
- click-to-select fact
- vertical transform list
- gold only at the bottom
- band strip or Case + Method only

Out:

- the rest of `dev750` / `dev140`
- holdout letters
- Workbench redesign
- F1 chips, family filters, matched-diff cards
- isometric / S-path map
- playback
- a fact picker dropdown as the primary selector (the letter is the
  picker)

## Build order

1. **Fact identity** on the four teaching runs: ids, spans, per-fact
   transform lists. This is the contract. The UI waits on it.
2. **Letter + click** on one ExECT letter (E2 / `EA0057`) and one
   method (hybrid). Predicted highlights only.
3. **Sidebar lineage** for that fact, gold last.
4. **Gan G1** with one candidate event as the fact.
5. **Band strip** once two letters prove the vertical list.
6. Remaining two letters and the other methods.

Do not restyle Workbench along the way. Share the letter component;
do not share the inspector.

## Success

On `EA0057` hybrid, clicking the structural-epilepsy span shows the
diagnosis-lens rewrite in the sidebar and gold only at the bottom.
On `GAN-15431` hybrid, clicking the model’s quiet-interval or cluster
span shows the selected-evidence rewrite, not a list of all repair
families. Workbench still answers whether those facts match gold.
