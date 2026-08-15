import { attributeRank, sortedAttributeKeys } from "../attributeOrder";

describe("sortedAttributeKeys", () => {
  it("pins CUI then CUIPhrase, then Diagnosis payload, then qualifiers", () => {
    expect(
      sortedAttributeKeys(
        ["Negation", "CUIPhrase", "Certainty", "DiagCategory", "CUI"],
        "Diagnosis"
      )
    ).toEqual(["CUI", "CUIPhrase", "DiagCategory", "Certainty", "Negation"]);
  });

  it("orders prescription as name, dose, unit, frequency", () => {
    expect(
      sortedAttributeKeys(
        ["Frequency", "CUI", "DoseUnit", "DrugDose", "CUIPhrase", "DrugName"],
        "Prescription"
      )
    ).toEqual(["CUI", "CUIPhrase", "DrugName", "DrugDose", "DoseUnit", "Frequency"]);
  });

  it("orders seizure frequency as change, count, cadence, then time window", () => {
    expect(
      sortedAttributeKeys(
        [
          "TimePeriod",
          "UpperNumberOfSeizures",
          "CUI",
          "PointInTime",
          "NumberOfTimePeriods",
          "FrequencyChange",
          "LowerNumberOfSeizures",
          "TimeSince_or_TimeOfEvent",
          "CUIPhrase",
        ],
        "SeizureFrequency"
      )
    ).toEqual([
      "CUI",
      "CUIPhrase",
      "FrequencyChange",
      "LowerNumberOfSeizures",
      "UpperNumberOfSeizures",
      "NumberOfTimePeriods",
      "TimePeriod",
      "TimeSince_or_TimeOfEvent",
      "PointInTime",
    ]);
  });

  it("ranks identity, primary, payload, and qualifier separately", () => {
    expect(attributeRank("CUI", "Diagnosis")).toBe("identity");
    expect(attributeRank("DiagCategory", "Diagnosis")).toBe("primary");
    expect(attributeRank("DrugDose", "Prescription")).toBe("payload");
    expect(attributeRank("Negation", "Diagnosis")).toBe("qualifier");
    expect(attributeRank("LowerNumberOfSeizures", "SeizureFrequency")).toBe("primary");
    expect(attributeRank("UpperNumberOfSeizures", "SeizureFrequency")).toBe("primary");
    expect(attributeRank("LowerNumberOfTimePeriods", "SeizureFrequency")).toBe("primary");
    expect(attributeRank("UpperNumberOfTimePeriods", "SeizureFrequency")).toBe("primary");
  });
});
