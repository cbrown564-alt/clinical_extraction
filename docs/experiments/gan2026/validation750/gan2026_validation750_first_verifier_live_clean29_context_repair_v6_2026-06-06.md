> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 First Verifier Live Run Clean29 V6

Validation-development first action-only verifier run over the clean 56-row V6 surface. This is not a scorer-label replacement protocol, does not authorize locked-test inspection, and keeps provenance-only rows out of the main table.

## Decision

The first verifier produced non-abstain action decisions on the clean surface. The primary table remains the 29-row ambiguity set.

## Artifacts

- Row JSONL: `experiments\gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.json`
- Source input: `experiments\gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| call ok rows | 56 |
| parse ok rows | 56 |
| parse error rows | 0 |
| contract ok rows | 56 |
| contract error rows | 0 |
| changed action rows | 27 |
| main score table rows | 29 |
| main score table changed action rows | 21 |
| appendix rows | 27 |
| affirm rows | 5 |
| reject rows | 5 |
| abstain rows | 29 |
| human review rows | 17 |
| parse error action rows | 0 |

## Main Table Actions

| Action | Rows |
| --- | ---: |
| `abstain` | 8 |
| `affirm` | 1 |
| `human_review` | 15 |
| `reject` | 5 |

## Appendix Actions

| Action | Rows |
| --- | ---: |
| `abstain` | 21 |
| `affirm` | 4 |
| `human_review` | 2 |

## Main Ambiguity Table

| Row | Baseline | Verifier | Sidecar | Route bucket | Rationale |
| ---: | --- | --- | --- | --- | --- |
| 5551 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence describes several episodes per day (focal) plus occasional generalized seizures approximately once weekly, with clusters and recent events. The frequency data is vague and additive across different time windows, and the selected evidence is not an exact trace for the primary fact, leading to normalization and projection issues. This complexity and ambiguity warrant human review. |
| 5791 | `abstain` | `affirm` | present | `verifier_eligible_ambiguity` | The evidence text explicitly states two brief myoclonic jerks and one generalized tonic–clonic seizure over the past three months, matching the clinical assessment summary. Despite normalization and projection issues, the direct textual evidence supports the frequency assertion reliably. |
| 6209 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | Evidence shows daily brief seizure-like events and 2–3 longer episodes per month, but additive frequency periods mismatch and incomplete projection semantics prevent clear verification. Selected evidence lacks exact trace, supporting abstention. |
| 6889 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes multiple seizure frequencies with different time frames (several times per week, three in six months, once every 2-3 weeks) combined additively, causing temporal mismatch and vagueness. The selected evidence is not an exact trace for the primary fact, and projection issues indicate incomplete and vague frequency values. These factors prevent confident verification, warranting human review. |
| 12127 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | The evidence shows several focal non-motor seizures weekly and two generalised convulsions per year, but frequency periods are mixed and counts vague, with no exact trace for primary facts; thus, verification cannot be confidently affirmed or rejected. |
| 12192 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows daily drop attacks (llm:12192:1) but also a conflicting frequency of approximately twice weekly seizures (det:12192:2) with unclear temporality. Additional seizure types with different frequencies are reported, and the aggregation policy is additive despite mixed or vague frequency periods. The evidence lacks an exact trace for the primary fact and has projection issues, making automated verification unreliable. |
| 12236 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | The primary candidates assert daily absence seizures and occasional generalized tonic-clonic seizures, but the evidence lacks exact traceability and frequency values are unparsed with additive period mismatches, making verification inconclusive. |
| 12366 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence asserts seizure frequencies for simple partial seizures (4/day) and tonic-clonic seizures (2/month) with certainty, but the additive frequency periods differ and the projection semantics are incomplete. The provenance sidecar notes missing exact trace and invalid source ID status, indicating uncertainty in evidence linkage. These factors necessitate human review rather than automatic affirm or reject. |
| 12378 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | The evidence shows two seizure frequencies with different time units (daily and monthly) combined additively, causing normalization and projection issues. The selected evidence lacks exact traceability, and the projection semantics are incomplete, supporting abstention. |
| 12403 | `abstain` | `abstain` | absent | `verifier_eligible_ambiguity` | The evidence supports focal aware seizures 2-3 times daily and tonic-clonic seizures twice monthly, with drop attacks clustered once or twice monthly. The additive frequency assessment mixes different time windows and has incomplete normalization, leading to projection issues and no clear final label. Policy directs abstention in such mixed-window or vague additive cases. |
| 12422 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | The evidence shows two seizure frequencies: nightly generalized convulsions and intermittent tonic seizures four times per year, which are additive but span different time windows, causing normalization and projection issues. The selected evidence is not an exact trace for a single frequency fact, leading to ambiguity in verification. |
| 12456 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes two asserted seizure frequencies: nightly generalized tonic-clonic seizures and intermittent tonic seizures three times per year. These frequencies span different time windows and are combined additively, but normalization is incomplete and inconsistent. The provenance indicates missing exact trace and invalid source ID status. Projection issues include missing semantics and incomplete frequency values. Given these complexities and uncertainties, human review is warranted. |
| 12460 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | Evidence shows two seizure frequencies: nightly generalized convulsions and intermittent tonic seizures twice per year, combined additively but with mismatched frequency periods and incomplete normalization, leading to uncertainty in verification. |
| 12484 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes multiple seizure frequency rates with different temporal references (yearly, daily, monthly) and seizure-free periods, with no exact trace linking primary facts to evidence. Additive frequency normalization is incomplete and inconsistent, leading to projection and semantic issues. This complexity and uncertainty warrant human review. |
| 12502 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows multiple seizure frequency rates with different time frames (daily absences, monthly tonic-clonic seizures, monthly clusters) and no exact trace for primary fact; additive frequency assessment is incomplete and inconsistent, necessitating human review. |
| 12506 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes multiple seizure frequency assertions with different time frames (daily absences, monthly generalized seizures, monthly clusters) and a rejected ambiguous 'once a month' frequency. The additive aggregation policy leads to frequency period mismatches and incomplete normalization. The primary facts lack an exact trace, and the projection has semantic and completeness issues, warranting human review. |
| 12537 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Primary candidates consistently report frequent seizures (up to three per week, daily drop attacks, focal seizures every 4-6 weeks) with stable frequency over 6 months, but other candidates assert no events since last review, causing contradictory seizure-free status. The additive aggregation includes mixed temporal windows and vague periods, leading to incomplete and inconsistent frequency representation. Thus, the verification cannot affirm the proposed frequency and should reject due to conflicting evidence. |
| 12548 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Evidence shows ongoing seizures including up to 3 generalized tonic-clonic per year, focal seizures every 4-6 weeks, and daily drop attacks, contradicting any seizure-free assertion. Additive frequency assessment is inconsistent and lacks exact trace, supporting rejection. |
| 12551 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes multiple seizure types with different frequencies (up to 2 generalized tonic-clonic seizures per year, focal impaired-awareness seizures every 4-6 weeks, daily drop attacks) and a statement of no events since the most recent review, creating temporal and frequency conflicts. The additive frequency period mismatch and lack of exact trace for primary facts prevent confident verification. Hence, human review is needed. |
| 12556 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | The evidence includes recent seizure frequency claims (2-3 per week, daily drop attacks, seizures every 4-6 weeks) alongside statements of no events since last review, which contradicts and causes additive frequency period mismatch, undermining verification confidence. |
| 12562 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows multiple seizure types with different frequencies (weekly, daily, every 4-6 weeks) and a recent seizure-free period, creating additive frequency period mismatches and incomplete normalization. The primary fact lacks an exact trace, and the evidence is mixed and vague, warranting human review. |
| 12573 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | Evidence indicates patient continues to have up to two generalized tonic-clonic seizures per month, daily drop attacks, and focal impaired-awareness seizures every 4-6 weeks, contradicting any seizure-free assertion. Additive frequency periods are mismatched and evidence lacks exact trace for primary fact, supporting rejection. |
| 12584 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The primary evidence candidates describe multiple seizure types with different frequencies (generalised tonic-clonic every 3 months, weekly absences, and atonic plus focal seizures every few months) combined additively, but the periods differ and counts are vague. The seizure-free period is short (max 4 weeks), and no seizures reported since last visit. The evidence trace is not exact for the chosen primary fact. These factors prevent a clear, reliable frequency rate rendering, requiring human review. |
| 12641 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence shows multiple seizure types with different frequencies (weekly, daily, every 3-4 weeks) combined additively, causing period mismatch and incomplete normalization. The primary fact lacks exact trace evidence. These complexities warrant human review. |
| 12676 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes multiple seizure types with different frequencies (yearly, weekly, daily) and some unclear temporality, leading to additive frequency period mismatch and incomplete normalization. The selected evidence is not an exact trace for the primary fact, warranting human review. |
| 12679 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | The evidence includes multiple seizure frequency assertions with different event types and time frames (monthly, every 3-4 weeks, daily), causing additive frequency mismatch and incomplete frequency values. The selected evidence is not an exact trace for the primary fact, and the projection has semantic and aggregation issues, warranting human review. |
| 12749 | `abstain` | `reject` | present | `verifier_eligible_ambiguity` | The evidence includes a certain candidate stating no seizures have been noted since a prior time (det:12749:1) and another stating focal motor seizures occur 3-4 per day (llm:12749:2), which directly conflicts. Additionally, generalised tonic-clonic seizures twice monthly (llm:12749:1) further complicate frequency assessment. These contradictions undermine verification confidence, warranting rejection. |
| 12751 | `abstain` | `human_review` | present | `verifier_eligible_ambiguity` | Evidence shows multiple seizure frequency statements with different seizure types and time frames (e.g., 4 focal clonic per day, generalized tonic-clonic twice monthly, drop attacks monthly clusters) plus seizure-free intervals, causing additive frequency assessment issues and unclear temporal alignment, necessitating human review. |
| 12823 | `abstain` | `abstain` | present | `verifier_eligible_ambiguity` | The evidence shows two seizure frequency assertions with different time frames (yearly and every 3-4 weeks) combined additively, causing period mismatch and incomplete frequency values. Additionally, the selected evidence lacks an exact trace for the primary fact. These issues prevent a confident verification decision. |

## Appendix By Section

| Section | Rows |
| --- | ---: |
| `abstain_exemplar_appendix` | 4 |
| `rendered_policy_sensitive_appendix` | 5 |
| `upstream_policy_appendix` | 18 |