import { fetchJson } from "../client";
import { fetchHealth, fetchLetter, fetchLetters, fetchRuns } from "../index";

describe("api/client", () => {
  it("throws on non-ok HTTP responses", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 503,
      text: async () => "unavailable",
    }) as unknown as typeof fetch;

    await expect(fetchJson("/health")).rejects.toThrow("HTTP 503");
  });

  it("uses the live Next API boundary", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok" }),
    }) as unknown as typeof fetch;

    await expect(fetchHealth()).resolves.toEqual({ status: "ok" });
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/health",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
  });

  it("requests the shared letter catalog", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ dataset: "gan2026", count: 750, letters: [] }),
    }) as unknown as typeof fetch;

    await fetchLetters("gan2026");
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/datasets/gan2026/letters",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
  });

  it("requests one letter and a dataset run catalog from the same prefix", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    }) as unknown as typeof fetch;

    await fetchLetter("gan2026", "10");
    await fetchRuns("exectv2");
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      "/api/datasets/gan2026/letters/10",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      "/api/datasets/exectv2/runs",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
  });
});
