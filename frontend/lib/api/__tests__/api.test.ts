import { fetchJson } from "../client";
import { isMockMode, enableMockMode } from "../mockMode";

describe("api/client", () => {
  it("throws on non-ok HTTP responses", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 503,
      text: async () => "unavailable",
    }) as unknown as typeof fetch;

    await expect(fetchJson("/health")).rejects.toThrow("HTTP 503");
  });
});

describe("api/mockMode", () => {
  const originalEnv = process.env.NEXT_PUBLIC_MOCK_API;

  afterEach(() => {
    process.env.NEXT_PUBLIC_MOCK_API = originalEnv;
  });

  it("can be enabled at runtime after health-check failure", () => {
    process.env.NEXT_PUBLIC_MOCK_API = undefined;
    enableMockMode("health-check");
    expect(isMockMode()).toBe(true);
  });
});
