import { fetchJson } from "../client";
import {
  fetchExectDev140Panel,
  fetchExectDev140Scored,
  fetchGanDev750Panel,
  fetchGanDev750Scored,
  fetchHealth,
  fetchLetter,
  fetchLetters,
  fetchRuns,
} from "../index";

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
      json: async () => ({
        dataset: "exectv2",
        split: "dev140",
        count: 2,
        letters: [
          { id: "EA0002", split: "dev140" },
          { id: "EA0001", split: "test60" },
        ],
      }),
    }) as unknown as typeof fetch;

    await expect(fetchLetters("exectv2")).resolves.toEqual({
      dataset: "exectv2",
      split: "dev140",
      count: 1,
      letters: [{ id: "EA0002", split: "dev140" }],
    });
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/datasets/exectv2/letters",
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

  it("requests the living Gan dev750 panel and one scored cell", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    }) as unknown as typeof fetch;

    await fetchGanDev750Panel();
    await fetchGanDev750Scored("gan_llm_with_rules", "grok46");
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      "/api/paper/gan/dev750",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      "/api/paper/gan/dev750/gan_llm_with_rules/grok46/scored",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
  });

  it("requests the living ExECT Compact dev140 panel and one scored cell", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    }) as unknown as typeof fetch;

    await fetchExectDev140Panel();
    await fetchExectDev140Scored("grok46");
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      "/api/paper/exect/dev140",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      "/api/paper/exect/dev140/grok46/scored",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } })
    );
  });
});
