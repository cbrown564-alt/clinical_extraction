"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Database, FileSearch, FlaskConical, ListChecks, Table2, X } from "lucide-react";
import {
  fetchGoldNoiseGanAudit,
  fetchGoldNoiseHypotheses,
  fetchGoldNoiseIssues,
  fetchGoldNoiseLedgers,
} from "@/lib/api";
import type { GoldNoiseFamilySummary, GoldNoiseItem } from "@/lib/types";
import LetterRenderer from "./LetterRenderer";
import {
  CORROBORATION,
  CeilingTile,
  DefectsView,
  GanAuditView,
  HypothesesView,
  ItemRow,
  MECHANISM_LABELS,
  MechanismMatrix,
  VERDICT_META,
  VERDICT_ORDER,
  VerdictStackedBar,
  findMentionSpans,
  mentionText,
} from "./GoldNoiseViews";

type SourceTab = "matrix" | "gan" | "hypotheses" | "defects";

const SOURCE_TABS: { id: SourceTab; label: string; Icon: typeof Table2 }[] = [
  { id: "matrix", label: "ExECT ledger", Icon: Table2 },
  { id: "gan", label: "Gan RQ10 audit", Icon: Database },
  { id: "hypotheses", label: "Hypotheses", Icon: FlaskConical },
  { id: "defects", label: "Gold defects", Icon: AlertTriangle },
];

