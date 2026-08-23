import {
  COMPARISON_KEY_TO_CELL,
  PAPER_CELLS,
  methodIdFor,
  resolvePaperCellId,
} from "../paperCells";

describe("paper cells", () => {
  it("orders five role cells and keeps the headline on LLM extract then rules", () => {
    expect(PAPER_CELLS.map((cell) => cell.id)).toEqual([
      "rules_only",
      "llm_pre_post",
      "llm_extract",
      "llm_encode",
      "llm_select",
    ]);
    expect(PAPER_CELLS.map((cell) => cell.shortLabel)).toEqual([
      "R / R / R",
      "both / R / R",
      "L / R / R",
      "L / L / R",
      "L / L / L",
    ]);
    expect(PAPER_CELLS.find((cell) => cell.headline)?.id).toBe("llm_extract");
  });

  it("loads sealed aliases onto the five-cell ids", () => {
    expect(resolvePaperCellId("llm_schema")).toBe("llm_extract");
    expect(resolvePaperCellId("llm_format")).toBe("llm_encode");
    expect(resolvePaperCellId("llm_post")).toBe("llm_select");
    expect(resolvePaperCellId("hybrid_full_stack")).toBe("llm_pre_post");
  });

  it("maps comparison.json keys onto cell ids", () => {
    expect(COMPARISON_KEY_TO_CELL.rules).toBe("rules_only");
    expect(COMPARISON_KEY_TO_CELL.both_extract_then_rules).toBe("llm_pre_post");
    expect(COMPARISON_KEY_TO_CELL.llm_extract_then_rules).toBe("llm_extract");
    expect(COMPARISON_KEY_TO_CELL.llm_extract_encode_then_select_rules).toBe(
      "llm_encode"
    );
    expect(COMPARISON_KEY_TO_CELL.llm).toBe("llm_select");
  });

  it("maps cells onto paper teaching MethodId values", () => {
    expect(methodIdFor("gan2026", "rules_only")).toBe("gan_rules");
    expect(methodIdFor("gan2026", "llm_pre_post")).toBe(
      "gan_llm_and_rules_extract"
    );
    expect(methodIdFor("gan2026", "llm_extract")).toBe(
      "gan_llm_extract"
    );
    expect(methodIdFor("gan2026", "llm_encode")).toBe("gan_llm_encode");
    expect(methodIdFor("gan2026", "llm_select")).toBe(
      "gan_llm_select_from_extract"
    );
    expect(methodIdFor("exectv2", "rules_only")).toBe("exect_rules");
    expect(methodIdFor("exectv2", "llm_pre_post")).toBe("exect_llm_pre_post");
    expect(methodIdFor("exectv2", "llm_extract")).toBe("exect_llm_only");
    expect(methodIdFor("exectv2", "llm_encode")).toBe("exect_llm_encode");
    expect(methodIdFor("exectv2", "llm_select")).toBe("exect_llm_select");
  });
});
