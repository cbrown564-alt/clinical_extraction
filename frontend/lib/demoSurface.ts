import { ganPickerMethodId, ganPaperRunId } from "./ganPipelineOptions";
import { paperCellById } from "./paperCells";
import type { Exectv2RunSummary, PipelineFamilyItem } from "./types";

/** Cited living cell: LLM extract, rules encode, rules select. */
export const DEMO_PAPER_CELL = "llm_extract" as const;
export const DEMO_MODEL = "gemini/gemini-3.7-flash";
export const DEMO_MODEL_LABEL = "Gemini 3.7 Flash";
export const DEMO_GAN_RUN_ID = ganPaperRunId("llm_extract", "gemini37flash");
export const DEMO_EXECT_RUN_ID = "exectv2_dev140_gemini37flash_llm_extract";

export function isDemoSurface(): boolean {
  return (
    process.env.VERCEL === "1" ||
    Boolean(process.env.NEXT_PUBLIC_VERCEL_ENV) ||
    process.env.NEXT_PUBLIC_DEMO_SURFACE === "1"
  );
}

export function demoMethodLabel(): string {
  return paperCellById(DEMO_PAPER_CELL).displayName;
}

export function isDemoGanFamily(option: PipelineFamilyItem): boolean {
  return (
    ganPickerMethodId(option) === DEMO_PAPER_CELL &&
    option.model === DEMO_MODEL
  );
}

export function lockDemoGanFamilies(
  families: PipelineFamilyItem[]
): PipelineFamilyItem[] {
  const locked = families.filter(isDemoGanFamily);
  return locked.length > 0 ? locked : families;
}

export function isDemoExectRun(run: Exectv2RunSummary): boolean {
  return (
    run.run_id === DEMO_EXECT_RUN_ID ||
    (run.paper_cell === DEMO_PAPER_CELL && run.model === DEMO_MODEL)
  );
}

export function lockDemoExectRuns(runs: Exectv2RunSummary[]): Exectv2RunSummary[] {
  const locked = runs.filter(isDemoExectRun);
  return locked.length > 0 ? locked : runs;
}
