# Seizure-frequency annotation guide

Locked 2026-09-24 by Conor Brown. This is the only annotation guide for the
one-call study. It defines the full seizure-frequency inventory that the
`expanded` prompt returns and that reference annotators record. Change it only
by an explicit owner decision added to the change log at the end; do not start
a new version series. Earlier guides (v0.1–v0.8.5, compact v0.1–v0.3) are
recoverable from Git tag `archive/pre-lockdown-2026-09-24`.

The primary study endpoint is the native Gan answer (Purist, Pragmatic
companion). The inventory is secondary and descriptive. Its boundaries are
naturally fuzzier than a single label, so this guide prefers simple, stable
defaults over exhaustive edge-case rules, and the finding score is lenient
(see [Scoring](#scoring)).

## One-sentence rule

Record, once each, every statement in the letter that says **how often, how
many, how long without, or when last** the patient's seizures occurred,
current or historical, under the letter's own label, with an exact quotation.

## What is a finding

| Measurement kind | Use for | Default reading |
| --- | --- | --- |
| `rate` | A stated recurrence: "twice weekly", "every 4–6 weeks", "daily", "3 seizure days per week" | A bare cadence is 1 per interval. "Bimonthly" is 1 per 2 months unless the letter defines it. |
| `observed_count` | Events in a stated window or on a date: "three in the past month", "one on 12 May" | The window goes in `time.source`. "N or M" is the range N–M. |
| `cluster` | Cluster count, cadence and seizures per cluster: "monthly clusters of 3–4" | One finding holds all stated cluster parts. The span within a cluster ("over 24 hours") stays in evidence. |
| `seizure_free` | Absence with a duration or since-anchor: "seizure-free for 14 months", "none since March" | Only for at least two weeks, or an anchor not known to be shorter. |
| `last_event` | An event the letter calls the last or most recent, with its time | A dated event that is not called the latest is an `observed_count`. |
| `median_interval` | A stated median time between events | Not a regular rate. |
| `qualitative` | A standalone level with no number: `occasional` or `frequent` | "Rare", "infrequent", "sporadic" → occasional; "most days", "near-daily" → frequent. Only when no more precise measurement of the same events and window exists. |

**Not findings:** plans, thresholds and expectations; family history; medication
schedules; explicitly non-epileptic events; symptoms the letter does not link to
seizures; denials with no duration or anchor ("no auras"); occurrence-only
wording ("ongoing seizures", "history of epilepsy"); trend-only or pattern-only
wording ("improved", "predominantly nocturnal"); typical gaps between recurring
events ("may go five days without").

## Filling a finding

The machine-readable shape is
[`expanded.schema.json`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/one_call/expanded.schema.json).

| Field | Rule |
| --- | --- |
| `event.label` | The letter's words for the counted events. Do not infer a subtype from the diagnosis. |
| `event.scope` | `overall` only for an explicit whole-population total; `named` for a stated seizure type; `combined` for an explicit joint total of several types; otherwise `unspecified`. |
| `counted_unit` | `individual_seizure` unless the letter counts affected days (`seizure_day`), affected nights (`seizure_night`), clusters (`cluster`), cluster days (`cluster_day`) or status epilepticus episodes (`status_episode`). Seizure-free, last-event and median-interval findings use `not_applicable`. |
| `status` | `stated`, or `uncertain` only when the letter questions whether the events are seizures. |
| `measurement` | The stated number, range (`2 to 3`) or bound (`at most 4`). Use `verbatim` for vague amounts or intervals ("few weeks", "several months"). Never convert units or compute values. |
| `time.phase` | `ongoing` when the finding describes the patient at this assessment; `superseded` when the letter states a later state that replaces it; `past_or_unclear` otherwise. |
| `time.source` | The letter's concise window or date wording, when stated. Do not resolve relative dates or compute durations. |
| `restriction` | Only a stated limit on which events were counted: "while asleep", "witnessed only". |
| `evidence` | One or more short exact quotations that together support the finding. |

## Counting each claim once

- A restatement of the same events, measurement and window is one finding;
  add its quotation to that finding's evidence.
- Trend or variability wording about a measured claim belongs in that finding's
  evidence, not in another finding.
- Different seizure types, windows or measurements are separate findings. Never
  sum, split or link counts across seizure types unless the letter states the
  joint total.
- A diary or list of counts for the same events across listed months or dates
  is one `observed_count` over that span when the parts do not overlap. Do not
  fill unreported months with zero, count a subtype twice, or count a cluster as
  one seizure.
- A correction ("in fact five, not four") keeps only the corrected value.

## Decision order

1. Does the statement say how often, how many, how long without, or when last? If not, skip it.
2. Is it excluded above? If so, skip it.
3. Choose the measurement kind from the table.
4. Fill event, counted unit, status, time and restriction by the defaults.
5. Merge it with an existing finding if it restates the same claim.
6. Quote the shortest exact span that supports it.

Do not stop to log alternatives. If two readings give materially different
values and no default settles it, record the more literal reading and add a
one-sentence `note` for the owner. Notes are never scored.

## Worked examples

| Letter text | Finding |
| --- | --- |
| "Patient reports seizures every 6 days … over the past two months." | `rate` 1 per 6 day; unspecified "seizures"; ongoing; source "over the past two months". |
| "Two cluster days this month, usually six seizures each within 24 hours." | `cluster` count 2, 6 per cluster; `cluster_day`; source "this month"; "within 24 hours" in evidence only. |
| "Seizures every night" with no per-night count | `rate` 1 per 1 day; `seizure_night`. |
| "Three focal aware seizures in May and four in June." | One `observed_count` of 7; named "focal aware seizures"; source "May and June". |
| "Previously daily seizures; now two per month." | Two findings: 1 per day `superseded`; 2 per month `ongoing`. |
| "No generalised tonic-clonic seizures since March 2018." | `seizure_free` since "March 2018"; named; `not_applicable`. |
| "Absences are infrequent." (no number anywhere for absences) | `qualitative` occasional; named "absences". |
| "Possible nocturnal events, ?seizures, about weekly." | `rate` 1 per week; `uncertain`. |
| "No auras." / "Seizures are better controlled." | Not findings. |

## Scoring

The native answer is scored by the existing Gan Purist/Pragmatic scorer. The
inventory score (`findings_score.py`) is lenient and descriptive. A returned
finding matches one reference finding when their quotations overlap in the
letter, their measurements are the same family (rate, count and median interval
together; cluster, seizure-free, last event and qualitative each alone), and
their values agree: rates in the same Purist band, counts overlapping,
qualitative levels equal. Seizure-free durations and last-event times are not
compared, as in native Purist. Event wording, scope, counted unit, status,
phase, window wording and restriction are reported as agreement among matched
pairs but never required. Matching is one-to-one.

Report precision, core recall and all-reference recall. Do not tune prompts to
this score, and do not version the matcher. Disagreements on fuzzy boundaries
are expected and are not a reason to reopen this guide.

## References

**dev750.** Local file `runs/seizure_frequency/reference/dev750.jsonl`
(sha256 `e40755d7…9943`), 750 letters including `row_ok=False`. It was derived
once, on 2026-09-24, from the owner-adjudicated compact v0.3 annotation, which
had source-reviewed every v0.8.5 finding:

- **core** (1,219): the owner-reviewed current activity, explicit last events
  and linked prior states;
- **supporting** (131): the remaining reviewed historical or contextual
  measurements that had a structured record, excluding 103 restatements
  already merged into a core finding's evidence.

Findings the compact review excluded (non-seizure or unlinked events) are
absent. Because the reference predates this guide, a small number of full
inventory claims (for example some excluded affected-day counts) may be
missing; that limits all-reference recall only. Every finding validates against
the schema and every quotation is an exact substring of its letter. The
derivation inputs are in the archived runs tarball
(`~/code/archives/clinical-extraction-runs-2026-09-24.tar.gz`).

**test450.** Not yet annotated under this guide; the earlier test450
annotations were discarded with the old guides. The source-only package is
built by `scripts/benchmarks/prepare_test450_annotation.py` into ignored
`runs/seizure_frequency/annotation/test450/`: all 450 letters (including
`row_ok=False`) in nine batches of 50, instructions taken verbatim from this
guide's rules, the record schema, a worked example and
`validate_annotations.py` (identity, coverage, schema and exact quotations).
No native labels, references, predictions or row-quality flags are exported.
The test450 reference has a single tier, so its findings are imported as core
and all-reference recall is the reported measure. Test450 stays
aggregate-only for evaluation; disclose annotation exposure.

## Change log

- 2026-09-24: Locked. Full inventory with phase tag, compact schema, lenient
  descriptive score.
