# ExECTv2 All-Entity Scoring Mechanics Deep Dive

Date: 2026-06-12

Status: diagnostic checkpoint read, not a frozen audit conclusion. The active
`exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612` process was
still running when this was written; the report file on disk was a checkpoint,
not the final 200-letter report.

## Trigger

The latest all-entity LLM-only checkpoint reported semantic F1 low enough to
suggest a mechanics problem:

- 60 rows completed (`EA0001` through `EA0060`)
- semantic per-item F1: `0.0938` (`TP=52 FP=384 FN=621`)
- semantic per-letter F1: `0.2493` (`TP=43 FP=30 FN=229`)
- phrase-only per-item F1: `0.1858` (`TP=103 FP=333 FN=570`)
- phrase-only per-letter F1: `0.4312` (`TP=83 FP=30 FN=189`)
- evidence-invalid drops: `20` mentions; evidence validity remains high enough
  that evidence gating is not the dominant explanation

The first artifact-level problem is procedural: the `.md` file looked like a
finished `full200` audit report while it only summarized the current checkpoint.
The runner loads `load_letters()` correctly; the misleading part is the
checkpoint report path, not the corpus loader.

## Mechanics Trace

The scorer computes an exact multiset match per letter. A predicted mention only
counts when this key matches a gold mention:

```text
entity + normalize_phrase(text) + exact non-ignored attribute set
```

Overall F1 micro-averages the per-entity item counts and per-letter entity
presence cells. Semantic scoring drops `CUI` and ignores `CUIPhrase`; benchmark
scoring keeps `CUI`. For SeizureFrequency only, `Certainty` and `Negation` are
also ignored.

This means the all-entity LLM can clinically find the right fact and still score
zero if it emits:

- a full clause instead of the benchmark's short phrase
- a source-near medication phrase instead of the gold phrase basis
- the right attribute family but with a casing or canonicalization mismatch
- a partial attribute bundle
- a correct mention under the wrong ExECT entity boundary

## Checkpoint Failure Ladder

Per-entity same-entity overlap shows that many misses are phrase/projection
misses before they are clinical misses:

| Entity | Gold | Pred | Exact semantic TP | Phrase TP | Substring-overlap extra |
| --- | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 18 | 11 | 0 | 4 | 6 |
| Diagnosis | 180 | 71 | 18 | 27 | 24 |
| EpilepsyCause | 13 | 6 | 0 | 1 | 3 |
| Investigations | 63 | 71 | 26 | 28 | 30 |
| Onset | 11 | 16 | 0 | 0 | 3 |
| PatientHistory | 211 | 91 | 1 | 2 | 35 |
| Prescription | 98 | 111 | 6 | 38 | 44 |
| SeizureFrequency | 78 | 59 | 1 | 3 | 33 |
| WhenDiagnosed | 1 | 0 | 0 | 0 | 0 |

Interpretation:

- Diagnosis and Investigations have real signal; exact F1 is suppressed by
  phrase span and a smaller number of missing attributes.
- Prescription is the loudest projection mismatch: phrase-only finds 38 matches,
  but semantic exact gets only 6. The LLM often emits `Lamotrigine 200mg bd`
  while gold text is often broader or differently canonicalized, and `DrugName`
  casing/canonicalization then breaks exact attributes.
- SeizureFrequency is mostly a phrase-span failure in this all-entity prompt.
  The model frequently puts the frequency phrase or an anaphoric clause in
  `text` instead of the seizure-type anchor.
- PatientHistory is probably a true entity-boundary and phrase-basis problem:
  the LLM emits narrative event spans, while gold tends to use compact concept
  phrases.

## Candidate Mechanics Problems

### 1. Checkpoint artifact looks final

The active runner writes the final-shaped markdown path during progress
checkpoints. If interrupted or inspected mid-run, `full200` appears to have only
50 or 60 letters.

Recommended fix: write checkpoints to a separate suffix such as
`*_checkpoint.md` or include a large banner in checkpoint reports:

```text
CHECKPOINT ONLY: processed N / 200 letters
```

This is a reporting reliability fix, not a scoring-policy change.

### 2. The all-entity prompt has one `text` instruction for nine phrase bases

