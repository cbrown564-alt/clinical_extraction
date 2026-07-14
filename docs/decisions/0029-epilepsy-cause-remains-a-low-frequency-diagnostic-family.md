# EpilepsyCause Remains a Low-Frequency Diagnostic Family

Date: 2026-06-18

Decision: do not promote `EpilepsyCause` to a new targeted extractor in the current ExECTv2 Plan 11 follow-up. Keep it as a low-frequency atomic diagnostic family scored through the `Concept-Identity Headline`, with certainty/negation and CUI handled as deterministic projection layers.

Development evidence supports treating EpilepsyCause as a small, representation-bound diagnostic family rather than a high-return specialist route. The gold schema has only 36 EpilepsyCause mentions in the 200-letter corpus, with no decomposable clinical attributes beyond CUI/CUIPhrase plus `Certainty` and `Negation`. In the Plan 11 dev140 replay, the all-entities LLM-first pass collapsed for EpilepsyCause (`0.000` F1), while deterministic all-9 reached `0.622` and the LLM-with-rules all-entities comparator reached only `0.200`. That is evidence that the broad single pass under-selects causes, but not evidence that a new targeted extractor is the best next architectural investment.

The strongest pro-extractor evidence is Phase B's focused per-entity probe: EpilepsyCause source-near recall rose from `0.286` to `0.809`, the largest recall lift among the nine entities. The same readout classified the family as `representation_bound`, reported low semantic item F1 (`0.175`), and increased over-emission from `6` to `42`. These development results point to boundary and projection control as important errors: deciding whether a structural lesion, syndrome, risk factor, history item, or aetiology statement is asserted as the epilepsy cause, then rendering the normalized concept and CUI. The Plan 11 certainty audit reported `0.95` certainty accuracy and `1.00` negation accuracy over gold rows. Keep deterministic certainty and negation projection as the default unless a predeclared comparison supports moving it.

Ownership and opportunity cost both argue against promotion now. EpilepsyCause is an atomic concept family, not a decomposable state object like SeizureFrequency or a high-volume operational family like Prescription and Investigations. A specialist cause extractor would add another prediction-bearing route and another over-emission control point for a small numerator. Prefer reusing the Diagnosis/PatientHistory concept-boundary code where it fits; justify a parallel family-specific route with a focused comparison.

Supported claim:

> EpilepsyCause is currently best treated as a low-frequency, representation-bound diagnostic concept family: LLM candidates can produce many cause concepts, but current evidence points to causal-boundary, projection, and over-emission control rather than to a justified standalone targeted extractor.

Not supported:

> The all-entities single LLM pass adequately recovers EpilepsyCause.

Not supported:

> A targeted EpilepsyCause extractor is already justified as a primary ExECTv2 architecture component.

Revisit this decision only with a predeclared dev-only study showing that EpilepsyCause errors are a material architecture bottleneck after concept projection, and that a cause-specific route improves concept-identity precision/recall over the existing diagnostic-family treatment without increasing causal-context over-emission. The revisit package must include a dev row-level boundary taxonomy, an ownership-clean comparison against the existing per-entity focused frame and deterministic projection layers, and explicit evidence that the gain is worth diverting effort from SeizureFrequency and the higher-frequency essential families. It must not use Gan holdout/test row-level artifacts or new model calls unless separately authorized and predeclared.
