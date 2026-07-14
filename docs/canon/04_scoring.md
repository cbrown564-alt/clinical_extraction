# 04 — ExECT scoring and annotation evidence

Last updated: 2026-07-14

| Score | Question | Use |
| --- | --- | --- |
| Clinical fact recovery (`clinical_headline`) | Were the right facts recovered across the four main entity types? | Primary internal comparison |
| Entity-specific score | Was the entity's clinical object recovered? | Entity analysis |
| Seizure-frequency state profile | Was the combined seizure-burden state recovered? | Seizure-frequency development |
| Phrase, CUI, and full attributes | Does the output match the published representation? | Published-metric comparison |
| Evidence groundedness | Is the cited text present after neutral text repair? | Evidence fidelity |

Do not describe `clinical_headline` as the published strict benchmark. The
deterministic system still needs full phrase, CUI, and attribute engineering.

| Method | Split | Selected result |
| --- | --- | ---: |
| Rules only, all nine entities | dev140 | strict item F1 0.3548 |
| GEPA LLM only | dev140 | clinical fact F1 0.7393 |
| LLM with rules (`v08`) | dev140 | clinical fact F1 0.9189 |

The selected annotation records include diagnosis and seizure-frequency row
analyses, a blind replication report, four entity ledgers,
`experiments/gold_data_issues.jsonl`, and the extracted annotation guidelines.
The same team produced and reviewed these records. They support limited claims
about multiplicity, representation, ambiguity, and specific defects; they are
not independent clinical validation.

Open work: implement the published phrase/CUI/full-attribute scores, check the
published inter-annotator agreement method against its primary source, and
combine cited annotation issues with their scoring effects and review status.
