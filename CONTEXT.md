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

**VerificationDecision**: A verifier-stage action over structurally valid
upstream clinical-assessment and projection/render objects. It may affirm,
reject, abstain, or require human review for risky clinical or projection
cases, but it does not repair missing drafts, malformed schema output, invalid
candidate references, parse failures, or model call failures.
_Avoid_: schema rescue, output repair, second selector

**Verification Route**: A predeclared issue or risk-family predicate that sends
a structurally valid clinical-assessment or projection/render object to
verification before score outcomes are used. Routes are defined by clinical or
projection risk, not by after-the-fact wrongness or null-label status alone.
_Avoid_: score triage, null-label bucket, post-hoc error filter

**Verifier Action**: The verifier output action for a routed object. `affirm`
accepts the current assessment, projection, or render action; `reject` blocks
an unsupported or unsafe current outcome; `abstain` leaves the row unresolved
because the automated pipeline has no reliable answer; and `human_review`
escalates a meaningful but high-risk, conflicting, or policy-sensitive case
that automation should not own.
_Avoid_: fallback label, repaired answer, hidden override

**Null Rendered Label**: A projection/render output with no scorer-facing label.
It is a symptom of the projection/render state, not a verifier route by itself.
Only null labels caused by a predeclared clinical or projection risk family
should enter verification.
_Avoid_: automatic verifier case, scored wrong row

**Seizure-Free Date Arithmetic**: A deterministic normalization or projection
policy that converts a source-near seizure-free anchor, such as "since January
2024", into a duration when the required dates are available and the anchor is
policy-approved. Date arithmetic is not a verifier job by itself.
_Avoid_: verifier repair, LLM duration inference

**Seizure-Free Conflict**: A verifier-route family where a seizure-free claim is
in tension with active-event evidence, scoped event types, breakthrough events,
or other current seizure-burden facts. Conflict handling belongs to
verification rather than silent projection arithmetic.
_Avoid_: date arithmetic, duration parsing

**Cluster-Axis Ambiguity**: A verifier-route family where it is unclear whether
a cluster statement describes cluster cadence, events per cluster, cluster
duration, or individual seizure frequency. Clear cluster operands belong to
deterministic projection; ambiguous cluster-axis meaning belongs to
verification.
_Avoid_: cluster parsing, deterministic cluster render

**Same-Window Additive Frequency**: A deterministic projection policy that may
sum multiple concrete `frequency_rate` primary facts only when they share the
same time window and compatible event scope. Mixed-window, vague-plus-concrete,
or event-scope-uncertain addition is a verifier or abstention case.
_Avoid_: mixed-window arithmetic, vague arithmetic, context aggregation

**Verifier Rejection**: A verifier action that blocks the current projected or
rendered outcome without inventing a replacement scorer-facing label. Any
replacement must come from a separately named deterministic fallback or action
policy.
_Avoid_: hidden render override, verifier fallback label

**Comparator Preservation Action**: A named fallback or action policy that may
preserve an existing comparator or baseline output after verification judges a
proposed projected outcome risky or unsupported. Comparator preservation is
benchmark/action policy, not clinical truth, verifier repair, or hidden
projection behavior.
_Avoid_: verifier label, projection guard, clinical assessment

**Verification Route Report**: A deterministic validation artifact that lists
structurally valid rows routed to verification by predeclared risk-family
predicates, such as seizure-free conflict, cluster-axis ambiguity,
mixed-window or vague addition, multiple current primary facts, comparator
preservation risk, or policy-sensitive rendered labels. It records route
reasons and trace ids but does not run a verifier model or emit verifier
actions.
_Avoid_: verifier decision report, score error report, Qwen schema report

**Route V0 Determinism Boundary**: The first verification-route artifact is
generated from deterministic predicates over existing validated pipeline
objects. Manual row annotations belong in a separate inspection layer or later
route refinement, not inside the V0 route-generation logic.
_Avoid_: human-coded route logic, mixed manual artifact

