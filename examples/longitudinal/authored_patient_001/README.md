# Authored patient 001: changing interpretation without rewriting history

Status: AI-authored fictional development example, version 0.1. No real patient,
source seed, paid model call, independent annotation or clinical review.
Implements P2.1 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).
These are provisional text-supported answers, not extraction predictions or expert gold.

## Read the letters first

Alex Morgan is a fictional 36-year-old outpatient with epilepsy of uncertain type.
Three event types appear: past nocturnal convulsions, recurring daytime staring
spells and morning jerks. The staring spells are later explicitly reinterpreted
as functional non-epileptic events; the morning jerks remain classified as epileptic.
Lamotrigine is proposed but never started. Two separate EEG requests must stay distinct.

| Letter | Consultation | Available to the evaluated system | Contents |
| --- | --- | --- | --- |
| [L1](letters/L1.txt) | 2025-01-15 | 2025-01-15 | Two patterns currently considered epileptic; deferred drug proposal; EEG requested. |
| [L2](letters/L2.txt) | 2025-06-20 | 2025-07-10 | Staring spells reinterpreted back to onset; non-initiation confirmed; old result and new EEG request. |
| [L3](letters/L3.txt) | 2025-07-14 | 2025-08-01 | Delayed account of the second index date; whole-window event history, continued non-initiation and repeat EEG result. |

The explicit interval-completeness statements are deliberate teaching-case scaffolding.
Ordinary pilot letters must also include incomplete histories; absence cannot usually
be established by counting the types that happen to be mentioned.

## Requests and allowed inputs

| Index | 90-day lookback | 180-day lookback | Retrospective cutoff |
| --- | --- | --- | --- |
| T1: 2025-01-15 | 2024-10-18–2025-01-15 | 2024-07-20–2025-01-15 | 2025-07-14 |
| T2: 2025-07-14 | 2025-04-16–2025-07-14 | 2025-01-16–2025-07-14 | 2026-01-10 |

Each index is queried in both views. The medication parameter is lamotrigine;
the investigation modality is EEG. All five queries apply; none are selected
after looking at a model's performance.

- [T1 visit input](inputs/T1_visit.json): L1 only.
- [T1 retrospective input](inputs/T1_retrospective.json): L1 and L2.
- [T2 visit input](inputs/T2_visit.json): L1 and L2.
- [T2 retrospective input](inputs/T2_retrospective.json): L1, L2 and L3.

The equal T1-retrospective and T2-visit source sets are intentional: the query
index/window still differs. Inputs contain only patient/document IDs, document
dates and source text. Keep this README, the manifest and the reference outside
extractor inputs. This case does not define a model prompt or output schema.

## All 20 expected answers

E = eligible, N = ineligible, U = indeterminate. “Eligible” refers to the documented
query predicate, never treatment or study recruitment eligibility for a real patient.
Every cell has evidence IDs and a reason in [reference.json](reference.json).

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1: epilepsy and a recent epileptic event | E | E | E | E |
| Q2: overlapping active epileptic patterns | E | N | U | N |
| Q3: actual lamotrigine start | U | N | U | N |
| Q4: qualifying EEG request with result available by index | N | N | U | E |
| Q5: explicit non-epileptic reinterpretation made by index | U | N | E | E |

### T1 visit account

January's staring spells and morning jerks are both considered epileptic, overlap
in time and occur in the lookback. Earlier nocturnal convulsion absence does not
erase these events. The lamotrigine plan does not establish a start, but the letter
also does not rule out an earlier course during the entire 180-day period: Q3 is
unknown, not a negative inferred from the plan. The sole qualifying EEG is pending.
No complete revision history is supplied for Q5.

### T1 retrospective account

The June clinician explicitly changes the interpretation of the same staring spells
back to their November onset. This changes Q2 to ineligible; the morning jerks keep
Q1 eligible. The never-taken medication history resolves Q3. February's EEG report
cannot satisfy a January result deadline. June's first reinterpretation changes how
the earlier events are understood, but the decision was not made by January: Q5 is
ineligible. Event interpretation and date of clinical recognition are different facts.

### T2 visit account

The June letter is available, but the July consultation letter is not. June's morning
jerks support Q1. Its negative history ends on 20 June and cannot cover the days
through 14 July for Q2/Q3. The repeat EEG's outcome is still unknown in allowed text.
The January request falls one day outside T2's 180-day lookback, so the February
result cannot substitute. The staring pattern had a June occurrence and was explicitly
reinterpreted in June; Q5 is eligible even though its first description was earlier.

### T2 retrospective account

The late letter supplies a history explicitly ending on 14 July. It resolves Q2 and
Q3 negatively and confirms the repeat EEG result was available to the treating team
on 11 July. Q4 becomes eligible even though the source letter reaches the evaluated
system on 1 August. Q1 remains eligible because 18 June is inside the window; Q5
remains eligible because the third letter repeats the June decision.

Six of the ten matched query/index pairs change status between views. Four stay
the same. This is authored reference variation, not a measured system improvement.

## Reference files and verification

- [manifest.json](manifest.json) owns case provenance, letter hashes and the 20
  requests, including exact cutoffs, lookback starts and query parameters.
- [reference.json](reference.json) owns 25 exact evidence spans, five explanatory
  cross-letter links and all 20 answer/status/reason records. Offsets are zero-based
  Unicode character indices in the UTF-8 text files, with exclusive ends and LF
  newlines. Relation names are local worked-example vocabulary, not a frozen schema.
- The four input JSON files physically omit unavailable letters. They do not
  contain reference answers, link annotations or hidden scenario truth.

There is no additional hidden clinical truth record: unsupported facts are deliberately
left unspecified. The story setup above does not override the letter evidence.
Unknown answers therefore cannot be “repaired” from author intention.

Checked on 2026-09-09: source hashes, all evidence substring offsets, link endpoints,
request coverage, date arithmetic, input filtering, reference evidence cutoffs and
the answer matrix. This author also reviewed the temporal logic; that is not a
second independent annotation pass. No extraction pipeline or scorer was run.

Important untested cases for the 12-patient pilot include genuine medication starts,
cluster/range arithmetic, missing availability dates, unresolved reporter conflicts,
cross-boundary partial dates and ordinary unchanged follow-up. This patient does not
satisfy the pilot coverage matrix by itself.

## Decisions exposed by the example

Task definition v0.2 clarifies three previously ambiguous points:

1. Q2 counts patterns interpreted as epileptic, while retaining non-epileptic events
   in the history. Otherwise the reinterpretation would not change that predicate.
2. Q4 distinguishes clinical result availability from the later letter reporting it.
   The latter governs input inclusion; the former is part of the query predicate.
3. Q5 permits a pattern first documented before the lookback when it has a supported
   occurrence inside the lookback. Its reinterpretation must still have occurred by T.

P2.2–P2.4 add [annotations.json](annotations.json): 35 assertions and 10
relationships under [guide v0.1](../../../docs/longitudinal/annotation_guide.md)
and its paired schema. These detailed relationships are distinct from the five
query-explanation links in the original reference. Original letters, inputs and
query answers are preserved. Run `python scripts/longitudinal/check_annotations.py`
from the repository root for structural and source checks.

Next is the expanded pilot and independent annotation pass (P2.5–P2.6). No schema
freeze, executable query scorer or clinical validation is claimed.
