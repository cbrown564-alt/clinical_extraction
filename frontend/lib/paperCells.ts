import type { MethodId } from "./isometricTypes";

export type PaperCellId =
  | "rules_only"
  | "llm_pre_post"
  | "llm_extract"
  | "llm_encode"
  | "llm_select";

export type StageRole = "rules" | "LLM" | "both";

export type PaperCell = {
  id: PaperCellId;
  order: 1 | 2 | 3 | 4 | 5;
  extract: StageRole;
  encode: StageRole;
  select: StageRole;
  shortLabel: string;
  displayName: string;
  headline: boolean;
};

export const PAPER_CELLS: readonly PaperCell[] = [
  {
    id: "rules_only",
    order: 1,
    extract: "rules",
    encode: "rules",
    select: "rules",
    shortLabel: "R / R / R",
    displayName: "Rules only",
    headline: false,
  },
  {
    id: "llm_pre_post",
    order: 2,
    extract: "both",
    encode: "rules",
    select: "rules",
    shortLabel: "both / R / R",
    displayName: "Both then rules",
    headline: false,
  },
  {
    id: "llm_extract",
    order: 3,
    extract: "LLM",
    encode: "rules",
    select: "rules",
    shortLabel: "L / R / R",
    displayName: "LLM extract then rules",
    headline: true,
  },
  {
    id: "llm_encode",
    order: 4,
    extract: "LLM",
    encode: "LLM",
    select: "rules",
    shortLabel: "L / L / R",
    displayName: "LLM extract+encode then rules",
    headline: false,
  },
  {
    id: "llm_select",
    order: 5,
    extract: "LLM",
    encode: "LLM",
    select: "LLM",
    shortLabel: "L / L / L",
    displayName: "LLM all the way",
    headline: false,
  },
] as const;

const LOAD_ALIASES: Record<string, PaperCellId> = {
  rules_only: "rules_only",
  llm_pre_post: "llm_pre_post",
  llm_extract: "llm_extract",
  llm_encode: "llm_encode",
  llm_select: "llm_select",
  llm_schema: "llm_extract",
  llm_format: "llm_encode",
  llm_post: "llm_select",
  hybrid_full_stack: "llm_pre_post",
  rules: "rules_only",
  llm: "llm_extract",
  llm_with_rules: "llm_pre_post",
};

export function resolvePaperCellId(value: string | null | undefined): PaperCellId {
  if (!value) return "llm_extract";
  return LOAD_ALIASES[value] ?? "llm_extract";
}

export function paperCellById(id: string): PaperCell {
  const resolved = resolvePaperCellId(id);
  return PAPER_CELLS.find((cell) => cell.id === resolved)!;
}

export type TeachingTask = "gan2026" | "exectv2";

/** Existing teaching MethodId only. Stand-ins are documented in teachingStandInCaption. */
export function methodIdFor(task: TeachingTask, cell: string): MethodId {
  const id = resolvePaperCellId(cell);
  if (task === "gan2026") {
    if (id === "rules_only") return "gan_rules";
    if (id === "llm_pre_post") return "gan_llm_with_rules";
    if (id === "llm_extract" || id === "llm_encode") return "gan_llm_only";
    return "gan_llm_with_rules";
  }
  if (id === "rules_only") return "exect_rules";
  if (id === "llm_pre_post") return "exect_llm_pre_post";
  return "exect_llm_only";
}

export function teachingStandInCaption(
  task: TeachingTask,
  cell: string
): string | null {
  const id = resolvePaperCellId(cell);
  if (task === "gan2026") {
    if (id === "llm_pre_post") {
      return "Teaching stand-in is gan_llm_with_rules, the source-near wording ablation, not cell 2 (gan_llm_pre_post_label_forms).";
    }
    if (id === "llm_extract") {
      return "Teaching stand-in is gan_llm_only, a live runner, not the results column. Cell 3 on disk is gan_llm_extract_label_forms.";
    }
    if (id === "llm_encode") {
      return "Same gan_llm_only teaching run; encode is a later-stage caption. Cell 4 on disk uses the same codebook extract with select families only.";
    }
    if (id === "llm_select") {
      return "Teaching stand-in is gan_llm_with_rules, the only select-ish teaching run. Cell 5 on disk is gan_llm_select_from_extract.";
    }
    return null;
  }
  if (id === "llm_encode") {
    return "Encode is later-stage exect_llm_encode; teaching fixture not rebuilt yet. Same raw as exect_llm_only.";
  }
  if (id === "llm_select") {
    return "Select is later-stage exect_llm_select; teaching fixture not rebuilt yet. Same raw as exect_llm_only.";
  }
  return null;
}

export const COMPARISON_KEY_TO_CELL: Record<string, PaperCellId> = {
  rules: "rules_only",
  both_extract_then_rules: "llm_pre_post",
  llm_extract_then_rules: "llm_extract",
  llm_extract_encode_then_select_rules: "llm_encode",
  llm: "llm_select",
};
