import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = join(process.cwd(), "public", "mock-data");

export function readFixture<T>(relativePath: string): T {
  return JSON.parse(readFileSync(join(root, relativePath), "utf8")) as T;
}

export function validationRecordIds(): number[] {
  return readdirSync(join(root, "records", "validation"))
    .filter((name) => /^\d+\.json$/.test(name))
    .map((name) => Number(name.slice(0, -5)))
    .sort((a, b) => a - b);
}

// Existing published aggregate/synthetic demonstration inputs, relative to repo root.
export function readSavedJson<T>(relativePath: string): T {
  return JSON.parse(readFileSync(join(process.cwd(), "..", relativePath), "utf8")) as T;
}
export function savedDataExists(relativePath: string): boolean {
  try { readSavedJson(relativePath); return true; } catch { return false; }
}
