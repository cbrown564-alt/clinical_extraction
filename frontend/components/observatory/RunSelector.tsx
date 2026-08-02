"use client";

import { useState, useMemo } from "react";
import { Telescope, Check, Filter, Search, X, ChevronDown, ChevronUp } from "lucide-react";
import type { RegistryEntry } from "@/lib/types";
import { laneMetaForRun } from "@/lib/observatoryLanes";
import { familyLabel, splitLabel } from "@/lib/plainLanguageLabels";
import { parseRunVariant } from "./useObservatoryData";

interface RunSelectorProps {
  runs: RegistryEntry[];
  selectedIds: Set<string>;
  loadingIds: Set<string>;
  errors: Map<string, string>;
  onToggle: (runId: string) => void;
  onSelectRuns: (runIds: string[]) => void;
}

type SortKey = "family" | "split" | "rows" | "decision" | "date";
type SortDir = "asc" | "desc";

const FAMILY_ORDER = [
  "rules",
  "llm_only_direct_labeler",
  "hybrid_structured_events",
  "llm_structured_events",
  "llm_first_direct_extractor",
  "llm_heavy_clinical_frequency_reasoner",
  "llm_heavy_evidence_selection_with_deterministic_adapters",
  "llm_replacement_postprocessing_ablation",
  "reset_clinical_assessment_pipeline",
  "hybrid_clinical_frequency_state_graph",
  "dspy_final_selection_adjudicator",
];

function familyColorClass(family: string): string {
  if (family === "rules" || family.includes("rules_only") || family.includes("deterministic")) {
    return "text-deterministic bg-deterministic/8 border-deterministic/20";
  }
  if (family.includes("hybrid")) {
    return "text-hybrid bg-hybrid/8 border-hybrid/20";
  }
  return "text-llm bg-llm/8 border-llm/20";
}

function decisionBadge(decision: string): string {
  switch (decision) {
    case "accept":
      return "bg-success/12 text-success";
    case "reject":
      return "bg-error/12 text-error";
    case "revise":
      return "bg-llm-alt/12 text-llm";
    case "historical":
      return "bg-deterministic-alt/12 text-deterministic-alt";
    default:
      return "bg-muted/10 text-muted";
  }
}

function formatDate(d: string): string {
  try {
    return new Date(d).toLocaleDateString(undefined, { month: "short", day: "numeric" });
  } catch {
    return d;
  }
}

