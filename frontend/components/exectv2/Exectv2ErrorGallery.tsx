"use client";

import { useMemo } from "react";
import Link from "next/link";
import { ArrowRight, ExternalLink, GalleryHorizontalEnd, ShieldAlert } from "lucide-react";
import { exectv2Dataset, EXECTV2_FAMILIES, surfaceHref, TONE_CLASSES } from "@/lib/datasets";
import type { ErrorClassDescriptor } from "@/lib/datasets";
import {
  deriveRunErrors,
  summarizeErrors,
  type Exectv2ErrorClassId,
  type Exectv2ErrorRow,
} from "@/lib/datasets/adapters/exectv2Errors";
import { compactRunLabel, useExectv2Runs, useExectv2UrlState } from "./useExectv2";

const ERROR_CLASSES = exectv2Dataset.errorClasses;

function classDescriptor(id: string): ErrorClassDescriptor | undefined {
  return ERROR_CLASSES.find((c) => c.id === id);
}

function ErrorRowCard({ row, runId }: { row: Exectv2ErrorRow; runId: string }) {
  const descriptor = classDescriptor(row.errorClass);
  const tone = descriptor?.tone ?? "muted";
  return (
    <div className="rounded-md border border-border bg-surface p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className={`rounded border px-1.5 py-0.5 text-[9px] font-medium ${TONE_CLASSES[tone]}`}>
            {descriptor?.label ?? row.errorClass}
          </span>
          <span className="rounded border border-border bg-surface-raised px-1.5 py-0.5 text-[9px] font-medium text-muted">
            {row.family}
          </span>
          <span className="font-mono text-[10px] text-muted">{row.letterId}</span>
        </div>
        <Link
          href={surfaceHref("workbench", "exectv2", { run: runId, letter: row.letterId })}
          className="inline-flex shrink-0 items-center gap-1 rounded border border-deterministic/20 bg-deterministic/5 px-1.5 py-0.5 text-[9px] font-medium text-deterministic hover:bg-deterministic/10"
        >
          <ExternalLink className="h-2.5 w-2.5" /> Letter
        </Link>
      </div>

      <div className="mt-2 flex items-center gap-2 text-[11px]">
        <span className="truncate text-muted" title={row.goldText ?? "—"}>
          {row.goldText ?? "∅"}
        </span>
        <ArrowRight className="h-3 w-3 shrink-0 text-muted" />
        <span
          className={`truncate font-mono font-medium ${row.predictedText ? "text-foreground" : "text-error"}`}
          title={row.predictedText ?? "—"}
        >
          {row.predictedText ?? "∅ (missed)"}
        </span>
      </div>

      {row.detail && <p className="mt-1.5 text-[10px] text-muted">{row.detail}</p>}

      {row.evidence && (
        <blockquote className="mt-2 border-l-2 border-border pl-2 font-serif text-[10px] italic leading-snug text-muted line-clamp-2">
          {row.evidence}
        </blockquote>
      )}

      {(row.componentOwner || row.sourceLane) && (
        <p className="mt-2 truncate font-mono text-[9px] text-muted">
          {row.componentOwner || "—"}
          {row.sourceLane ? ` / ${row.sourceLane}` : ""}
        </p>
      )}
    </div>
  );
}

export default function Exectv2ErrorGallery() {
  const { runs, isLoading, error } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();

  const selectedRun = useMemo(
    () => runs.find((r) => r.run_id === get("run")) ?? runs.find((r) => r.decision === "control") ?? runs[0],
    [runs, get]
  );

  const familyFilter = get("family") ?? "all";
  const classFilter = (get("errorClass") as Exectv2ErrorClassId | "all") ?? "all";

  const allRows = useMemo(() => (selectedRun ? deriveRunErrors(selectedRun) : []), [selectedRun]);
  const summary = useMemo(() => summarizeErrors(allRows), [allRows]);

  const filteredRows = useMemo(() => {
    return allRows.filter((row) => {
      if (familyFilter !== "all" && row.family !== familyFilter) return false;
      if (classFilter !== "all" && row.errorClass !== classFilter) return false;
      return true;
    });
  }, [allRows, familyFilter, classFilter]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <p className="text-sm font-medium">Loading error gallery…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center bg-background p-8">
        <div className="max-w-md rounded-md border border-error/25 bg-error/8 p-5">
          <div className="flex items-center gap-2 text-error">
            <ShieldAlert className="h-4 w-4" />
            <p className="text-sm font-semibold">ExECTv2 data failed to load</p>
          </div>
          <p className="mt-2 text-xs text-muted">{String(error)}</p>
        </div>
      </div>
    );
  }

  if (!selectedRun) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <p className="text-sm font-medium">No ExECTv2 runs available.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-background">
      <header className="border-b border-border bg-surface px-5 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <GalleryHorizontalEnd className="h-4 w-4 text-error" />
              <h1 className="text-sm font-semibold text-foreground">ExECTv2 · Error Gallery</h1>
              <span className="rounded border border-border bg-surface-raised px-2 py-0.5 text-[10px] text-muted">
                {summary.total} residuals
              </span>
            </div>
            <p className="mt-1 text-[11px] text-muted">
              Mention-level residuals derived from gold↔predicted matching — no seizure-frequency
              transitions. Each row links to its letter in the Example Explorer.
            </p>
          </div>
          <select
            value={selectedRun.run_id}
            onChange={(e) => set({ run: e.target.value, letter: undefined })}
            className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-foreground focus:outline-none"
          >
            {runs.map((run) => (
              <option key={run.run_id} value={run.run_id}>
                {compactRunLabel(run)} ({run.decision})
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="mx-auto w-full max-w-[1100px] space-y-4 p-5">
        {/* Error-class chips */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => set({ errorClass: undefined })}
            className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors ${
              classFilter === "all" ? "border-foreground/30 bg-surface-raised text-foreground" : "border-border text-muted hover:bg-surface-raised"
            }`}
          >
            All · {summary.total}
          </button>
          {ERROR_CLASSES.map((cls) => {
            const count = summary.byClass[cls.id as Exectv2ErrorClassId] ?? 0;
            const active = classFilter === cls.id;
            return (
              <button
                key={cls.id}
                onClick={() => set({ errorClass: active ? undefined : cls.id })}
                disabled={count === 0}
                title={cls.description}
                className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors disabled:opacity-40 ${
                  active ? TONE_CLASSES[cls.tone] : "border-border text-muted hover:bg-surface-raised"
                }`}
              >
                {cls.label} · {count}
              </button>
            );
          })}
        </div>

        {/* Family chips */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => set({ family: undefined })}
            className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors ${
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
                className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors disabled:opacity-40 ${
                  active ? TONE_CLASSES[family.tone] : "border-border text-muted hover:bg-surface-raised"
                }`}
              >
                {family.label} · {count}
              </button>
            );
          })}
        </div>

        {filteredRows.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-md border border-dashed border-border bg-surface py-12 text-center">
            <GalleryHorizontalEnd className="mb-3 h-8 w-8 text-muted/40" />
            <p className="text-sm font-medium text-muted">No residuals match the current filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {filteredRows.map((row) => (
              <ErrorRowCard key={row.id} row={row} runId={selectedRun.run_id} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
