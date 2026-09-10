# Independent annotation inputs: complete attempt coverage

The 48 files under inputs are the only model-facing payloads. Each contains five
questions and physically filtered letters. Run each in a fresh context; do not
carry a later-view job into an earlier-view job. An independent annotator must
not see the existing case references, scenario descriptions or this conversation.
Give the annotator these files alone, without repository access to reference data.
These input files are frozen preparatory material. The separately saved medium-effort
agy pass returned 44 jobs, failed four and left none unstarted. See
`../agy_pass_medium/analysis_evidence_v2.json` and the canonical pilot disagreement report.

Before running, record annotator/model identity, exact model/configuration, prompt
hash, and whether the annotator previously saw these references. The authorized
additional paid-call budget remains £0; this pack does not authorize a provider run.
Store each untouched output alongside a separate record with actual start/end
UTC times, failures, token usage/cost if applicable and any subsequent repair.
Keep raw output separate from repaired output. For manual work record actual time
by family, temporal annotation and linkage; do not estimate it from answer length.
Model wall time is not human annotation effort.

After all jobs are saved, compare all 240 answers and assertions/links by family
and temporal field against the corresponding permitted reference subset. Preserve
unresolved disagreements; do not fit the reference to the second pass. Do not
report kappa, agreement or field utility until real outputs and a stated matching
procedure support the calculations. AI agreement remains distinct from expert review.

Language audit: rendered input inspected; instructions use plain language;
research metadata is separate; non-obvious fields have descriptions; internal
jargon removed or defined; length matches the structured task. No experimental
wording deviations. No provider compatibility or extraction performance claimed.
