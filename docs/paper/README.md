# Paper keep-set

Current owners for the final paper. Campaign reports and numbered
decisions are not current.

## Central argument

The proposed method translates clinic letters into structured clinical
facts in a designed form, with quoted source text. A model collects the
facts and evidence. Recorded rules then shape those facts into the
required form. Those mappings can be replayed on the same model output
without a new call.

The two public golds are the forms used for evaluation. They are not
the task. Gan's evaluation form is one current seizure-frequency state.
ExECT's is a complete four-family fact inventory. Written rules and a
model alone are baselines. Tables cite one model, Gemini 3.7 Flash, so
the story stays on the method. Grok, Luna, DeepSeek, Qwen, and Gemma
are companion rows. Later-stage LLM encode and LLM select calls are
Gemini only.

The paper claims visibility for the recorded object: the source span,
the later rule changes, and the submitted answer. It does not claim
access to a model's internal reasoning, or that a visible step is
clinically correct.

Headline tables: five role rows (rules, LLM, or both at find /
encode / select). The cited score is the select stop. The six-model
row is cell 3 (LLM find, rules encode, rules select) on both
tasks. On ExECT, cell 3 is the Gemini peak and the roster row; all
five rows use 4-family micro F1 (`clinical_inventory_unit_keys`).
Gemini thinking and the source-near Gan find are ablations. Gan
LLM find is `gan_llm_extract`; ExECT LLM find is
`exect_llm_extract`. ExECT LLM encode is a second later-stage call.
See
[methods](sections/methods.md),
[Gan five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md),
[ExECT inventory grid](../research/exectv2/exect_both_extract_on_inventory_protocol_2026-08-23.md),
[six-model roster](../research/paper/three_variables_rules_model_thinking_2026-08-23.md)
(Gan `gan_llm_extract` rungs and ExECT inventory extract),
and
[ExECT cell 4](../research/exectv2/exect_rule_select_after_llm_encode_2026-08-22.md).
`gan_llm_only` is not a results column. Full ledger is the only
comparator when cited—not a headline method.

| File | Job |
| --- | --- |
| [methods](sections/methods.md) | Proposed method, baselines, roster, splits, scorers |
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
| [results](sections/results.md) | Gan-only dissertation results draft, including the inventory feasibility panel |
| [lineage](lineage.md) | How the living requests were reached and what kind of method change each revision made |
| [decisions](decisions/) | Current decisions |
| [Gan is the dissertation paper](decisions/gan-is-the-dissertation-paper.md) | Dissertation cites Gan only; ExECT is a later paper; inventory feasibility is descriptive |
| [Gan inventory feasibility](../research/gan2026/gan_inventory_feasibility_dev750_n100_2026-08-28.md) | Descriptive 100-letter `dev750` inventory panel; not an accuracy table |
| [living comparison contract](decisions/living-comparison-contract.md) | Envelope, stage stops, forbidden living names |
| [source library](../research/paper/) | Writing sources |
| [paper experiments](../../paper_experiments/README.md) | Replayable cells |
| [cells and runners](cells_and_runners.md) | Live runner names mapped onto the five cells |
| [architecture](architecture.md) | Find / encode / select and rule authority |
| [Gan find prompt template](../../paper/supporting%20materials/gan_llm_extract_prompt_template.json) | Frozen `gan_llm_extract` request without `note_text` |
| [decision history](../history/decisions.md) | Closed numbered series |
