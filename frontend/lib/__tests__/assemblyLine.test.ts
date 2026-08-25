import {
  bandHasSteps,
  clickableFacts,
  displayPayload,
  factById,
  isEmptyPayload,
  hasMentionList,
  highlightToneForFact,
  isShapeCompareStage,
  parseStationFact,
  sameOutgoing,
} from "../assemblyLine";
import type { PredictedFactData } from "../assemblyLineTypes";

const fact = (overrides: Partial<PredictedFactData> = {}): PredictedFactData => ({
  fact_id: "diagnosis:structural:0",
  label: "symptomatic structural focal epilepsy",
  span: { start: 10, end: 40, text: "structural epilepsy" },
  transforms: [
    {
      stage_id: "exect.llm_pre_post.model_call",
      stage_name: "Model proposes findings",
      band: "propose",
      entered: "(none)",
      left: "Diagnosis: structural epilepsy",
      idle: false,
      note: "",
    },
    {
      stage_id: "exect.llm_pre_post.lens.diagnosis",
      stage_name: "Diagnosis family transform",
      band: "reshape",
      entered: "Diagnosis: Symptomatic structural epilepsy",
      left: "Diagnosis: symptomatic structural focal epilepsy",
      idle: false,
      note: "Dictionary rewrote diagnosis.",
    },
  ],
  gold: {
    label: "symptomatic-structural-focal-epilepsy",
    has_counterpart: true,
    note: "",
  },
  ...overrides,
});

