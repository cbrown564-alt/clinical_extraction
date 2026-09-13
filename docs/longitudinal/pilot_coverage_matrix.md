# Pilot case coverage

Updated: 2026-09-10. Pilot v0.8 retains authored coverage and reference statuses.
Internal development coverage accepted; clinical validation remains absent.
Query dates are unchanged. Earlier files for revised cases 002, 005, 007, 011 and 012
are retained under `results/longitudinal/pilot_v0.2/source_snapshot/`.
This document owns coverage; [task definition](task_definition.md) owns requirements.
Counts below are an authoring review, not independent or clinical validation.

## Required patient-level coverage

| Requirement | Minimum | Cases and supporting content |
| --- | ---: | --- |
| Ordinary unchanged follow-up | 3 | 002 L1–L2: stable focal frequency and maintenance therapy; 004: unchanged clinical pattern with modernized terminology; 007: stable absence frequency and unchanged valproate. |
| Concurrent patterns / type-specific absence | 3 | 001 concurrent patterns; 004 focal events despite convulsion absence; 007 absence events despite convulsion/myoclonus absence; 011 explicitly concurrent focal clusters and shaking. |
| Copied or renamed history | 2 | 003 L2 copied seizure-free background; 004 L2 explicit terminology correspondence. |
| Planned medication not enacted | 2 | 001 lamotrigine never taken; 005 L1 August proposal explicitly not enacted, with non-use through T1. |
| Actual medication start | 2 | 010 L2 confirms January initiation; 005 L2 confirms first use on 20 May after a new decision. |
| Requested test with later result | 2 | 001 linked requests/results; 010 January EEG; 005 distinct May EEG. |
| Pending/cancelled test | 2 | 001 L1 and 005 L1 explicitly pending EEG. Both use the pending alternative. |
| Explicit reinterpretation | 2 | 001 L2 staring events; 011 L2 shaking events, same pattern back to onset and decision dated 20 June. |
| Unresolved reporter disagreement | 2 | 006 L1 patient/partner conflict; 012 L1 patient/mother conflict over awareness, explicitly unresolved. |
| Delayed document | 2 | 001 L3 issued after consultation; 005 L2 July consultation available 5 August, after T2. |
| Partial event dates | 2 | 005 Christmas/spring/summer; 006 mid-June/early-August bounds unresolved. |
| No-reference letter / missing outcome / irregular gap | 3 | 002 L3 administrative missed appointment without clinical assertions; 009 no medication/test outcome; 008 follow-up outside fixed retrospective cutoffs. |

All 12 cases have 20 requests. All five queries meet the required minimum of two
examples of each status in the provisional authored reference:

| Query | Eligible | Ineligible | Indeterminate |
| --- | ---: | ---: | ---: |
| Q1 | 31 | 3 | 14 |
| Q2 | 2 | 10 | 36 |
| Q3 | 2 | 5 | 41 |
| Q4 | 2 | 2 | 44 |
| Q5 | 4 | 2 | 42 |

There are 15 differences among 120 matched view pairs. Multi-letter decisions
include 001 T1 retrospective Q2, 011 T1 retrospective Q2, and 011 T2 Q5. The
earlier interpretation and later revision must both be retained. 005 T2 visit
cannot access the delayed confirmation that makes retrospective Q3/Q4 eligible.

## Internal acceptance and remaining limits

The required patient-level examples above and the two-per-query/status minimums
are accepted for authored development coverage. This decision follows the saved
44 successful independent AI outputs, query-status adjudication and the v0.7
source-backed temporal review. It is not an expert-validation claim. The
[pilot review](pilot_disagreement_report.md) owns disagreement, measured query-field
comparisons and remaining representation defects. All source letters and fixed
query dates remain unchanged by v0.8.

The earlier suggested class-balance and 25% view-divergence targets were not
canonical task minimums. Current references are 73.75% indeterminate, with 12.5%
view divergence; dates and reference decisions are not tuned to percentages.

Patient 011 demonstrates exact cluster counts rather than a cluster-size range.
That range is a future history stress case, not an unmet minimum patient count.
Qualitative seasonal dates still need explicit interpretation, and current Q1–Q4
structured evaluation leaves 11 reference-supported answers indeterminate.
The v0.8 timed probe measures AI wall time by activity on three selected patients;
human effort and comprehensive semantic link agreement remain unestablished.
Phase 2 is complete under its provisional-development criteria, with these
limitations explicit in the pilot review. No corpus freeze is authorized by coverage.
