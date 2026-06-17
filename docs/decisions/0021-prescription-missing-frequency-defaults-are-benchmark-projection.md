# Prescription Missing-Frequency Defaults Are Benchmark Projection

Date: 2026-06-17

When an ExECTv2 Prescription source span names an anti-seizure medication and dose but does not state a schedule, guideline defaults such as once daily or `As_Required` for rescue-medication conventions should be treated as benchmark projection rather than source-stated frequency extraction. This lets benchmark-facing output follow the annotation guideline while keeping clinical component reports honest about whether the schedule was actually recovered from the letter text.
