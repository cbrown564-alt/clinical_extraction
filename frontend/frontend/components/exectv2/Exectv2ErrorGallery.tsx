"use client";

import { useMemo, useState } from "react";
import { ArrowRight, ChevronDown, ChevronUp, GalleryHorizontalEnd, Layers } from "lucide-react";
import { exectv2Dataset, EXECTV2_FAMILIES, TONE_CLASSES } from "@/lib/datasets";
import type { DatasetTone, ErrorClassDescriptor } from "@/lib/datasets";
import {
  deriveRunErrors,
  summarizeErrors,
  type Exectv2ErrorClassId,
  type Exectv2ErrorRow,
} from "@/lib/datasets/adapters/exectv2Errors";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceEmpty,
  SurfaceLink,
} from "@/components/surface";
import {
  compactRunLabel,
  useExectv2RunDetails,
  useExectv2Runs,
  useExectv2Selection,
  useExectv2UrlState,
} from "./useExectv2";

const ERROR_CLASSES = exectv2Dataset.errorClasses;
const ERROR_CLASS_IDS = ERROR_CLASSES.map((c) => c.id as Exectv2ErrorClassId);

function classDescriptor(id: string): ErrorClassDescriptor | undefined {
  return ERROR_CLASSES.find((c) => c.id === id);
}

/** Solid fill for a tone, used by the distribution bar segments. */
const TONE_SOLID: Record<DatasetTone, string> = {
  deterministic: "bg-deterministic",
  "deterministic-alt": "bg-deterministic-alt",
  llm: "bg-llm",
  hybrid: "bg-hybrid",
  success: "bg-success",
  error: "bg-error",
  muted: "bg-muted",
};

// ── Executive summary ────────────────────────────────────────────────

function SummaryCards({
  total,
  byClass,
  byFamily,
}: {
  total: number;
  byClass: Record<Exectv2ErrorClassId, number>;
  byFamily: Record<string, number>;
}) {
  const dominantClass = ERROR_CLASS_IDS.reduce<Exectv2ErrorClassId | null>(
    (best, id) => (byClass[id] > (best ? byClass[best] : 0) ? id : best),
    null
  );
  const weakestFamily = EXECTV2_FAMILIES.reduce<{ id: string; count: number } | null>(
    (best, f) => {
      const count = byFamily[f.id] ?? 0;
      return count > (best?.count ?? 0) ? { id: f.id, count } : best;
    },
    null
  );

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-muted">Residuals</div>
        <div className="text-2xl font-semibold text-error">{total}</div>
      </div>
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-muted">Dominant Error</div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-lg font-semibold text-foreground">
            {dominantClass ? classDescriptor(dominantClass)?.label ?? dominantClass : "–"}
          </span>
          <span className="text-[11px] text-muted">{dominantClass ? byClass[dominantClass] : 0}</span>
        </div>
      </div>
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-muted">Weakest Family</div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-lg font-semibold text-foreground">
            {weakestFamily ? EXECTV2_FAMILIES.find((f) => f.id === weakestFamily.id)?.label ?? weakestFamily.id : "–"}
          </span>
          <span className="text-[11px] text-muted">{weakestFamily?.count ?? 0}</span>
        </div>
      </div>
    </div>
  );
}

// ── Distribution bar ─────────────────────────────────────────────────

