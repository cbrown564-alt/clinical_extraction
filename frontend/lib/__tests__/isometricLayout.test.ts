import {
  lensRewriteLine,
  lensThisCaseLine,
  sourceLetterLine,
  usefulStageNote,
} from "../isometricLayout";
import type { StageObservationData } from "../isometricTypes";

const lensObs = (
  note: string,
  changed: boolean
): StageObservationData => ({
  stage_id: "exect.llm_with_rules.lens.diagnosis",
  stage_name: "Diagnosis",
  owner: "deterministic",
  effect_class: "clinical_meaning",
  input: "in",
  output: "out",
  changed,
  note,
});

describe("sourceLetterLine", () => {
  it("prefers the gold span when the letter has one", () => {
    expect(
      sourceLetterLine(
        "Centre for Epilepsy\n\nShe has monthly seizures.",
        "monthly seizures",
        "Quiet interval versus cluster grammar"
      )
    ).toBe("monthly seizures");
  });

  it("uses the teaching story when ExECT has no gold span", () => {
    expect(
      sourceLetterLine(
        "Centre for Epilepsy\nQueen Square, London\nDear Dr Fiona,",
        "",
        "All four families are present; seizure-frequency windows must stay named."
      )
    ).toBe(
      "All four families are present; seizure-frequency windows must stay named."
    );
  });
});

describe("lensRewriteLine", () => {
  it("uses the first clinical rewrite note", () => {
    expect(
      lensRewriteLine([
        lensObs("Assembled this family; no further clinical rewrite.", false),
        lensObs("Dictionary rewrote diagnosis: a → b.", true),
      ])
    ).toBe("Dictionary rewrote diagnosis: a → b.");
  });

  it("does not surface the generic hybrid filler", () => {
    expect(usefulStageNote("Canonical LLM-with-rules stage.")).toBe("");
    expect(lensRewriteLine([lensObs("Canonical LLM-with-rules stage.", true)])).toBe(
      ""
    );
    expect(
      lensThisCaseLine(
        { id: "diagnosis", label: "Diagnosis", stageIdPattern: "lens.diagnosis" },
        lensObs("Canonical LLM-with-rules stage.", true)
      )
    ).toBe("Diagnosis");
    expect(
      lensThisCaseLine(
        { id: "diagnosis", label: "Diagnosis", stageIdPattern: "lens.diagnosis" },
        lensObs("Canonical LLM-with-rules stage.", false)
      )
    ).toBe("Diagnosis: assembled, no rewrite");
  });
});
