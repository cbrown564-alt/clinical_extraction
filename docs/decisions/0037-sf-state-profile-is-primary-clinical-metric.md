# 0037: Use the change-aware seizure-frequency state score

Date: 2026-06-29
Status: accepted

`state_profile` is the primary internal seizure-frequency score for future ExECT
model studies. It distinguishes seizure-free, active rate, changed frequency,
and unknown. The older `clinical_headline` seizure-frequency score does not
credit a qualitative change unless a count is also present, so it remains only
a compatibility score.

A deterministic development change added 18 change facts across 15 letters.
`state_profile` rose from 0.710 to 0.779, while the older score could not see
those facts. Future seizure-frequency conclusions and optimizer targets use
`state_profile`; diagnosis, prescription, and investigation scoring is unchanged.
