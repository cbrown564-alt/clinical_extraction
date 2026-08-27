# Protocol: hybrid rescue source provenance

Date: 2026-08-13
Status: predeclared development mechanism study; no model calls

Reports: [hybrid rescue source provenance](hybrid_rescue_source_provenance_2026-08-13.md)
Parents: [Gan stage ablation](../gan2026/hybrid_stage_ablation_2026-08-06.md),
[ExECT stage ablation](../exectv2/hybrid_stage_ablation_2026-08-06.md)
Paper sources: [Gan story](../paper/gan_story_2026-08-10.md),
[ExECT story](../paper/exect_story_2026-08-12.md)

## Primary question

When a deterministic stage first turns a wrong development cell into a correct
one, where did the rescued answer come from?

1. **Render the selected span** — the model already chose the supporting
   quote and the rule only changes label form or concept wording.
2. **Promote a relegated model reading** — another event or mention the
   model emitted already carried the rescued answer, but the model did not
   select it.
3. **Compose from captured events** — Gan clinical or free-interval rules
   build a new label from events the model extracted, without any single
   event already holding that label.
4. **Use a model quote the model did not treat as that answer** — the
   supporting words appear in some model evidence or mention, but not as
   the rescued diagnosis or frequency answer.
5. **Trim the inventory to exact** — ExECT Diagnosis exactness is rescued
   by dropping extra keys, not by adding a concept.
6. **Add from letter text the model never quoted** — the supporting fragment
   is found by scanning the note, and no saved model event or mention quotes
   that fragment.

The essential paper question is how often (6) happens, especially on Gan,
versus how often the lift is (1)–(3).

## Why it matters

Stage ablation already names the first-changer family. It does not say
whether that family normalised the model's own answer, switched to another
model-generated candidate, or introduced a fact the model had not captured.

## Scope

| Item | Value |
| --- | --- |
| Gan split | `dev750` (`validation`); inspection permitted |
| ExECT split | `dev140`; inspection permitted |
| Surface | `llm_with_rules` six-model saved ledgers |
| Gan metric | Purist first-rescue (wrong → correct) |
| ExECT metric | Per-family clinical-headline first-rescue on Diagnosis, SeizureFrequency, Prescription, and Investigations |
| Calls | none |
| Holdout | sealed; no locked-test row inspection |

## Method

1. Replay the same Gan and ExECT no-call stacks used by the 6 Aug stage
   ablations.
2. Keep only first hops that rescue the cell (Gan Purist; each ExECT
   family's own first clinical-headline rescue).
3. Classify each first-rescue with the source classes above, using
   saved model events, selection evidence, and (ExECT) flattened mentions.
   Gan `repair.selected_evidence` is always class (1): that stage only
   rereads the model's selected quote. ExECT Diagnosis keeps the quote
   vs letter-scan split; SF, Prescription, and Investigations use the
   same classes on added vs dropped keys.
4. Keep a small set of already-public development examples per class.
5. Do not write holdout component estimates or claim clinical validity.

## Claim boundary

Development mechanism evidence only. Not holdout attribution. Not a claim
that residual additions or selected-evidence rendering are clinically
correct, only that they change the scored benchmark answer.
