# 0033: LLM-only ExECT predicts de-duplicated clinical facts

Date: 2026-06-23
Status: closed negative

The LLM-only study asked the model to emit the facts used by the internal
clinical recovery score: diagnosis and assertion, seizure type and state,
current medication regimen, and investigation status and result. Deterministic
code could parse JSON, check evidence, and map those emitted facts to the scorer;
it could not add facts or choose omitted states.

The study did not exceed 0.900 on dev140 or replace the selected combined method.
The GEPA result remains as a negative LLM-only comparison. Its selected program,
adapter, outputs, tests, and evidence limit are recorded in the retained
evidence index. Do not describe it as clearing the published strict benchmark.
