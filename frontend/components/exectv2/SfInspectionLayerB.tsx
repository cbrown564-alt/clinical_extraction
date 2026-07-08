"use client";

import { useMemo, useState } from "react";
import { ChevronRight } from "lucide-react";
import type { SfComponentMeta, SfInspectionLetter, SfInspectionScorecard } from "@/lib/types";
import {
  familyHasAnyError,
  familyTriageStatus,
  letterVerdict,
  SF_FAMILIES,
} from "@/lib/sfFamilies";
import { componentShortLabel, componentStatsLabel } from "@/lib/sfPresentation";
import { FAMILY_TONE } from "@/lib/sfInspectionUi";
import { MentionFlowList } from "./SfMentionFlow";

function erroredComponentNames(letter: SfInspectionLetter): Set<string> {
  return new Set(letter.layer_b.components.filter((c) => c.has_error).map((c) => c.name));
}

export function LayerB({
  letter,
  scorecard,
}: {
  letter: SfInspectionLetter;
  componentsMeta?: SfComponentMeta[];
  scorecard: SfInspectionScorecard;
}) {
  const verdict = useMemo(() => letterVerdict(letter), [letter]);
  const errorNames = useMemo(() => erroredComponentNames(letter), [letter]);
  const [openFamilies, setOpenFamilies] = useState<Set<string>>(
    () => new Set(verdict.primaryFamilyId ? [verdict.primaryFamilyId] : [])
  );
  const [openClean, setOpenClean] = useState<Set<string>>(new Set());

  const toggleFamily = (id: string) =>
    setOpenFamilies((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const toggleClean = (name: string) =>
    setOpenClean((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });

  return (
    <div className="space-y-3">
      <p className="text-[12px] leading-relaxed text-muted">
        Each lens projects mentions into scorer keys and counts TP / FP / FN. Schema mismatch above
        shows attribute truth; here you see what each scoring component actually compared.
      </p>
      <div className="space-y-1.5">
        {SF_FAMILIES.map((family) => {
          const isOpen = openFamilies.has(family.id);
          const tone = FAMILY_TONE[family.id];
          const anyError = familyHasAnyError(letter, family);
          const triage = familyTriageStatus(letter, family);
          return (
            <div key={family.id} className={`border-l-[3px] ${tone.leftBorder} bg-surface`}>
              <button
                onClick={() => toggleFamily(family.id)}
                className="flex w-full items-center gap-2 px-3 py-2 text-left"
              >
                <ChevronRight
                  className={`h-3 w-3 shrink-0 text-muted transition-transform ${isOpen ? "rotate-90" : ""}`}
                />
                <span className={`text-[12px] font-bold ${tone.text}`}>{family.label}</span>
                <span className={`text-[11px] ${anyError ? "font-bold text-error" : "text-success"}`}>
                  {anyError
                    ? componentStatsLabel(triage.tp, triage.fp, triage.fn)
                    : "all match"}
                </span>
              </button>
              {isOpen && (
                <div className="border-t border-border px-3 py-2">
                  {family.id === "bench" && (
                    <p className="mb-2 text-[11px] text-muted">
                      Strict exact-match benchmark · dataset F1{" "}
                      {scorecard[family.root]?.f1.toFixed(4) ?? "—"} (low by design)
                    </p>
                  )}
                  <div className="flex flex-col gap-3">
                    {family.children.map((childName) => {
                      const comp = letter.layer_b.components.find((c) => c.name === childName);
                      if (!comp) return null;
                      const isError = errorNames.has(childName);
                      const cleanOpen = openClean.has(childName);

                      if (isError) {
                        return (
                          <div
                            key={childName}
                            id={`sf-lens-${childName}`}
                            className="scroll-mt-4 overflow-hidden rounded-md border border-error/25"
                          >
                            <div className="border-b border-error/20 bg-error/5 px-3 py-2">
                              <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                                <span className="text-[12px] font-bold text-foreground">
                                  {componentShortLabel(childName)}
                                </span>
                                <span className="font-mono text-[10px] text-muted">{childName}</span>
                                <span className="ml-auto text-[11px] font-bold text-error">
                                  {componentStatsLabel(comp.tp, comp.fp, comp.fn)}
                                </span>
                              </div>
                              {comp.info && (
                                <p className="mt-1 text-[11px] leading-relaxed text-muted">{comp.info}</p>
                              )}
                            </div>
                            <div className="px-2 py-2">
                              <MentionFlowList rows={comp.rows} />
                            </div>
                          </div>
                        );
                      }

                      return (
                        <div key={childName} className="rounded-md border border-border/60">
                          <button
                            type="button"
                            onClick={() => toggleClean(childName)}
                            className="flex w-full items-center gap-2 px-3 py-1.5 text-left hover:bg-surface-raised"
                          >
                            <ChevronRight
                              className={`h-2.5 w-2.5 shrink-0 text-muted transition-transform ${
                                cleanOpen ? "rotate-90" : ""
                              }`}
                            />
                            <span className="text-[11px] font-semibold text-foreground">
                              {componentShortLabel(childName)}
                            </span>
                            <span className="ml-auto text-[10px] text-success">
                              {componentStatsLabel(comp.tp, comp.fp, comp.fn)}
                            </span>
                          </button>
                          {cleanOpen && (
                            <div className="border-t border-border px-2 py-2">
                              {comp.info && (
                                <p className="mb-2 px-1 text-[10px] leading-relaxed text-muted">{comp.info}</p>
                              )}
                              <MentionFlowList rows={comp.rows} />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
