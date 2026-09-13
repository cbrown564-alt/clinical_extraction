import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { timeDescription, type ClinicalTime, type Frame } from "../longitudinal";

test("unknown and one-sided dates remain explicit in patient histories", () => {
  const unknown: ClinicalTime = { kind: "active_interval", text: null, start: null, end: { earliest: null, latest: null } };
  expect(timeDescription(unknown)).toBe("Time not established");
  expect(timeDescription({ ...unknown, end: { earliest: null, latest: "2025-02-15" } })).toBe("Start unknown; end on or before 15 Feb 2025");
  expect(timeDescription({ ...unknown, text: "around Christmas" })).toBe("around Christmas");
});

test("every bundled source/view history can format its dates without a render error", () => {
  const root = path.resolve(process.cwd(), "../results/longitudinal/prototype_v0.1/frames");
  let frames = 0;
  for (const patient of readdirSync(root)) {
    for (const filename of readdirSync(path.join(root, patient))) {
      const frame: Frame = JSON.parse(readFileSync(path.join(root, patient, filename), "utf8"));
      for (const group of frame.history ?? []) {
        for (const account of group.accounts) expect(timeDescription(account.time)).not.toMatch(/Invalid|NaN|undefined/);
        for (const link of group.links) expect(timeDescription(link.decision_time)).not.toMatch(/Invalid|NaN|undefined/);
      }
      frames++;
    }
  }
  expect(frames).toBe(96);
});
