"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  ChevronRight,
  HelpCircle,
  PanelLeftClose,
  PanelLeftOpen,
  ShieldCheck,
  X,
} from "lucide-react";
import {
  fetchGoldAuditDecisions,
  fetchGoldAuditRows,
  fetchRecord,
  postGoldAuditDecision,
} from "@/lib/api";
import { useActiveDataset } from "@/lib/datasets";
import type {
  FullRecordResponse,
  GoldAuditDecision,
  GoldAuditRow,
} from "@/lib/types";
import { splitLabel } from "@/lib/plainLanguageLabels";
import LetterRenderer from "./LetterRenderer";

const SIMPLE_CLASSES = [
  { value: "correct" as const, label: "Correct", shortcut: "1", icon: Check },
  { value: "ambiguous" as const, label: "Ambiguous", shortcut: "2", icon: HelpCircle },
  { value: "wrong" as const, label: "Wrong", shortcut: "3", icon: X },
];

const ASSERTION_STATUSES = ["present", "negated", "historical", "future", "uncertain", "unsupported"] as const;
const ENTAILMENT_OPTIONS = ["entailed", "plausible", "ambiguous", "contradicted", "absent"] as const;
const CONFIDENCE_OPTIONS = ["low", "medium", "high"] as const;

function rowId(row: GoldAuditRow): string {
  return row.audit_id ?? String(row.source_row_index);
}

function decisionId(decision: GoldAuditDecision): string {
  return decision.audit_id ?? String(decision.source_row_index);
}

function parseBool(value: string | boolean | undefined): boolean {
  return typeof value === "boolean" ? value : value?.toLowerCase() === "true";
}

function badgeStyle(value?: string | null): string {
  if (["correct", "entailed", "high", "present"].includes(value ?? "")) {
    return "border-success/25 bg-success/10 text-success";
  }
  if (["wrong", "contradicted", "unsupported", "low"].includes(value ?? "")) {
    return "border-error/25 bg-error/10 text-error";
  }
  return "border-llm/25 bg-llm/10 text-llm";
}

function exactHighlight(text: string, span: string, offset?: number) {
  let start = typeof offset === "number" && text.slice(offset, offset + span.length) === span
    ? offset
    : text.indexOf(span);
  if (start < 0) start = text.toLowerCase().indexOf(span.toLowerCase());
  return start < 0
    ? []
    : [{ start, end: start + span.length, kind: "gold" as const, label: "Source span under review" }];
}

