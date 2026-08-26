import { normalizeLetterDisplay } from "../letterDisplay";

describe("normalizeLetterDisplay", () => {
  it("collapses extra blank lines to one paragraph break", () => {
    const raw =
      "NHS No 1\nDate 19/9/2016\n\n\n\nDear Dr\n\nI reviewed this man today.\n\n\nHe remains well.";
    const { text } = normalizeLetterDisplay(raw);
    expect(text).toBe(
      "NHS No 1\nDate 19/9/2016\n\nDear Dr\n\nI reviewed this man today.\n\nHe remains well."
    );
  });

  it("inserts one paragraph break before jammed sections and body prose", () => {
    const raw = [
      "40, Hospital pass, Johnstown. SA5 3ZZ",
      "Diagnosis\t1. Dissociative seizures",
      "\t\t2. Symptomatic structural epilepsy",
      "Medication:\tLevetiracetam 1000mg bd",
      "I reviewed this 56-year-old man in clinic today.",
    ].join("\n");
    const { text } = normalizeLetterDisplay(raw);
    expect(text).toBe(
      [
        "40, Hospital pass, Johnstown. SA5 3ZZ",
        "",
        "Diagnosis\t1. Dissociative seizures",
        "\t\t2. Symptomatic structural epilepsy",
        "",
        "Medication:\tLevetiracetam 1000mg bd",
        "",
        "I reviewed this 56-year-old man in clinic today.",
      ].join("\n")
    );
  });

  it("keeps highlight offsets on the same evidence after rewriting", () => {
    const raw =
      "Date 19/9/2016\n\n\nDiagnosis\tDissociative seizures\nMedication:\tLevetiracetam";
    const evidence = "Dissociative seizures";
    const start = raw.indexOf(evidence);
    const { text, remap } = normalizeLetterDisplay(raw);
    expect(text.slice(remap(start), remap(start + evidence.length))).toBe(
      evidence
    );
  });
});
