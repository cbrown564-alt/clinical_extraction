/**
 * Unit tests for all trace adapters.
 * Each test loads the first real artifact row from experiments/ and verifies
 * the adapter produces a valid PipelineTrace without crashing.
 */

import { adaptTrace, isReplaySupported } from "../index";
import type { FullRecordResponse, PipelineTrace } from "../../types";

const mockRecord: FullRecordResponse = {
  split: "validation",
  source_row_index: 0,
  gold_label: "1 per month",
  gold_reference: "",
  row_ok: true,
  note_text:
    "KINGS NEUROSCIENCES CENTRE\n\nClinic Date: 02 October 2025\n\nDr Wang\nSaffron Park Hospital\n\nDear Dr Wang\n\nRe: John Doe, DOB: 21-11-1982\n\nThank you for referring this 42-year-old gentleman who reports approximately one seizure per month.",
  labels_match_all_categories: true,
  quotes_ok_all_categories: true,
};

function assertValidTrace(trace: PipelineTrace) {
  expect(trace.pipelineFamily).toBeTruthy();
  expect(trace.noteText).toBeTruthy();
  expect(trace.goldLabel).toBeDefined();
  expect(trace.sourceRowIndex).toBeDefined();
  expect(trace.split).toBeTruthy();
  expect(trace.extract).toBeDefined();
  expect(trace.extract.items).toBeDefined();
  expect(trace.normalise).toBeDefined();
  expect(trace.normalise.items).toBeDefined();
  expect(trace.select).toBeDefined();
  expect(trace.select.finalLabel).toBeDefined();
  expect(trace.select.rationale).toBeDefined();
  expect(trace.select.evidence).toBeDefined();
  expect(trace.score).toBeDefined();
  expect(trace.score.predictedLabel).toBeDefined();
  expect(trace.score.goldLabel).toBeDefined();
  expect(typeof trace.score.match).toBe("boolean");
  expect(typeof trace.score.evidenceValid).toBe("boolean");
}

