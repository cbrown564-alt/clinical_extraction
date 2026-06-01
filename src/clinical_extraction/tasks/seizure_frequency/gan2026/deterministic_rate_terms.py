from __future__ import annotations

WORD_TOKEN = r"[a-z][a-z\-‑–—]*"
SEIZURE_TERMS = (
    r"seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|"
    r"myoclonics?|jerks?|auras?|status epilepticus"
)
QUALIFIED_SEIZURE_TERMS = rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})"
SEIZURE_RATE_PHRASE = (
    rf"(?:(?:tonic-clonic|myoclonic|convulsive|focal|absence|drop|epileptic|"
    rf"impaired awareness|focal onset|petit mal|brief)\s+){{0,4}}(?:{SEIZURE_TERMS})"
)
SEIZURE_DESCRIPTOR_PHRASE = (
    r"(?:tonic-clonic|myoclonic|convulsive|focal(?:\s+[a-z][a-z-]*){0,3}|"
    r"absence|drop|epileptic|impaired awareness|focal onset|petit mal|simple partial)"
)
SEIZURE_TYPE_DESCRIPTOR = (
    r"(?:focal\s+(?:non-motor|sensory|tonic|clonic|motor|aware|impaired-awareness|"
    r"impaired\s+awareness)|tonic|atonic|myoclonic|absence|petit\s+mal)"
)
