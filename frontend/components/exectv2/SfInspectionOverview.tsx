"use client";

import { useState } from "react";
import { ChevronRight } from "lucide-react";
import type { SfInspectionLetter, SfInspectionScorecard } from "@/lib/types";
import { cellSeverity, familyTriageStatus, rootF1, SF_FAMILIES } from "@/lib/sfFamilies";
import { COMPONENT_ORDER, FAMILY_TONE } from "@/lib/sfInspectionUi";

export function FamilyLegend() {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
      {SF_FAMILIES.map((f) => (
        <span key={f.id} className="flex items-center gap-1">
          <span className={`inline-block h-1.5 w-1.5 rounded-full ${FAMILY_TONE[f.id].dot}`} />
          <span className={`font-semibold ${FAMILY_TONE[f.id].text}`}>{f.label.split(" ")[0]}</span>
        </span>
      ))}
      <span>
        <span className="text-gold">G</span>/<span className="text-llm">P</span>
        <span className="mx-1 text-border">·</span>
        <span className="text-success">TP</span>
        <span className="mx-1 text-border">·</span>
        <span className="text-error">FP/FN</span>
      </span>
    </div>
  );
}

export function FamilyCards({ scorecard }: { scorecard: SfInspectionScorecard }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
      {SF_FAMILIES.map((family) => {
        const tone = FAMILY_TONE[family.id];
        const root = rootF1(scorecard, family);
        const isOpen = expanded.has(family.id);
        return (
          <div
            key={family.id}
            className={`rounded-lg border border-border border-t-[3px] ${tone.topBorder} bg-surface p-3.5 shadow-sm`}
          >
            <div
              className={`mb-1.5 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wide ${tone.text}`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${tone.dot}`} />
              {family.label}
            </div>
            {root ? (
              <>
                <div className="mb-1 flex items-baseline gap-2">
                  <span className="font-mono text-2xl font-bold tracking-tight text-foreground">
                    {root.f1.toFixed(4)}
                  </span>
                  <span className="text-[11px] text-muted">F1 · {family.root}</span>
                </div>
                <div className="mb-1 flex h-1 overflow-hidden rounded-full bg-surface-raised">
                  <div className={`${tone.dot} opacity-80`} style={{ width: `${root.precision * 100}%` }} />
                </div>
                <div className="mb-2 flex justify-between font-mono text-[11px] text-muted">
                  <span>P {root.precision.toFixed(4)}</span>
                  <span>R {root.recall.toFixed(4)}</span>
                </div>
              </>
            ) : (
              <p className="mb-2 text-[11px] text-muted">no scorecard entry</p>
            )}
            <p className="mb-2.5 min-h-[54px] text-xs leading-relaxed text-muted">{family.blurb}</p>
            <div className="border-t border-border pt-1.5">
              <button
                type="button"
                onClick={() => toggle(family.id)}
                className={`flex w-full items-center gap-1 text-[11px] font-semibold ${tone.text}`}
                aria-expanded={isOpen}
              >
                <ChevronRight className={`h-2.5 w-2.5 transition-transform ${isOpen ? "rotate-90" : ""}`} />
                {family.children.length} child lens{family.children.length === 1 ? "" : "es"}
              </button>
              {isOpen && (
                <ul className="mt-1.5 flex flex-col gap-1">
                  {family.children.map((childName) => {
                    const cf1 = scorecard[childName];
                    const low = cf1 && root && cf1.f1 < root.f1 - 0.05;
                    return (
                      <li
                        key={childName}
                        className={`flex items-center justify-between gap-2 rounded px-1.5 py-0.5 text-[11px] ${
                          low ? "bg-error/10" : "bg-surface-raised"
                        }`}
                      >
                        <span className="font-mono text-foreground">{childName}</span>
                        <span className={`font-mono font-semibold ${low ? "text-error" : "text-foreground"}`}>
                          {cf1 ? cf1.f1.toFixed(4) : "–"}
                          {low && <span className="ml-1 text-[11px] font-bold">↓</span>}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

const SEVERITY_CLASS: Record<string, string> = {
  clean: "bg-success/10 text-success",
  err1: "bg-error/15 text-error",
  err2: "bg-error/25 text-error",
  na: "text-muted",
};

function CellPill({
  status,
  letterHasActivity,
}: {
  status: { fp: number; fn: number; tp: number };
  letterHasActivity: boolean;
}) {
  const sev = cellSeverity(status, letterHasActivity);
  if (sev === "na") {
    return (
      <span className={`inline-block min-w-[52px] rounded px-1.5 py-0.5 text-center font-mono text-[11px] ${SEVERITY_CLASS.na}`}>
        –
      </span>
    );
  }
  const label = sev === "clean" ? "clean" : `fp${status.fp}/fn${status.fn}`;
  return (
    <span
      className={`inline-block min-w-[52px] rounded px-1.5 py-0.5 text-center font-mono text-[11px] font-bold ${SEVERITY_CLASS[sev]}`}
    >
      {label}
    </span>
  );
}

export function LetterMatrix({
  letters,
  selectedLetterId,
  onSelect,
  compact = false,
}: {
  letters: SfInspectionLetter[];
  selectedLetterId: string | null;
  onSelect: (id: string) => void;
  compact?: boolean;
}) {
  const cellPad = compact ? "px-2 py-1" : "px-3 py-1.5";
  const headPad = compact ? "px-2 py-1.5" : "px-3 py-2";
  return (
    <div className={compact ? "" : "overflow-hidden overflow-x-auto rounded-lg border border-border bg-surface shadow-sm"}>
      <table className={`w-full border-collapse ${compact ? "text-[11px]" : "min-w-[560px] text-xs"}`}>
        <thead className={compact ? "sticky top-0 z-10" : undefined}>
          <tr>
            <th
              className={`border-b border-border bg-surface-raised ${headPad} text-left text-[11px] font-bold uppercase tracking-wide text-muted`}
            >
              letter
            </th>
            <th
              className={`border-b border-border bg-surface-raised ${headPad} text-left text-[11px] font-bold uppercase tracking-wide text-muted`}
            >
              {compact ? "g/p" : "gold / pred"}
            </th>
            {SF_FAMILIES.map((f) => (
              <th
                key={f.id}
                title={f.label}
                className={`border-b border-border bg-surface-raised ${headPad} text-center text-[11px] font-bold uppercase tracking-wide ${FAMILY_TONE[f.id].text}`}
              >
                {compact ? f.label.split(" ")[0] : f.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {letters.map((letter) => {
            const active = selectedLetterId === letter.letter_id;
            return (
              <tr
                key={letter.letter_id}
                onClick={() => onSelect(letter.letter_id)}
                className={`cursor-pointer border-b border-border transition-colors last:border-b-0 ${
                  active ? "bg-hybrid/15 ring-1 ring-inset ring-hybrid/30" : "hover:bg-surface-raised"
                } ${!letter.has_activity ? "italic text-muted" : ""}`}
              >
                <td className={`${cellPad} font-mono font-bold text-foreground`}>
                  <button
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation();
                      onSelect(letter.letter_id);
                    }}
                    className="rounded-sm font-mono font-bold text-foreground underline-offset-2 hover:underline"
                    aria-current={active ? "true" : undefined}
                    aria-label={`Inspect letter ${letter.letter_id}`}
                  >
                    {letter.letter_id}
                  </button>
                </td>
                <td className={`${cellPad} font-mono text-muted`}>
                  g{letter.gold_count}/p{letter.pred_count}
                </td>
                {SF_FAMILIES.map((f) => (
                  <td key={f.id} className={`${cellPad} text-center`}>
                    <CellPill status={familyTriageStatus(letter, f)} letterHasActivity={letter.has_activity} />
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function ScorecardTable({ scorecard }: { scorecard: SfInspectionScorecard }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-[11px]">
        <thead>
          <tr>
            <th className="border border-border bg-surface-raised px-2 py-1 text-left font-semibold text-muted">
              component
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              F1
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              P
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              R
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              TP
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              FP
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              FN
            </th>
          </tr>
        </thead>
        <tbody>
          {COMPONENT_ORDER.map((name) => {
            const cell = scorecard[name];
            if (!cell) return null;
            const family = SF_FAMILIES.find(
              (f) => f.root === name || (f.children as readonly string[]).includes(name)
            );
            const isRoot = family?.root === name;
            return (
              <tr key={name} className="odd:bg-surface">
                <td
                  className={`border border-border px-2 py-1 font-mono ${
                    isRoot ? `font-semibold ${family ? FAMILY_TONE[family.id].text : "text-foreground"}` : "text-foreground"
                  }`}
                >
                  {name}
                  {isRoot && <span className="ml-1 text-[11px] text-muted">root</span>}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-foreground">
                  {cell.f1.toFixed(4)}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-muted">
                  {cell.precision.toFixed(4)}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-muted">
                  {cell.recall.toFixed(4)}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-success">{cell.tp}</td>
                <td className="border border-border px-2 py-1 text-right font-mono text-error">{cell.fp}</td>
                <td className="border border-border px-2 py-1 text-right font-mono text-error">{cell.fn}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
