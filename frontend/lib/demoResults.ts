/** Transcribed from the submitted PDFs, September 2026. Rounded values, not recomputed runs.
 * Owners: paper/draft/Extract, then decide.pdf, Tables V, VII, IX;
 * paper/supporting materials/Supporting materials.pdf, Development vs. test results.
 * Gan synthetic test450 is aggregate-only. No patient rows are bundled here.
 */
export const modelResults = [
  { name: "Gemini 3.7 Flash", provisional: .79, hybrid: .86, llm: .85 },
  { name: "Grok 4.6", provisional: .79, hybrid: .85, llm: .84 },
  { name: "DeepSeek V4 Flash", provisional: .74, hybrid: .82, llm: .77 },
  { name: "GPT-5.6 Luna", provisional: .69, hybrid: .79, llm: .74 },
  { name: "Qwen 3.8 27B", provisional: .70, hybrid: .76, llm: .65 },
  { name: "Gemma 4 26B", provisional: .66, hybrid: .72, llm: .62 },
];
export const ablationResults = [
  { name: "Full extraction prompt", provisional: .79, hybrid: .86, detail: "Examples, allowed label forms, and exact evidence quotations." },
  { name: "Without examples", provisional: .77, hybrid: .82, detail: "Remove the worked examples; keep the other prompt ingredients." },
  { name: "Without evidence obligation", provisional: .77, hybrid: .82, detail: "Remove the requirement to quote the source evidence." },
  { name: "Without closed label forms", provisional: .77, hybrid: .81, detail: "Remove the closed list of allowed label forms." },
];
export const splitResults = [
  { name: "Hybrid", dev: .87, test: .86 },
  { name: "LLM-only", dev: .85, test: .85 },
];
export const externalResults = [
  { name: "Hybrid", model: "DeepSeek V4 Flash", value: .80 },
  { name: "Synthetic-trained fine-tune · Gan et al.", model: "Qwen2.5-14B", value: .79 },
  { name: "LLM-only", model: "DeepSeek V4 Flash", value: .77 },
];