export default function GoldNoisePanel() {
  const [tab, setTab] = useState<SourceTab>("matrix");
  const [filter, setFilter] = useState<{ family: string; mechanism: string } | null>(null);
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);

  const { data: ledgersData, isLoading: ledgersLoading } = useQuery({
    queryKey: ["gold-noise-ledgers"],
    queryFn: fetchGoldNoiseLedgers,
  });
  const { data: ganData } = useQuery({
    queryKey: ["gold-noise-gan-audit"],
    queryFn: fetchGoldNoiseGanAudit,
  });
  const { data: issuesData } = useQuery({
    queryKey: ["gold-noise-issues"],
    queryFn: fetchGoldNoiseIssues,
  });
  const { data: hypothesesData } = useQuery({
    queryKey: ["gold-noise-hypotheses"],
    queryFn: fetchGoldNoiseHypotheses,
  });

  const families = useMemo(() => ledgersData?.families ?? [], [ledgersData]);

  // Flatten all items across families for the filtered item list.
  const allItems = useMemo(() => {
    const items: (GoldNoiseItem & { family: string })[] = [];
    for (const fam of families) for (const row of fam.rows) items.push(row);
    return items;
  }, [families]);

  const filteredItems = useMemo(() => {
    if (!filter) return allItems;
    return allItems.filter(
      (it) => it.family === filter.family && it.mechanism === filter.mechanism
    );
  }, [allItems, filter]);

  const selectedItem = useMemo(() => {
    if (!selectedRowId) return null;
    return allItems.find((it) => it.row_id === selectedRowId) ?? null;
  }, [allItems, selectedRowId]);

  if (ledgersLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading gold noise evidence…</p>
      </div>
    );
  }

  const totalRows = families.reduce((s, f) => s + f.total, 0);
  const totalGoldRight = families.reduce((s, f) => s + f.gold_right, 0);

  return (
    <div className="flex h-full flex-col bg-background">
      <SummaryHeader
        families={families}
        totalRows={totalRows}
        totalGoldRight={totalGoldRight}
      />

      <div className="flex flex-1 flex-col overflow-hidden lg:flex-row">
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Tab bar */}
          <div className="flex shrink-0 items-center gap-1 border-b border-border bg-surface px-3 py-1.5">
            {SOURCE_TABS.map(({ id, label, Icon }) => (
              <button
                key={id}
                onClick={() => setTab(id)}
                className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-[10px] font-medium transition-colors ${
                  tab === id ? "bg-surface-raised text-foreground" : "text-muted hover:text-foreground"
                }`}
              >
                <Icon className="h-3 w-3" />
                {label}
              </button>
            ))}
            {filter && (
              <span className="ml-auto flex items-center gap-1 rounded border border-hybrid/30 bg-hybrid/10 px-2 py-0.5 text-[9px] text-hybrid">
                <ListChecks className="h-2.5 w-2.5" />
                {filter.family} · {MECHANISM_LABELS[filter.mechanism] ?? filter.mechanism} (
                {filteredItems.length})
                <button onClick={() => setFilter(null)} className="ml-0.5 hover:text-foreground">
                  <X className="h-2.5 w-2.5" />
                </button>
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-6xl space-y-3 p-4 pb-8">
              {tab === "matrix" && (
                <>
                  <div className="rounded-lg border border-border bg-surface p-3">
                    <h3 className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
                      <Table2 className="h-3 w-3" />
                      Mechanism × family (click a cell to filter items)
                    </h3>
                    <MechanismMatrix
                      families={families}
                      filter={filter}
                      onCellClick={(family, mechanism) => {
                        setFilter({ family, mechanism });
                        setSelectedRowId(null);
                      }}
                    />
                  </div>
                  <div className="rounded-lg border border-border bg-surface">
                    <h3 className="flex items-center gap-1.5 border-b border-border px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-muted">
                      <FileSearch className="h-3 w-3" />
                      Items {filter ? `(${filteredItems.length})` : `(${allItems.length})`}
                    </h3>
                    <div className="max-h-72 overflow-y-auto">
                      {(filter ? filteredItems : allItems.slice(0, 50)).map((item) => (
                        <ItemRow
                          key={item.row_id}
                          item={item}
                          active={selectedRowId === item.row_id}
                          onClick={() => setSelectedRowId(item.row_id)}
                        />
                      ))}
                      {!filter && allItems.length > 50 && (
                        <p className="px-3 py-2 text-center text-[9px] text-muted">
                          Showing first 50 of {allItems.length}. Filter via the matrix to narrow.
                        </p>
                      )}
                    </div>
                  </div>
                </>
              )}
              {tab === "gan" && ganData && <GanAuditView data={ganData} />}
              {tab === "hypotheses" && hypothesesData && <HypothesesView data={hypothesesData} />}
              {tab === "defects" && issuesData && <DefectsView data={issuesData} />}
            </div>
          </div>
        </div>

        {selectedItem && (
          <ItemInspector
            item={selectedItem}
            onClose={() => setSelectedRowId(null)}
          />
        )}
      </div>
    </div>
  );
}

// ── Summary header ──

function SummaryHeader({
  families,
  totalRows,
  totalGoldRight,
}: {
  families: GoldNoiseFamilySummary[];
  totalRows: number;
  totalGoldRight: number;
}) {
  return (
    <div className="shrink-0 border-b border-border bg-surface px-5 py-3">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-error" />
        <h1 className="text-sm font-semibold text-foreground">Gold noise evidence</h1>
        <span className="text-[10px] text-muted">
          {totalRows} disagreements across {families.length} families · {totalGoldRight} genuine
          model errors
        </span>
      </div>
      <p className="mt-1 max-w-4xl text-[10px] text-muted">
        Benchmark labels are not clinical truth. Each ceiling below is the genuine-model-error rate
        (verdict = gold_right), derived live from the canonical adjudication ledgers — never
        hard-coded. Its complement is the gold-contested share.
      </p>

      <div className="mt-2.5 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {families.map((fam) => (
          <CeilingTile key={fam.family} fam={fam} />
        ))}
      </div>

      <div className="mt-2.5 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface-raised p-2.5">
          <h3 className="mb-1.5 text-[9px] font-semibold uppercase tracking-wider text-muted">
            Cross-project corroboration (three independent codebases)
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {CORROBORATION.map((c) => (
              <div key={c.source} className="rounded border border-border bg-surface px-2 py-1">
                <div className="text-[10px] font-medium text-foreground">{c.value}</div>
                <div className="text-[8px] text-muted">
                  {c.source} · {c.note}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-border bg-surface-raised p-2.5">
          <h3 className="mb-1.5 text-[9px] font-semibold uppercase tracking-wider text-muted">
            Verdict composition by family
          </h3>
          <VerdictStackedBar families={families} />
          <div className="mt-1.5 flex flex-wrap gap-2">
            {VERDICT_ORDER.map((v) => (
              <span key={v} className="flex items-center gap-1 text-[8px] text-muted">
                <span className={`h-2 w-2 rounded-sm ${VERDICT_META[v]?.bar}`} />
                {VERDICT_META[v]?.label ?? v}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-2 flex flex-wrap gap-1.5">
        <span className="rounded border border-border bg-surface-raised px-1.5 py-0.5 text-[8px] text-muted">
          Dx: 15.6% (199-row ledger) vs 14.8% (209-row original) — shown with numerators
        </span>
        <span className="rounded border border-border bg-surface-raised px-1.5 py-0.5 text-[8px] text-muted">
          Gan RQ10 uses a different class taxonomy than ExECT Mechanism — never mixed
        </span>
      </div>
    </div>
  );
}

// ── Item inspector (right rail) ──

function ItemInspector({ item, onClose }: { item: GoldNoiseItem; onClose: () => void }) {
  return (
    <div className="flex w-full shrink-0 flex-col border-t border-border bg-surface lg:w-[440px] lg:border-l lg:border-t-0">
      <div className="flex items-center justify-between border-b border-border px-4 py-2">
        <h3 className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-foreground">
          <FileSearch className="h-3 w-3" />
          Item inspection
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
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="font-mono text-[10px] text-muted">{item.letter_id}</span>
            <span className="rounded border border-border bg-surface-raised px-1.5 py-0 text-[9px] text-muted">
              {item.family}
            </span>
            <span className="rounded border border-border bg-surface-raised px-1.5 py-0 text-[9px] text-muted">
              {item.disagreement_type}
            </span>
            <span
              className={`rounded border px-1.5 py-0 text-[9px] font-medium ${
                VERDICT_META[item.verdict]?.tone ?? ""
              }`}
            >
              {item.verdict}
            </span>
            <span
              className={`rounded border px-1.5 py-0 text-[9px] font-medium ${
                item.mechanism.startsWith("gold_")
                  ? "border-deterministic/30 text-deterministic bg-deterministic/10"
                  : "border-error/30 text-error bg-error/10"
              }`}
            >
              {MECHANISM_LABELS[item.mechanism] ?? item.mechanism}
            </span>
          </div>

          <div className="rounded-lg border border-border bg-surface-raised p-2.5">
            <p className="text-[9px] font-semibold uppercase tracking-wider text-muted">Match key</p>
            <p className="mt-0.5 font-mono text-[11px] text-foreground">{item.match_key}</p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="rounded border border-gold/30 bg-gold/5 p-2">
              <p className="text-[8px] font-semibold uppercase tracking-wider text-muted">
                Gold mention
              </p>
              <p className="mt-0.5 font-mono text-[10px] text-foreground">
                {mentionText(item.gold) || "—"}
              </p>
            </div>
            <div className="rounded border border-repair/30 bg-repair/5 p-2">
              <p className="text-[8px] font-semibold uppercase tracking-wider text-muted">
                Pred mention
              </p>
              <p className="mt-0.5 font-mono text-[10px] text-foreground">
                {mentionText(item.pred) || "—"}
              </p>
            </div>
          </div>

          {item.reason && (
            <div className="rounded-lg border border-border bg-surface-raised p-2.5">
              <p className="text-[9px] font-semibold uppercase tracking-wider text-muted">
                Adjudication reason
              </p>
              <p className="mt-0.5 text-[11px] text-foreground">{item.reason}</p>
            </div>
          )}

          {item.source_letter_text && (
            <div>
              <p className="mb-1 text-[9px] font-semibold uppercase tracking-wider text-muted">
                Source letter (gold + pred highlighted)
              </p>
              <LetterRenderer
                text={item.source_letter_text}
                highlights={findMentionSpans(item.source_letter_text, item)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
