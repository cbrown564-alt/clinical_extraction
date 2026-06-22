"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  Activity,
  BarChart3,
  CheckCircle2,
  FileText,
  GalleryHorizontalEnd,
  Layers3,
  Search,
  ShieldAlert,
} from "lucide-react";
import LetterRenderer from "@/components/observatory/LetterRenderer";
import { exectv2Dataset, EXECTV2_FAMILIES, surfaceHref } from "@/lib/datasets";
import type { RunDecision } from "@/lib/datasets";
import type {
  Exectv2Entity,
  Exectv2LetterRecord,
  Exectv2Mention,
  Exectv2RunSummary,
} from "@/lib/types";
import { compactRunLabel, formatMetric, useExectv2Runs, useExectv2UrlState } from "./useExectv2";

const FAMILY_IDS = EXECTV2_FAMILIES.map((f) => f.id as Exectv2Entity);

function shortFamily(family: string): string {
  return EXECTV2_FAMILIES.find((f) => f.id === family)?.shortLabel ?? family.slice(0, 2);
}

function decisionClass(decision: string): string {
  switch (decision as RunDecision) {
    case "control":
      return "border-deterministic/25 bg-deterministic/10 text-deterministic";
    case "simplification":
      return "border-success/25 bg-success/10 text-success";
    case "diagnostic":
      return "border-llm/25 bg-llm/10 text-llm";
    default:
      return "border-muted/20 bg-muted/10 text-muted";
  }
}

function familyTint(family: string): string {
  const tone = EXECTV2_FAMILIES.find((f) => f.id === family)?.tone ?? "muted";
  switch (tone) {
    case "deterministic":
      return "border-deterministic/25 bg-deterministic/8";
    case "llm":
      return "border-llm/25 bg-llm/8";
    case "success":
      return "border-success/25 bg-success/10";
    case "deterministic-alt":
      return "border-deterministic-alt/25 bg-deterministic-alt/8";
    default:
      return "border-border bg-surface";
  }
}

function MentionRow({ mention }: { mention: Exectv2Mention }) {
  const attrs = Object.entries(mention.attributes).slice(0, 6);
  return (
    <div className="border-b border-border/60 px-3 py-2 last:border-b-0">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-[11px] font-semibold text-foreground" title={mention.text}>
            {mention.text || "(blank mention)"}
          </p>
          <p className="mt-1 line-clamp-2 text-[10px] leading-snug text-muted" title={mention.evidence}>
            {mention.evidence || "No evidence text"}
          </p>
        </div>
        <span
          className={`shrink-0 rounded px-1.5 py-0.5 text-[9px] font-medium ${
            mention.evidence_valid ? "bg-success/10 text-success" : "bg-error/10 text-error"
          }`}
        >
          {mention.evidence_valid ? "exact" : "invalid"}
        </span>
      </div>
      {attrs.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {attrs.map(([key, value]) => (
            <span
              key={`${mention.id}:${key}`}
              className="rounded border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[9px] text-muted"
              title={`${key}: ${value}`}
            >
              {key}: {value}
            </span>
          ))}
        </div>
      )}
      {(mention.component_owner || mention.source_lane) && (
        <p className="mt-2 truncate font-mono text-[9px] text-muted">
          {mention.component_owner || "owner unknown"}
          {mention.source_lane ? ` / ${mention.source_lane}` : ""}
        </p>
      )}
    </div>
  );
}

function FamilyPanel({
  family,
  letter,
}: {
  family: Exectv2Entity;
  letter: Exectv2LetterRecord;
}) {
  const gold = letter.gold_mentions.filter((m) => m.entity === family);
  const predicted = letter.predicted_mentions.filter((m) => m.entity === family);
  return (
    <section className={`overflow-hidden rounded-md border ${familyTint(family)}`}>
      <div className="flex items-center justify-between border-b border-border/60 px-3 py-2">
        <h3 className="text-[11px] font-semibold text-foreground">{family}</h3>
        <div className="flex items-center gap-1 font-mono text-[10px] text-muted">
          <span>G {gold.length}</span>
          <span>/</span>
          <span>P {predicted.length}</span>
        </div>
      </div>
      <div className="grid grid-cols-1 divide-y divide-border/60 bg-surface md:grid-cols-2 md:divide-x md:divide-y-0">
        <div>
          <div className="border-b border-border/60 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
            Gold
          </div>
          {gold.length === 0 ? (
            <div className="px-3 py-4 text-[11px] text-muted">No gold mentions</div>
          ) : (
            gold.map((mention) => <MentionRow key={mention.id} mention={mention} />)
          )}
        </div>
        <div>
          <div className="border-b border-border/60 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
            Predicted
          </div>
          {predicted.length === 0 ? (
            <div className="px-3 py-4 text-[11px] text-muted">No predicted mentions</div>
          ) : (
            predicted.map((mention) => <MentionRow key={mention.id} mention={mention} />)
          )}
        </div>
      </div>
    </section>
  );
}