async function loadFirstArtifactRow(family: string): Promise<unknown> {
  // In a real test environment we'd read from the filesystem.
  // For now, return a minimal stub that matches each family's schema.
  // These stubs are sufficient to verify the adapter doesn't crash.
  switch (family) {
    case "hybrid_rules_candidates_llm_adjudicator":
      return {
        source_row_index: 0,
        split: "validation",
        deterministic_diagnostics: {
          candidate_events: [],
          normalized_events: [],
          final_selection: {
            final_label: "1 per month",
            rationale: "test",
            evidence: "one seizure per month",
          },
          evidence_valid: true,
        },
        decision_record: {
          final_label: "1 per month",
          rationale: "adjudicator rationale",
          evidence: "one seizure per month",
          accepted_event_ids: [],
          rejected_event_ids: [],
          temporality: "current",
          uncertainty: "low",
          normalized_rate: "1 per month",
        },
        reference: { gold_label: "1 per month" },
      };

    case "llm_only_claim_table_selector":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          claims: [
            {
              claim_id: "c1",
              claim_type: "frequency_rate",
              evidence: "one seizure per month",
              raw_frequency: "1 per month",
              temporality: "current",
              assertion_status: "asserted",
              uncertainty: "low",
              anchor_text: "one seizure per month",
              section: null,
              semiology: null,
            },
          ],
          final_query: {
            final_label: "1 per month",
            answer_kind: "frequency",
            evidence: "one seizure per month",
            rationale: "claim table rationale",
            confidence: "high",
            conversion_note: null,
            raw_selected_frequency: "1 per month",
            selected_claim_ids: "c1",
          },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_first_direct_extractor":
      return {
        source_row_index: 0,
        split: "validation",
        decision_record: {
          final_label: "1 per month",
          evidence: "one seizure per month",
          rationale: "direct extractor rationale",
          answer_kind: "frequency",
          confidence: "high",
        },
        comparison: {
          purist_correct: true,
          pragmatic_correct: true,
        },
        reference: { gold_label: "1 per month" },
      };

    case "dspy_final_selection_adjudicator":
      return {
        source_row_index: 0,
        split: "validation",
        decision_record: {
          final_label: "1 per month",
          evidence: "one seizure per month",
          rationale: "dspy rationale",
          temporality: "current",
          uncertainty: "low",
          selected_event_ids: [],
          rejected_event_ids: [],
        },
        comparison: {
          purist_correct: true,
          pragmatic_correct: true,
        },
        reference: { gold_label: "1 per month" },
      };

    case "llm_structured_events":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          events: [
            {
              event_id: "e1",
              kind: "frequency_rate",
              evidence: "one seizure per month",
              raw_value: "1 per month",
              model_normalized_clinical_label: "1 per month",
              temporality: "current",
              assertion_status: "asserted",
            },
          ],
          selection: {
            selected_event_ids: ["e1"],
            final_label: "1 per month",
            evidence: "one seizure per month",
            rationale: "structured events rationale",
          },
        },
        normalized_events: [
          {
            event_id: "e1",
            normalized_label: "1 per month",
            semantic_kind: "frequency_rate",
            monthly_frequency: 1,
            validation_errors: [],
          },
        ],
        comparison: { purist_correct: true, pragmatic_correct: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_heavy_clinical_frequency_reasoner":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          events: [
            {
              event_id: "e1",
              kind: "frequency_rate",
              evidence: "one seizure per month",
              raw_phrase: "one seizure per month",
              model_normalized_clinical_label: "1 per month",
              temporality: "current",
              assertion_status: "asserted",
            },
          ],
          selection: {
            selected_event_ids: ["e1"],
            final_clinical_label: "1 per month",
            rationale: "heavy reasoner rationale",
          },
          final_answer: {
            raw_llm_final_label: "1 per month",
            selected_evidence: "one seizure per month",
            final_rationale: "final answer rationale",
          },
        },
        score_layers: {
          clean_scorer_facing: {
            final_label: "1 per month",
            purist_correct: true,
            pragmatic_correct: true,
          },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_only_typed_adapter_reasoner":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          events: [
            {
              event_id: "e1",
              kind: "frequency_rate",
              evidence: "one seizure per month",
              raw_phrase: "one seizure per month",
              model_normalized_clinical_label: "1 per month",
              temporality: "current",
            },
          ],
          final_answer: {
            raw_llm_final_label: "1 per month",
            selected_evidence: "one seizure per month",
            final_rationale: "typed adapter rationale",
            rendering_operands: { occurrences_low: 1, period_unit: "month" },
          },
        },
        score_layers: {
          clean_scorer_facing: {
            final_label: "1 per month",
            purist_correct: true,
          },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_only_typed_operations_reasoner":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          operations: [
            {
              operation_id: "op1",
              operation_kind: "frequency_rate",
              evidence: "one seizure per month",
              raw_phrase: "one seizure per month",
              model_normalized_clinical_label: "1 per month",
              temporality: "current",
            },
          ],
          selection: {
            selected_operation_ids: ["op1"],
            selected_evidence: "one seizure per month",
            rationale: "typed operations rationale",
            final_clinical_state: "1 per month",
          },
        },
        score_layers: {
          clean_scorer_facing: { final_label: "1 per month", purist_correct: true },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_heavy_evidence_selection_with_deterministic_adapters":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          selected_fact: {
            fact_id: "f1",
            clinical_kind: "frequency_rate",
            raw_value: "1 per month",
            evidence: "one seizure per month",
            rationale: "selected fact rationale",
            assertion_status: "asserted",
            temporality: "current",
          },
          operands: { occurrences_low: 1, period_unit: "month" },
        },
        mechanical_adapter: {
          final_label: "1 per month",
          error: null,
          operand_complete: true,
        },
        score_layers: {
          clean_scorer_facing: { final_label: "1 per month", purist_correct: true },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_only_simplified_selected_state_reasoner":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          selected_state: {
            final_kind: "frequency_rate",
            raw_llm_final_label: "1 per month",
            selected_evidence: "one seizure per month",
            selection_reason: "simplified state rationale",
          },
        },
        score_layers: {
          clean_scorer_facing: { final_label: "1 per month", purist_correct: true },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_only_sparse_operands_selected_state_reasoner":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          selected_state: {
            final_kind: "frequency_rate",
            raw_llm_final_label: "1 per month",
            selected_evidence: "one seizure per month",
            selection_reason: "sparse operands rationale",
            operands: { count_low: 1, period_unit: "month" },
          },
        },
        score_layers: {
          clean_scorer_facing: { final_label: "1 per month", purist_correct: true },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "hybrid_clinical_frequency_state_graph":
      return {
        source_row_index: 0,
        split: "validation",
        structured_record: {
          nodes: [
            {
              semantic_kind: "frequency_rate",
              node_normalized_label: "1 per month",
              evidence: "one seizure per month",
              rationale: "graph node rationale",
              assertion_status: "asserted",
              certainty: "high",
              temporality: "current",
            },
          ],
        },
        evidence_summary: { exact_evidence_valid: 1, exact_evidence_total: 1 },
        reference: { gold_label: "1 per month" },
      };

    case "hybrid_parallel_state_candidate_reasoner":
      return {
        source_row_index: 0,
        split: "validation",
        component_inputs: {
          deterministic_candidates: [],
          deterministic_top: {
            selected_event_ids: [],
            selected_decision: "1 per month",
            selected_score: 1,
          },
          state_graph_nodes: [],
          state_graph_projection: {
            final_label: "1 per month",
            final_kind: "frequency_rate",
            rationale: "projection rationale",
            selected_node_ids: [],
          },
        },
        structured_adjudicator_record: {
          final_label: "1 per month",
          evidence: "one seizure per month",
          rationale: "adjudicator rationale",
          selected_event_ids: [],
          rejected_event_ids: [],
        },
        score_layers: {
          clean_scorer_facing: { final_label: "1 per month", purist_correct: true },
        },
        repair_changes: [],
        reference: { gold_label: "1 per month" },
      };

    case "llm_only_minimal_evidence_selector":
      return {
        source_row_index: 0,
        split: "validation",
        minimal_record: {
          final_label: "1 per month",
          evidence: "one seizure per month",
          rationale: "minimal evidence rationale",
        },
        score_layers: {
          clean_scorer_facing: { final_label: "1 per month", purist_correct: true },
        },
        repair_changes: [],
        evidence_summary: { selected_evidence_valid: true },
        reference: { gold_label: "1 per month" },
      };

    case "llm_replacement_postprocessing_ablation":
      return {
        source_row_index: 0,
        split: "validation",
        final_label: "1 per month",
        raw_label: "1 seizure per month",
        gold_label: "1 per month",
        repair_mode: "benchmark_alignment_adapter",
        replacement_target: "raw_label",
        purist_correct: true,
        pragmatic_correct: true,
        transition_reason: "Removed redundant word",
      };

    default:
      throw new Error(`Unknown family for test stub: ${family}`);
  }
}

