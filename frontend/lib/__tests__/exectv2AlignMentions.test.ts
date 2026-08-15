import { alignFamilyMentions, filledAttributeCount } from "../exectv2AlignMentions";
import type { Exectv2Mention } from "../types";

function mention(
  id: string,
  source: "gold" | "predicted",
  text: string,
  attributes: Record<string, string>
): Exectv2Mention {
  return {
    id,
    source,
    entity: "Prescription",
    text,
    evidence: text,
    evidence_valid: true,
    component_owner: "test",
    source_lane: "test",
    source_model: "test",
    confidence: "",
    assertion: "",
    attributes,
    status: "",
    headline_status: "",
  };
}

describe("alignFamilyMentions", () => {
  it("pairs gold with the richer of two same-CUI / same-CUIPhrase predictions", () => {
    const gold = [
      mention("g-sv", "gold", "Sodium-Valproate-500mg-bd", {
        CUI: "C0037567",
        CUIPhrase: "sodium-valproate",
        DrugName: "sodium-valproate",
        DrugDose: "500",
        DoseUnit: "mg",
        Frequency: "2",
      }),
    ];
    const nameOnly = mention("p-sv-name", "predicted", "sodium valproate", {
      CUI: "C0037567",
      CUIPhrase: "sodium-valproate",
      DrugName: "sodium-valproate",
    });
    const full = mention("p-sv-full", "predicted", "Sodium Valproate 500mg bd", {
      CUI: "C0037567",
      CUIPhrase: "sodium-valproate",
      DrugName: "sodium-valproate",
      DrugDose: "500",
      DoseUnit: "mg",
      Frequency: "2",
    });

    const groups = alignFamilyMentions(gold, [nameOnly, full]);
    const matched = groups.filter((g) => g.type === "matched");
    const extra = groups.filter((g) => g.type === "extra_predicted");

    expect(matched).toHaveLength(1);
    if (matched[0].type !== "matched") throw new Error("expected match");
    expect(matched[0].predicted.id).toBe("p-sv-full");
    expect(extra).toHaveLength(1);
    if (extra[0].type !== "extra_predicted") throw new Error("expected extra");
    expect(extra[0].predicted.id).toBe("p-sv-name");
  });

  it("still matches a lone name-only prediction when it is the only candidate", () => {
    const gold = [
      mention("g-cbz", "gold", "Carbamazepine 400mg bd", {
        CUI: "C0006949",
        CUIPhrase: "carbamazepine",
        DrugName: "carbamazepine",
        DrugDose: "400",
        DoseUnit: "mg",
        Frequency: "2",
      }),
    ];
    const nameOnly = mention("p-cbz-name", "predicted", "carbamazepine", {
      CUI: "C0006949",
      CUIPhrase: "carbamazepine",
      DrugName: "carbamazepine",
    });

    const groups = alignFamilyMentions(gold, [nameOnly]);
    expect(groups).toHaveLength(1);
    expect(groups[0].type).toBe("matched");
  });

  it("does not steal a richer mention that belongs to a different CUI", () => {
    const gold = [
      mention("g-sv", "gold", "Sodium-Valproate-500mg-bd", {
        CUI: "C0037567",
        CUIPhrase: "sodium-valproate",
        DrugName: "sodium-valproate",
      }),
    ];
    const otherFull = mention("p-cbz-full", "predicted", "Carbamazepine 400mg bd", {
      CUI: "C0006949",
      CUIPhrase: "carbamazepine",
      DrugName: "carbamazepine",
      DrugDose: "400",
      DoseUnit: "mg",
      Frequency: "2",
    });
    const svName = mention("p-sv-name", "predicted", "sodium valproate", {
      CUI: "C0037567",
      CUIPhrase: "sodium-valproate",
      DrugName: "sodium-valproate",
    });

    const groups = alignFamilyMentions(gold, [otherFull, svName]);
    const matched = groups.find((g) => g.type === "matched");
    expect(matched?.type === "matched" && matched.predicted.id).toBe("p-sv-name");
  });
});

describe("filledAttributeCount", () => {
  it("ignores blank values", () => {
    expect(
      filledAttributeCount(
        mention("x", "predicted", "x", { CUI: "C1", CUIPhrase: "a", DrugDose: "  ", Frequency: "" })
      )
    ).toBe(2);
  });
});
