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

/** Paper cell identities. Stand-in captions stay null when a real run exists. */
export function methodIdFor(task: TeachingTask, cell: string): MethodId {
  const id = resolvePaperCellId(cell);
  if (task === "gan2026") {
    if (id === "rules_only") return "gan_rules";
    if (id === "llm_pre_post") return "gan_llm_and_rules_extract";
    if (id === "llm_extract") return "gan_llm_extract";
    if (id === "llm_encode") return "gan_llm_encode";
    return "gan_llm_select_from_extract";
  }
  if (id === "rules_only") return "exect_rules";
  if (id === "llm_pre_post") return "exect_llm_pre_post";
  if (id === "llm_extract") return "exect_llm_only";
  if (id === "llm_encode") return "exect_llm_encode";
  return "exect_llm_select";
}

export function teachingStandInCaption(
  _task: TeachingTask,
  _cell: string
): string | null {
  return null;
}

export const COMPARISON_KEY_TO_CELL: Record<string, PaperCellId> = {
  rules: "rules_only",
  both_extract_then_rules: "llm_pre_post",
  llm_extract_then_rules: "llm_extract",
  llm_extract_encode_then_select_rules: "llm_encode",
  llm: "llm_select",
};
