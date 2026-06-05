# Clinical Extraction

This context covers the Gan 2026 seizure-frequency extraction work and its
evaluation surfaces.

## Language

**Validation250**: The first 250 rows of the `validation` split from
`gan2026_split_v1`, used as a stronger development signal after the validation
ladder gate is met. It is not a separate stratified panel.
_Avoid_: saved validation250 panel, stratified validation250 panel

**ExtractedCandidate**: A source-near seizure-frequency fact candidate emitted
by extraction before selection, normalization, projection, verification, or
rendering. It may be one of many candidates in a row-level candidate set.
_Avoid_: prediction label, scorer label, selected fact

**CandidateSet**: The collection of extracted candidates available for one row
before a selector chooses the clinically relevant fact or conflict.
_Avoid_: final answer, adjudicated label

**SelectedClinicalFact**: A selector output that chooses the clinically relevant
source-near fact from a `CandidateSet`, or explicitly abstains because the row
is ambiguous, conflicting, lacks reliable evidence, or needs verifier action. It
is upstream of normalization, projection, verification, rendering, and scoring.
_Avoid_: normalized fact, projected label, scorer answer

**Cluster Details**: The part of a cluster-frequency extracted candidate that
records cluster frequency, events per cluster, cluster count, and cluster
period.
_Avoid_: cluster schema, cluster label

**Time Period**: The source-near time basis attached to a seizure-frequency
candidate, such as day, week, month, year, or a range like 7 to 9 days.
_Avoid_: denominator

**Kind-Specific Detail Object**: The candidate detail object selected by
`candidate_kind`, such as `frequency`, `seizure_free`, `cluster_details`,
`unknown_frequency`, or `no_reference`.
_Avoid_: universal frequency details

**LLM Candidate Extraction Role**: The LLM should find source-near clinical
candidate statements, choose broad candidate kind/event type/temporality, and
mark simple certainty. It should not be responsible for parsing counts, ranges,
intervals, durations, ids, spans, source artifacts, or scorer-facing labels.
_Avoid_: LLM parser, LLM final labeler

**Deterministic Normalization Role**: Deterministic code expands source-near
candidate phrases into parsed counts, ranges, time periods, durations, canonical
states, and later projection inputs.
_Avoid_: hidden semantic repair

**Deterministic Candidate Extraction**: Rule-based extraction emits
source-near candidates into a `CandidateSet`. Any legacy deterministic label
carried with the raw candidate is extraction provenance for later normalization
or projection, not a selected clinical fact or final scorer answer.
_Avoid_: deterministic top answer, selected deterministic label

**Compatible-Kind Coverage**: An extract-stage diagnostic that asks whether a
candidate set contains at least one source-near candidate kind compatible with
the gold semantic kind. It is weaker than normalized-label recall and must not
be reported as scorer-facing performance.
_Avoid_: accuracy, label recall, benchmark score

**CandidateSet Union Coverage**: Compatible-kind coverage after combining
candidate sources, such as deterministic and LLM candidate sets, at the row
level. It measures whether any extraction source supplied a compatible
source-near candidate kind; it does not decide selection, normalization,
projection, or scorer-facing correctness.
_Avoid_: ensemble score, final hybrid accuracy

**Candidate Burden**: The number of source-near candidates emitted for one row
before selection. Higher burden can improve extraction coverage but increases
selector ambiguity and should be reported separately from coverage.
_Avoid_: coverage, recall

**High-Recall Extract Mode**: An extract-stage posture that deliberately emits
additional source-near candidates, including vague or uncertain candidates, so
selection and later pipeline stages can decide among them. It accepts higher
candidate burden and must be evaluated separately from selector accuracy.
_Avoid_: final assembly, tuned scoring policy

**Unknown Frequency Candidate**: A source-near extracted candidate indicating
that the note discusses seizure frequency without a usable rate, duration, or
cluster cadence. It is only one possible representation of unknown frequency;
unknown may also be reconstructed downstream from absent reliable evidence,
uncertain candidates, contradictions, or verifier action.
_Avoid_: final unknown label, proof of unknown state

**Unknown By Absence**: A selector abstention that represents unknown frequency
because no reliable current seizure-frequency candidate is available. It is not
the same as selecting an `unknown_frequency` extracted candidate.
_Avoid_: extracted unknown candidate, final unknown label
