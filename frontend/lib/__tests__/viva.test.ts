import { createHash } from "node:crypto";
import { batchCases, demoCases, decisionEvidence, evidenceParagraphs, exportBatch, guidedCases, quoteSegments } from "../viva";
import method from "../viva-method.json";

describe("viva evidence boundaries", () => {
  it("pairs batch answers with their recorded selection and exposes unchanged attribution after rewrites", () => {
    const c = batchCases.find(c => c.id === 8924)!;
    expect(decisionEvidence(c)).toEqual({
      ids: ["e2"], quotes: [c.hybrid.selection.evidence], attributionUnchanged: false,
    });
    expect(decisionEvidence(c).quotes).not.toContain(c.record.events[0].evidence);
    const multi = batchCases.find(c => c.id === 1591)!;
    expect(decisionEvidence(multi).ids).toEqual(["e1", "e2"]);
    const rewritten = batchCases.find(c => c.id === 14821)!;
    expect(decisionEvidence(rewritten).attributionUnchanged).toBe(true);
    expect(decisionEvidence(rewritten).ids).toEqual(["e3"]);
    const missing = structuredClone(c);
    missing.hybrid.selection.evidence = "not in the letter";
    missing.hybrid.selection.selected_event_ids = ["missing"];
    expect(decisionEvidence(missing).quotes).toEqual([]);
  });
  it("retains exact source quotes and the unmodified extraction for every bundled development record", () => {
    expect(guidedCases.map(c => c.id)).toEqual([16021, 10, 14187, 11254, 743]);
    expect(batchCases).toHaveLength(25);
    expect(new Set(batchCases.map(c => c.id)).size).toBe(25);
    for (const c of demoCases) {
      expect(c.extract_source).toContain("/dev750/");
      expect(createHash("sha256").update(c.raw).digest("hex")).toBe(c.sha256);
      const raw = JSON.parse(c.raw.slice(c.raw.indexOf("{"), c.raw.lastIndexOf("}") + 1));
      expect(raw.selection.final_label).toBe(c.record.selection.final_label);
      expect(c.decide_input.events.map(e => [e.event_id, e.evidence])).toEqual(c.record.events.map(e => [e.event_id, e.evidence]));
      for (const e of c.record.events) {
        expect(e.evidence.length).toBeGreaterThan(0);
        expect(c.note).toContain(e.evidence);
        expect(evidenceParagraphs(c.note, c.record.events).join("\n\n")).toContain(e.evidence);
      }
    }
  });

  it("does not manufacture source links when quotes overlap, repeat, or are missing", () => {
    const event = guidedCases[0].record.events[0];
    const events = [{ ...event, event_id: "e1", evidence: "two seizures" }, { ...event, event_id: "e2", evidence: "seizures" }, { ...event, event_id: "missing", evidence: "three seizures" }];
    const text = "two seizures, then two seizures";
    const segments = quoteSegments(text, events);
    expect(segments.map(s => s.text).join("")).toBe(text);
    expect(segments.filter(s => s.ids.length === 2)).toHaveLength(2);
    expect(segments.some(s => s.ids.includes("missing"))).toBe(false);
  });

  it("exports only chosen predictions with evidence and an explicit review status", () => {
    const output = exportBatch(batchCases.slice(0, 2));
    expect(output.split).toBe("dev750");
    expect(output.records).toHaveLength(2);
    output.records.forEach((r, i) => {
      expect(r.review_status).toBe("not_reviewed");
      expect(r.source_text).toBe(batchCases[i].note);
      expect(r.label).toBe(batchCases[i].hybrid.selection.final_label);
      expect(r).not.toHaveProperty("gold");
      expect(r.decision_trace).toEqual(batchCases[i].hybrid);
    });
  });

  it("keeps prompts and rule source distinct, with known failure cases visible", () => {
    expect(method.prompts.extract).not.toHaveProperty("note_text");
    expect(method.prompts.decide).not.toHaveProperty("note_text");
    expect(method.prompts.decide).not.toHaveProperty("events");
    expect(method.rules.decide.find(r => r.id === "gan.select.monthly_diary")?.source).toContain("def monthly_diary_label_from_events");
    expect(guidedCases.find(c => c.id === 743)?.hybrid_correct).toBe(false);
    const revised = guidedCases.find(c => c.id === 14187)!;
    expect(revised.hybrid.selection.selected_event_ids).toEqual(["e2"]);
    expect(revised.hybrid.selection.final_label).not.toBe(revised.record.selection.final_label);
  });
});