function ChoiceGroup<T extends string>({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: readonly T[];
  value: T | null;
  onChange: (value: T) => void;
}) {
  return (
    <fieldset className="space-y-1.5">
      <legend className="text-[11px] font-semibold uppercase tracking-wider text-muted">{label}</legend>
      <div className="flex flex-wrap gap-1.5">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            aria-pressed={value === option}
            onClick={() => onChange(option)}
            className={`rounded-md border px-2 py-1.5 text-[11px] font-medium capitalize transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-deterministic ${
              value === option ? badgeStyle(option) : "border-border bg-surface text-muted hover:bg-surface-raised hover:text-foreground"
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

export default function GoldAuditPanel() {
  const datasetId = useActiveDataset();
  return <DatasetGoldAuditPanel key={datasetId} datasetId={datasetId} />;
}

function DatasetGoldAuditPanel({ datasetId }: { datasetId: "gan2026" | "exectv2" }) {
  const isExect = datasetId === "exectv2";
  const split = isExect ? "full200" : "validation";
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<"queue" | "reviewed">("queue");
  const [queueOpen, setQueueOpen] = useState(true);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [simpleClass, setSimpleClass] = useState<"correct" | "ambiguous" | "wrong" | null>(null);
  const [notes, setNotes] = useState("");
  const [correctedGoldLabel, setCorrectedGoldLabel] = useState("");
  const [assertionStatus, setAssertionStatus] = useState<GoldAuditDecision["assertion_status"]>(null);
  const [attributeEntailment, setAttributeEntailment] = useState<GoldAuditDecision["attribute_entailment"]>(null);
  const [factBoundaries, setFactBoundaries] = useState("");
  const [clinicalInterpretation, setClinicalInterpretation] = useState("");
  const [reviewerRationale, setReviewerRationale] = useState("");
  const [reviewConfidence, setReviewConfidence] = useState<GoldAuditDecision["review_confidence"]>(null);
  const [auditor, setAuditor] = useState("maintainer");

  const rowsQuery = useQuery({
    queryKey: ["gold-audit-rows", datasetId, split],
    queryFn: () => fetchGoldAuditRows(split, datasetId),
  });
  const decisionsQuery = useQuery({
    queryKey: ["gold-audit-decisions", datasetId, split],
    queryFn: () => fetchGoldAuditDecisions(split, datasetId),
  });

  const decisionsMap = useMemo(
    () => new Map((decisionsQuery.data?.decisions ?? []).map((decision) => [decisionId(decision), decision])),
    [decisionsQuery.data?.decisions]
  );

  const sortedRows = useMemo(() => {
    const rows = [...(rowsQuery.data?.rows ?? [])];
    rows.sort((a, b) => {
      const aDone = decisionsMap.has(rowId(a));
      const bDone = decisionsMap.has(rowId(b));
      if (aDone !== bDone) return aDone ? 1 : -1;
      return (b.priority_score ?? 0) - (a.priority_score ?? 0);
    });
    return rows;
  }, [decisionsMap, rowsQuery.data?.rows]);

  const visibleRows = useMemo(() => {
    if (mode === "reviewed") return sortedRows.filter((row) => decisionsMap.has(rowId(row)));
    return sortedRows;
  }, [decisionsMap, mode, sortedRows]);

  const currentRow = useMemo(() => {
    if (currentId) return visibleRows.find((row) => rowId(row) === currentId);
    return visibleRows.find((row) => !decisionsMap.has(rowId(row))) ?? visibleRows[0];
  }, [currentId, decisionsMap, visibleRows]);

  const existing = currentRow ? decisionsMap.get(rowId(currentRow)) : undefined;
  const ganSourceIndex = currentRow?.source_row_index == null ? null : Number(currentRow.source_row_index);
  const fullRecord = useQuery<FullRecordResponse>({
    queryKey: ["record", datasetId, split, ganSourceIndex],
    queryFn: () => fetchRecord(split, ganSourceIndex!),
    enabled: !isExect && ganSourceIndex != null,
  });

  useEffect(() => {
    if (!currentRow) return;
    // A keyed record switch intentionally initializes the editable review draft.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSimpleClass(existing?.simple_class ?? null);
    setNotes(existing?.notes ?? "");
    setCorrectedGoldLabel(existing?.corrected_gold_label ?? "");
    setAssertionStatus(existing?.assertion_status ?? null);
    setAttributeEntailment(existing?.attribute_entailment ?? null);
    setFactBoundaries(existing?.fact_boundaries ?? "");
    setClinicalInterpretation(existing?.clinical_interpretation ?? "");
    setReviewerRationale(existing?.reviewer_rationale ?? "");
    setReviewConfidence(existing?.review_confidence ?? null);
    setAuditor(existing?.auditor ?? "maintainer");
  }, [currentRow, existing]);

  const saveMutation = useMutation({
    mutationFn: postGoldAuditDecision,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["gold-audit-rows", datasetId] }),
        queryClient.invalidateQueries({ queryKey: ["gold-audit-decisions", datasetId] }),
      ]);
      setCurrentId(null);
    },
  });

  const goNext = useCallback(() => {
    if (!currentRow) return;
    const index = visibleRows.findIndex((row) => rowId(row) === rowId(currentRow));
    if (index >= 0 && index < visibleRows.length - 1) setCurrentId(rowId(visibleRows[index + 1]));
  }, [currentRow, visibleRows]);

  const canSave = isExect
    ? Boolean(assertionStatus && attributeEntailment && reviewConfidence && auditor.trim())
    : Boolean(simpleClass);

  const handleSave = useCallback(() => {
    if (!currentRow || !canSave) return;
    const base = { dataset: datasetId, split, auditor: auditor.trim() } as GoldAuditDecision;
    const decision: GoldAuditDecision = isExect
      ? {
          ...base,
          audit_id: rowId(currentRow),
          assertion_status: assertionStatus,
          attribute_entailment: attributeEntailment,
          fact_boundaries: factBoundaries || null,
          clinical_interpretation: clinicalInterpretation || null,
          reviewer_rationale: reviewerRationale || null,
          review_confidence: reviewConfidence,
        }
      : {
          ...base,
          source_row_index: Number(currentRow.source_row_index),
          simple_class: simpleClass,
          rq10_class: null,
          notes,
          corrected_gold_label: correctedGoldLabel || null,
          benchmark_convention_flag: false,
          all_system_fail: false,
          exact_evidence_but_scorer_wrong: false,
          clinically_defensible_alternative: false,
          likely_gold_defect: false,
        };
    saveMutation.mutate(decision);
  }, [assertionStatus, attributeEntailment, auditor, canSave, clinicalInterpretation, correctedGoldLabel, currentRow, datasetId, factBoundaries, isExect, notes, reviewConfidence, reviewerRationale, simpleClass, split, saveMutation]);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
      if (!isExect && ["1", "2", "3"].includes(event.key)) {
        event.preventDefault();
        setSimpleClass(SIMPLE_CLASSES[Number(event.key) - 1].value);
      } else if ((event.key === "j" || event.key === "ArrowRight") && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        goNext();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [goNext, isExect]);

  const sourceText = isExect
    ? currentRow?.full_letter_text ?? currentRow?.source_context ?? ""
    : fullRecord.data?.note_text ?? currentRow?.note_text_single_line?.replace(/\\n/g, "\n") ?? "";
  const highlights = useMemo(() => {
    if (!currentRow) return [];
    if (isExect) {
      return exactHighlight(sourceText, currentRow.source_span ?? "", currentRow.span_offsets?.[0]);
    }
    return exactHighlight(sourceText, currentRow.gold_reference ?? "");
  }, [currentRow, isExect, sourceText]);

  if (rowsQuery.isLoading || decisionsQuery.isLoading) {
    return <div className="flex h-full items-center justify-center text-sm text-muted">Loading gold audit queue…</div>;
  }

  if (!currentRow) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-muted">
        <ShieldCheck className="h-6 w-6" />
        <p className="text-sm font-medium">{mode === "reviewed" ? "No completed reviews yet." : "No audit packets available."}</p>
      </div>
    );
  }

  const id = rowId(currentRow);
  const decided = decisionsMap.size;
  const total = rowsQuery.data?.total ?? 0;
  const progress = total ? decided / total : 0;
  const currentIndex = visibleRows.findIndex((row) => rowId(row) === id);

  return (
    <div className="flex h-full min-h-0 flex-col bg-background">
      <header className="flex flex-wrap items-center gap-3 border-b border-border bg-surface px-4 py-2">
        <button
          onClick={() => setQueueOpen((open) => !open)}
          aria-label={queueOpen ? "Close audit queue" : "Open audit queue"}
          className="rounded-md border border-border bg-surface p-1.5 text-muted hover:bg-surface-raised hover:text-foreground focus-visible:outline-2 focus-visible:outline-deterministic"
        >
          {queueOpen ? <PanelLeftClose className="h-3.5 w-3.5" /> : <PanelLeftOpen className="h-3.5 w-3.5" />}
        </button>

        <div className="flex overflow-hidden rounded-md border border-border bg-surface-raised">
          {(["queue", "reviewed"] as const).map((value) => (
            <button
              key={value}
              onClick={() => { setMode(value); setCurrentId(null); }}
              className={`px-3 py-1.5 text-[11px] font-medium capitalize ${mode === value ? "bg-surface text-foreground" : "text-muted hover:text-foreground"}`}
            >
              {value} {value === "reviewed" ? `(${decided})` : ""}
            </button>
          ))}
        </div>

        <div className="min-w-40 flex-1">
          <div className="h-1.5 overflow-hidden rounded-full bg-surface-raised">
            <div className="h-full rounded-full bg-deterministic transition-[width] duration-200" style={{ width: `${progress * 100}%` }} />
          </div>
          <div className="mt-1 flex justify-between text-[11px] text-muted">
            <span>{decided.toLocaleString()} of {total.toLocaleString()} reviewed</span>
            <span>{(progress * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px]">
          <span className="rounded border border-deterministic/20 bg-deterministic/10 px-2 py-1 font-medium text-deterministic">
            {isExect ? "ExECTv2 · blinded full200" : `Gan 2026 · ${splitLabel("validation750")}`}
          </span>
          {existing && (
            <span className={`rounded border px-2 py-1 font-medium capitalize ${badgeStyle(existing.review_confidence ?? existing.simple_class)}`}>
              {existing.review_confidence ? `${existing.review_confidence} confidence` : existing.simple_class}
            </span>
          )}
        </div>

        <button
          onClick={goNext}
          disabled={currentIndex >= visibleRows.length - 1}
          className="flex items-center gap-1 rounded-md border border-border bg-surface px-2 py-1.5 text-[11px] font-medium text-muted hover:text-foreground disabled:opacity-30"
        >
          Next <ChevronRight className="h-3 w-3" />
        </button>
      </header>

      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        {queueOpen && (
          <aside className="flex max-h-48 w-full shrink-0 flex-col border-b border-border bg-surface lg:max-h-none lg:w-64 lg:border-b-0 lg:border-r">
            <div className="flex items-center justify-between border-b border-border px-3 py-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">{mode} ({visibleRows.length})</span>
              <span className="text-[11px] text-muted">priority ordered</span>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">
              {visibleRows.map((row) => {
                const itemId = rowId(row);
                const decision = decisionsMap.get(itemId);
                return (
                  <button
                    key={itemId}
                    onClick={() => setCurrentId(itemId)}
                    className={`w-full border-b border-border px-3 py-2 text-left transition-colors ${id === itemId ? "bg-deterministic/8" : "hover:bg-surface-raised"}`}
                  >
                    <div className="flex items-center gap-2">
                      {decision ? <Check className="h-3 w-3 text-success" /> : <span className="h-2 w-2 rounded-full border border-border" />}
                      <span className="min-w-0 flex-1 truncate text-xs font-medium text-foreground">
                        {isExect ? `${row.letter_id} · ${row.entity}` : row.gold_label}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center justify-between pl-5 text-[11px] text-muted">
                      <span className="font-mono">{isExect ? itemId.slice(0, 8) : `#${row.source_row_index}`}</span>
                      {decision && <span className="capitalize">{decision.review_confidence ?? decision.simple_class}</span>}
                    </div>
                  </button>
                );
              })}
            </div>
          </aside>
        )}

        <section aria-label="Gold annotation evidence" className="min-h-0 min-w-0 flex-1 overflow-y-auto">
          <div className="mx-auto max-w-5xl p-5">
            <div className="mb-4 flex flex-wrap items-start justify-between gap-3 border-b border-border pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-lg font-semibold text-foreground">
                    {isExect ? currentRow.source_span : currentRow.gold_label}
                  </h1>
                  {existing && <span className="rounded border border-success/25 bg-success/10 px-2 py-0.5 text-[11px] font-medium text-success">Reviewed</span>}
                </div>
                <p className="mt-1 text-xs text-muted">
                  {isExect
                    ? `${currentRow.letter_id} · ${currentRow.entity} · fact ${id}`
                    : currentRow.gold_reference}
                </p>
              </div>
              <div className="text-right text-[11px] text-muted">
                {isExect ? (
                  <>
                    <p>Full source letter</p>
                    <p className="text-foreground">Gold attributes and predictions hidden</p>
                  </>
                ) : (
                  <>
                    <p>Kind: <span className="text-foreground">{currentRow.gold_label_kind}</span></p>
                    <p>Reference found: <span className={parseBool(currentRow.reference_found_in_note) ? "text-success" : "text-error"}>{parseBool(currentRow.reference_found_in_note) ? "Yes" : "No"}</span></p>
                  </>
                )}
              </div>
            </div>
            <LetterRenderer text={sourceText} highlights={highlights} />
          </div>
        </section>

        <aside className="flex w-full shrink-0 flex-col border-t border-border bg-surface lg:w-[360px] lg:border-l lg:border-t-0">
          <div className="border-b border-border px-4 py-3">
            <h2 className="text-xs font-semibold text-foreground">{isExect ? "Independent source review" : "Audit decision"}</h2>
            <p className="mt-1 text-[11px] leading-relaxed text-muted">
              {isExect
                ? "Judge the source before consulting stored gold, predictions, scores, or issue leads. Confidence is your certainty in this review."
                : "Classify the gold reference and record any ambiguity or correction."}
            </p>
          </div>

          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
            <label className="block space-y-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">Reviewer ID</span>
              <input
                value={auditor}
                onChange={(event) => setAuditor(event.target.value)}
                className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground focus:border-deterministic focus:outline-2 focus:outline-deterministic/20"
              />
            </label>

            {isExect ? (
              <>
                <ChoiceGroup label="Assertion status" options={ASSERTION_STATUSES} value={assertionStatus ?? null} onChange={setAssertionStatus} />
                <ChoiceGroup label="Attribute entailment" options={ENTAILMENT_OPTIONS} value={attributeEntailment ?? null} onChange={setAttributeEntailment} />
                <ChoiceGroup label="Reviewer confidence" options={CONFIDENCE_OPTIONS} value={reviewConfidence ?? null} onChange={setReviewConfidence} />
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">Fact boundaries</span>
                  <select
                    value={factBoundaries}
                    onChange={(event) => setFactBoundaries(event.target.value)}
                    className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground focus:border-deterministic focus:outline-2 focus:outline-deterministic/20"
                  >
                    <option value="">Not recorded</option>
                    <option value="correct">Correct</option>
                    <option value="too_narrow">Too narrow</option>
                    <option value="too_broad">Too broad</option>
                    <option value="merged_facts">Merged facts</option>
                    <option value="duplicated_fact">Duplicated fact</option>
                    <option value="unclear">Unclear</option>
                  </select>
                </label>
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">Clinical interpretation</span>
                  <textarea value={clinicalInterpretation} onChange={(event) => setClinicalInterpretation(event.target.value)} placeholder="Record temporality, current status, or clinical meaning…" className="h-24 w-full resize-y rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground placeholder:text-muted focus:border-deterministic focus:outline-2 focus:outline-deterministic/20" />
                </label>
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">Reviewer rationale</span>
                  <textarea value={reviewerRationale} onChange={(event) => setReviewerRationale(event.target.value)} placeholder="Cite the source language supporting your verdict…" className="h-28 w-full resize-y rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground placeholder:text-muted focus:border-deterministic focus:outline-2 focus:outline-deterministic/20" />
                </label>
              </>
            ) : (
              <>
                <ChoiceGroup label="Gold assessment" options={SIMPLE_CLASSES.map((item) => item.value)} value={simpleClass} onChange={setSimpleClass} />
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">Review notes</span>
                  <textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Describe ambiguity or error…" className="h-32 w-full resize-y rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground placeholder:text-muted focus:border-deterministic focus:outline-2 focus:outline-deterministic/20" />
                </label>
                <label className="block space-y-1.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-muted">Corrected gold label</span>
                  <input value={correctedGoldLabel} onChange={(event) => setCorrectedGoldLabel(event.target.value)} placeholder="Optional correction" className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground placeholder:text-muted focus:border-deterministic focus:outline-2 focus:outline-deterministic/20" />
                </label>
                {currentRow.predicted_simple_class && (
                  <div className="rounded-lg border border-border bg-surface-raised p-3 text-[11px] text-muted">
                    Queue model: <span className="font-medium text-foreground">{currentRow.predicted_simple_class}</span> at {Math.round((currentRow.prediction_confidence ?? 0) * 100)}% confidence. This ranks review order only.
                  </div>
                )}
              </>
            )}
          </div>

          <div className="border-t border-border p-3">
            <button
              onClick={handleSave}
              disabled={!canSave || saveMutation.isPending}
              className="w-full rounded-lg bg-deterministic px-3 py-2.5 text-sm font-medium text-surface transition-colors hover:bg-deterministic/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-deterministic disabled:cursor-not-allowed disabled:opacity-40"
            >
              {saveMutation.isPending ? "Saving…" : existing ? "Update review" : "Save and next"}
            </button>
            {saveMutation.isError && <p className="mt-2 text-center text-[11px] text-error">Could not save: {String(saveMutation.error)}</p>}
          </div>
        </aside>
      </div>
    </div>
  );
}
