import {
  GAN_INVENTORY_VIEW,
  INVENTORY_DISPLAY_FAMILIES,
  compactInventoryFact,
  inventoryEvidenceSpans,
  isGanInventoryView,
  isInventoryDisplayFamily,
  resolveInventoryRow,
} from "../ganInventory";

describe("Gan inventory workbench helpers", () => {
  it("omits SeizureFrequency from the inventory workbench families", () => {
    expect(INVENTORY_DISPLAY_FAMILIES).toEqual([
      "Diagnosis",
      "Prescription",
      "Investigations",
    ]);
    expect(isInventoryDisplayFamily("SeizureFrequency")).toBe(false);
    expect(isInventoryDisplayFamily("Diagnosis")).toBe(true);
  });

  it("recognises only the explicit inventory view", () => {
    expect(isGanInventoryView("inventory")).toBe(true);
    expect(isGanInventoryView(GAN_INVENTORY_VIEW)).toBe(true);
    expect(isGanInventoryView("exect")).toBe(false);
    expect(isGanInventoryView(null)).toBe(false);
  });

  it("keeps the current letter when it is in the 100-letter sample", () => {
    expect(resolveInventoryRow(5551, [2748, 5551, 2759], 2748)).toBe(5551);
  });

  it("falls back to the illustration letter when the current row is outside the sample", () => {
    expect(resolveInventoryRow(10, [2748, 5551, 2759], 2748)).toBe(2748);
    expect(resolveInventoryRow(null, [2748, 5551], 2748)).toBe(2748);
  });

  it("maps mention evidence onto letter spans without gold alignment", () => {
    const note = "Focal epilepsy on levetiracetam. MRI normal.";
    const spans = inventoryEvidenceSpans(
      [
        {
          entity: "Diagnosis",
          text: "Focal epilepsy",
          subtype: "Epilepsy",
          attributes: { DiagCategory: "Epilepsy" },
          evidence: "Focal epilepsy",
        },
        {
          entity: "Investigations",
          text: "MRI",
          subtype: "MRI:Normal",
          attributes: { MRI_Results: "Normal" },
          evidence: "missing quote",
        },
      ],
      note
    );

    expect(spans).toEqual([
      {
        start: 0,
        end: 14,
        entity: "Diagnosis",
        label: "Diagnosis",
      },
    ]);
  });

  it("compacts Diagnosis to identity and evidence only", () => {
    expect(
      compactInventoryFact({
        entity: "Diagnosis",
        text: "focal seizures without change in awareness",
        subtype: "Epilepsy",
        attributes: {
          CUI: "C0751495",
          CUIPhrase: "focal-seizures",
          DiagCategory: "MultipleSeizures",
        },
        evidence: "In March she had 2 to 3 of her focal seizures",
      })
    ).toEqual({
      identity: "focal-seizures",
      clinical: null,
      evidence: "In March she had 2 to 3 of her focal seizures",
    });
  });

  it("compacts SeizureFrequency to change or a count", () => {
    expect(
      compactInventoryFact({
        entity: "SeizureFrequency",
        text: "seizures",
        subtype: "Decreased",
        attributes: { CUIPhrase: "seizures", FrequencyChange: "Decreased" },
        evidence: "fewer seizures",
      }).clinical
    ).toBe("Decreased");
    expect(
      compactInventoryFact({
        entity: "SeizureFrequency",
        text: "seizures",
        subtype: "seizures",
        attributes: {
          CUIPhrase: "seizures",
          LowerNumberOfSeizures: "2",
          UpperNumberOfSeizures: "3",
        },
        evidence: "2 to 3",
      }).clinical
    ).toBe("2–3");
  });

  it("compacts Prescription to dose and frequency, not the drug name", () => {
    expect(
      compactInventoryFact({
        entity: "Prescription",
        text: "Lamotrigine 150 mg twice daily",
        subtype: "lamotrigine",
        attributes: {
          CUIPhrase: "lamotrigine",
          DrugName: "lamotrigine",
          DrugDose: "150",
          DoseUnit: "mg",
          Frequency: "2",
        },
        evidence: "Lamotrigine 150 mg twice daily",
      }).clinical
    ).toBe("150mg, 2 doses");
  });

  it("compacts Investigations to identity only", () => {
    expect(
      compactInventoryFact({
        entity: "Investigations",
        text: "MRI",
        subtype: "MRI:Normal",
        attributes: {
          CUIPhrase: "mri normal",
          MRI_Performed: "Yes",
          MRI_Results: "Normal",
          EEG_Results: "Abnormal",
        },
        evidence: "MRI brain unremarkable",
      })
    ).toEqual({
      identity: "mri normal",
      clinical: null,
      evidence: "MRI brain unremarkable",
    });
  });
});