function DistributionBar({
  byClass,
  total,
  activeClass,
  onSelect,
}: {
  byClass: Record<Exectv2ErrorClassId, number>;
  total: number;
  activeClass: Exectv2ErrorClassId | "all";
  onSelect: (id: Exectv2ErrorClassId | "all") => void;
}) {
  if (total === 0) return null;
  const segments = ERROR_CLASSES.filter((c) => byClass[c.id as Exectv2ErrorClassId] > 0);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">Error Distribution</div>
        <span className="text-[11px] text-muted">{total} residuals total</span>
      </div>
      <div className="flex h-3 overflow-hidden rounded-full border border-border bg-surface-raised">
        {segments.map((c) => {
          const count = byClass[c.id as Exectv2ErrorClassId];
          const active = activeClass === c.id;
          return (
            <button
              key={c.id}
              onClick={() => onSelect(active ? "all" : (c.id as Exectv2ErrorClassId))}
              className={`${TONE_SOLID[c.tone]} transition-opacity hover:opacity-80 ${active ? "ring-2 ring-inset ring-foreground/30" : ""}`}
              style={{ width: `${(count / total) * 100}%` }}
              title={`${c.label}: ${count}`}
            />
          );
        })}
      </div>
      <div className="flex flex-wrap gap-3">
        {segments.map((c) => {
          const count = byClass[c.id as Exectv2ErrorClassId];
          const active = activeClass === c.id;
          return (
            <button
              key={c.id}
              onClick={() => onSelect(active ? "all" : (c.id as Exectv2ErrorClassId))}
              className={`flex items-center gap-1.5 text-[11px] transition-opacity hover:opacity-70 ${active ? "font-semibold" : ""}`}
            >
              <div className={`h-2 w-2 rounded-full ${TONE_SOLID[c.tone]}`} />
              <span className="text-muted">{c.label}</span>
              <span className="font-medium text-foreground">{count}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Error row ────────────────────────────────────────────────────────

function ErrorRow({
  row,
  runLabel,
  expanded,
  onToggle,
}: {
  row: Exectv2ErrorRow;
  runLabel?: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="rounded-md border border-border bg-surface transition-colors hover:bg-surface-raised/40">
      <button onClick={onToggle} className="flex w-full items-center gap-2 px-3 py-2 text-left">
        <span className="rounded border border-border bg-surface-raised px-1.5 py-0.5 text-[11px] font-medium text-muted">
          {row.family}
        </span>
        <div className="flex min-w-0 flex-1 items-center gap-2 text-xs">
          <span className="truncate text-muted" title={row.goldText ?? "–"}>
            {row.goldText ?? "∅"}
          </span>
          <ArrowRight className="h-3 w-3 shrink-0 text-muted" />
          <span
            className={`truncate font-mono font-medium ${row.predictedText ? "text-foreground" : "text-error"}`}
            title={row.predictedText ?? "–"}
          >
            {row.predictedText ?? "∅ (missed)"}
          </span>
        </div>
        {runLabel && (
          <span className="shrink-0 rounded border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[11px] text-muted">
            {runLabel}
          </span>
        )}
        <span className="shrink-0 font-mono text-[11px] text-muted">{row.letterId}</span>
        {expanded ? (
          <ChevronUp className="h-3.5 w-3.5 shrink-0 text-muted" />
        ) : (
          <ChevronDown className="h-3.5 w-3.5 shrink-0 text-muted" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-border/50 px-3 pb-3 pt-2 space-y-2">
          <div className="mb-1">
            <SurfaceLink
              surface="workbench"
              datasetId="exectv2"
              params={{ run: row.runId, letter: row.letterId }}
              label="Open Letter"
            />
          </div>
          {row.detail && <p className="text-[11px] text-muted">{row.detail}</p>}
          {row.evidence && (
            <div className="space-y-1">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">Evidence</div>
              <blockquote className="font-serif text-xs italic leading-relaxed text-foreground">
                {row.evidence}
              </blockquote>
              <span
                className={`inline-block rounded px-1.5 py-0.5 text-[11px] font-medium ${
                  row.evidenceValid ? "bg-success/10 text-success" : "bg-error/10 text-error"
                }`}
              >
                {row.evidenceValid ? "exact evidence" : "evidence not exact"}
              </span>
            </div>
          )}
          {(row.componentOwner || row.sourceLane) && (
            <p className="truncate font-mono text-[11px] text-muted">
              {row.componentOwner || "–"}
              {row.sourceLane ? ` / ${row.sourceLane}` : ""}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ── Grouped sections ─────────────────────────────────────────────────

function ErrorGroups({
  rows,
  runLabelById,
  showRunBadge,
  activeClass,
  expandedId,
  onToggleRow,
}: {
  rows: Exectv2ErrorRow[];
  runLabelById: Map<string, string>;
  showRunBadge: boolean;
  activeClass: Exectv2ErrorClassId | "all";
  expandedId: string | null;
  onToggleRow: (id: string) => void;
}) {
  const grouped = useMemo(() => {
    const map = new Map<Exectv2ErrorClassId, Exectv2ErrorRow[]>();
    for (const id of ERROR_CLASS_IDS) map.set(id, []);
    for (const row of rows) map.get(row.errorClass)?.push(row);
    return map;
  }, [rows]);

  const [collapsed, setCollapsed] = useState<Set<Exectv2ErrorClassId>>(new Set());
  const toggle = (id: Exectv2ErrorClassId) =>
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const visible = ERROR_CLASS_IDS.filter((id) => {
    const list = grouped.get(id) ?? [];
    if (list.length === 0) return false;
    if (activeClass !== "all" && activeClass !== id) return false;
    return true;
  });

  if (visible.length === 0) {
    return (
      <SurfaceEmpty message="No residuals match the current filters." icon={<GalleryHorizontalEnd className="h-8 w-8" />} />
    );
  }

  return (
    <div className="space-y-4">
      {visible.map((id) => {
        const list = grouped.get(id) ?? [];
        const descriptor = classDescriptor(id);
        const isCollapsed = collapsed.has(id);
        return (
          <div key={id} className="rounded-lg border border-error/15 bg-error/[0.02]">
            <button
              onClick={() => toggle(id)}
              className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-surface-raised/30"
            >
              <span className={`rounded border px-1.5 py-0.5 text-[11px] font-medium ${TONE_CLASSES[descriptor?.tone ?? "muted"]}`}>
                {descriptor?.label ?? id}
              </span>
              <span className="rounded border border-border bg-surface-raised px-1.5 py-0 text-[11px] font-medium text-muted">
                {list.length}
              </span>
              <p className="flex-1 truncate text-[11px] text-muted">{descriptor?.description}</p>
              {isCollapsed ? <ChevronDown className="h-4 w-4 shrink-0 text-muted" /> : <ChevronUp className="h-4 w-4 shrink-0 text-muted" />}
            </button>
            {!isCollapsed && (
              <div className="space-y-1.5 px-2 pb-2">
                {list.map((row) => (
                  <ErrorRow
                    key={row.id}
                    row={row}
                    runLabel={showRunBadge ? runLabelById.get(row.runId) : undefined}
                    expanded={expandedId === row.id}
                    onToggle={() => onToggleRow(row.id)}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Gallery ──────────────────────────────────────────────────────────

export default function Exectv2ErrorGallery() {
  const { runs, isLoading, error } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();
  const { selectedRunIds } = useExectv2Selection(runs);
  const details = useExectv2RunDetails(selectedRunIds);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const selectedRuns = details.runs;

  const runLabelById = useMemo(() => {
    const map = new Map<string, string>();
    for (const r of runs) map.set(r.run_id, compactRunLabel(r));
    return map;
  }, [runs]);

  const familyFilter = get("family") ?? "all";
  const classFilter = (get("errorClass") as Exectv2ErrorClassId | "all") ?? "all";

  const allRows = useMemo(() => selectedRuns.flatMap((run) => deriveRunErrors(run)), [selectedRuns]);
  const summary = useMemo(() => summarizeErrors(allRows), [allRows]);

  // Family filter applies before grouping; class filter is handled by the groups.
  const familyFilteredRows = useMemo(
    () => (familyFilter === "all" ? allRows : allRows.filter((r) => r.family === familyFilter)),
    [allRows, familyFilter]
  );

  const showRunBadge = selectedRuns.length > 1;

  if (isLoading || details.isLoading) {
    return <SurfaceLoading message="Loading error gallery…" />;
  }
  if (error || details.error) {
    return (
      <SurfaceError
        title="ExECTv2 data failed to load"
        detail={String(error ?? details.error)}
      />
    );
  }

  return (
    <SurfaceLayout
      variant="report"
      maxWidth={1100}
      contentClassName="space-y-6"
      header={
        <SurfaceHeader
          surface="gallery"
          dataset={exectv2Dataset}
          description="Mention-level residuals derived from gold↔predicted matching across the selected architectures. Each row links to its letter in the Example Explorer."
          right={
            <>
              <span className="rounded border border-border bg-surface-raised px-2 py-0.5 text-[11px] text-muted">
                {selectedRunIds.length} {selectedRunIds.length === 1 ? "architecture" : "architectures"}
              </span>
              <SurfaceLink surface="observatory" datasetId="exectv2" params={{ runs: selectedRunIds.join(",") || undefined }} label="Select runs" />
            </>
          }
        />
      }
    >
      {selectedRuns.length === 0 ? (
        <SurfaceEmpty
          message="No architectures selected."
          hint="Select architectures in Aggregate Performance to populate the gallery."
          icon={<GalleryHorizontalEnd className="h-8 w-8" />}
        />
      ) : (
        <>
          <SummaryCards total={summary.total} byClass={summary.byClass} byFamily={summary.byFamily} />

          <div className="rounded-lg border border-border bg-surface p-4">
            <DistributionBar
              byClass={summary.byClass}
              total={summary.total}
              activeClass={classFilter}
              onSelect={(id) => set({ errorClass: id === "all" ? undefined : id })}
            />
          </div>

          {/* Family filter chips */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => set({ family: undefined })}
              className={`rounded-md border px-2 py-1 text-[11px] font-medium transition-colors ${
                familyFilter === "all" ? "border-foreground/30 bg-surface-raised text-foreground" : "border-border text-muted hover:bg-surface-raised"
              }`}
            >
              All families
            </button>
            {EXECTV2_FAMILIES.map((family) => {
              const count = summary.byFamily[family.id] ?? 0;
              const active = familyFilter === family.id;
              return (
                <button
                  key={family.id}
                  onClick={() => set({ family: active ? undefined : family.id })}
                  disabled={count === 0}
                  className={`rounded-md border px-2 py-1 text-[11px] font-medium transition-colors disabled:opacity-40 ${
                    active ? TONE_CLASSES[family.tone] : "border-border text-muted hover:bg-surface-raised"
                  }`}
                >
                  {family.label} · {count}
                </button>
              );
            })}
          </div>

          {/* Grouped error sections */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-muted" />
              <span className="text-xs font-semibold uppercase tracking-wider text-muted">Error Cases</span>
              <span className="text-[11px] text-muted">{familyFilteredRows.length} rows</span>
            </div>
            <ErrorGroups
              rows={familyFilteredRows}
              runLabelById={runLabelById}
              showRunBadge={showRunBadge}
              activeClass={classFilter}
              expandedId={expandedId}
              onToggleRow={(id) => setExpandedId((prev) => (prev === id ? null : id))}
            />
          </div>
        </>
      )}
    </SurfaceLayout>
  );
}