function RunButton({
  run,
  active,
  onClick,
}: {
  run: Exectv2RunSummary;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-md border px-3 py-2 text-left transition-colors ${
        active ? "border-deterministic/30 bg-deterministic/8" : "border-border bg-surface hover:bg-surface-raised"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate text-[11px] font-semibold text-foreground">{compactRunLabel(run)}</p>
          <p className="mt-0.5 truncate font-mono text-[9px] text-muted">{run.model}</p>
        </div>
        <span className={`shrink-0 rounded border px-1.5 py-0.5 text-[9px] font-medium ${decisionClass(run.decision)}`}>
          {run.decision}
        </span>
      </div>
      <div className="mt-2 grid grid-cols-5 gap-1 font-mono text-[9px] text-muted">
        <span>O {formatMetric(run.metrics.overall_f1, 3)}</span>
        {FAMILY_IDS.map((family) => (
          <span key={family}>
            {shortFamily(family)} {formatMetric(run.metrics.families[family]?.f1, 3)}
          </span>
        ))}
      </div>
    </button>
  );
}

function MetricStrip({ run }: { run: Exectv2RunSummary }) {
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
      <div className="rounded-md border border-border bg-surface px-3 py-2">
        <p className="text-[10px] uppercase tracking-wider text-muted">Overall</p>
        <p className="font-mono text-lg font-semibold text-foreground">{formatMetric(run.metrics.overall_f1)}</p>
      </div>
      {FAMILY_IDS.map((family) => (
        <div key={family} className="rounded-md border border-border bg-surface px-3 py-2">
          <p className="truncate text-[10px] uppercase tracking-wider text-muted">{family}</p>
          <p className="font-mono text-lg font-semibold text-foreground">
            {formatMetric(run.metrics.families[family]?.f1)}
          </p>
        </div>
      ))}
    </div>
  );
}

