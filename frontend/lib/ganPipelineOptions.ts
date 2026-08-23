import { activeMethodLabel } from "./plainLanguageLabels";
import { PAPER_CELLS, paperCellById, type PaperCellId } from "./paperCells";
import type { ActiveMethod, PipelineFamilyItem } from "./types";

const MODEL_ORDER = [
  "xai/grok-4.6",
  "openai/gpt-5.6-luna",
  "gemini/gemini-3.7-flash",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.8:27b",
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

function kindForPaperCell(id: PaperCellId): ActiveMethod {
  if (id === "rules_only") return "rules";
  if (id === "llm_pre_post") return "llm_with_rules";
  return "llm";
}

export function groupGanPipelineOptions(options: PipelineFamilyItem[]) {
  const withCells = options.filter((option) => option.paper_cell);
  if (withCells.length > 0) {
    return PAPER_CELLS.map((cell) => ({
      method: kindForPaperCell(cell.id),
      label: cell.displayName,
      paper_cell: cell.id,
      options: options
        .filter((option) => option.paper_cell === cell.id)
        .sort((a, b) => modelRank(a.model) - modelRank(b.model)),
    })).filter((group) => group.options.length > 0);
  }
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

export type GanDev750PanelCell = {
  model_slug: string;
  model: string;
  label: string;
  method:
    | "rules_only"
    | "llm_extract"
    | "llm_encode"
    | "llm_select"
    | "gan_llm_only"
    | "gan_llm_extract_raw";
  status: "present" | "pending";
  n: number;
  purist_correct?: number | null;
  purist_accuracy?: number | null;
};

export type GanDev750PanelLike = {
  claim_boundary?: string;
  cells: GanDev750PanelCell[];
};

export function ganPaperRunId(
  method: GanDev750PanelCell["method"],
  slug: string
): string {
  const suffix =
    method === "rules_only"
      ? "rules"
      : method === "gan_llm_extract_raw"
        ? "llm_with_rules"
        : method === "gan_llm_only"
          ? "llm_only"
          : method;
  return `gan2026_validation750_${slug}_${suffix}`;
}

function paperCellForDev750Method(
  method: GanDev750PanelCell["method"]
): PaperCellId | undefined {
  if (
    method === "rules_only" ||
    method === "llm_extract" ||
    method === "llm_encode" ||
    method === "llm_select"
  ) {
    return method;
  }
  return undefined;
}

function modeLabelForCell(method: GanDev750PanelCell["method"]): string {
  if (method === "gan_llm_only") return "live runner (not a results column)";
  if (method === "gan_llm_extract_raw") return "source-near wording ablation";
  const cell = paperCellForDev750Method(method);
  return cell ? paperCellById(cell).displayName : method;
}

function rulesOnlyFamily(): PipelineFamilyItem {
  return {
    value: "rules",
    run_id: "rules",
    label: "Deterministic canonical",
    display_label: "Deterministic canonical",
    model_label: "No model",
    executable: true,
    kind: "rules",
    paper_cell: "rules_only",
    pipeline_family: "rules",
    model: "(model-independent)",
    comparison_role: "control",
    availability: "live",
    evidence_scope: "validation_rows",
    has_replay_artifact: false,
    run_count: 1,
  };
}

export function ganFamiliesFromDev750Panel(
  panel: GanDev750PanelLike
): PipelineFamilyItem[] {
  return [
    ...panel.cells
      .map((cell) => {
      const paperCell = paperCellForDev750Method(cell.method);
      const kind: ActiveMethod = paperCell
        ? kindForPaperCell(paperCell)
        : cell.method === "gan_llm_extract_raw"
          ? "llm_with_rules"
          : cell.method === "rules_only"
            ? "rules"
            : "llm";
      const present = cell.status === "present";
      const runId = ganPaperRunId(cell.method, cell.model_slug);
      const modeLabel = modeLabelForCell(cell.method);
      const family: PipelineFamilyItem = {
        value: runId,
        run_id: runId,
        label: cell.label,
        display_label: `${cell.label} · ${present ? modeLabel : "in progress"}`,
        model_label: cell.label,
        executable: false,
        kind,
        paper_cell: paperCell,
        pipeline_family: kind,
        model: cell.model,
        comparison_role: kind === "llm_with_rules" ? "winner" : "diagnostic",
        availability: present ? "replay" : "not_retained",
        evidence_scope: present
          ? "validation750_row_level"
          : "incomplete_not_served",
        has_replay_artifact: present,
        run_count: present ? 1 : 0,
        progress: {
          completed_rows: present ? cell.n : 0,
          expected_rows: 750,
        },
      };
      if (present) {
        family.metrics = {
          row_count: cell.n,
          purist_correct: cell.purist_correct ?? 0,
          purist_accuracy: cell.purist_accuracy ?? 0,
          pragmatic_correct: 0,
          pragmatic_accuracy: 0,
        };
      } else {
        family.unavailable_reason =
          "This condition is incomplete; partial validation rows are not served.";
      }
      return family;
    }),
    rulesOnlyFamily(),
  ];
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
