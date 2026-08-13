import { activeMethodLabel } from "./plainLanguageLabels";
import type { ActiveMethod, PipelineFamilyItem } from "./types";

const MODEL_ORDER = [
  "openai/gpt-5.6-luna",
  "gemini/gemini-3.7-flash",
  "openai/gpt-5.6-sol",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.6:35b",
  "ollama_chat/gemma4:26b",
];

const GROUPS: Array<{ method: ActiveMethod; label: string }> = [
  { method: "llm_with_rules", label: activeMethodLabel("llm_with_rules") },
  { method: "llm", label: activeMethodLabel("llm") },
  { method: "rules", label: activeMethodLabel("rules") },
];

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
      .filter((option) => option.kind === group.method)
      .sort((a, b) => modelRank(a.model) - modelRank(b.model)),
  })).filter((group) => group.options.length > 0);
}

export function resolveGanPipelineOption(
  options: PipelineFamilyItem[],
  selectedRunId: string
): PipelineFamilyItem | undefined {
  return (
    options.find((option) => option.run_id === selectedRunId)
  );
}

export function isGanAggregateRunId(runId: string): boolean {
  return (
    runId.startsWith("gan2026_winning_mode_") &&
    runId.endsWith("_llm_plus_rules_test450")
  );
}