function SameLetterComparison({
  runs,
  letterId,
}: {
  runs: Exectv2RunSummary[];
  letterId: string;
}) {
  const rows = runs
    .map((run) => ({ run, letter: run.letters.find((item) => item.letter_id === letterId) }))
    .filter((row): row is { run: Exectv2RunSummary; letter: Exectv2LetterRecord } => Boolean(row.letter));

  if (rows.length <= 1) return null;

  return (
    <section className="rounded-md border border-border bg-surface">
      <div className="flex items-center gap-2 border-b border-border px-3 py-2">
        <Layers3 className="h-3.5 w-3.5 text-muted" />
        <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">Same Letter Across Runs</h3>
      </div>
      <div className="divide-y divide-border/70">
        {rows.map(({ run, letter }) => (
          <div key={run.run_id} className="grid grid-cols-[150px_1fr] gap-3 px-3 py-2">
            <div className="min-w-0">
              <p className="truncate text-[11px] font-semibold text-foreground">{compactRunLabel(run)}</p>
              <p className="font-mono text-[9px] text-muted">{formatMetric(run.metrics.overall_f1)}</p>
            </div>
            <div className="grid grid-cols-4 gap-1 font-mono text-[9px] text-muted">
              {FAMILY_IDS.map((family) => (
                <span key={family}>
                  {shortFamily(family)} {letter.family_counts.predicted[family]}/{letter.family_counts.gold[family]}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function Exectv2ExampleExplorer() {
  const { runs, isLoading, error, sourceIndex } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();
  const [letterSearch, setLetterSearch] = useState("");

  const selectedRun = useMemo(
    () => runs.find((run) => run.run_id === get("run")) ?? runs[0],
    [runs, get]
  );

  const filteredLetters = useMemo(() => {
    if (!selectedRun) return [];
    const query = letterSearch.trim().toLowerCase();
    if (!query) return selectedRun.letters;
    return selectedRun.letters.filter((letter) => {
      const haystack = [
        letter.letter_id,
        letter.letter_text,
        ...letter.predicted_mentions.map((m) => m.text),
        ...letter.gold_mentions.map((m) => m.text),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    });
  }, [letterSearch, selectedRun]);

  const selectedLetter = useMemo(() => {
    if (!selectedRun) return undefined;
    return (
      selectedRun.letters.find((letter) => letter.letter_id === get("letter")) ??
      filteredLetters[0] ??
      selectedRun.letters[0]
    );
  }, [filteredLetters, get, selectedRun]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <div className="space-y-3 text-center">
          <div className="mx-auto h-8 w-40 animate-pulse rounded bg-surface-raised" />
          <p className="text-sm font-medium">Loading ExECTv2 data…</p>
        </div>
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

  if (!selectedRun || !selectedLetter) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <p className="text-sm font-medium">No ExECTv2 runs available.</p>
      </div>
    );
  }

  const highlightSpans = selectedLetter.evidence_spans.map((span) => ({
    start: span.start,
    end: span.end,
    kind: span.kind,
    label: span.label,
  }));

  return (
    <div className="flex h-full min-h-0 flex-col bg-background">
      <header className="shrink-0 border-b border-border bg-surface px-5 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-deterministic" />
              <h1 className="text-sm font-semibold text-foreground">ExECTv2 · Example Explorer</h1>
              <span className="rounded border border-border bg-surface-raised px-2 py-0.5 text-[10px] text-muted">
                {runs.length} {exectv2Dataset.runLabel}s
              </span>
            </div>
            <p className="mt-1 font-mono text-[10px] text-muted">{sourceIndex}</p>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href={surfaceHref("observatory", "exectv2", { run: selectedRun.run_id })}
              className="inline-flex items-center gap-1 rounded border border-llm/25 bg-llm/10 px-2 py-1 text-[10px] font-medium text-llm transition-colors hover:bg-llm/15"
            >
              <BarChart3 className="h-3 w-3" /> Aggregate
            </Link>
            <Link
              href={surfaceHref("gallery", "exectv2", { run: selectedRun.run_id })}
              className="inline-flex items-center gap-1 rounded border border-error/25 bg-error/8 px-2 py-1 text-[10px] font-medium text-error transition-colors hover:bg-error/12"
            >
              <GalleryHorizontalEnd className="h-3 w-3" /> Errors
            </Link>
            <span className="rounded border border-success/25 bg-success/10 px-2 py-1 text-[10px] font-medium text-success">
              exact evidence {formatMetric(selectedRun.operational.exact_evidence_rate, 2)}
            </span>
            <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono text-[10px] text-muted">
              {selectedRun.split} / {selectedRun.row_count}
            </span>
          </div>
        </div>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[320px_1fr]">
        <aside className="min-h-0 overflow-y-auto border-b border-border bg-surface-raised/40 p-4 lg:border-b-0 lg:border-r">
          <div className="mb-3 flex items-center gap-2">
            <Activity className="h-3.5 w-3.5 text-muted" />
            <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted">Architectures</h2>
          </div>
          <div className="space-y-2">
            {runs.map((run) => (
              <RunButton
                key={run.run_id}
                run={run}
                active={run.run_id === selectedRun.run_id}
                onClick={() => set({ run: run.run_id, letter: undefined })}
              />
            ))}
          </div>

          <div className="mt-5 rounded-md border border-border bg-surface p-3">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">Claim Boundary</p>
            <p className="mt-2 text-[11px] leading-snug text-foreground">{selectedRun.claim_boundary}</p>
            <p className="mt-2 font-mono text-[9px] text-muted">{selectedRun.scorer_view}</p>
          </div>
        </aside>

        <main className="min-h-0 overflow-y-auto p-4 lg:p-5">
          <div className="mx-auto max-w-[1400px] space-y-4">
            <MetricStrip run={selectedRun} />

            <div className="grid grid-cols-1 gap-4 xl:grid-cols-[260px_1fr]">
              <section className="rounded-md border border-border bg-surface">
                <div className="border-b border-border px-3 py-2">
                  <div className="relative">
                    <Search className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted" />
                    <input
                      value={letterSearch}
                      onChange={(event) => setLetterSearch(event.target.value)}
                      placeholder="Search letters"
                      className="h-8 w-full rounded-md border border-border bg-surface pl-7 pr-2 text-[11px] text-foreground placeholder:text-muted focus:border-deterministic/40 focus:outline-none"
                    />
                  </div>
                </div>
                <div className="max-h-[420px] overflow-y-auto">
                  {filteredLetters.map((letter) => (
                    <button
                      key={letter.letter_id}
                      onClick={() => set({ letter: letter.letter_id })}
                      className={`grid w-full grid-cols-[1fr_auto] items-center gap-2 border-b border-border/60 px-3 py-2 text-left transition-colors last:border-b-0 ${
                        selectedLetter.letter_id === letter.letter_id ? "bg-deterministic/8" : "hover:bg-surface-raised"
                      }`}
                    >
                      <span className="font-mono text-[11px] font-semibold text-foreground">{letter.letter_id}</span>
                      {selectedLetter.letter_id === letter.letter_id && (
                        <CheckCircle2 className="h-3.5 w-3.5 text-deterministic" />
                      )}
                      <span className="col-span-2 truncate text-[10px] text-muted">
                        {letter.predicted_mentions.length} predicted / {letter.gold_mentions.length} gold
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              <div className="min-w-0 space-y-4">
                <div className="rounded-md border border-border bg-surface px-3 py-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="font-mono text-xs font-semibold text-foreground">{selectedLetter.letter_id}</p>
                      <p className="mt-1 text-[11px] text-muted">
                        {selectedRun.label} / {selectedRun.model}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-1 font-mono text-[9px] text-muted">
                      {FAMILY_IDS.map((family) => (
                        <span key={family} className="rounded border border-border bg-surface-raised px-1.5 py-0.5">
                          {shortFamily(family)} {selectedLetter.family_counts.predicted[family]}/
                          {selectedLetter.family_counts.gold[family]}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <LetterRenderer text={selectedLetter.letter_text} highlights={highlightSpans} />

                <div className="grid grid-cols-1 gap-3">
                  {FAMILY_IDS.map((family) => (
                    <FamilyPanel key={family} family={family} letter={selectedLetter} />
                  ))}
                </div>

                <SameLetterComparison runs={runs} letterId={selectedLetter.letter_id} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
