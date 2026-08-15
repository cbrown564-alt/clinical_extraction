import {
  adjacentPickerValue,
  filterPickerItems,
  highlightedPickerIndex,
} from "../controlPicker";

const items = [
  { value: "EA0188", label: "EA0188 – 4P / 5G" },
  { value: "EA0195", label: "EA0195 – 7P / 6G" },
  { value: "EA0200", label: "EA0200 – 6P / 7G" },
];

describe("filterPickerItems", () => {
  it("returns every item in order when the query is empty or whitespace", () => {
    expect(filterPickerItems(items, "")).toEqual(items);
    expect(filterPickerItems(items, "   ")).toEqual(items);
  });

  it("matches letter ids case-insensitively", () => {
    expect(filterPickerItems(items, "ea0195").map((item) => item.value)).toEqual([
      "EA0195",
    ]);
  });

  it("matches a numeric fragment and the P/G label", () => {
    expect(filterPickerItems(items, "195").map((item) => item.value)).toEqual([
      "EA0195",
    ]);
    expect(filterPickerItems(items, "7p").map((item) => item.value)).toEqual([
      "EA0195",
    ]);
  });

  it("returns an empty list when nothing matches", () => {
    expect(filterPickerItems(items, "zzz")).toEqual([]);
  });
});

describe("adjacentPickerValue", () => {
  it("steps forward and backward through the full catalog", () => {
    expect(adjacentPickerValue(items, "EA0195", 1)).toBe("EA0200");
    expect(adjacentPickerValue(items, "EA0195", -1)).toBe("EA0188");
  });

  it("returns null at the ends instead of wrapping", () => {
    expect(adjacentPickerValue(items, "EA0188", -1)).toBeNull();
    expect(adjacentPickerValue(items, "EA0200", 1)).toBeNull();
  });

  it("returns null when the current value is missing", () => {
    expect(adjacentPickerValue(items, "EA0000", 1)).toBeNull();
    expect(adjacentPickerValue([], "EA0195", 1)).toBeNull();
  });
});

describe("highlightedPickerIndex", () => {
  it("keeps the current value highlighted when it is still visible", () => {
    expect(highlightedPickerIndex(items, "EA0195")).toBe(1);
  });

  it("falls back to the first match, or -1 when the list is empty", () => {
    expect(highlightedPickerIndex(filterPickerItems(items, "200"), "EA0195")).toBe(0);
    expect(highlightedPickerIndex([], "EA0195")).toBe(-1);
  });
});
