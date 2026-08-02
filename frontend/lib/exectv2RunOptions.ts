import { activeMethodLabel } from "./plainLanguageLabels";
import type {
  ActiveMethod,
  Exectv2RunWireResponse,
  Exectv2RunsResponse,
  Exectv2RunsWireResponse,
  Exectv2SharedLetterRecord,
  Exectv2RunWireSummary,
  Exectv2RunSummary,
} from "./types";

const UNOWNED_RULES_ALIASES = new Set(["deterministic_all9", "exectv2_deterministic_all9"]);
const ACTIVE_METHOD_ALIASES: Readonly<Record<string, string>> = {
  llm: "llm",
  llm_only: "llm",
  exectv2_llm_only: "llm",
  llm_with_rules: "llm_with_rules",
  exectv2_llm_with_rules: "llm_with_rules",
};

const MODEL_ORDER = [
  "openai/gpt-4.1-mini",
  "openai/gpt-5.6-luna",
  "openai/gpt-5.6-sol",
  "deepseek/deepseek-v4-flash",
  "ollama_chat/qwen3.6:35b",
  "ollama_chat/gemma4:26b",
] as const;

const GROUPS: ReadonlyArray<{
  method: ActiveMethod;
  label: string;
  caption: string;
}> = [
  {
    method: "llm_with_rules",
    label: activeMethodLabel("llm_with_rules"),
    caption: "Six models under the fixed one-call architecture after bounded assembly",
  },
  {
    method: "llm",
    label: activeMethodLabel("llm"),
    caption: "The same six calls before deterministic assembly",
  },
  {
    method: "rules",
    label: activeMethodLabel("rules"),
    caption: "No-call all-9 rules baseline",
  },
];

const MODEL_RANK: ReadonlyMap<string, number> = new Map(
  MODEL_ORDER.map((model, index): [string, number] => [model, index])
);

export interface Exectv2RunGroup {
  method: ActiveMethod;
  label: string;
  caption: string;
  runs: Exectv2RunSummary[];
}

/** Resolve the selected active method for grouping and badges. */
export function exectv2RunActiveMethod(run: Exectv2RunSummary): ActiveMethod {
  if (run.kind === "rules" || run.kind === "llm" || run.kind === "llm_with_rules") {
    return run.kind;
  }
  if (run.pipeline_family === "rules" || run.run_id === "rules") {
    return "rules";
  }
  if (run.scorer_view === "raw_lane_score" || run.pipeline_family === "llm") {
    return "llm";
  }
  if (run.scorer_view === "headline_target") {
    return "llm_with_rules";
  }
  const method = run.active_method ?? run.method_id;
  if (method === "rules" || method === "llm" || method === "llm_with_rules") {
    return method;
  }
  return "llm_with_rules";
}

/** Resolve only exact canonical or explicitly retained aliases. */
export function resolveExectv2RunId(
  runs: Exectv2RunSummary[],
  requested: string
): string | null {
  if (UNOWNED_RULES_ALIASES.has(requested)) return null;
  const activeMethod = ACTIVE_METHOD_ALIASES[requested];
  const matches = runs.filter((run) =>
    (activeMethod !== undefined &&
      [run.active_method, run.method_id].includes(activeMethod)) ||
    [
      run.run_id,
      run.saved_run_id,
      run.retained_evidence_id,
      run.active_method,
      run.method_id,
      ...(run.legacy_run_ids ?? []),
    ].includes(requested)
  );
  return matches.length === 1 ? matches[0].run_id : null;
}

export function groupExectv2Runs(runs: Exectv2RunSummary[]): Exectv2RunGroup[] {
  return GROUPS.map((group) => ({
    ...group,
    runs: runs
      .filter((run) => exectv2RunActiveMethod(run) === group.method)
      .sort(
        (a, b) =>
          (MODEL_RANK.get(a.model) ?? MODEL_ORDER.length) -
          (MODEL_RANK.get(b.model) ?? MODEL_ORDER.length)
      ),
  })).filter((group) => group.runs.length > 0);
}

export function sortExectv2Runs(runs: Exectv2RunSummary[]): Exectv2RunSummary[] {
  return groupExectv2Runs(runs).flatMap((group) => group.runs);
}

export function hydrateExectv2Runs(
  response: Exectv2RunsWireResponse
): Exectv2RunsResponse {
  const sharedById = new Map(
    response.shared_letters.map((letter) => [letter.letter_id, letter])
  );
  return {
    generated_on: response.generated_on,
    source_index: response.source_index,
    runs: response.runs.map((run) => hydrateRun(run, sharedById)),
  };
}

export function hydrateExectv2Run(response: Exectv2RunWireResponse): Exectv2RunSummary {
  const sharedById = new Map(
    response.shared_letters.map((letter) => [letter.letter_id, letter])
  );
  return hydrateRun(response.run, sharedById);
}

function hydrateRun(
  run: Exectv2RunWireSummary,
  sharedById: ReadonlyMap<string, Exectv2SharedLetterRecord>
): Exectv2RunSummary {
  return {
    ...run,
    letters: run.letters.map((letter) => {
      const shared = sharedById.get(letter.letter_id);
      if (!shared) {
        throw new Error(`Missing shared ExECTv2 letter ${letter.letter_id}`);
      }
      return {
        letter_id: letter.letter_id,
        split: letter.split,
        stage: letter.stage,
        letter_text: shared.letter_text,
        gold_mentions: shared.gold_mentions,
        predicted_mentions: letter.predicted_mentions,
        family_counts: {
          gold: shared.gold_family_counts,
          predicted: letter.predicted_family_counts,
        },
        evidence_spans: [...letter.evidence_spans, ...shared.evidence_spans],
      };
    }),
  };
}
