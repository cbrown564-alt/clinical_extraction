# Paper keep-set

Current owners for the final paper. Campaign reports and numbered
decisions are not current.

## Central argument

The dissertation cites Gan 2026 only
([Gan is the dissertation paper](decisions/gan-is-the-dissertation-paper.md)).
The paper story is fixed by
[paper-story simplification](decisions/paper-story-simplification.md):
one Gan manuscript, one shared LLM evidence record, two ways to
decide, a small mechanism table, and tight claim language.

The pipeline has two paper-facing stages. **Extract** is one LLM call
that returns every candidate seizure-frequency event with its exact
quoted span, category, and canonical label, plus a provisional answer.
**Decide** applies a fixed policy to that record, never the letter, and
is performed in two ways on the same saved record: recorded rules
(**Hybrid**) or a second LLM call (**LLM-only**). Because decide is
replayed from the saved record, the two executors form a paired
comparison. Implementation names (`find`, `encode`, `select`) are
historical and appear only where they identify an artifact. LLM calls
are LLM calls, not agents; the system is a fixed sequence, not agentic.

Primary claim: a bounded comparison with the previously reported
fine-tuned benchmark on a different held-out sample of the same
synthetic corpus (Hybrid 0.86, LLM-only 0.85, benchmark 0.81 Purist).
Not paired, not state of the art, not deployment. Secondary
contribution: extract-then-decide, with the provisional answer (0.79)
as the one-prompt baseline and three extraction-prompt ablations
(examples, closed allowed-label forms, evidence obligation) as the
mechanism table. Rules-only, the five-cell grid, source-near, Holgate,
extra LLM encode/select, and the one-call prompt stay repository
evidence and supporting-material secondary rows, not paper rows.

The paper claims visibility for the recorded object: the source span,
the later rule changes, and the submitted answer. It does not claim
access to a model's internal reasoning, or that a visible step is
clinically correct. Local models show technical feasibility on
synthetic data only.

Tables cite one model, Gemini 3.7 Flash, so the story stays on the
method. Grok, Luna, DeepSeek, Qwen, and Gemma are the six-model
extraction-call comparison with compact contract adherence. The
second-call decide, prompt ablations, thinking, and temperature are
Gemini only. Cited Gan extraction is `gan_llm_extract`, which already
writes codebook form. See
[methods](sections/methods.md), [results](sections/results.md),
[Gan five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md)
(secondary), and
[six-model roster](../research/paper/three_variables_rules_model_thinking_2026-08-23.md).
`gan_llm_only` is not a results column. ExECT owners below are
later-paper evidence.

| File | Job |
| --- | --- |
| [methods](sections/methods.md) | Gan-only method: two stages, interface contract, two decision executors, prompt ingredients, splits, scorers |
| [introduction](sections/introduction.md) | Gan-only introduction draft matching FES Section I |
| [literature review](sections/literature_review.md) | Gan-only review draft matching FES Section II |
| [manuscript](../../paper/draft/FES.tex) | The dissertation draft; [supporting materials](../../paper/supporting%20materials/Supporting%20materials.tex) hold moved detail |
| [directional evidence protocol](../research/gan2026/gan_directional_evidence_adjudication_dev750_protocol_2026-09-02.md) | `dev750` reference-exactness and semantic-sufficiency study; drafted, adjudication not started |
| [experiment environment](experiment_environment.md) | Mac mini orchestration + Dell XPS 16 local serving; hosted accelerators undisclosed |
| [hardware](hardware_details.md) | Dated local-device snapshot for Qwen/Gemma |
| [method × stage](method_x_stage.md) | Plain-language method × stage grid, with one Gan and one ExECT development example |
| [Gan rules and models](../research/paper/gan_rules_and_llms_across_stages_2026-08-21.md) | Gemini Gan reading: roles, order, encode/select lift |
| [Three variables](../research/paper/three_variables_rules_model_thinking_2026-08-23.md) | Draft results: stage ownership, model, thinking; temperature 0/1 ablation |
| [Source-near vs bundled encode](../research/paper/gan_source_near_vs_bundled_encode_2026-08-23.md) | Draft Gan ablation: codebook request vs second encode call |
| [Find then Select vs find-and-select](../research/paper/exect_extract_vs_extract_and_select_2026-08-25.md) | Draft ExECT ablation: inventory find vs one-call filter |
| [Gan five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md) | Cited Gemini frequency five-cell totals |
| [ExECT inventory grid](../research/exectv2/exect_both_extract_on_inventory_protocol_2026-08-23.md) | Cited Gemini ExECT five-cell grid (4-family micro F1; cell 3 peak). Replay: [`paper_experiments/exect/five_cell_grid/`](../../paper_experiments/exect/five_cell_grid/) |
| [ExECT cell 4](../research/exectv2/exect_rule_select_after_llm_encode_2026-08-22.md) | Cited Gemini inventory LLM / LLM / rules stop |
| [rule catalogue](rule_catalogue.md) | Named find / encode / select rules on both tasks |
| [claims](claims.md) | Repository evidence reading; stale as a dissertation claim list |
| [results](sections/results.md) | Gan-only dissertation results draft: two executors, class table, three prompt ablations, six-model roster; inventory panel is supporting material |
| [lineage](lineage.md) | How the living requests were reached and what kind of method change each revision made |
| [decisions](decisions/) | Current decisions |
| [Gan is the dissertation paper](decisions/gan-is-the-dissertation-paper.md) | Dissertation cites Gan only; ExECT is a later paper; inventory feasibility is descriptive |
| [Paper-story simplification](decisions/paper-story-simplification.md) | Two decision executors on a shared extract; Rules-only leaves the paper; mechanism and claim bounds |
| [Gan inventory feasibility](../research/gan2026/gan_inventory_feasibility_dev750_n100_2026-08-28.md) | Descriptive 100-letter `dev750` inventory panel; not an accuracy table |
| [living comparison contract](decisions/living-comparison-contract.md) | Envelope, stage stops, forbidden living names |
| [source library](../research/paper/) | Writing sources |
| [paper experiments](../../paper_experiments/README.md) | Replayable cells |
| [cells and runners](cells_and_runners.md) | Live runner names mapped onto the five cells |
| [architecture](architecture.md) | Implementation stages (find / encode / select) and rule authority; paper names are extract / decide |
| [Gan find prompt template](../../paper/supporting%20materials/gan_llm_extract_prompt_template.json) | Frozen `gan_llm_extract` request without `note_text` |
| [decision history](../history/decisions.md) | Closed numbered series |
