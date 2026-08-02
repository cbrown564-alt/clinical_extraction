import type { ActiveMethod } from "./types";

/**
 * Plain-language label helpers.
 *
 * Single source for the user-visible names that appear in pickers, ladders,
 * tables, and charts. Maps internal codenames (pipeline families, splits,
 * decisions) to the plain display names defined in
 * `docs/reference/plain_language_glossary.md`.
 *
 * Rule: the plain name leads; a short distinguishing suffix in parens adds
 * granularity where the glossary's three buckets (rules / llm /
 * llm_with_rules) would otherwise collapse distinct architectures.
 */

/**
 * Architecture-family labels. All families collapse into one of three glossary
 * buckets — rules, llm, llm_with_rules — with a short parenthetical suffix
 * that keeps known sub-variants distinguishable in pickers and ladders.
 *
 * Unknown families fall back to a de-snake_cased version of the codename rather
 * than the raw id, so a new family still reads as words instead of
 * `llm_with_rules_something_new`.
 */
/** Selected-method labels for badges, pickers, and grouped selectors. */
export function activeMethodLabel(method: ActiveMethod): string {
  const LABELS: Record<ActiveMethod, string> = {
    rules: "Rules only",
    llm: "LLM only",
    llm_with_rules: "LLM with rules",
  };
  return LABELS[method];
}

export function familyLabel(pipelineFamily: string): string {
  const RULES_ONLY = "Rules-only";
  const BUCKETS: Record<string, string> = {
    // rules-only
    rules: RULES_ONLY,
    rules_only: RULES_ONLY,

    // LLM-only
    llm_only_direct_labeler: "LLM-only (direct)",
    llm_structured_events: "LLM-only (events)",
    llm_first_direct_extractor: "LLM-only (direct)",
    llm_heavy_clinical_frequency_reasoner: "LLM-only (heavy)",
    llm_heavy_evidence_selection_with_deterministic_adapters: "LLM-only (heavy + rules)",
    llm_replacement_postprocessing_ablation: "LLM-only (replacement)",
    llm_only_canonical_pipeline: "LLM-only",
    llm: "LLM-only",

    // llm_with_rules (retained legacy family ids resolve to the same label)
    hybrid_structured_events: "LLM with rules",
    llm_with_rules: "LLM with rules",
    hybrid_clinical_frequency_state_graph: "LLM with rules (state graph)",
    reset_clinical_assessment_pipeline: "LLM with rules (reset)",
    dspy_final_selection_adjudicator: "LLM with rules (DSPy adjudicator)",

    // fresh-evidence / ceiling architectures
    fresh_evidence_reasoner: "LLM-only (fresh-evidence)",
  };

  return BUCKETS[pipelineFamily] ?? deSnake(pipelineFamily);
}

/**
 * ExECTv2 architecture labels for the component ladder. The glossary maps v08
 * to "frozen production control" and v01–v07 to "prior assembly versions";
 * the model-named diagnostics keep the model family so the column stays
 * meaningful, but drop the internal version-suffix jargon.
 */
export function exectv2ArchitectureLabel(runId: string): string {
  const LABELS: Array<[string, string]> = [
    ["v09_partial_hybrid", "Simplification study (single-pass)"],
    ["v0916_deepseek", "DeepSeek diagnostic"],
    ["v0922_qwen", "Qwen diagnostic"],
    ["v08_dev140_p7fix", "Frozen production control (P7 rescore)"],
    ["v08", "Frozen production control"],
  ];
  for (const [needle, label] of LABELS) {
    if (runId.includes(needle)) return label;
  }
  return deSnake(runId.replace("exectv2_holistic_finding_assembly_", ""));
}

/**
 * Split labels. Maps the internal split codenames to the glossary's plain
 * split names. Returns the codename de-snaked for anything unrecognized.
 */
export function splitLabel(split: string | undefined | null): string {
  if (!split) return "—";
  const MAP: Record<string, string> = {
    // Gan
    validation: "Gan validation",
    test: "Gan holdout",
    "validation+test": "Validation + holdout",
    synthetic: "Synthetic",
    // Gan size prefixes
    validation750: "Gan dev (750)",
    validation250: "Gan validation (250)",
    validation50: "Gan validation (50)",
    validation25: "Gan validation (25)",
    test450: "Gan holdout (450)",
    // ExECT
    dev140: "ExECT dev (140)",
    dev25: "ExECT dev (25)",
    dev: "ExECT dev",
    "full-200": "ExECT full (200)",
    holdout: "Holdout",
  };
  if (MAP[split]) return MAP[split];
  // Composite splits like "validation+test" or size-tagged variants.
  if (split.includes("+")) return split.split("+").map(splitLabel).join(" + ");
  return deSnake(split);
}

/** De-snake_case a codename into Title Case words. */
function deSnake(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
