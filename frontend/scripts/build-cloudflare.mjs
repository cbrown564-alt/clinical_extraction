import { readdirSync, mkdirSync, writeFileSync, readFileSync, statSync, rmSync } from "node:fs";
import path from "node:path";
import { packageScoredResponses } from "./package-scored-responses.mjs";
import { spawnSync } from "node:child_process";

const mode = process.argv[2] ?? "migration-preview";
if (!["migration-preview", "production"].includes(mode)) throw new Error(`Unknown mode: ${mode}`);
const root = path.resolve("public/mock-data");
const files = [];
const walk = (directory) => {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Fixture symlink is forbidden: ${file}`);
    if (entry.isDirectory()) walk(file);
    else if (entry.name.endsWith(".json")) files.push(file);
  }
};
walk(root);
// Preserve existing published aggregate panels and authored synthetic examples.
// Locked-test rows, raw model captures and arbitrary research files are excluded.
const saved = [
  "results/letter-benchmarks/gan/dev750_panel.json",
  "results/letter-benchmarks/exect/dev140_panel.json",
  "results/letter-benchmarks/gan/five_cell_grid/gemini37flash/test450/comparison.json",
  "results/letter-benchmarks/exect/five_cell_grid/gemini37flash/test60/comparison.json",
  "results/longitudinal/prototype_v0.1/patients.json",
];
const tracked = spawnSync("git", ["ls-files", "results/longitudinal/prototype_v0.1/frames"], { cwd: "..", encoding: "utf8" });
if (tracked.status !== 0) throw new Error("Cannot enumerate tracked public frames");
saved.push(...tracked.stdout.trim().split("\n").filter(file => /\/frames\/authored_patient_\d{3}\/T[12]_(visit|retrospective)\.(reference|predicted)\.json$/.test(file)));
const savedEntries = saved.map(file => {
  const data = JSON.parse(readFileSync(path.join("..", file), "utf8"));
  if (file.includes("/frames/")) {
    const { documents, history, answers, requests, status, error, program_version, offset_repairs, provenance } = data;
    return [file, { documents, history, answers, requests, status, error, program_version, offset_repairs, provenance: { mode: provenance.mode, attempt: provenance.attempt ? { model_requested: provenance.attempt.model_requested } : undefined, query_context_visible_during_extraction: provenance.query_context_visible_during_extraction } }];
  }
  return [file, data];
});
files.sort();
mkdirSync(".cloudflare", { recursive: true });
const imports = files.map((file, i) => `import f${i} from ${JSON.stringify('../'+path.relative(process.cwd(), file).replaceAll(path.sep, '/'))};`);
const entries = files.map((file, i) => `${JSON.stringify(path.relative(root, file).replaceAll(path.sep, '/'))}: f${i}`);
writeFileSync(".cloudflare/fixture-registry.ts", `${imports.join('\n')}\nconst fixtures: Record<string, unknown> = {${entries.join(',\n')}, ...${JSON.stringify(Object.fromEntries(savedEntries))}};\nexport default fixtures;\n`);
console.log(`Bundling ${files.length} existing public demo fixtures; plus ${saved.length} published aggregates/synthetic frames; no locked rows or raw captures`);
const env = { ...process.env, NEXT_PUBLIC_DEMO_SURFACE: "1", CF_MIGRATION_MODE: mode };
const generatedTypes = spawnSync("npm", ["exec", "--", "cf", "workers", "types", "--mode", mode], { stdio: "inherit", env });
if (generatedTypes.status !== 0) process.exit(generatedTypes.status ?? 1);
const types = spawnSync("npm", ["exec", "--", "tsc", "--project", "tsconfig.cloudflare.json"], { stdio: "inherit" });
if (types.status !== 0) process.exit(types.status ?? 1);
// Next and vinext generate different route types in the same directory.
// Remove only rebuildable provider output before vinext generates its types.
rmSync(".next/types", { recursive: true, force: true });
rmSync(".next/dev/types", { recursive: true, force: true });
const build = spawnSync("npm", ["run", "build:vinext", "--", "--mode", mode], { stdio: "inherit", env });
if (build.status !== 0) process.exit(build.status ?? 1);
// Vite's public copy must never turn the fixture directory into direct assets.
// The output checks below run before cf deployment.
const check = (directory) => {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) check(file);
    else if (statSync(file).size > 25 * 1024 * 1024) throw new Error(`Asset exceeds 25 MiB: ${file}`);
  }
};
const assets = ".cloudflare/output/v0/workers/default/assets";
rmSync(path.join(assets, "mock-data"), { recursive: true, force: true });
await packageScoredResponses(assets);
writeFileSync(path.join(assets, "_headers"), mode === "migration-preview" ? "/*\n  X-Robots-Tag: noindex, nofollow\n" : "");
check(assets);

const sourceTypes = spawnSync("npm", ["exec", "--", "tsc", "--noEmit"], { stdio: "inherit", env });
if (sourceTypes.status !== 0) process.exit(sourceTypes.status ?? 1);
