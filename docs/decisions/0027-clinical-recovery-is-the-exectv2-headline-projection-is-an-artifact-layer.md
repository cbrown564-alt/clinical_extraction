# 0027: ExECT’s primary internal score measures clinical fact recovery

Date: 2026-06-18

ExECT uses de-duplicated clinical fact recovery as its primary internal score.
Exact annotation phrases and CUI formatting remain separate published-metric
companions.

The development analysis found high concept overlap but low exact phrase
agreement, and a gold-snapping diagnostic remained far below the published
score. This suggests that exact phrase scoring mixes clinical recovery with
annotation representation. The internal score therefore measures diagnosis
concepts, seizure-frequency state, prescription regimen, and investigation
status in entity-appropriate ways.

This choice gives up direct comparability to the published 0.87 item target.
Phrase, CUI, and full-attribute scores must still be reported when the paper
makes a published-benchmark comparison.
