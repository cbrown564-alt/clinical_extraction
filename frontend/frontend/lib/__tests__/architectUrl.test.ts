import { preserveWorkbenchDataset } from "../architectUrl";

describe("workbench URL state", () => {
  it("preserves the active dataset while trace parameters change", () => {
    const next = new URLSearchParams();
    preserveWorkbenchDataset(next, new URLSearchParams("dataset=gan2026&row=10"));

    expect(next.get("dataset")).toBe("gan2026");
  });

  it("does not invent a dataset when the route has none", () => {
    const next = new URLSearchParams();
    preserveWorkbenchDataset(next, new URLSearchParams("row=10"));

    expect(next.has("dataset")).toBe(false);
  });
});
