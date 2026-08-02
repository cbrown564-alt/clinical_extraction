import { fetchJson } from "../client";
import { fetchHealth } from "../index";
import { runAblation } from "../index";

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

  it("sends the canonical rules pipeline for an ablation request", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ pipeline: "rules" }),
    }) as unknown as typeof fetch;

    await runAblation({ split: "validation", pipeline: "rules" });
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/run/ablation",
      expect.objectContaining({ body: JSON.stringify({ split: "validation", pipeline: "rules" }) })
    );
  });
});
