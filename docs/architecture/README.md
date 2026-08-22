<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Architecture: how a record moves through each method

This directory answers one question: what happens to a letter, stage by stage, in each of the six implemented task-method runners, and who owns each change. These runners explain mechanism only; they are not the paper's five-cell headline table. For cited methods, scores, and claims see [docs/paper/methods.md](../paper/methods.md).

Everything here is generated from the stage manifests in `src/clinical_extraction/architecture/manifests/` and from teaching cases that execute the real pipelines. Do not edit these files by hand - change the manifest or the code, then run `python scripts/build_architecture_docs.py`.

## Start here

1. [Two tasks x three implemented runners](diagrams/overview.md) - the whole system on one page.
2. [Four-letter teaching walkthrough](teaching_cases/six_paths.md) - one continuous reading order across the paper flagship letters.
3. [Ownership matrix](diagrams/ownership_matrix.md) - who may change a clinical answer, everywhere.
4. A method card below, for the method you need.
5. A teaching letter for that task, to see a development letter move through it.

## Method cards

| Task | Method | One sentence | Card |
| --- | --- | --- | --- |
| Gan 2026 | Rules only | Deterministic rules find every seizure-frequency statement in the letter, normalize them, pick one as the current answer, and render it as a Gan label. | [card](method_cards/gan2026_rules_only.md) |
| Gan 2026 | LLM only | One model call reads the letter and returns the final Gan label directly; deterministic code then repairs, validates, and scores that answer. | [card](method_cards/gan2026_llm_only.md) |
| Gan 2026 | LLM with rules | The model extracts the event history and chooses an answer; deterministic rules then check and sometimes correct that answer. This is the source-near wording ablation; the cited Gan extract is gan_llm_extract_label_forms. | [card](method_cards/gan2026_llm_with_rules.md) |
| ExECTv2 | Rules only | Nine independent deterministic extractors produce the all-nine prediction, while an explicit four-family projection defines the primary model comparison. | [card](method_cards/exectv2_rules_only.md) |
| ExECTv2 | LLM only | ExECT LLM only: one model call on the note proposes four-family findings, and the raw-candidate view scores those findings without family repair. | [card](method_cards/exectv2_llm_only.md) |
| ExECTv2 | LLM pre-post | ExECT LLM pre-post: the model proposes findings for four families in one request; deterministic family transforms and named Select rules reconcile those findings into the scored representation (hybrid F1). This is the both-extract row; the paper's cited select stop uses later-stage encode/select per docs/paper/methods.md. | [card](method_cards/exectv2_llm_pre_post.md) |

## Teaching cases

- [Four-letter walkthrough](teaching_cases/six_paths.md) - the supervisor reading order for G1, G3, E1, and E2.
- [Gan 2026 letters](teaching_cases/gan2026.md) - quiet-interval versus cluster grammar, and qualitative frequent versus unknown.
- [ExECTv2 letters](teaching_cases/exectv2.md) - four-family named windows, and epileptic versus dissociative rates.

- [`GAN-15431`](teaching_cases/gan-15431.md) - Quiet interval and cluster grammar compete; this Grok replay does not assemble the two-part gold.
- [`GAN-2166`](teaching_cases/gan-2166.md) - Qualitative 'frequent' has no countable rate; gold is unknown.
- [`EA0186`](teaching_cases/ea0186.md) - All four families are present; seizure-frequency windows must stay named, not become a monthly rate.
- [`EA0057`](teaching_cases/ea0057.md) - Epileptic and dissociative diagnoses share the letter; rates must stay attached to the right one.

## Diagrams

- [Overview](diagrams/overview.md)
- [Ownership matrix](diagrams/ownership_matrix.md)
- [Gan LLM-with-rules stages](diagrams/gan2026_llm_with_rules_stages.md)
- [ExECT LLM pre-post stages](diagrams/exectv2_llm_pre_post_stages.md)
- [Result attribution origins](diagrams/attribution_origins.md)

## What this layer does not own

Scores, claim strength, and evidence freshness are owned elsewhere: `PROJECT_STATUS.md` for current evidence and `docs/paper/` for methods and claims. This layer explains mechanism only, and links to those owners rather than restating them.
