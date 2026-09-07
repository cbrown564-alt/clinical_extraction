import bundle from "./viva-data.json";

export type DemoCase = (typeof bundle.cases)[number];
export type DemoEvent = DemoCase["record"]["events"][number];
export const demoCases = bundle.cases;
export const guidedCases = bundle.guided_ids.map(id => demoCases.find(c => c.id === id)!);
export const batchCases = bundle.batch_ids.map(id => demoCases.find(c => c.id === id)!);
export const batchPolicy = bundle.batch_policy;
export const demoProvenance = { dataset: bundle.dataset, split: bundle.split, model: bundle.model, repair: bundle.repair_mode };

export const caseStories: Record<number, { title: string; question: string; lesson: string; rule: string; explanation: string; calculation?: string; caveat?: string }> = {
  16021: {
    title: "Two months of evidence",
    question: "Five seizures in April. Is that the whole answer?",
    lesson: "A letter can contain more than one useful frequency statement. Extract keeps them; decide applies a policy to the record.",
    rule: "Combine the diary counts",
    explanation: "The diary policy totals the recorded counts over the inclusive calendar span, February through April. March is part of the denominator; its count is not separately reported.",
    calculation: "(3 + 1) + (5 + 0) = 9 seizures · February–April = 3 months",
  },
  10: {
    title: "A straightforward rate",
    question: "What does “four per day” become?",
    lesson: "Begin with one clear frequency statement. The model keeps the quote and writes a label in the required form.",
    rule: "Keep the provisional answer",
    explanation: "The extraction call has already expressed the upper bound as 4 per day, following the allowed-label instructions. The decision rules make no further change.",
  },
  14187: {
    title: "Seizures, then seizure freedom",
    question: "Seizure-free now. What about the recent events?",
    lesson: "The letter describes a brief run of seizures after a medication change, followed by seizure freedom. Both statements belong in the evidence record.",
    rule: "Account for the post-change seizures",
    explanation: "The post-change burst rule uses the recorded count and time window to revise the seizure-free proposal. This is the study’s decision policy, rather than a new clinical judgement.",
    caveat: "The rule changes the label but retains the original E2 selection and seizure-free quote. The saved trace exposes this attribution limitation; it does not claim that E2 alone supports the new rate.",
  },
  11254: {
    title: "A last event and its time window",
    question: "A dated seizure, followed by three quiet months.",
    lesson: "A date and an event-free interval support more than one possible interpretation. The policy determines which representation is submitted.",
    rule: "Count the last event over the interval",
    explanation: "The last-event rule writes 1 per 3 month from the dated seizure and subsequent interval. Both executors produce this label, but the gold label is unknown. Agreement between executors does not establish correctness.",
    caveat: "Both final answers disagree with the gold label on this development example.",
  },
  743: {
    title: "When the evidence is ambiguous",
    question: "How often is “most shifts”?",
    lesson: "The evidence can be quoted exactly while the frequency remains uncertain. Inspecting the words makes that uncertainty visible.",
    rule: "Retain unknown frequency",
    explanation: "The model does not infer how many shifts the patient works. The rules leave unknown unchanged. The gold label is multiple per week, so this is a scored error despite the exact quote.",
    caveat: "An exact quotation checks where the words came from. It does not prove that the answer is correct or that the quote is sufficient.",
  },
};

export function storyFor(current: DemoCase) {
  return caseStories[current.id] ?? {
    title: `Letter ${current.id}`,
    question: "From a batch result back to its evidence.",
    lesson: "Open the original passage, inspect the extracted events, and follow the recorded decision before using this result.",
    rule: current.hybrid.hops.some(h => h.changed) ? "A recorded rule changed the answer" : "Keep the provisional answer",
    explanation: current.hybrid.hops.some(h => h.changed)
      ? "The trace below records each label change. The source quotes and the original extraction remain available for inspection."
      : "No rule changed the provisional label on this record. Keeping an answer is still a decision under the fixed policy.",
    caveat: current.hybrid_correct ? undefined : "The final answer does not match the gold Purist category on this development letter.",
    calculation: undefined,
  };
}

export const categoryNames: Record<string, string> = {
  seizure_frequent: "Frequent", seizure_infrequent: "Infrequent",
  currently_no_seizure: "Seizure-free", seizure_freq_unknown: "Unknown",
};

/** Display recorded attribution, without inventing new support for a rule rewrite. */
export function decisionEvidence(current: DemoCase) {
  const selection = current.hybrid.selection;
  const original = current.record.selection;
  const ids = selection.selected_event_ids;
  const quotes = selection.evidence && current.note.includes(selection.evidence)
    ? [selection.evidence]
    : current.record.events.filter(e => ids.includes(e.event_id) && e.evidence && current.note.includes(e.evidence)).map(e => e.evidence);
  const attributionUnchanged = selection.final_label !== original.final_label
    && selection.evidence === original.evidence
    && JSON.stringify(ids) === JSON.stringify(original.selected_event_ids);
  return { ids, quotes, attributionUnchanged };
}

export function exportBatch(records: DemoCase[]) {
  return {
    purpose: "Illustrative research export; predictions are not reviewed training labels.",
    ...demoProvenance, selection: batchPolicy,
    records: records.map(c => ({ source_id: c.id, label: c.hybrid.selection.final_label,
      category: categoryNames[c.category] ?? c.category, evidence_record: c.record,
      decision_trace: c.hybrid, extraction_sha256: c.sha256,
      source_artifact: c.extract_source, source_text: c.note, review_status: "not_reviewed" })),
  };
}

export function evidenceParagraphs(note: string, events: DemoEvent[]): string[] {
  return note.split(/\n\s*\n/).filter(p => events.some(e => p.includes(e.evidence)));
}

/** Split without altering the source; overlap is represented by all matching IDs. */
export function quoteSegments(text: string, events: DemoEvent[]) {
  const spans = events.flatMap(e => {
    const found: { start: number; end: number; id: string }[] = [];
    if (!e.evidence) return found;
    let start = text.indexOf(e.evidence);
    while (start !== -1) {
      found.push({ start, end: start + e.evidence.length, id: e.event_id });
      start = text.indexOf(e.evidence, start + e.evidence.length);
    }
    return found;
  });
  const boundaries = [...new Set([0, text.length, ...spans.flatMap(s => [s.start, s.end])])].sort((a, b) => a - b);
  return boundaries.slice(0, -1).map((start, i) => ({
    text: text.slice(start, boundaries[i + 1]),
    ids: spans.filter(s => s.start <= start && s.end >= boundaries[i + 1]).map(s => s.id),
  }));
}
