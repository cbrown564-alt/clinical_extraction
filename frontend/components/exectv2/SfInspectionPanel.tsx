"use client";

import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ChevronLeft,
  ChevronRight,
  FileSearch,
  Gauge,
  Info,
  Maximize2,
} from "lucide-react";
import { fetchExectv2SfInspection } from "@/lib/api";
import type { SfInspectionLetter } from "@/lib/types";
import {
  countLettersByTriage,
  familyTriageStatus,
  letterMatchesTriageFilter,
  LETTER_TRIAGE_FILTERS,
  neighborLetterIds,
  SF_FAMILIES,
  sortLettersForTriage,
  type LetterTriageFilter,
} from "@/lib/sfFamilies";
import {
  CandidateSpansContext,
  FamilyCards,
  FamilyLegend,
  LayerA,
  LayerB,
  LetterMatrix,
  LineagePanel,
  ScorecardTable,
  VerdictBanner,
} from "./SfInspectionViews";

type DetailDepth = "preview" | "deep";

export default function SfInspectionPanel() {
  const [selectedLetterId, setSelectedLetterId] = useState<string | null>(null);
  const [triageFilter, setTriageFilter] = useState<LetterTriageFilter>("actionable");
  const [detailDepth, setDetailDepth] = useState<DetailDepth>("preview");
  const [scorecardOpen, setScorecardOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["exectv2-sf-inspection"],
    queryFn: fetchExectv2SfInspection,
  });

  const letters = useMemo(() => data?.letters ?? [], [data]);

  const triageCounts = useMemo(() => countLettersByTriage(letters), [letters]);

  const visibleLetters = useMemo(() => {
    const filtered = letters.filter((l) => letterMatchesTriageFilter(l, triageFilter));
    return triageFilter === "all" ? filtered : sortLettersForTriage(filtered);
  }, [letters, triageFilter]);

  // Clamp selection to the visible list synchronously so filter changes never
  // leave the detail pane on a letter that is no longer in the sidebar.
  const resolvedSelectedId = useMemo(() => {
    if (!visibleLetters.length) return null;
    if (selectedLetterId && visibleLetters.some((l) => l.letter_id === selectedLetterId)) {
      return selectedLetterId;
    }
    return visibleLetters[0].letter_id;
  }, [visibleLetters, selectedLetterId]);

  const selectedLetter = useMemo(() => {
    if (!resolvedSelectedId) return null;
    return letters.find((l) => l.letter_id === resolvedSelectedId) ?? null;
  }, [letters, resolvedSelectedId]);

  const neighbors = useMemo(
    () => neighborLetterIds(visibleLetters, resolvedSelectedId),
    [visibleLetters, resolvedSelectedId]
  );

  const inspectableIds = useMemo(() => new Set(letters.map((l) => l.letter_id)), [letters]);

  useEffect(() => {
    if (resolvedSelectedId !== selectedLetterId) {
      setSelectedLetterId(resolvedSelectedId);
      setDetailDepth("preview");
    }
  }, [resolvedSelectedId, selectedLetterId]);

  const selectLetter = (id: string, depth: DetailDepth = "preview") => {
    setSelectedLetterId(id);
    setDetailDepth(depth);
  };

  const openDeep = (id: string) => selectLetter(id, "deep");

  const goNeighbor = (dir: -1 | 1) => {
    const id = dir < 0 ? neighbors.prevId : neighbors.nextId;
    if (id) setSelectedLetterId(id);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (el?.tagName === "INPUT" || el?.tagName === "TEXTAREA" || el?.isContentEditable) {
        return;
      }
      if (e.key === "j" || e.key === "ArrowDown") {
        if (neighbors.nextId) {
          e.preventDefault();
          setSelectedLetterId(neighbors.nextId);
        }
      } else if (e.key === "k" || e.key === "ArrowUp") {
        if (neighbors.prevId) {
          e.preventDefault();
          setSelectedLetterId(neighbors.prevId);
        }
      } else if (e.key === "Enter" && resolvedSelectedId && detailDepth === "preview") {
        e.preventDefault();
        setDetailDepth("deep");
      } else if (e.key === "Escape" && detailDepth === "deep") {
        e.preventDefault();
        setDetailDepth("preview");
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [neighbors.prevId, neighbors.nextId, resolvedSelectedId, detailDepth]);

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
      <TopBar
        nLetters={data.n_letters}
        nWithErrors={data.n_with_errors}
        artifact={data.artifact}
        split={data.split}
        scorecardOpen={scorecardOpen}
        onToggleScorecard={() => setScorecardOpen((v) => !v)}
      />

      {scorecardOpen && (
        <div className="shrink-0 border-b border-border bg-surface px-4 py-3">
          <FamilyCards scorecard={data.scorecard} />
          <details className="mt-2">
            <summary className="cursor-pointer list-none text-[10px] text-muted before:mr-1 before:content-['▸']">
              show raw scorecard (all 11 lenses)
            </summary>
            <div className="mt-1.5">
              <ScorecardTable scorecard={data.scorecard} />
            </div>
          </details>
        </div>
      )}

      <div className="flex min-h-0 flex-1">
        <aside className="flex w-[min(42%,28rem)] shrink-0 flex-col border-r border-border bg-surface">
          <TriageFilterBar
            filter={triageFilter}
            counts={triageCounts}
            visibleCount={visibleLetters.length}
            onChange={setTriageFilter}
          />
          <div className="min-h-0 flex-1 overflow-y-auto">
            <LetterMatrix
              letters={visibleLetters}
              selectedLetterId={resolvedSelectedId}
              onSelect={(id) => selectLetter(id, "preview")}
              onInspect={openDeep}
              inspectableIds={inspectableIds}
              compact
            />
            {visibleLetters.length === 0 && (
              <p className="px-3 py-8 text-center text-[11px] text-muted">
                No letters match this filter.
              </p>
            )}
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          {selectedLetter ? (
            <>
              <LetterNavBar
                letter={selectedLetter}
                index={neighbors.index}
                total={visibleLetters.length}
                prevId={neighbors.prevId}
                nextId={neighbors.nextId}
                detailDepth={detailDepth}
                onPrev={() => goNeighbor(-1)}
                onNext={() => goNeighbor(1)}
                onPreview={() => setDetailDepth("preview")}
                onDeep={() => setDetailDepth("deep")}
              />
              <div className="min-h-0 flex-1 overflow-y-auto p-4">
                {detailDepth === "preview" ? (
                  <PreviewPane letter={selectedLetter} onDeep={() => setDetailDepth("deep")} />
                ) : (
                  <InspectorScreen
                    key={selectedLetter.letter_id}
                    letter={selectedLetter}
                    scorecard={data.scorecard}
                  />
                )}
              </div>
            </>
          ) : (
            <div className="flex flex-1 flex-col items-center justify-center gap-2 text-muted">
              <FileSearch className="h-5 w-5" />
              <p className="text-[11px]">Select a letter from the list to inspect.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

// ── Top bar ──

function TopBar({
  nLetters,
  nWithErrors,
  artifact,
  split,
  scorecardOpen,
  onToggleScorecard,
}: {
  nLetters: number;
  nWithErrors: number;
  artifact: string;
  split: string;
  scorecardOpen: boolean;
  onToggleScorecard: () => void;
}) {
  return (
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2.5">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
        <Gauge className="h-4 w-4 text-deterministic" />
        <h1 className="text-sm font-semibold text-foreground">
          SeizureFrequency · gold vs. prediction
        </h1>
        <span className="text-[10px] text-muted">
          {split} · {nLetters} letters · {nWithErrors} with ≥1 component error
        </span>
        <div className="ml-auto flex items-center gap-2">
          <FamilyLegend />
          <button
            onClick={onToggleScorecard}
            className={`rounded-md border px-2.5 py-1 text-[10px] font-semibold transition-colors ${
              scorecardOpen
                ? "border-foreground bg-foreground text-background"
                : "border-border text-muted hover:border-muted hover:text-foreground"
            }`}
          >
            {scorecardOpen ? "Hide families" : "Family F1"}
          </button>
          <span
            title={`Predictions: ${artifact}. Scorer-faithful — backend re-scores with score_frequency_state and aborts unless published F1 reproduces within 1e-4.`}
            className="inline-flex h-6 w-6 cursor-help items-center justify-center rounded-full border border-border text-muted hover:text-foreground"
          >
            <Info className="h-3 w-3" />
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Triage filter chips ──

function TriageFilterBar({
  filter,
  counts,
  visibleCount,
  onChange,
}: {
  filter: LetterTriageFilter;
  counts: Record<LetterTriageFilter, number>;
  visibleCount: number;
  onChange: (f: LetterTriageFilter) => void;
}) {
  return (
    <div className="shrink-0 border-b border-border px-3 py-2">
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
          Letters
        </span>
        <span className="font-mono text-[10px] text-muted">{visibleCount}</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {LETTER_TRIAGE_FILTERS.map((f) => {
          const active = filter === f.id;
          return (
            <button
              key={f.id}
              title={f.hint}
              onClick={() => onChange(f.id)}
              className={`rounded-md px-2 py-0.5 text-[10px] font-semibold transition-colors ${
                active
                  ? f.id === "actionable" || f.id === "headline" || f.id === "change"
                    ? "bg-error/15 text-error"
                    : "bg-foreground text-background"
                  : "bg-surface-raised text-muted hover:text-foreground"
              }`}
            >
              {f.label}
              <span className="ml-1 font-mono font-normal opacity-70">{counts[f.id]}</span>
            </button>
          );
        })}
      </div>
      <p className="mt-1.5 text-[9px] text-muted">j/k · Enter · Esc</p>
    </div>
  );
}

// ── Letter nav in detail pane ──

function LetterNavBar({
  letter,
  index,
  total,
  prevId,
  nextId,
  detailDepth,
  onPrev,
  onNext,
  onPreview,
  onDeep,
}: {
  letter: SfInspectionLetter;
  index: number;
  total: number;
  prevId: string | null;
  nextId: string | null;
  detailDepth: DetailDepth;
  onPrev: () => void;
  onNext: () => void;
  onPreview: () => void;
  onDeep: () => void;
}) {
  return (
    <div className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border bg-surface px-4 py-2">
      <div className="flex items-center gap-1">
        <button
          onClick={onPrev}
          disabled={!prevId}
          className="rounded border border-border p-1 text-muted hover:text-foreground disabled:opacity-30"
          title="Previous letter (k)"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={onNext}
          disabled={!nextId}
          className="rounded border border-border p-1 text-muted hover:text-foreground disabled:opacity-30"
          title="Next letter (j)"
        >
          <ChevronRight className="h-3.5 w-3.5" />
        </button>
      </div>
      <h2 className="font-mono text-base font-bold text-foreground">{letter.letter_id}</h2>
      <span className="font-mono text-[10px] text-muted">
        {index >= 0 ? index + 1 : "—"} / {total}
      </span>
      <span className="rounded border border-border px-1.5 py-0 font-mono text-[9px] text-muted">
        g{letter.gold_count} / p{letter.pred_count}
      </span>
      {SF_FAMILIES.map((f) => {
        const s = familyTriageStatus(letter, f);
        const clean = s.fp + s.fn === 0;
        return (
          <span
            key={f.id}
            className={`font-mono text-[10px] font-semibold ${
              clean ? "text-success" : "text-error"
            }`}
          >
            {f.label.split(" ")[0]} {clean ? "✓" : `fp${s.fp}/fn${s.fn}`}
          </span>
        );
      })}
      <div className="ml-auto flex gap-1">
        <button
          onClick={onPreview}
          className={`rounded-md px-2.5 py-1 text-[10px] font-semibold ${
            detailDepth === "preview"
              ? "bg-foreground text-background"
              : "text-muted hover:bg-surface-raised hover:text-foreground"
          }`}
        >
          Preview
        </button>
        <button
          onClick={onDeep}
          className={`rounded-md px-2.5 py-1 text-[10px] font-semibold ${
            detailDepth === "deep"
              ? "bg-foreground text-background"
              : "text-muted hover:bg-surface-raised hover:text-foreground"
          }`}
        >
          Deep dive
        </button>
      </div>
    </div>
  );
}

// ── Right-pane preview (verdict + primary evidence) ──

function PreviewPane({
  letter,
  onDeep,
}: {
  letter: SfInspectionLetter;
  onDeep: () => void;
}) {
  const spans = letter.lineage.candidate_spans;
  const hasOverride = !!letter.lineage.override?.applied;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-5">
      {spans.length > 0 && <CandidateSpansContext spans={spans} />}

      <VerdictBanner letter={letter} />

      {hasOverride && <LineagePanel letter={letter} hideSpans />}

      <section>
        <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted">Evidence</h3>
        <LayerA letter={letter} hideClean />
      </section>

      <button
        onClick={onDeep}
        className="inline-flex items-center gap-1.5 self-start text-[11px] font-semibold text-hybrid hover:underline"
      >
        <Maximize2 className="h-3.5 w-3.5" />
        Deep dive — lenses & all pairs
      </button>
    </div>
  );
}

// ── Full inspector ──

function InspectorScreen({
  letter,
  scorecard,
}: {
  letter: SfInspectionLetter;
  scorecard: import("@/lib/types").SfInspectionScorecard;
}) {
  const hasOverride = !!letter.lineage.override?.applied;
  const hasSpans = letter.lineage.candidate_spans.length > 0;

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 pb-8">
      <VerdictBanner letter={letter} />

      {(hasOverride || hasSpans) && (
        <section>
          <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted">Cause</h3>
          <LineagePanel letter={letter} />
        </section>
      )}

      <section>
        <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted">Evidence</h3>
        <LayerA letter={letter} hideClean />
      </section>

      <section>
        <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted">Lenses</h3>
        <LayerB letter={letter} scorecard={scorecard} />
      </section>
    </div>
  );
}
