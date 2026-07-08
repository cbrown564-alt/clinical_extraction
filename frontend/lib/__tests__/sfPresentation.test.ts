import { phraseSurfaceKind, displayPhraseNorm } from "../sfPresentation";

describe("phraseSurfaceKind", () => {
  it("treats hyphen and plural-s differences as surface spelling", () => {
    expect(
      phraseSurfaceKind(
        "focal-to-bilateral-convulsive-seizure",
        "Focal to bilateral convulsive seizures"
      )
    ).toBe("surface");
    expect(displayPhraseNorm("focal-to-bilateral-convulsive-seizure")).toBe(
      displayPhraseNorm("Focal to bilateral convulsive seizures")
    );
  });

  it("flags genuinely different phrases as substantive", () => {
    expect(phraseSurfaceKind("myoclonic jerks", "generalised tonic clonic seizures")).toBe(
      "substantive"
    );
  });

  it("detects identical strings", () => {
    expect(phraseSurfaceKind("seizures", "seizures")).toBe("identical");
  });
});
