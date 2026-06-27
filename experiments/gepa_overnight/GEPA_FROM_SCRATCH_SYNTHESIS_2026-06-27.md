# DSPy-native GEPA from-scratch — overnight synthesis (2026-06-27)

Question driving the work: *if we do this in a truly DSPy-native way with GEPA at
the core, how far can we get — and can a scoring mechanism stop the prompt from
blowing up?*

## TL;DR

- **Yes, a length penalty in the eval works — but only once it reaches GEPA's
  candidate selection.** A per-example penalty that reads the instruction from
  `pred_trace` fires only in GEPA's *reflective* path, whose score GEPA discards.
  The fix: the program stamps its own instruction/demo token counts onto the
  prediction, so the penalty bites in *every* path, selection included.
- With the working penalty, from-scratch GEPA on **deepseek-reasoner** reached
  **0.833 purist** on validation with a **547-token** evolved instruction — vs the
  un-penalized-selection ablation at **0.822 purist / 1101 tokens**. **Half the
  prompt, slightly better accuracy**, both grown from a **105-token seed**.
- That 0.833 (from a lean, auto-evolved prompt, zero hand-tuning) is on par with /
  edges the hand-tuned DeepSeek prompt (~0.829 on validation). DSPy-native
  from-scratch GEPA is clearly viable for this task.
- Local **Qwen** could not complete overnight on this machine (hardware limits,
  detailed below). Left as a follow-up.

## Results

| Run | Task model | Penalty in selection? | Seed→final instruction (tok) | Purist (val, 718 scorable) | Pragmatic |
| --- | --- | --- | --- | --- | --- |
| Base seed | deepseek-reasoner | n/a | 105 | base valset 0.5715 | — |
| **Feedback-only ablation** | deepseek-reasoner | no (penalty only in feedback) | 105 → **1101** | 0.8217 (590) | 0.862 |
| **Fixed (penalty in selection)** | deepseek-reasoner | **yes** | 105 → **547** | **0.8329 (598)** | 0.865 |
| Qwen (intended) | qwen3.6:35b → 27b → 9b | yes | — | **blocked (hardware)** | — |

Artifacts:
- `experiments/gan2026_gepa_from_scratch_deepseek_reasoner_20260627.{json,md,jsonl,instruction.txt}` (fixed)
- `experiments/gan2026_gepa_from_scratch_deepseek_reasoner_feedbackonly_20260627.{json,md,jsonl,instruction.txt}` (ablation)

## What the length penalty mechanism is

`metric.py` returns `dspy.Prediction(score, feedback)`:
- `score = graded_quality − length_penalty`, clamped to [0,1]. Quality tiers:
  1.0 purist-correct / 0.4 pragmatic-only / 0.1 scorable-but-wrong / 0.0 unscorable.
- `length_penalty` over soft budgets: instruction 600 tok, demos 800, output 1200
  (weights β=0.25/0.25, α=0.10; capped at 0.6).
- `feedback` encodes the clinical failure taxonomy (weekly-band hardest,
  seizure-free-vs-active-frequency, cluster cadence, don't-demote-countable) **and**
  the live token counts vs budget, so reflection is told in words to stay concise.

**Key implementation detail (the bug we found and fixed):** GEPA scores candidates
for selection via plain `dspy.Evaluate` → `metric(example, pred)` — no trace, no
program. So a penalty reading `pred_trace` is invisible during selection (it only
runs in the reflective path, whose differing score GEPA explicitly ignores;
gepa_utils line ~303 warning). The program now stamps `prediction.instruction_tokens`
/ `demo_tokens` at forward time; the metric reads those, so the penalty enters the
aggregate selection score. The 1101→547 token drop is the direct evidence it works.

## What GEPA discovered (evolved 547-token instruction)

From a 105-token seed, GEPA independently re-derived the rules we built by hand:
clusters count as frequency; aggregate dated monthly counts into a rate; prefer
explicit recent frequency over generic "seizure-free"; `unresolved_multiple` when
several seizure types jointly define burden; normalize numbers to digits;
seizure-free only if sustained with no recent countable seizures. The ablation
reached the same idea at ~2x the length (4532 vs 2226 chars) with more redundant
worked examples — i.e. bloat that bought nothing.

## Protocol & provenance

- Trained on the optimizer-only `train` split (287 row_ok of 300); valset = 200 of
  `validation`; final eval on full `validation` (718 row_ok). **test450 never touched.**
- Reflection (teacher) LM = deepseek-reasoner; GEPA budget = medium (~1690 metric
  calls); temperature 0 for the task model.
- Caveat: the 200-row valset GEPA selected on is a subset of the 718-row eval, so
  the reported purist is mildly optimistic vs a fully held-out split. Development
  surface only.

## Qwen: why it didn't complete (hardware, not method)

- **qwen3.6:35b** OOM-killed the driver — needs ~21 GB system RAM, left only ~1.5 GB
  free on this 33.8 GB box; OS kills the python process at model load (happened twice).
- **qwen3.6:27b** fit RAM (~6 GB free) but was far too slow — ~43 s for a trivial
  call at ~27 % GPU offload; a 750-call run would take 12–25 h.
- **qwen3.5:9b** fits with headroom and returns valid JSON in ~1–5 s via *direct*
  ollama calls, but GEPA's threaded eval against the local ollama endpoint **hung**
  (0 % CPU on both python and ollama, log frozen) — the standalone dspy probe worked
  sequentially, so the issue is in the GEPA-eval/litellm↔ollama local path, not the
  model. Stopped to avoid a rabbit hole.

## Follow-ups for the operator

1. **Registry blocker:** `experiments/registry.jsonl` line 63
   (`gan2026_agentic_boundary_audit_prompt_v2_panel`) has a nested dict in
   `primary_metrics` (`evidence_grounded_by_grade`) that fails schema validation and
   blocks *all* registration. GEPA runs wrote artifacts but skipped registry
   registration. Fix line 63 (flatten that field) to re-enable registration.
2. **Qwen GEPA:** re-run on a machine with free RAM (for 35b) or debug the
   litellm↔ollama hang in GEPA's threaded eval (try `num_threads=1` sequential eval
   path / explicit LM timeout), or run a transfer eval of the 547-token prompt on
   local Qwen via the working direct-ollama path.
3. Consider a held-out (disjoint from valset) re-score of the fixed prompt for a
   clean development number, and — only if warranted — a single test450 readout via
   the freeze-warden protocol.
