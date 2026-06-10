"""Deterministic ExECTv2 extractor — Satellite 02.

Anchor + association pipeline:
  text → anchor rules (seizure-type/event phrases) → resolve overlaps
       → attribute-extraction rules (rate/seizure-free/change) → resolve overlaps
       → associate attributes onto nearest anchor → PredictedLetter

Gold ``SeizureFrequency.text`` is a seizure-type/event-description phrase (the
"anchor"); frequency information (counts, periods, change direction) is
encoded purely as attributes. Anchors with no nearby frequency information are
dropped.

Phase 2: SeizureFrequency only.  Phase 6: all nine entities (anchors generalize
to Diagnosis-style entity detection).
"""
