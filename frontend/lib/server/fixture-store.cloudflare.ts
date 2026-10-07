import fixtures from "../../.cloudflare/fixture-registry";

// Only the existing public demo JSON is bundled; repository research artifacts
// never enter this registry or the Worker assets.
export function readFixture<T>(relativePath: string): T {
  if (!Object.hasOwn(fixtures, relativePath)) throw new Error("Fixture not found");
  // Match filesystem reads: callers receive a fresh object on every request.
  return structuredClone(fixtures[relativePath]) as T;
}

export function validationRecordIds(): number[] {
  return Object.keys(fixtures)
    .flatMap((name) => {
      const match = /^records\/validation\/(\d+)\.json$/.exec(name);
      return match ? [Number(match[1])] : [];
    })
    .sort((a, b) => a - b);
}

export function readSavedJson<T>(relativePath: string): T {
  return readFixture<T>(relativePath);
}
export function savedDataExists(relativePath: string): boolean {
  return Object.hasOwn(fixtures, relativePath);
}