export default function RunSelector({
  runs,
  selectedIds,
  loadingIds,
  errors,
  onToggle,
  onSelectRuns,
}: RunSelectorProps) {
  const [search, setSearch] = useState("");
  const [filterFamily, setFilterFamily] = useState<string>("all");
  const [filterHasTest, setFilterHasTest] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("rows");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [collapsedFamilies, setCollapsedFamilies] = useState<Set<string>>(new Set());

  const filtered = useMemo(() => {
    let list = runs.filter((r) => r.artifact_paths.some((p) => p.endsWith(".jsonl")));
    if (filterFamily !== "all") {
      list = list.filter((r) => r.pipeline_family === filterFamily);
    }
    if (filterHasTest) {
      list = list.filter((r) => r.split?.includes("test"));
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (r) =>
          r.run_id.toLowerCase().includes(q) ||
          r.pipeline_family.toLowerCase().includes(q) ||
          (r.split ?? "").toLowerCase().includes(q)
      );
    }
    return list;
  }, [runs, filterFamily, filterHasTest, search]);

  const sorted = useMemo(() => {
    const list = [...filtered];
    list.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "family":
          cmp = a.pipeline_family.localeCompare(b.pipeline_family);
          break;
        case "split":
          cmp = (a.split ?? "").localeCompare(b.split ?? "");
          break;
        case "rows":
          cmp = a.row_count - b.row_count;
          break;
        case "decision":
          cmp = (a.decision ?? "").localeCompare(b.decision ?? "");
          break;
        case "date":
          cmp = (a.date ?? "").localeCompare(b.date ?? "");
          break;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [filtered, sortKey, sortDir]);

  const grouped = useMemo(() => {
    const map = new Map<string, RegistryEntry[]>();
    for (const run of sorted) {
      const list = map.get(run.pipeline_family) ?? [];
      list.push(run);
      map.set(run.pipeline_family, list);
    }
    // Sort families by preferred order
    const ordered = FAMILY_ORDER.filter((f) => map.has(f));
    for (const f of map.keys()) {
      if (!ordered.includes(f)) ordered.push(f);
    }
    return ordered.map((family) => ({ family, runs: map.get(family)! }));
  }, [sorted]);

  const allVisibleIds = useMemo(() => sorted.map((r) => r.run_id), [sorted]);
  const allSelected = allVisibleIds.length > 0 && allVisibleIds.every((id) => selectedIds.has(id));
  const someSelected = allVisibleIds.some((id) => selectedIds.has(id));

  const toggleFamilyCollapse = (family: string) => {
    setCollapsedFamilies((prev) => {
      const next = new Set(prev);
      if (next.has(family)) next.delete(family);
      else next.add(family);
      return next;
    });
  };

  const handleSelectAll = () => {
    if (allSelected) {
      // Deselect all visible
      const remaining = new Set(selectedIds);
      for (const id of allVisibleIds) remaining.delete(id);
      onSelectRuns(Array.from(remaining));
    } else {
      onSelectRuns([...new Set([...selectedIds, ...allVisibleIds])]);
    }
  };

  const renderSortButton = (k: SortKey, label: string) => {
    const active = sortKey === k;
    return (
      <button
        type="button"
        key={k}
        onClick={() => {
          if (active) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
          else {
            setSortKey(k);
            setSortDir("desc");
          }
        }}
        className={`flex items-center gap-0.5 text-[11px] font-medium uppercase tracking-wider transition-colors ${
          active ? "text-foreground" : "text-muted hover:text-foreground"
        }`}
      >
        {label}
        {active && (sortDir === "asc" ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />)}
      </button>
    );
  };

  return (
    <div className="space-y-3">
      {/* Header with filters */}
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Telescope className="h-4 w-4 text-muted" />
            <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
              Run Registry
            </h3>
            <span className="rounded-full bg-surface-raised px-2 py-0.5 text-[11px] text-muted border border-border">
              {filtered.length} runs
            </span>
            {selectedIds.size > 0 && (
              <span className="rounded-full bg-deterministic/10 px-2 py-0.5 text-[11px] text-deterministic border border-deterministic/20">
                {selectedIds.size} selected
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Quick actions */}
            <button
              type="button"
              onClick={() => onSelectRuns([])}
              className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] font-medium text-muted hover:bg-surface-raised transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Filter bar */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search runs..."
              className="h-7 w-48 rounded-md border border-border bg-surface pl-7 pr-6 text-xs text-foreground placeholder:text-muted focus:border-deterministic/40 focus:outline-none"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 text-muted hover:text-foreground"
                aria-label="Clear run search"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </div>

          <div className="flex items-center gap-1 rounded-md border border-border bg-surface p-0.5">
            <Filter className="ml-1.5 h-3 w-3 text-muted" />
            <select
              value={filterFamily}
              onChange={(e) => setFilterFamily(e.target.value)}
              className="h-6 bg-transparent px-1.5 text-[11px] text-foreground focus:outline-none"
            >
              <option value="all">All families</option>
              {FAMILY_ORDER.filter((f) => runs.some((r) => r.pipeline_family === f)).map((f) => (
                <option key={f} value={f}>
                  {familyLabel(f)}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={() => setFilterHasTest((v) => !v)}
            className={`flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-[11px] font-medium transition-colors ${
              filterHasTest
                ? "border-llm/30 bg-llm/8 text-llm"
                : "border-border bg-surface text-muted hover:text-foreground"
            }`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${filterHasTest ? "bg-llm" : "bg-muted/30"}`} />
            Has test data
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-border bg-surface">
        {/* Table header */}
        <div className="grid min-w-[720px] grid-cols-[32px_140px_120px_64px_72px_72px_1fr] items-center gap-1 border-b border-border bg-surface-raised/60 px-3 py-1.5">
          <button
            type="button"
            onClick={handleSelectAll}
            className="flex items-center justify-center"
            aria-label={allSelected ? "Deselect all visible runs" : "Select all visible runs"}
            aria-pressed={allSelected}
          >
            <div
              className={`flex h-3.5 w-3.5 items-center justify-center rounded border transition-colors ${
                allSelected
                  ? "bg-deterministic border-deterministic"
                  : someSelected
                  ? "bg-surface border-deterministic"
                  : "border-border bg-surface"
              }`}
            >
              {allSelected && <Check className="h-2.5 w-2.5 text-surface" strokeWidth={3} />}
              {!allSelected && someSelected && <div className="h-2 w-2 rounded-sm bg-deterministic" />}
            </div>
          </button>
          {renderSortButton("family", "Family")}
          {renderSortButton("split", "Split")}
          {renderSortButton("rows", "Rows")}
          {renderSortButton("decision", "Decision")}
          {renderSortButton("date", "Date")}
          <span className="text-[11px] font-medium uppercase tracking-wider text-muted">Variant</span>
        </div>

        {/* Table body */}
        <div className="max-h-[340px] min-w-[720px] overflow-y-auto">
          {grouped.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-muted">No runs match your filters.</div>
          ) : (
            grouped.map(({ family, runs: familyRuns }) => {
              const collapsed = collapsedFamilies.has(family);
              const familySelected = familyRuns.every((r) => selectedIds.has(r.run_id));
              const familySome = familyRuns.some((r) => selectedIds.has(r.run_id));

              return (
                <div key={family}>
                  {/* Family header row */}
                  <div className="sticky top-0 z-10 flex items-center gap-2 border-b border-border bg-surface-raised/90 px-3 py-1">
                    <button
                      type="button"
                      onClick={() => {
                        if (familySelected) {
                          const remaining = new Set(selectedIds);
                          for (const r of familyRuns) remaining.delete(r.run_id);
                          onSelectRuns(Array.from(remaining));
                        } else {
                          onSelectRuns([...new Set([...selectedIds, ...familyRuns.map((r) => r.run_id)])]);
                        }
                      }}
                      className="flex items-center justify-center"
                      aria-label={`${familySelected ? "Deselect" : "Select"} ${familyLabel(family)} runs`}
                      aria-pressed={familySelected}
                    >
                      <div
                        className={`flex h-3 w-3 items-center justify-center rounded border transition-colors ${
                          familySelected
                            ? "bg-deterministic border-deterministic"
                            : familySome
                            ? "bg-surface border-deterministic"
                            : "border-border bg-surface"
                        }`}
                      >
                        {familySelected && <Check className="h-2 w-2 text-surface" strokeWidth={3} />}
                        {!familySelected && familySome && <div className="h-1.5 w-1.5 rounded-sm bg-deterministic" />}
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleFamilyCollapse(family)}
                      className="flex min-w-0 items-center gap-2 rounded-sm text-left"
                      aria-expanded={!collapsed}
                    >
                      <span className={`rounded px-1.5 py-0.5 text-[11px] font-semibold border ${familyColorClass(family)}`}>
                        {familyLabel(family)}
                      </span>
                      <span className="text-[11px] text-muted">{familyRuns.length} runs</span>
                      {collapsed ? <ChevronDown className="h-3 w-3 text-muted" /> : <ChevronUp className="h-3 w-3 text-muted" />}
                    </button>
                  </div>

                  {!collapsed &&
                    familyRuns.map((run) => {
                      const selected = selectedIds.has(run.run_id);
                      const loading = loadingIds.has(run.run_id);
                      const error = errors.get(run.run_id);
                      const variant = parseRunVariant(run.run_id, run.pipeline_family);
                      const lane = laneMetaForRun(run);

                      return (
                        <div
                          key={run.run_id}
                          onClick={() => onToggle(run.run_id)}
                          className={`grid grid-cols-[32px_140px_120px_64px_72px_72px_1fr] items-center gap-1 px-3 py-1.5 border-b border-border/50 cursor-pointer transition-colors ${
                            selected ? "bg-deterministic/4" : "hover:bg-surface-raised/50"
                          } ${loading ? "opacity-60" : ""}`}
                          title={error ?? run.run_id}
                        >
                          <button
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation();
                              onToggle(run.run_id);
                            }}
                            className="flex items-center justify-center"
                            aria-label={`${selected ? "Deselect" : "Select"} ${familyLabel(run.pipeline_family)} run`}
                            aria-pressed={selected}
                          >
                            <div
                              className={`flex h-3 w-3 items-center justify-center rounded border transition-colors ${
                                selected ? "bg-deterministic border-deterministic" : "border-border bg-surface"
                              }`}
                            >
                              {selected && <Check className="h-2 w-2 text-surface" strokeWidth={3} />}
                            </div>
                          </button>
                          <span className="flex items-center gap-1 truncate">
                            <span className="text-xs font-medium text-foreground truncate">
                              {familyLabel(run.pipeline_family)}
                            </span>
                            {lane && (
                              <span
                                className={`shrink-0 rounded border px-1 py-0 text-[11px] font-semibold ${lane.badgeClass} ${lane.textClass}`}
                                title={lane.title}
                              >
                                {lane.label}
                              </span>
                            )}
                          </span>
                          <span className="text-[11px] text-muted truncate">
                            {splitLabel(run.split)}
                          </span>
                          <span className="text-[11px] font-mono text-foreground">
                            {run.row_count}
                          </span>
                          <span
                            className={`w-fit rounded px-1 py-0 text-[11px] font-medium ${decisionBadge(
                              run.decision ?? ""
                            )}`}
                          >
                            {run.decision ?? "–"}
                          </span>
                          <span className="text-[11px] text-muted">
                            {formatDate(run.date)}
                          </span>
                          <span className="text-[11px] font-mono text-muted truncate">
                            {variant}
                          </span>
                        </div>
                      );
                    })}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
