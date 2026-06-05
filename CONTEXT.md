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
