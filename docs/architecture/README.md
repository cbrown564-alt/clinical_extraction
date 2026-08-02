<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Architecture: how a record moves through each method

This directory answers one question: what happens to a letter, stage by stage, in each of the six selected task-method pairs, and who owns each change. It was built to close the gaps reported in the [pipeline understandability review](../reviews/pipeline-understandability-review-2026-07-30.md).

Everything here is generated from the stage manifests in `src/clinical_extraction/architecture/manifests/` and from teaching cases that execute the real pipelines. Do not edit these files by hand - change the manifest or the code, then run `python scripts/build_architecture_docs.py`.

## Start here

1. [Two tasks x three methods](diagrams/overview.md) - the whole system on one page.
2. [Ownership matrix](diagrams/ownership_matrix.md) - who may change a clinical answer, everywhere.
3. A method card below, for the method you need.
4. The teaching case for that task, to see a real letter move through it.

## Method cards

| Task | Method | One sentence | Card |
| --- | --- | --- | --- |
| Gan 2026 | Rules only | Deterministic rules find every seizure-frequency statement in the letter, normalize them, pick one as the current answer, and render it as a Gan label. | [card](method_cards/gan2026_rules_only.md) |
| Gan 2026 | LLM only | One model call reads the letter and returns the final Gan label directly; deterministic code then repairs, validates, and scores that answer. | [card](method_cards/gan2026_llm_only.md) |
| Gan 2026 | LLM with rules | The model extracts the event history and chooses an answer; deterministic rules then check and sometimes correct that answer. | [card](method_cards/gan2026_llm_with_rules.md) |
| ExECTv2 | Rules only | Nine independent deterministic extractors produce the all-nine prediction, while an explicit four-family projection defines the primary model comparison. | [card](method_cards/exectv2_rules_only.md) |
| ExECTv2 | LLM only | One structured model call proposes four-family findings, and the selected LLM-only view scores those findings without the hybrid family lenses. | [card](method_cards/exectv2_llm_only.md) |
| ExECTv2 | LLM with rules | The model proposes findings for four families in one call; deterministic family transforms reconcile those findings into the final scored representation. | [card](method_cards/exectv2_llm_with_rules.md) |

## Teaching cases

- [Gan 2026](teaching_cases/gan2026.md) - one letter where the model selects the wrong competing rate and the deterministic layer rescues it.
- [ExECTv2](teaching_cases/exectv2.md) - one ordinary letter through all three methods, showing the four-family versus nine-entity comparison boundary.

## Diagrams

- [Overview](diagrams/overview.md)
- [Ownership matrix](diagrams/ownership_matrix.md)
- [Gan LLM-with-rules stages](diagrams/gan2026_llm_with_rules_stages.md)
- [ExECT LLM-with-rules stages](diagrams/exectv2_llm_with_rules_stages.md)
- [Result attribution origins](diagrams/attribution_origins.md)

## What this layer does not own

Scores, claim strength, and evidence freshness are owned elsewhere: `PROJECT_STATUS.md` for current evidence, `docs/canon/` for governing claims, and `docs/plans/ACTIVE_ROADMAP.md` for sequence. This layer explains mechanism only, and links to those owners rather than restating them.
