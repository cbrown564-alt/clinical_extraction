# Why the proposed method is a model plus recorded rules

Date: 2026-08-09  
Revised: 2026-08-13 (prompt-enumeration argument made explicit)  
Revised: 2026-08-19 (proposed method named without Grok or hybrid shorthand)  
Status: representative paper source; author test passed 2026-08-09; enumeration revision writing-test passed 2026-08-14

## The short answer

An epilepsy clinic letter contains linked clinical statements. It can describe
what happened, when it happened, how often it happened, which event the
statement refers to, what treatment was taken, and how those facts relate.
Making this information usable for cohort finding, retrospective or
longitudinal analysis, and future modelling requires structured output that
retains the meaning and source of the clinical statements. These are motivating
research uses, not claims that this system is ready for clinical deployment.

The two project tasks ask different questions. Gan 2026 turns several
possibly true temporal statements into one current seizure-frequency state.
ExECTv2 turns a dense letter into a complete set of phenotype facts. In both,
finding a phrase is not enough: the output must be a designed structured
form. The two public golds are the forms this paper uses for evaluation.

The proposed method uses a model plus recorded rules. The model collects a
structured ledger with quoted letter text. Named rules then shape those
facts into the required form. Those mappings can be replayed on the same
model output without a new call. Written rules and a model alone are
baselines. Rules are not a black box; they capture thinner evidence and
struggle with paraphrase. A recorded rule is not always a free switch.

## The two tasks are hard in different ways

| Task | What the system must do | What makes it difficult |
| --- | --- | --- |
| Gan 2026 | Return one current seizure-frequency label | A letter may contain a usual rate, a recent cluster, a seizure-free interval, a dated total, and historical statements. Several statements can be true while only one satisfies the task's definition of the current answer. Counts, denominators, time windows, and cluster meaning must survive the choice. |
| ExECTv2 | Return a coherent set of diagnoses, seizure-frequency facts, prescriptions, and investigations | A short letter can contain many related facts and attributes. The system must recover the complete set without merging distinct facts, losing repeated or split regimens, omitting a family, or adding an unsupported inference. |

Gan is mainly a selection problem: find the relevant evidence and commit to one
current state. ExECT is mainly an inventory problem: recover all supported facts
and keep their attributes and relationships straight. One architecture is
applied to both, but each task keeps its own schema, clinical policies, and
measure.

## Why the decisions must remain distinguishable

Deterministic rules are useful when the requirement is explicit: normalize a
rate, enforce an allowed label, split a supported medication regimen, reject an
unsupported attribute, or check that quoted evidence occurs in the letter.
They are less suited to every paraphrase, indirect reference, temporal relation,
or densely expressed clinical connection. The retained development analyses
show both strong rule competence and task-specific floors; they do not support
the claim that rules are generally inadequate.

A direct LLM answer can interpret varied language and relations, but the final
answer can hide which statement was selected, how uncertainty was handled, or
whether a later formatting step changed clinical meaning. Exact quoted evidence
does not by itself prove that the right evidence was chosen. The retained
development cases include model answers that are well formed and grounded in a
real span but still disagree with the task's selected answer.

The gap is therefore not simply “rules versus models.” Either can find evidence,
construct a representation, make a task decision, or change clinical meaning.
The proposed method uses the model to collect a rich ledger, then uses named
rules to shape that ledger into a designed form. A collapsed model-only
answer hides those mappings. Exact quoted evidence does not by itself prove
that the right evidence was chosen.

## Why those controls do not belong in the prompt

A direct-LLM alternative is to write every normalisation, selection, and
rendering rule into the prompt. In principle the list is finite. On Gan
development gold alone it is already large: 45 render templates, 333 distinct
labels, and 852 distinct official source phrases, with the gold string itself
present in the official reference on only 11 of 1,050 rows. One ordinary
label, `1 per day`, is licensed by 42 different official phrases. The
[Gan phrase-variant inventory](gan_gold_phrase_variants_2026-08-13.md) is the
worked list, with a
[row workbook](../artifacts/gan_gold_phrase_variants_2026-08-13.xlsx).

ExECT is the same shape on a different task. On `dev140` four-family gold
there are 31 templates, 288 distinct keys, and 335 official source spans,
with the scored key itself present in the official span on only 3 of 934
mentions. Diagnosis `epilepsy` has seven official surfaces; `MRI abnormal`
is licensed by `MRI`, `MRI scan`, `MRI brain`, and a dated infarct line;
seventy SF mentions are type tokens whose scored state lives elsewhere.
Listing those aliases still would not specify which facts to keep, drop,
or split. The
[ExECT phrase-variant inventory](exect_gold_phrase_variants_2026-08-13.md)
is the worked list, with a
[mention workbook](../artifacts/exect_gold_phrase_variants_2026-08-13.xlsx).

