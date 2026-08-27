# 0015: Prompts use task language, not project jargon

Date: 2026-06-07
Status: accepted

Text read by a model must brief a capable reader who knows the clinical task but
has never seen this repository. Prompt docstrings, field descriptions, and JSON
instructions must state the required action directly.

Avoid project-only terms such as pipeline stage names, component ownership,
ablation, benchmark-facing output, or downstream processing when the model does
not need them. For example, say “return one complete final answer; nothing will
revise it” instead of describing internal extraction and formatting steps.

This rule prevents prompts from adding irrelevant instructions and stops models
from echoing project terminology into rationales. It applies only to model-facing
text; human code comments may use exact software terms when they help.

`tests/test_gan2026_llm_prompt_hygiene.py` checks known jargon leaks. Extend the
shared list when a new recurring term appears.

See also [decision 0053](0053-gan-structured-events-final-prompt.md): the
Gan structured-events `final` payload drops remaining envelope identity
(`Gan 2026 LLM-only…`, `prompt_version`, `source_row_index`) from the
model-facing JSON.

See also [decision 0054](0054-model-request-order-and-metadata-are-explicit.md):
framework-generated system text, serialization order, and research metadata are
part of the effective prompt and must be reviewed in the rendered request.
