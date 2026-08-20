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

/** ExECT picker and badge labels (paper method names). */
export function exectActiveMethodLabel(method: ActiveMethod): string {
  if (method === "llm_with_rules") {
    return "LLM pre-post";
  }
  return activeMethodLabel(method);
}

export function familyLabel(pipelineFamily: string): string {
  const RULES_ONLY = activeMethodLabel("rules");
  const LLM_ONLY = activeMethodLabel("llm");
  const BUCKETS: Record<string, string> = {
    // rules-only
    rules: RULES_ONLY,
    rules_only: RULES_ONLY,

    // LLM-only
    llm_only_direct_labeler: `${LLM_ONLY} (direct)`,
    llm_structured_events: `${LLM_ONLY} (events)`,
    llm_first_direct_extractor: `${LLM_ONLY} (direct)`,
    llm_heavy_clinical_frequency_reasoner: `${LLM_ONLY} (heavy)`,
    llm_heavy_evidence_selection_with_deterministic_adapters: `${LLM_ONLY} (heavy + rules)`,
    llm_replacement_postprocessing_ablation: `${LLM_ONLY} (replacement)`,
    llm_only_canonical_pipeline: LLM_ONLY,
    llm: LLM_ONLY,

    // llm_with_rules (retained legacy family ids resolve to the same label)
    hybrid_structured_events: "LLM with rules",
    llm_with_rules: "LLM with rules",
    hybrid_clinical_frequency_state_graph: "LLM with rules (state graph)",
    reset_clinical_assessment_pipeline: "LLM with rules (reset)",
    dspy_final_selection_adjudicator: "LLM with rules (DSPy adjudicator)",

    // fresh-evidence / ceiling architectures
    fresh_evidence_reasoner: `${LLM_ONLY} (fresh-evidence)`,
  };

  return BUCKETS[pipelineFamily] ?? deSnake(pipelineFamily);
}

/** ExECT run labels for legacy registry rows (paper methods only). */
export function exectv2ArchitectureLabel(runId: string): string {
  if (runId.includes("llm_plus_rules") || runId.includes("llm_pre_post")) {
    return "LLM pre-post";
  }
  if (runId.includes("llm_only")) {
    return "LLM only";
  }
  if (runId.includes("deterministic") || runId === "rules") {
    return "Rules only";
  }
  return deSnake(runId.replace(/^exectv2_/, ""));
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

/**
 * Last diverging assembly action on an ExECT mention. Empty string when the
 * finding is still the model (or rules-only) baseline.
 */
export function lastRuleActionLabel(action: string | undefined | null): string {
  if (!action) return "";
  const LABELS: Record<string, string> = {
    normalized_prescription_from_dictionary:
      "Dictionary normalized this regimen",
    split_prescription_regimen_from_dictionary:
      "Dictionary split this regimen",
    rewrote_diagnosis_convention_from_dictionary:
      "Dictionary rewrote the diagnosis wording",
    added_diagnosis_residual_from_dictionary:
      "Dictionary added this diagnosis",
    added_sf_residual_convention_from_dictionary:
      "Dictionary added this seizure-frequency fact",
  };
  return LABELS[action] ?? deSnake(action);
}

/** De-snake_case a codename into Title Case words. */
function deSnake(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
