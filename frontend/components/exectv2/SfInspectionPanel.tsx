"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileSearch, Gauge, ListFilter, X } from "lucide-react";
import { fetchExectv2SfInspection } from "@/lib/api";
import type { SfInspectionLetter } from "@/lib/types";
import {
  LayerA,
  LayerB,
  LetterRow,
  LineagePanel,
  ScorecardTable,
} from "./SfInspectionViews";

export default function SfInspectionPanel() {
  const [selectedLetterId, setSelectedLetterId] = useState<string | null>(null);
  const [errorsOnly, setErrorsOnly] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["exectv2-sf-inspection"],
    queryFn: fetchExectv2SfInspection,
  });

  const letters = useMemo(() => data?.letters ?? [], [data]);

  const visibleLetters = useMemo(
    () => (errorsOnly ? letters.filter((l) => l.total_errors > 0) : letters),
    [letters, errorsOnly]
  );

  const selectedLetter = useMemo(() => {
    if (!selectedLetterId) return null;
    return letters.find((l) => l.letter_id === selectedLetterId) ?? null;
  }, [letters, selectedLetterId]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading SeizureFrequency inspection…</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">No inspection data available.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-background">
      <SummaryHeader
        nLetters={data.n_letters}
        nWithErrors={data.n_with_errors}
        artifact={data.artifact}
        split={data.split}
        scorecard={data.scorecard}
      />

      <div className="flex flex-1 flex-col overflow-hidden lg:flex-row">
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Controls */}
          <div className="flex shrink-0 items-center gap-2 border-b border-border bg-surface px-3 py-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              {visibleLetters.length} / {data.n_letters} letters
            </span>
            <button
              onClick={() => setErrorsOnly((v) => !v)}
              className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-[10px] font-medium transition-colors ${
                errorsOnly
                  ? "bg-error/10 text-error border border-error/20"
                  : "text-muted border border-transparent hover:text-foreground hover:bg-surface-raised"
              }`}
            >
              <ListFilter className="h-3 w-3" />
              {errorsOnly ? "Errors only (on)" : "Errors only"}
            </button>
            <span className="ml-auto text-[9px] text-muted">
              click a letter to inspect
            </span>
          </div>

          {/* Master letter list */}
          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-4xl p-2">
              <div className="overflow-hidden rounded-lg border border-border bg-surface">
                {visibleLetters.map((letter) => (
                  <LetterRow
                    key={letter.letter_id}
                    letter={letter}
                    active={selectedLetterId === letter.letter_id}
                    onClick={() => setSelectedLetterId(letter.letter_id)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {selectedLetter && (
          <LetterInspector
            letter={selectedLetter}
            componentsMeta={data.components}
            onClose={() => setSelectedLetterId(null)}
          />
        )}
      </div>
    </div>
  );
}

// ── Summary header (sticky, carries the 11-component scorecard) ──

function SummaryHeader({
  nLetters,
  nWithErrors,
  artifact,
  split,
  scorecard,
}: {
  nLetters: number;
  nWithErrors: number;
  artifact: string;
  split: string;
  scorecard: import("@/lib/types").SfInspectionScorecard;
}) {
  return (
    <div className="shrink-0 border-b border-border bg-surface px-5 py-3">
      <div className="flex items-center gap-2">
        <Gauge className="h-4 w-4 text-deterministic" />
        <h1 className="text-sm font-semibold text-foreground">
          SeizureFrequency · gold vs. prediction inspection
        </h1>
        <span className="text-[10px] text-muted">
          {split} · {nLetters} letters · {nWithErrors} with ≥1 component error
        </span>
      </div>
      <p className="mt-1 max-w-4xl text-[10px] text-muted">
        Predictions: <span className="font-mono">{artifact}</span>. The scorecard below is
        scorer-faithful — the backend re-scores with the real{" "}
        <span className="font-mono">score_frequency_state</span> and aborts unless F1
        reproduces the published 0.9338 / 0.8602 / 0.9244 within 1e-4.
      </p>

      <div className="mt-2.5">
        <ScorecardTable scorecard={scorecard} />
      </div>

      <div className="mt-2 flex flex-wrap gap-3 text-[9px] text-muted">
        <span>
          <span className="font-semibold text-foreground">Layer A</span> per schema
          attribute: raw → validity → canonicalized vs gold
        </span>
        <span>
          <span className="font-semibold text-foreground">Layer B</span> per scoring
          component: attributes → count-state → projected state → key
        </span>
        <span>
          <span className="text-gold">gold</span> /{" "}
          <span className="text-llm">pred</span> ·{" "}
          <span className="text-success">TP</span> match ·{" "}
          <span className="text-error">FP</span> pred-only ·{" "}
          <span className="text-error">FN</span> gold-only
        </span>
      </div>
    </div>
  );
}

// ── Letter inspector (right rail) ──

function LetterInspector({
  letter,
  componentsMeta,
  onClose,
}: {
  letter: SfInspectionLetter;
  componentsMeta: import("@/lib/types").SfComponentMeta[];
  onClose: () => void;
}) {
  return (
    <div className="flex w-full shrink-0 flex-col border-t border-border bg-surface lg:w-[560px] lg:border-l lg:border-t-0">
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <h3 className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-foreground">
          <FileSearch className="h-3 w-3" />
          {letter.letter_id}
        </h3>
        <button
          onClick={onClose}
          className="rounded p-1 text-muted hover:bg-surface-raised hover:text-foreground"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-3 p-4">
          {/* Letter summary chips */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="rounded border border-border bg-surface-raised px-1.5 py-0 text-[9px] text-muted">
              gold SF {letter.gold_count}
            </span>
            <span className="rounded border border-border bg-surface-raised px-1.5 py-0 text-[9px] text-muted">
              pred SF {letter.pred_count}
            </span>
            {letter.total_errors === 0 ? (
              <span className="rounded border border-success/30 bg-success/10 px-1.5 py-0 text-[9px] font-medium text-success">
                clean across all components
              </span>
            ) : (
              <>
                <span className="rounded border border-error/30 bg-error/10 px-1.5 py-0 text-[9px] font-medium text-error">
                  dir fp={letter.direction_errors.fp}/fn={letter.direction_errors.fn}
                </span>
                <span className="rounded border border-error/30 bg-error/10 px-1.5 py-0 text-[9px] font-medium text-error">
                  mag fp={letter.magnitude_errors.fp}/fn={letter.magnitude_errors.fn}
                </span>
                <span className="rounded border border-llm/30 bg-llm/10 px-1.5 py-0 text-[9px] font-semibold text-llm">
                  {letter.total_errors} FP/FN total
                </span>
              </>
            )}
          </div>

          {/* Layer A */}
          <div>
            <h4 className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-foreground">
              Layer A · Schema attributes
            </h4>
            <LayerA pairs={letter.layer_a.pairs} />
          </div>

          {/* Layer B */}
          <div>
            <h4 className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-foreground">
              Layer B · Scoring components
            </h4>
            <LayerB components={letter.layer_b.components} componentsMeta={componentsMeta} />
          </div>

          {/* Lineage */}
          <div>
            <h4 className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-foreground">
              Lineage
            </h4>
            <LineagePanel lineage={letter.lineage} />
          </div>
        </div>
      </div>
    </div>
  );
}
