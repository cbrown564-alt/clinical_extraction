export const QUERIES = [
  { id: "Q1", title: "Epilepsy with a recent seizure", detail: "Documented epilepsy at the index date and an epileptic event in the preceding 90 days." },
  { id: "Q2", title: "Two concurrent epileptic patterns", detail: "At least two distinct epileptic patterns active together during the preceding 90 days." },
  { id: "Q3", title: "Lamotrigine started", detail: "Confirmed actual initiation of lamotrigine in the preceding 180 days. A plan alone does not qualify." },
  { id: "Q4", title: "EEG requested with a result", detail: "An EEG requested in the preceding 180 days, with a matched result available to the clinical team by the index date." },
  { id: "Q5", title: "Events reinterpreted as non-epileptic", detail: "A previously epileptic event occurring in the preceding 180 days, explicitly reinterpreted by the index date." },
] as const;
export type Status = "eligible" | "ineligible" | "indeterminate" | "failed";
export type Evidence = { letter_id: string; start: number; end: number; text: string };
export type Letter = { letter_id: string; visit_date: string; available_date: string; text: string; sha256: string };
export type ClinicalTime = { kind: string; text: string | null; start: { earliest: string | null; latest: string | null } | null; end: { earliest: string | null; latest: string | null } | null };
export type Assertion = {
  assertion_id: string; letter_id: string; evidence: Evidence[]; reporter: string;
  certainty: string; polarity: string; coverage: string; time: ClinicalTime | null;
  content: { family: string; name?: string; names?: string[]; kind?: string; interpretation?: string; status?: string; modality?: string; result?: string | null; burden?: { text: string | null } | null };
};
export type HistoryLink = { link_id: string; relation: string; earlier_assertion: string; later_assertion: string; evidence: Evidence[]; decision_time: ClinicalTime | null };
export type Answer = { request_id: string; query_id: string; status: Status; reason?: string; error?: string; evidence: Evidence[]; rule_ids: string[]; conflicted_assertion_ids?: string[] };
export type Frame = {
  program_version: string; status: "ready" | "failed"; error?: string;
  documents: Letter[]; answers: Answer[];
  requests: { index_date: string; information_cutoff: string; view: string; lookback_90_start: string; lookback_180_start: string }[];
  history?: { assertion_ids: string[]; accounts: Assertion[]; links: HistoryLink[] }[];
  provenance: { mode: string; attempt?: { model_requested: string }; query_context_visible_during_extraction?: boolean };
  offset_repairs?: unknown[];
};
export type Patient = { id: string; case_id: string; label: string; origin: string };
export type LongitudinalData = {
  program_version: string; patients: Patient[]; selected: Frame;
  cohort: { patient: string; label: string; index_date: string; cutoff: string; status: Status; reason: string }[];
};
export function displayDate(value: string | null | undefined) {
  if (!value) return "Unknown date";
  const parsed = new Date(value + "T00:00:00Z");
  if (!Number.isFinite(parsed.getTime())) return "Unknown date";
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(parsed);
}
export function assertionTitle(a: Assertion) {
  return a.content.name ?? a.content.names?.join(", ") ?? a.content.modality ?? a.content.family;
}
function describeBound(bound: ClinicalTime["start"]) {
  if (!bound?.earliest && !bound?.latest) return "unknown";
  if (!bound.earliest) return `on or before ${displayDate(bound.latest)}`;
  if (!bound.latest) return `on or after ${displayDate(bound.earliest)}`;
  if (bound.earliest === bound.latest) return displayDate(bound.earliest);
  return `${displayDate(bound.earliest)} – ${displayDate(bound.latest)}`;
}
export function timeDescription(value: ClinicalTime | null) {
  if (!value) return "Time not established";
  if (value.text) return value.text;
  const start = describeBound(value.start);
  const end = describeBound(value.end);
  if (start === "unknown" && end === "unknown") return "Time not established";
  if (start === end || (end === "unknown" && value.kind === "as_of")) return start;
  return `Start ${start}; end ${end}`;
}