Putting that list in the prompt would fail in three ways.

1. **Cost.** Most of the list is idle on any one letter. Carrying it on every
   call spends tokens and latency on unused constructions.
2. **Interference.** A simple “once a week” letter then sits beside cluster
   grammar, diary aggregation, date arithmetic, and abstention policy. The
   model is invited to do complicated work on an ordinary rate.
3. **Opacity.** A later change to what `monthly` means, or to when a countable
   phrase should still be `unknown`, becomes a wording edit in a long prompt
   rather than a named, replayable stage.

On ExECT a fourth failure appears even if the alias list were complete: the
prompt still would not say which facts to keep, drop, or split.

The model still has to read paraphrases, indirect references, and relations
that no list will finish. The staged-method argument is not that language can
be replaced by rules. It is that the closed output dialect, winner or inventory
policy, and later mappings should have named owners rather than be re-derived
or hidden inside generated prose on every letter.

The cited ExECT row uses inventory extract (`exect_llm_extract`) with
rule encode and rule select (cell 3). Compact ledger is a historical
ablation: the same one-call hybrid written in ordinary language,
without the example zoo and without the non-seizure-frequency encoding
rules ([Decision 0058](../../decisions/0058-compact-ledger-is-the-paper-cited-exect-hybrid.md)).
Full ledger remains the longer control book.

## The implemented response

The proposed method divides the work:

1. The model interprets flexible clinical language, proposes structured events
   or findings, and quotes supporting letter text.
2. Task-specific recorded rules normalize the proposal, apply selection or
   inventory policies, check that the quote is in the letter, and render the
   required form.
3. The recorded object keeps the source span, the named rule that changed it,
   the submitted answer, and the score.

On Gan the model also makes the first selection; rules can later change it.
This division does not make every decision correct. Direct-model paths collapse
decisions that the recorded trace can separate. A named rule is not always a
free switch. Performance must still be presented as two parallel task stories
because the tasks use different targets and measures. Tables cite Grok 4.6 so
the story stays on the method. Gemini is in the same band where cells exist.

## Evidence and limits

This brief uses both evidence lanes defined in the
[paper-evidence exploration brief](evidence_exploration_brief_2026-08-09.md#two-evidence-lanes).

- **Literature and dataset lane:**
  [why narrative letters are a research problem](why_narrative_letters_are_a_research_problem_2026-08-17.md)
  owns the opening motivation;
  [what prior extraction approaches already did](what_prior_extraction_approaches_already_did_2026-08-17.md)
  owns the related-work location of prior systems;
  [what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md)
  and the [task-shape framework](../shared/task_shape_framework_2026-08-06.md)
  own the task definitions and label or ambiguity limits. The
  [Gan phrase-variant inventory](gan_gold_phrase_variants_2026-08-13.md)
  and the [ExECT phrase-variant inventory](exect_gold_phrase_variants_2026-08-13.md)
  own the development-gold input dialects and the prompt-enumeration
  argument. This brief does not claim novelty over those prior systems
  or evidence of real-world use.
- **Project, system, and experimental lane:** [system architecture](../../canon/01_system_architecture.md),
  [pipeline ownership](../../canon/02_pipeline_steps.md), the
  [cross-task mechanism synthesis](../shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md),
  and [paper provenance](../../canon/10_paper_provenance.md) support the
  description of this implementation and its bounded development behaviour.

The strength of paper claims remains with
[paper provenance](../../canon/10_paper_provenance.md). This brief does not establish
state of the art, a universal advantage for hybrid systems, absolute clinical
truth, clinical validation, or deployment readiness.

## Later writing test

**Question:** can the user obtain a concise, qualified explanation of why the
proposed method is a model plus recorded rules, and what that record keeps?

**Success:** without returning to a large report, the user can locate the two
task difficulties, see why the gold dialect should not live only in a prompt,
name the source span and the change log, preserve the claim limits, and use
the explanation while writing.

**Result:** passed 2026-08-09 for the original brief. The 2026-08-13
enumeration section passed a writing-test on 2026-08-14: the two task
difficulties, the model versus rules jobs, the three prompt-enumeration
costs plus ExECT set assembly, and the claim limits are all locatable
here without reopening a large report. Worked phrase lists stay in the
linked inventories.
