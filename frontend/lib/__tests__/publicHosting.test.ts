import { execFile } from "node:child_process";
import { proxyPython } from "../../app/api/_upstream";
import { POST } from "../../app/demo/replay/route";
import { demoCases } from "../viva";

jest.mock("node:child_process", () => ({ execFile: jest.fn() }));

describe("public hosting boundary", () => {
  const originalMode = process.env.NEXT_PUBLIC_DEMO_SURFACE;
  const originalFetch = global.fetch;

  beforeEach(() => {
    process.env.NEXT_PUBLIC_DEMO_SURFACE = "1";
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });
  afterEach(() => {
    if (originalMode === undefined) delete process.env.NEXT_PUBLIC_DEMO_SURFACE;
    else process.env.NEXT_PUBLIC_DEMO_SURFACE = originalMode;
    global.fetch = originalFetch;
  });

  it("serves fixtures without trying the local Python server", async () => {
    expect(await proxyPython("/api/registry")).toBeNull();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("returns the saved-decision recovery path without executing Python", async () => {
    const response = await POST(new Request("https://demo.example/demo/replay", {
      method: "POST", headers: { "Origin": "https://demo.example", "Content-Type": "application/json" },
      body: JSON.stringify({ id: demoCases[0].id }),
    }));
    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({ error: "Live rules require the local Python environment. The saved decision is available." });
    expect(execFile).not.toHaveBeenCalled();
  });

  it("rejects an unrelated origin before any execution", async () => {
    const response = await POST(new Request("https://demo.example/demo/replay", {
      method: "POST", headers: { "Origin": "https://unrelated.example", "Content-Type": "application/json" },
      body: JSON.stringify({ id: demoCases[0].id }),
    }));
    expect(response.status).toBe(403);
    expect(execFile).not.toHaveBeenCalled();
  });
});
