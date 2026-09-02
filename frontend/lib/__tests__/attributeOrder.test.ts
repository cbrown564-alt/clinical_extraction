import {
  attributeRank,
  inventoryCardAttributeKeys,
  sortedAttributeKeys,
  workbenchAttributeKeys,
} from "../attributeOrder";

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

  it("puts CT results before performed", () => {
    expect(
      sortedAttributeKeys(["CT_Performed", "CUI", "CT_Results", "CUIPhrase"], "Investigations")
    ).toEqual(["CUI", "CUIPhrase", "CT_Results", "CT_Performed"]);
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
    expect(attributeRank("kind", "GanEvent")).toBe("primary");
    expect(attributeRank("temporality", "GanEvent")).toBe("payload");
  });
});

describe("workbenchAttributeKeys", () => {
  it("omits Certainty and Negation from ExECT workbench tables", () => {
    expect(
      workbenchAttributeKeys(
        ["Negation", "CUIPhrase", "Certainty", "DiagCategory", "CUI"],
        "Diagnosis"
      )
    ).toEqual(["CUI", "CUIPhrase", "DiagCategory"]);
  });
});

describe("inventoryCardAttributeKeys", () => {
  it("keeps Diagnosis CUI, CUIPhrase, and DiagCategory", () => {
    expect(
      inventoryCardAttributeKeys(
        {
          CUI: "C0751495",
          CUIPhrase: "focal-seizures",
          DiagCategory: "MultipleSeizures",
          Certainty: "5",
          Negation: "Affirmed",
        },
        "Diagnosis"
      )
    ).toEqual(["CUI", "CUIPhrase", "DiagCategory"]);
  });

  it("keeps every filled Prescription workbench field", () => {
    expect(
      inventoryCardAttributeKeys(
        {
          CUI: "C0064636",
          CUIPhrase: "lamotrigine",
          DrugName: "lamotrigine",
          DrugDose: "150",
          DoseUnit: "mg",
          Frequency: "2",
        },
        "Prescription"
      )
    ).toEqual(["CUI", "CUIPhrase", "DrugName", "DrugDose", "DoseUnit", "Frequency"]);
  });

  it("keeps every filled Investigations workbench field", () => {
    expect(
      inventoryCardAttributeKeys(
        {
          CUI: "C0436481",
          CUIPhrase: "mri normal",
          MRI_Performed: "Yes",
          MRI_Results: "Normal",
          EEG_Performed: "Yes",
          EEG_Results: "Abnormal",
        },
        "Investigations"
      )
    ).toEqual([
      "CUI",
      "CUIPhrase",
      "EEG_Performed",
      "EEG_Results",
      "MRI_Performed",
      "MRI_Results",
    ]);
  });

  it("keeps filled SeizureFrequency count and time fields", () => {
    expect(
      inventoryCardAttributeKeys(
        {
          CUI: "C0036572",
          CUIPhrase: "seizures",
          NumberOfSeizures: "4",
          TimeSince_or_TimeOfEvent: "since last clinic",
          PointInTime: "March",
          FrequencyChange: "",
        },
        "SeizureFrequency"
      )
    ).toEqual([
      "CUI",
      "CUIPhrase",
      "NumberOfSeizures",
      "TimeSince_or_TimeOfEvent",
      "PointInTime",
    ]);
  });
});
