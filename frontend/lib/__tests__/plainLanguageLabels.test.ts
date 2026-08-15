import { lastRuleActionLabel } from "../plainLanguageLabels";

describe("lastRuleActionLabel", () => {
  it("is blank for the unchanged baseline", () => {
    expect(lastRuleActionLabel("")).toBe("");
    expect(lastRuleActionLabel(undefined)).toBe("");
  });

  it("uses a plain sentence for known dictionary actions", () => {
    expect(lastRuleActionLabel("normalized_prescription_from_dictionary")).toBe(
      "Dictionary normalized this regimen"
    );
  });

  it("falls back to words for an unknown action", () => {
    expect(lastRuleActionLabel("split_prescription_regimen_from_dictionary")).toBe(
      "Dictionary split this regimen"
    );
    expect(lastRuleActionLabel("some_new_rule")).toBe("Some New Rule");
  });
});
