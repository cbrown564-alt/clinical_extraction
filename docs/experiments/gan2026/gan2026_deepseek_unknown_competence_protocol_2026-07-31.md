# DeepSeek unknown-competence protocol

Date: 2026-07-31  
Status: open thread; Phase 2 candidate U **stopped (negative)** on UNK-slice pilot; full-750 aborted; local route still deferred  
Thread owner: [thread note](../../research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md)  
Baseline artifact: [dev750 unknown-slice baseline](../../../experiments/gan2026_deepseek_unknown_competence_baseline_dev750_20260731.json)  
Phase 2 draft: [unknown prompt draft notes](gan2026_deepseek_unknown_prompt_draft_notes_2026-07-31.md)  
Phase 2 run: [A/U dev750 protocol](gan2026_deepseek_unknown_prompt_dev750_protocol_2026-07-31.md)

## Primary question

On Gan `validation750`, can **local DeepSeek** reach collaboration-grade
unknown handling for both required product arms — **LLM-only** and
**LLM-with-rules** — without a rules-only arm, without inspecting sealed
`test450` rows, and without tuning on the author's Real(300) patient letters?

Design aim: Real(300)-like unknown-heavy clinic letters (~54% UNK in the Gan
paper test set). Tuning and selection stay on permitted development data only.

## Why this thread exists

- Collaboration constraint: DeepSeek on the partner's own servers; deliver
  LLM-only and LLM-with-rules only (no rules-only).
- Retained six-model DeepSeek is hosted **V4 Flash API**, not a local route.
- On synthetic `dev750`, DeepSeek LLM-only unknown-band F1 is ~0.70 and
  LLM-with-rules ~0.81–0.83 — below stronger hybrid models and below a
  conservative collaboration bar for an unknown-heavy real set.
- Synthetic Purist UNK prevalence (~23%) understates Real(300) (~54%).

## Fixed conditions

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 synthetic clinical letters |
| Split | `validation750` (`dev750`); row inspection permitted |
| Locked | `test450` sealed; Real(300) not for tuning or iterative repair |
| Scorer | Gan Purist primary; Pragmatic secondary |
| Prompt comparator | `gan2026_hybrid_structured_events_v0.5` |
| Rules comparator | Final `hybrid_full_stack` (2026-07-31) |
| Product arms | `llm_only`, `llm_with_rules` only |
| Model scope | **Active tuning route:** hosted DeepSeek V4 Flash (same family as retained matched panel). **Deferred (~weeks):** partner local DeepSeek — re-smoke under this protocol before Real(300), do not block hosted Phase 2–3 |
| Out of scope | Rules-only product arm; ExECT unknown transfer; sealed-row tuning |

## Unknown-slice definitions

Purist **UNK band** = gold monthly frequency sentinel `1000.0` /
`seizure_freq_unknown` (includes scored `unknown`, `no seizure frequency
reference`, and vague multiples that map to the sentinel).

| Metric | Definition |
| --- | --- |
| UNK precision / recall / F1 | Predicted UNK band vs gold UNK band |
| UNK accuracy | Correct UNK-band predictions / gold UNK count |
| Over-read rate | Gold UNK and predicted band is a non-zero active rate |
| False seizure-free rate | Gold UNK and predicted band is `currently_no_seizure` |
| False abstention rate | Gold non-UNK countable/zero band and predicted UNK band |

Report all five for both arms. Do not treat Purist-correct sentinel matches
on vague `multiple …` strings as clinical abstention quality without noting
the scorer collapse.

## Collaboration gates (development stop criteria)

Clear hosted development for a later local re-smoke / Real(300) freeze only if
**hosted** DeepSeek V4 Flash meets all of:

1. **LLM-with-rules:** UNK accuracy ≥ 0.90, over-read ≤ 0.05, false SF ≤ 0.03.
2. **LLM-only:** UNK accuracy ≥ 0.80, over-read ≤ 0.05.
3. **Non-damage:** on gold non-UNK rows, net Purist Δ from the Phase 0
   comparator ≥ 0, or any loss is predeclared and smaller than the unknown
   gain under the study's accounting.
4. **False abstention** does not rise enough to erase countable-rate wins
   (report explicitly; reject if rate→unknown / vague-`multiple` regressions
   dominate).

Passing hosted gates does **not** equal local or Real(300) evidence. Local
parity remains mandatory before author Real(300) runs.

## Phased work

### Phase 0 — Baseline (complete)

No-call unknown-slice metrics on retained DeepSeek matched v0.5 `dev750`
traces for LLM-only (model boundary) and LLM-with-rules (frozen panel final
and final-ruleset replay proxy). Hosted V4 Flash. Gates fail — candidate work
authorized on this route.

### Phase 1 — Local route parity (deferred ~weeks)

Partner local DeepSeek is not available yet. Do not block hosted Phase 2–3.
When the local runtime arrives: name model id, structured-output repair
([decision 0042](../../decisions/0042-shared-local-model-structured-output-repair.md)),
and re-score the winning hosted candidate on `dev750` before Real(300).

### Phase 2 — LLM-only unknown selection (active; hosted)

One prompt/selection candidate on hosted DeepSeek V4 Flash aimed at false
seizure-free on unclear quiet intervals, invented rates on incomplete evidence,
and collapse of clear counts into vague `multiple` labels. Audited with
`$plain-language-prompt-auditor`. Comparator: Phase 0 hosted LLM-only (v0.5).
Requires a predeclared hosted DeepSeek call campaign on `dev750` only.

### Phase 3 — Unknown-preserving rules gates (secondary)

Only if LLM-only still fails gates or LLM-with-rules over-read stays high.
Narrow anti-over-projection / false-SF gates with C→W accounting. Does not
reopen broad hybrid tuning; any accepted gate is a named additive candidate.

### Phase 4 — Local re-smoke, then freeze for Real(300)

After hosted gates pass (or a negative stop), re-smoke the selected candidate
on local DeepSeek when available. Only then write a frozen Real(300)
evaluation protocol with the author. No iterative repair from Real(300).

## Stop rule

- **Answer (hosted):** both arms meet collaboration gates on hosted DeepSeek
  `dev750`.
- **Answer (deploy-ready):** hosted answer plus local re-smoke within the same
  gates (or a predeclared local delta bound).
- **Negative:** hosted DeepSeek cannot meet LLM-only gates after one prompt
  cycle and one optional rules-gate cycle.
- **Revise:** metrics show false abstention / vague-`multiple` tradeoff needs a
  different component.
- **Reject:** any use of `test450` rows or Real(300) for candidate tuning.
- **Blocked (local only):** partner local runtime unavailable — does not block
  hosted Phase 2–3.

## Artifact schema

Machine artifact rows or summary must record:

- date, commit or dirty-tree note, model id, route (hosted vs local);
- prompt version, repair policy, arm (`llm_only` / `llm_with_rules`);
- split, scorer, gold UNK denominator;
- UNK P/R/F1, UNK accuracy, over-read, false SF, false abstention;
- overall Purist / Pragmatic;
- claim boundary.

## Claim boundary

Development unknown-competence evidence for named DeepSeek routes and the two
product arms. Not Real(300) performance, not clinical validation, not
six-model ranking, not ExECT transfer, and not authorization to inspect
sealed holdout rows.
