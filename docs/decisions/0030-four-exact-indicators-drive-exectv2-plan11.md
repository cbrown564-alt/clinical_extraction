# 0030: Focus ExECT development on four entity types

Date: 2026-06-19
Status: accepted

Current ExECT optimization covers diagnosis, seizure frequency, prescriptions,
and investigations. The development target is F1 above 0.900 for each entity
before any holdout or published-benchmark claim.

Other ExECT entities remain diagnostic unless a later decision expands scope.
Reports lead with the four entity scores and may add their micro-average. They
must preserve raw model output separately from deterministic changes. Any rule
that changes a selected fact, state, or entity membership is part of the
combined method and must be named, tested, and removed in a component comparison.