**Route Score Context Boundary**: A verification-route report may consume a
score-policy artifact when it already embeds projection/render objects, but
route predicates must be based on clinical-assessment, projection, render, and
predeclared risk fields. Score status and correctness fields are audit context,
not route triggers.
_Avoid_: score-triggered route, wrong-row routing

**Route V0 Predicate Boundary**: The first verification-route predicates map
existing structured contract fields and issue names to predeclared route
families. Candidate text and detail objects may be displayed for trace review,
but V0 route triggering does not parse evidence or discover new clinical facts.
_Avoid_: verifier discovery, second extraction pass, raw-text routing

**Concrete Frequency Precedence**: A deterministic clinical-assessment
normalization rule where a renderable frequency-rate candidate can override a
cluster-framed assessment when the cluster framing is contextual and the
frequency burden is concrete or policy-approved vague frequency from the shared
selected-evidence parser. It must not override already renderable
cluster-burden operands or medication-use cadence.
_Avoid_: cluster erasure, medication cadence as seizure frequency

**Projection Owner**: The named policy authority responsible for turning a
clinical state into a benchmark-facing label, such as rate projection, cluster
projection, boundary projection, or benchmark-only rendering. Projection
ownership must be explicit whenever a label change could be confused with a
clinical extraction decision.
_Avoid_: hidden renderer policy, unattributed final-label change

**Benchmark Renderer**: A projection owner that changes only the
benchmark-facing label convention while preserving the input clinical state.
It may emit scorer sentinels or Gan-specific cluster syntax, but it must not
choose a different clinical fact.
_Avoid_: clinical selector, semantic repair, final-label policy

**Cluster Cadence As Event Rate**: A narrow cluster projection policy where a
clear current cluster cadence may render as a simple seizure-frequency rate
when events-per-cluster burden is absent. It is owned by
`cluster_projection_policy`, must not apply to ambiguous cluster axes,
medication cadence, or contradictory per-cluster evidence, and should carry an
explicit rule id.
_Avoid_: benchmark renderer fallback, cluster erasure, medication cadence

**Medication Cadence Ambiguity**: A verification-route family where cadence
evidence may describe medication use, rescue dosing, or another non-event
schedule rather than seizure or seizure-cluster occurrence. Projection must not
convert this cadence into seizure frequency without reliable event evidence.
_Avoid_: cluster-axis ambiguity, frequency-rate projection, medication cadence as seizure frequency

**Unknown-Cadence Cluster Burden**: A cluster projection state where
events-per-cluster burden is supported, but cluster recurrence cadence is not
known. It may render to an explicit unknown-cadence cluster sentinel only under
a named `cluster_projection_policy` rule; it is not benchmark-renderer
formatting.
_Avoid_: cluster cadence fallback, simple rate projection, hidden sentinel rendering

**Cyclic Vulnerability Window**: A clinical statement that events occur within
a recurring biological or contextual window, such as a perimenstrual interval,
without specifying the number of events in that window. It is not itself a
seizure-frequency count or cluster-burden operand.
_Avoid_: cluster frequency, unknown-cadence cluster burden, inferred event count

**Dominant Vague Current Burden**: A rate projection policy where a vague but
current high-frequency burden, such as events on most weekdays, may be selected
over lower-frequency contextual burden when both labels are derivable and the
vague burden mechanically dominates. It is a named projection policy, not
additive arithmetic.
_Avoid_: mixed-window addition, hidden selector preference, score-only rescue

**Seizure-Free Proxy Evidence Overreach**: A boundary projection block where
the selected evidence supports only proxy improvement, such as no rescue
medication, no injury, no admission, better control, or conditional future
breakthrough-event planning, rather than explicit no-seizure or no-event
evidence. It must not render a seizure-free duration.
_Avoid_: seizure-free state, duration projection, rescue-medication absence as seizure freedom
