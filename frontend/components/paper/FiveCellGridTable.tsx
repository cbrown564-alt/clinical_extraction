"use client";

import { useEffect, useState } from "react";

type GridTask = "gan" | "exect";

type GridRow = {
  id: string;
  order: number;
  display_name: string;
  short_label: string;
  extract: string;
  encode: string;
  select: string;
  select_stop: number | null;
  extract_ablation: number | null;
  encode_ablation: number | null;
  headline: boolean;
};

type GridPayload = {
  task: GridTask;
  model: string;
  split: string;
  n: number | null;
  headline: string;
  claim_boundary: string | null;
  source: string;
  cells: GridRow[];
};

function formatScore(task: GridTask, value: number | null): string {
  if (value === null || Number.isNaN(value)) return "—";
  if (task === "gan") return String(value);
  return value.toFixed(4);
}

export default function FiveCellGridTable() {
  const [task, setTask] = useState<GridTask>("gan");
  const [payload, setPayload] = useState<GridPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    fetch(`/api/paper/five-cell-grid?task=${task}&model=gemini37flash`)
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.json() as Promise<GridPayload>;
      })
      .then((data) => {
        if (!cancelled) setPayload(data);
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setPayload(null);
          setError(err.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [task]);

  return (
    <section className="border-b border-border bg-surface px-4 py-3">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold text-foreground">
          Five-cell role grid
        </h2>
        <div className="flex items-center gap-1">
          {(["gan", "exect"] as const).map((id) => (
            <button
              key={id}
              type="button"
              onClick={() => setTask(id)}
              className={`h-7 rounded-md px-2.5 text-xs ${
                task === id
                  ? "bg-deterministic/10 font-semibold text-deterministic"
                  : "text-muted hover:bg-surface-raised"
              }`}
            >
              {id === "gan" ? "Gan" : "ExECT"}
            </button>
          ))}
        </div>
      </div>
      {error && <p className="text-xs text-error">{error}</p>}
      {payload && (
        <>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-border text-muted">
                  <th className="py-1.5 pr-2 font-medium">Cell</th>
                  <th className="py-1.5 pr-2 font-medium">Extract</th>
                  <th className="py-1.5 pr-2 font-medium">Encode</th>
                  <th className="py-1.5 pr-2 font-medium">Select</th>
                  <th className="py-1.5 pr-2 font-medium">Select stop (headline)</th>
                  <th className="py-1.5 pr-2 font-medium">Extract ablation</th>
                  <th className="py-1.5 font-medium">Encode ablation</th>
                </tr>
              </thead>
              <tbody>
                {payload.cells.map((row) => (
                  <tr
                    key={row.id}
                    className={`border-b border-border/60 ${
                      row.headline ? "font-semibold text-foreground" : "text-foreground"
                    }`}
                  >
                    <td className="py-1.5 pr-2">
                      {row.order}. {row.display_name}
                      <span className="ml-1 font-normal text-muted">{row.short_label}</span>
                    </td>
                    <td className="py-1.5 pr-2">{row.extract}</td>
                    <td className="py-1.5 pr-2">{row.encode}</td>
                    <td className="py-1.5 pr-2">{row.select}</td>
                    <td className="py-1.5 pr-2">{formatScore(payload.task, row.select_stop)}</td>
                    <td className="py-1.5 pr-2">{formatScore(payload.task, row.extract_ablation)}</td>
                    <td className="py-1.5">{formatScore(payload.task, row.encode_ablation)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-1.5 text-[11px] text-muted">
            {payload.source}
            {payload.n != null ? ` · n=${payload.n}` : ""}
            {payload.headline ? ` · headline=${payload.headline}` : ""}
          </p>
        </>
      )}
    </section>
  );
}