The current prompt says `text` is "the short phrase in the letter naming the
finding." That is too generic. ExECT phrase basis differs by entity:

- SF: seizure-type anchor only; frequency belongs in attributes
- Diagnosis: compact diagnostic phrase
- Investigations: test phrase such as EEG/MRI/CT, not the result phrase
- Prescription: likely medication concept or a policy-decided medication span,
  with dose/frequency in attributes
- PatientHistory: compact clinical concept, not the full historical clause
- Onset/WhenDiagnosed: the phrase often names the condition while attributes
  carry the age/date

Recommended fix: add entity-specific `text_target` guidance and examples before
another audit. This stays LLM-only because the model still owns the clinical
selection; deterministic code is only clarifying the requested output contract.

### 3. Some projection normalization is semantically neutral and should be shared

Several current misses are surface/canonicalization issues, not clinical
judgment:

- `DrugName`: `Levetiracetam` vs `levetiracetam`
- `DoseUnit`: stable lowercase
- whitespace, hyphen, tab, and quote normalization
- medication frequency aliases already partly handled by closed vocab

Recommended fix: define a strictly format-preserving normalization layer for
attribute values before scoring, with tests that gold-vs-gold stays perfect and
the layer cannot invent missing attributes.

Do not use this layer to add absent `Certainty`, `DiagCategory`, `CUI`, dates, or
frequency values. Those are prediction-bearing.

### 4. Phrase projection needs a policy split, not one global fuzzy scorer

Substring overlap suggests a tempting metric change, but a global substring
matcher would be too lenient and would make false positives look correct.

Safer alternatives:

- official score remains exact
- add a diagnostic "source-near phrase overlap" ladder
- add entity-specific scorer-facing projection only where the phrase basis is
  already policy-decided and deterministic from the model's selected text
- require a before/after audit table: exact semantic, phrase-only, source-near
  overlap, and attribute-on-overlap

This preserves benchmark comparability while exposing whether the model is close.

### 5. CUI remains a benchmark-gating item

The with-CUI benchmark score is structurally zero for LLM-only unless a shared
phrase-to-CUI lexicon is applied. That should remain explicit. Extending CUI
assignment is a shared scorer-facing benchmark-format step, not an LLM-only
clinical-quality improvement.

## Improvement Order

1. Fix checkpoint report labeling so partial runs cannot be mistaken for final
   full-200 audits.
2. Add a diagnostic scoring ladder to the all-entity report:
   exact semantic, phrase-only, same-entity source-near/substring overlap, and
   attribute agreement conditioned on overlap.
3. Tighten the all-entity prompt with entity-specific `text_target` rules and
   examples.
4. Add a semantically neutral attribute canonicalizer for case/unit spelling
   only.
5. Decide per-entity phrase projection policies, starting with Prescription,
   PatientHistory, and SeizureFrequency.
6. Treat CUI assignment as a separate shared benchmark-format workstream.

## Claim Language

Until the final process reaches all 200 letters, use:

```text
60-row checkpoint diagnostic, not a frozen full-200 audit result.
```

Even after completion, the current `v0.1` all-entity prompt should be read as a
contract-probe result. Its low exact F1 is real under the current scorer, but it
mixes at least three causes: clinical miss, phrase-basis mismatch, and
format/canonicalization mismatch.

## Implementation Completion Note

Completed on 2026-06-12:

- Checkpoint reports now write to a `_checkpoint.md` path and include a
  `CHECKPOINT ONLY: processed N / total letters` banner.
- The all-entity report now includes a diagnostic scoring ladder with exact
  semantic, benchmark, phrase-only, source-near substring overlap, and
  attribute agreement conditioned on overlap.
- The all-entity prompt now includes entity-specific `text_target` guidance for
  all nine ExECTv2 entities, including the seizure-type anchor rule for
  `SeizureFrequency` and medication-name rule for `Prescription`.
- Attribute matching and the repair gate now share format-only canonicalization
  for whitespace/quote cleanup, `DrugName` casing, and `DoseUnit` casing.
- Official exact scoring remains unchanged as the benchmark-comparable headline;
  source-near overlap remains diagnostic rather than a replacement scorer.
- CUI assignment remains a separate benchmark-format workstream.
