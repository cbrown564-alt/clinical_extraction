import { isIdentityAttributeKey, sortedAttributeKeys } from "../attributeOrder";

describe("sortedAttributeKeys", () => {
  it("pins CUI and CUIPhrase first, then the rest alphabetically", () => {
    expect(
      sortedAttributeKeys([
        "Certainty",
        "CUI",
        "CUIPhrase",
        "DiagCategory",
        "Negation",
      ])
    ).toEqual(["CUI", "CUIPhrase", "Certainty", "DiagCategory", "Negation"]);
    expect(
      sortedAttributeKeys(["Negation", "CUIPhrase", "CUI", "DiagCategory", "Certainty"])
    ).toEqual(["CUI", "CUIPhrase", "Certainty", "DiagCategory", "Negation"]);
  });

  it("keeps only the identity keys that are present", () => {
    expect(sortedAttributeKeys(["Negation", "CUIPhrase", "DrugName"])).toEqual([
      "CUIPhrase",
      "DrugName",
      "Negation",
    ]);
    expect(isIdentityAttributeKey("CUI")).toBe(true);
    expect(isIdentityAttributeKey("Certainty")).toBe(false);
  });
});