describe("assembly line facts", () => {
  it("keeps only predicted spans as clickable facts", () => {
    const hidden = fact({ fact_id: "empty", span: null });
    expect(clickableFacts([fact(), hidden]).map((item) => item.fact_id)).toEqual([
      "diagnosis:structural:0",
    ]);
  });

  it("selects one fact by id", () => {
    expect(factById([fact()], "diagnosis:structural:0")?.label).toContain("structural");
    expect(factById([fact()], null)).toBeUndefined();
  });

  it("mutes bands that never touched the selected fact", () => {
    const selected = fact();
    expect(bandHasSteps(selected, "propose")).toBe(true);
    expect(bandHasSteps(selected, "reshape")).toBe(true);
    expect(bandHasSteps(selected, "gate")).toBe(false);
    expect(bandHasSteps(undefined, "propose")).toBe(false);
  });

  it("keeps payloads intact and treats empty sentinels as empty", () => {
    expect(isEmptyPayload("(none)")).toBe(true);
    expect(
      displayPayload(
        '{"family":"diagnosis","anchor_text":"focal motor seizures","evidence":"As you recall"}'
      )
    ).toContain('"anchor_text": "focal motor seizures"');
    expect(
      displayPayload(
        "{'family': 'diagnosis', 'anchor_text': 'focal motor seizures'}"
      )
    ).toContain("anchor_text");
    expect(
      sameOutgoing(
        '{\n  "anchor_text": "epilepsy"\n}',
        '{"anchor_text":"epilepsy"}'
      )
    ).toBe(true);
    expect(
      sameOutgoing(
        '{"event_state":{"attributes":{}}}',
        '{"event_state":{"attributes":{"NumberOfSeizures":"0"}}}'
      )
    ).toBe(false);
  });

  it("reads phrase and mention attributes from an event payload", () => {
    const view = parseStationFact(
      JSON.stringify({
        family: "seizure_frequency",
        anchor_text: "focal to bilateral convulsive seizures",
        evidence: "his last one was on Christmas day 2009",
        confidence: "high",
        rationale: "last occurrence date",
        mentions: [
          {
            entity: "SeizureFrequency",
            text: "focal to bilateral convulsive seizures",
            attributes: { YearDate: "2009", NumberOfSeizures: "0" },
          },
        ],
      })
    );
    expect(view).toEqual({
      kind: "structured",
      family: "SeizureFrequency",
      phrase: "focal to bilateral convulsive seizures",
      attributes: { YearDate: "2009", NumberOfSeizures: "0" },
      evidence: "his last one was on Christmas day 2009",
      confidence: "high",
      rationale: "last occurrence date",
    });
  });

  it("reads a flattened mention without losing attributes", () => {
    const view = parseStationFact(
      JSON.stringify({
        entity: "SeizureFrequency",
        text: "focal to bilateral convulsive seizures",
        attributes: { DayDate: "Christmas day", YearDate: "2009" },
        evidence: "his last one was on Christmas day 2009",
      })
    );
    expect(view.kind).toBe("structured");
    if (view.kind !== "structured") return;
    expect(view.attributes.DayDate).toBe("Christmas day");
    expect(view.phrase).toBe("focal to bilateral convulsive seizures");
  });

  it("reads gan event slots as a structured fact", () => {
    const view = parseStationFact(
      JSON.stringify({
        event_id: "e1",
        kind: "cluster_frequency",
        raw_value: "clusters of 5 seizures in a single day every up to 4 month",
        evidence: "She may remain seizure-free for up to 4 month",
        assertion_status: "asserted",
        temporality: "current",
        label: "unknown",
      })
    );
    expect(view.kind).toBe("structured");
    if (view.kind !== "structured") return;
    expect(view.family).toBe("GanEvent");
    expect(view.phrase).toBe(
      "clusters of 5 seizures in a single day every up to 4 month"
    );
    expect(view.evidence).toContain("seizure-free");
    expect(view.attributes.kind).toBe("cluster_frequency");
    expect(view.attributes.assertion_status).toBe("asserted");
    expect(view.attributes.label).toBe("unknown");
  });

  it("reads a gan extract object as events plus selection", () => {
    const view = parseStationFact(
      JSON.stringify({
        events: [
          {
            event_id: "e1",
            kind: "cluster_frequency",
            raw_value: "clusters of 5 seizures in a single day every up to 4 month",
            evidence: "She may remain seizure-free for up to 4 month",
            assertion_status: "asserted",
            temporality: "current",
          },
        ],
        selection: {
          selected_event_ids: ["e1"],
          final_kind: "frequency",
          final_label: "1 cluster per 4 month, 5 per cluster",
          evidence: "She may remain seizure-free for up to 4 month",
          confidence: "high",
          rationale: "cluster pattern",
        },
      })
    );
    expect(view.kind).toBe("gan_extract");
    if (view.kind !== "gan_extract") return;
    expect(view.events).toHaveLength(1);
    expect(view.events[0]?.phrase).toContain("clusters of 5");
    expect(view.events[0]?.attributes.kind).toBe("cluster_frequency");
    expect(view.selection?.phrase).toBe("1 cluster per 4 month, 5 per cluster");
    expect(view.selection?.attributes.selected_event_ids).toBe("e1");
  });

  it("keeps gan one-liners as prose and marks lens as compare stages", () => {
    expect(parseStationFact("5 per cluster [quiet interval]")).toEqual({
      kind: "prose",
      text: "5 per cluster [quiet interval]",
    });
    expect(isShapeCompareStage("exect.llm.parse_and_retry")).toBe(false);
    expect(isShapeCompareStage("exect.llm_pre_post.lens.diagnosis")).toBe(true);
    expect(isShapeCompareStage("exect.llm.model_call")).toBe(false);
    expect(isShapeCompareStage("gan.llm_with_rules.normalize_events")).toBe(true);
    expect(isShapeCompareStage("gan.rules.normalize")).toBe(true);
    expect(hasMentionList('{"mentions":[{"entity":"Diagnosis"}]}')).toBe(true);
    expect(hasMentionList('{"entity":"Diagnosis","attributes":{}}')).toBe(false);
  });

  it("colours letter spans by workbench family tone", () => {
    expect(highlightToneForFact(fact({ fact_id: "Diagnosis:structural:0" }))).toBe("hybrid");
    expect(
      highlightToneForFact(fact({ fact_id: "SeizureFrequency:christmas:6" }))
    ).toBe("llm");
    expect(highlightToneForFact(fact({ fact_id: "Prescription:keppra:1" }))).toBe(
      "success"
    );
    expect(
      highlightToneForFact(fact({ fact_id: "Investigations:mri:2" }))
    ).toBe("deterministic-alt");
    expect(highlightToneForFact(fact({ fact_id: "GAN-15431" }))).toBe("deterministic");
  });
});
