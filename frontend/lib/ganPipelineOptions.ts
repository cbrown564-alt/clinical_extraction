import type { PipelineFamilyItem } from "./types";

export type GanComparisonMode = NonNullable<PipelineFamilyItem["comparison_mode"]>;

const MODEL_ORDER = [
  "openai/gpt-4.1-mini",
  "openai/gpt-5.6-luna",
  "openai/gpt-5.6-sol",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.6:35b",
  "ollama_chat/gemma4:26b",
];

const GROUPS: Array<{ mode: GanComparisonMode; label: string }> = [
  { mode: "llm_plus_rules", label: "Winning mode · LLM + rules" },
  { mode: "llm_only", label: "LLM only · raw one-call output" },
  { mode: "deterministic_only", label: "Deterministic only · no model" },
];

const MODE_LABELS: Record<GanComparisonMode, string> = {
  llm_plus_rules: "LLM + Rules",
  llm_only: "LLM Only",
  deterministic_only: "Rules Only",
};

export function ganPipelineModeLabel(mode: GanComparisonMode): string {
  return MODE_LABELS[mode];
}

export function ganPipelineOptionLabel(label: string): string {
  return label.replace(/\s*[·-]\s*(?:replay|live)\s*$/i, "");
}

function modelRank(model?: string): number {
  const index = MODEL_ORDER.indexOf(model ?? "");
  return index < 0 ? MODEL_ORDER.length : index;
}

export function groupGanPipelineOptions(options: PipelineFamilyItem[]) {
  return GROUPS.map((group) => ({
    ...group,
    options: options
      .filter((option) => option.comparison_mode === group.mode)
      .sort((a, b) => modelRank(a.model) - modelRank(b.model)),
  })).filter((group) => group.options.length > 0);
}

export function resolveGanPipelineOption(
  options: PipelineFamilyItem[],
  selectedRunId: string
): PipelineFamilyItem | undefined {
  return (
    options.find((option) => option.run_id === selectedRunId) ??
    options.find((option) => option.comparison_mode === "deterministic_only") ??
    options[0]
  );
}

export function isGanAggregateRunId(runId: string): boolean {
  return (
    runId.startsWith("gan2026_winning_mode_") &&
    runId.endsWith("_llm_plus_rules_test450")
  );
}
