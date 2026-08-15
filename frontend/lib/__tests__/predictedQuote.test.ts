import { displayPredictedEvidence } from "../predictedQuote";

const spans = [
  { kind: "llm" as const, entity: "Diagnosis", text: "Symptomatic epilepsy" },
  {
    kind: "llm" as const,
    entity: "Diagnosis",
    text: "Symptomatic epilepsy with generalised tonic clonic seizures with right temporal meningioma",
  },
];

describe("displayPredictedEvidence", () => {
  it("keeps a letter quote that is already distinct from the answer", () => {
    expect(
      displayPredictedEvidence(
        {
          text: "symptomatic",
          evidence:
            "Diagnosis: Symptomatic epilepsy with generalised tonic clonic seizures with right temporal meningioma (2013)",
          entity: "Diagnosis",
        },
        spans
      )
    ).toBe(
      "Diagnosis: Symptomatic epilepsy with generalised tonic clonic seizures with right temporal meningioma (2013)"
    );
  });

  it("replaces an answer-only evidence string with the overlapping letter quote", () => {
    expect(
      displayPredictedEvidence(
        {
          text: "Symptomatic epilepsy",
          evidence: "Symptomatic epilepsy",
          entity: "Diagnosis",
        },
        spans
      )
    ).toBe(
      "Symptomatic epilepsy with generalised tonic clonic seizures with right temporal meningioma"
    );
  });

  it("leaves evidence alone when no longer quote exists", () => {
    expect(
      displayPredictedEvidence(
        { text: "Investigations", evidence: "Investigations", entity: "Investigations" },
        spans
      )
    ).toBe("Investigations");
  });
});
