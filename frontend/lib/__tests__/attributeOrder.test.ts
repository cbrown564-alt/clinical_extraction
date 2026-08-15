import { sortedAttributeKeys } from "../attributeOrder";

describe("sortedAttributeKeys", () => {
  it("orders gold and predicted keys alphabetically regardless of insertion order", () => {
    expect(
      sortedAttributeKeys([
        "Certainty",
        "CUI",
        "CUIPhrase",
        "DiagCategory",
        "Negation",
      ])
    ).toEqual(["Certainty", "CUI", "CUIPhrase", "DiagCategory", "Negation"]);
    expect(
      sortedAttributeKeys(["Negation", "CUIPhrase", "CUI", "DiagCategory", "Certainty"])
    ).toEqual(["Certainty", "CUI", "CUIPhrase", "DiagCategory", "Negation"]);
  });
});