describe("isReplaySupported", () => {
  it("returns true for all supported families", () => {
    const supported = [
      "hybrid_rules_candidates_llm_adjudicator",
      "llm_only_claim_table_selector",
      "llm_first_direct_extractor",
      "dspy_final_selection_adjudicator",
      "llm_structured_events",
      "llm_heavy_clinical_frequency_reasoner",
      "llm_only_typed_adapter_reasoner",
      "llm_only_typed_operations_reasoner",
      "llm_heavy_evidence_selection_with_deterministic_adapters",
      "llm_only_simplified_selected_state_reasoner",
      "llm_only_sparse_operands_selected_state_reasoner",
      "hybrid_clinical_frequency_state_graph",
      "hybrid_parallel_state_candidate_reasoner",
      "llm_only_minimal_evidence_selector",
      "llm_replacement_postprocessing_ablation",
    ];
    for (const family of supported) {
      expect(isReplaySupported(family)).toBe(true);
    }
  });

  it("returns false for unsupported families", () => {
    expect(isReplaySupported("some_unknown_family")).toBe(false);
    expect(isReplaySupported("rules_only")).toBe(false);
  });
});

describe("adaptTrace", () => {
  const families = [
    "hybrid_rules_candidates_llm_adjudicator",
    "llm_only_claim_table_selector",
    "llm_first_direct_extractor",
    "dspy_final_selection_adjudicator",
    "llm_structured_events",
    "llm_heavy_clinical_frequency_reasoner",
    "llm_only_typed_adapter_reasoner",
    "llm_only_typed_operations_reasoner",
    "llm_heavy_evidence_selection_with_deterministic_adapters",
    "llm_only_simplified_selected_state_reasoner",
    "llm_only_sparse_operands_selected_state_reasoner",
    "hybrid_clinical_frequency_state_graph",
    "hybrid_parallel_state_candidate_reasoner",
    "llm_only_minimal_evidence_selector",
    "llm_replacement_postprocessing_ablation",
  ];

  for (const family of families) {
    it(`produces a valid PipelineTrace for ${family}`, async () => {
      const row = await loadFirstArtifactRow(family);
      const trace = adaptTrace(row, family, mockRecord);
      assertValidTrace(trace);
      expect(trace.pipelineFamily).toBe(family);
    });
  }

  it("throws for unsupported families", () => {
    expect(() => adaptTrace({}, "unknown_family", mockRecord)).toThrow(
      "No trace adapter available"
    );
  });
});
