"use client";

import { useMemo, useCallback, useState } from "react";
import { Check, Copy, FileSpreadsheet } from "lucide-react";

interface PaperTableProps {
  title: string;
  caption?: string;
  headers: string[];
  rows: (string | number | null)[][];
  align?: ("left" | "right" | "center")[];
  cellClasses?: string[][];
  footer?: string;
}

function escapeCsvCell(val: string | number | null): string {
  if (val === null || val === undefined) return "";
  const s = String(val);
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function formatCell(val: string | number | null): string {
  if (val === null || val === undefined) return "—";
  if (typeof val === "number") {
    if (val >= 0.01 && val <= 1) return val.toFixed(3);
    if (Number.isInteger(val)) return String(val);
    return val.toFixed(2);
  }
  return String(val);
}

export function tableToMarkdown(
  title: string,
  headers: string[],
  rows: (string | number | null)[][],
  align?: ("left" | "right" | "center")[]
): string {
  const alignChar = (a?: string) => {
    if (a === "right") return "---:";
    if (a === "center") return ":---:";
    return "---";
  };
  const headerLine = `| ${headers.join(" | ")} |`;
  const sepLine = `| ${headers.map((_, i) => alignChar(align?.[i])).join(" | ")} |`;
  const bodyLines = rows.map((row) => `| ${row.map((c) => formatCell(c)).join(" | ")} |`);
  return [`### ${title}`, "", headerLine, sepLine, ...bodyLines, ""].join("\n");
}

export function tableToCsv(
  headers: string[],
  rows: (string | number | null)[][]
): string {
  const headerLine = headers.map(escapeCsvCell).join(",");
  const bodyLines = rows.map((row) => row.map(escapeCsvCell).join(","));
  return [headerLine, ...bodyLines].join("\n");
}

export default function PaperTable({
  title,
  caption,
  headers,
  rows,
  align,
  cellClasses,
  footer,
}: PaperTableProps) {
  const [copied, setCopied] = useState(false);

  const md = useMemo(
    () => tableToMarkdown(title, headers, rows, align),
    [title, headers, rows, align]
  );
  const csv = useMemo(() => tableToCsv(headers, rows), [headers, rows]);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(md).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }, [md]);

  const handleDownloadCsv = useCallback(() => {
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const safeTitle = title.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
    a.download = `${safeTitle}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [csv, title]);

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border bg-surface-raised px-4 py-2">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
            {title}
          </h3>
          {caption && <p className="text-[10px] text-muted mt-0.5">{caption}</p>}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 rounded-md border border-border bg-surface px-2 py-1 text-[10px] font-medium text-muted hover:text-foreground transition-colors"
            title="Copy Markdown"
          >
            {copied ? <Check className="h-3 w-3 text-success" /> : <Copy className="h-3 w-3" />}
            <span className="hidden sm:inline">{copied ? "Copied" : "Copy MD"}</span>
          </button>
          <button
            onClick={handleDownloadCsv}
            className="flex items-center gap-1 rounded-md border border-border bg-surface px-2 py-1 text-[10px] font-medium text-muted hover:text-foreground transition-colors"
            title="Download CSV"
          >
            <FileSpreadsheet className="h-3 w-3" />
            <span className="hidden sm:inline">CSV</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60">
              {headers.map((h, i) => (
                <th
                  key={i}
                  className={`px-3 py-2 font-semibold text-muted text-left ${
                    align?.[i] === "right" ? "text-right" : align?.[i] === "center" ? "text-center" : ""
                  }`}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} className="border-b border-border last:border-0 hover:bg-surface-raised/30 transition-colors">
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    className={`px-3 py-2 text-foreground ${
                      align?.[ci] === "right" ? "text-right font-mono" : align?.[ci] === "center" ? "text-center" : ""
                    } ${cellClasses?.[ri]?.[ci] ?? ""}`}
                  >
                    {formatCell(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {footer && (
        <div className="border-t border-border bg-surface-raised/40 px-4 py-2">
          <p className="text-[10px] text-muted leading-relaxed">{footer}</p>
        </div>
      )}
    </div>
  );
}
