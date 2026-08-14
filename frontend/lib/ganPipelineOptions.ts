import { activeMethodLabel } from "./plainLanguageLabels";
import type { ActiveMethod, PipelineFamilyItem } from "./types";

const MODEL_ORDER = [
  "openai/gpt-5.6-sol",
  "openai/gpt-5.6-luna",
  "gemini/gemini-3.7-flash",
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
  const cleaned = label.replace(/\s*[·-]\s*(?:replay|live)\s*$/i, "").trim();
  if (
    /^deterministic(?:\s+canonical|\s+all-?9|\s+rules)?$/i.test(cleaned) ||
    /^rules(?:\s+only)?$/i.test(cleaned)
  ) {
    return "Deterministic rules";
  }
  return cleaned;
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

export function ganOverallScore(
  option?: PipelineFamilyItem
): number | null {
  if (!option) return null;
  if (option.metrics?.purist_accuracy !== undefined) {
    return option.metrics.purist_accuracy;
  }
  if (
    option.kind === "rules" ||
    option.pipeline_family === "rules" ||
    option.run_id === "rules"
  ) {
    return 0.929;
  }
  return null;
}
