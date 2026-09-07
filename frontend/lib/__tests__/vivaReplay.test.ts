const mockExecute = jest.fn();
jest.mock("node:util", () => ({ promisify: () => (...args: unknown[]) => mockExecute(...args) }));
import { POST } from "../../app/demo/replay/route";
import { guidedCases } from "../viva";

const request = (body: string, origin = "http://localhost:3000") => new Request("http://localhost:3000/demo/replay", {
  method: "POST", headers: { "Content-Type": "application/json", Origin: origin }, body,
});

afterEach(() => { mockExecute.mockReset(); });

it("rejects unlisted records, malformed input and a different origin before executing Python", async () => {
  expect((await POST(request('{"id":-1}'))).status).toBe(400);
  expect((await POST(request("null"))).status).toBe(400);
  expect((await POST(request('{"id":16021}', "https://another.example"))).status).toBe(403);
  expect(mockExecute).not.toHaveBeenCalled();
});

it("reports an unavailable interpreter without returning a fixture or gold label as live output", async () => {
  mockExecute.mockRejectedValue(new Error("Python unavailable"));
  const result = await POST(request('{"id":16021}'));
  expect(result.status).toBe(503);
  expect(await result.json()).toEqual({ error: "The local rules could not run. Retry or use the saved decision." });
});

it("executes only the bundled record ID and returns the real replay result", async () => {
  const c = guidedCases[0];
  const output = { mode: "live_rules", id: c.id, sha256: c.sha256, ...c.hybrid };
  mockExecute.mockResolvedValue({ stdout: JSON.stringify(output) });
  const result = await POST(request(JSON.stringify({ id: c.id, note: "must not enter the decision input" })));
  expect(result.status).toBe(200);
  expect(await result.json()).toEqual(output);
  const [, args, options] = mockExecute.mock.calls[0];
  expect(args.slice(1)).toEqual(["--decide", String(c.id)]);
  expect(options.timeout).toBe(15000);
});
