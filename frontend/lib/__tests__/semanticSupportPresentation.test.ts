import {
  clinicalSupportFromShortcut,
  presentConclusionFields,
  shouldSaveReviewShortcut,
  structureConclusionFields,
} from "../semanticSupportPresentation";

describe("presentConclusionFields", () => {
  it("turns investigation keys into readable review claims", () => {
    expect(
      presentConclusionFields({
        text: "CT Head",
        normalized_concept: "C0436539",
        assertion: null,
        attributes: {
          CT_Performed: "Yes",
          CT_Results: "Abnormal",
          CUI: "C0436539",
          CUIPhrase: "ct abnormal",
        },
      })
    ).toEqual([
      { label: "Investigation", value: "CT Head" },
      { label: "Performed", value: "Yes" },
      { label: "Result", value: "Abnormal" },
      { label: "Standard concept", value: "ct abnormal (C0436539)" },
      { label: "Assertion and time", value: "Not specified" },
    ]);
  });

  it("keeps unfamiliar attributes visible with readable labels", () => {
    expect(
      presentConclusionFields({
        text: "Lamotrigine",
        assertion: "present",
        attributes: { dose_frequency: "twice daily" },
      })
    ).toEqual([
      { label: "Finding", value: "Lamotrigine" },
      { label: "Dose frequency", value: "twice daily" },
      { label: "Assertion and time", value: "present" },
    ]);
  });
});

describe("clinicalSupportFromShortcut", () => {
  it("maps the review keys to the three clinical support values", () => {
    expect(clinicalSupportFromShortcut("s")).toBe("supported");
    expect(clinicalSupportFromShortcut("D")).toBe("unsupported");
    expect(clinicalSupportFromShortcut("a")).toBe("unclear");
    expect(clinicalSupportFromShortcut("x")).toBeNull();
  });
});

describe("shouldSaveReviewShortcut", () => {
  it("uses Enter everywhere in the review, including while writing notes", () => {
    expect(shouldSaveReviewShortcut("Enter", "BUTTON")).toBe(true);
    expect(shouldSaveReviewShortcut("Enter", "BODY")).toBe(true);
    expect(shouldSaveReviewShortcut("Enter", "TEXTAREA")).toBe(true);
    expect(shouldSaveReviewShortcut("Enter", "INPUT")).toBe(false);
    expect(shouldSaveReviewShortcut(" ", "BODY")).toBe(false);
  });
});

describe("structureConclusionFields", () => {
  it("separates the clinical finding headline from its associated metadata", () => {
    expect(
      structureConclusionFields([
        { label: "Finding", value: "Focal seizures with altered awareness" },
        { label: "Number of seizures", value: "0" },
        { label: "Assertion and time", value: "Not specified" },
      ])
    ).toEqual({
      headline: { label: "Finding", value: "Focal seizures with altered awareness" },
      metadata: [
        { label: "Number of seizures", value: "0" },
        { label: "Assertion and time", value: "Not specified" },
      ],
    });
  });
});
