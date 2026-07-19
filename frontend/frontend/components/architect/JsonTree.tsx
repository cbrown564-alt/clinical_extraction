"use client";

import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isArray(value: unknown): value is unknown[] {
  return Array.isArray(value);
}

function formatValue(value: unknown): string {
  if (value === null) return "null";
  if (value === undefined) return "undefined";
  if (typeof value === "string") return `"${value}"`;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (isArray(value)) return `[] ${value.length} items`;
  if (isObject(value)) return `{} ${Object.keys(value).length} keys`;
  return String(value);
}

function getValueColor(value: unknown): string {
  if (value === null || value === undefined) return "text-muted";
  if (typeof value === "string") return "text-success";
  if (typeof value === "number") return "text-deterministic-alt";
  if (typeof value === "boolean") return "text-hybrid";
  return "text-foreground";
}

interface TreeNodeProps {
  label: string;
  value: unknown;
  depth?: number;
}

function TreeNode({ label, value, depth = 0 }: TreeNodeProps) {
  const [expanded, setExpanded] = useState(depth < 1);
  const hasChildren = isObject(value) || (isArray(value) && value.length > 0);

  return (
    <div className="font-mono text-xs">
      <div
        className="flex items-start gap-1 py-0.5 hover:bg-surface-raised/50 rounded px-1"
        style={{ paddingLeft: `${depth * 12 + 4}px` }}
      >
        {hasChildren && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-0.5 text-muted hover:text-foreground shrink-0"
          >
            {expanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          </button>
        )}
        {!hasChildren && <span className="w-3 shrink-0" />}
        <span className="text-muted shrink-0">{label}:</span>
        {!hasChildren && (
          <span className={`break-all ${getValueColor(value)}`}>{formatValue(value)}</span>
        )}
        {hasChildren && (
          <span className="text-muted">
            {isArray(value) ? `[] ${value.length} items` : `{} ${Object.keys(value as object).length} keys`}
          </span>
        )}
      </div>
      {hasChildren && expanded && (
        <div>
          {isArray(value) &&
            value.map((item, idx) => (
              <TreeNode key={idx} label={String(idx)} value={item} depth={depth + 1} />
            ))}
          {isObject(value) &&
            Object.entries(value).map(([key, val]) => (
              <TreeNode key={key} label={key} value={val} depth={depth + 1} />
            ))}
        </div>
      )}
    </div>
  );
}

interface JsonTreeProps {
  data: unknown;
  title?: string;
}

export default function JsonTree({ data, title }: JsonTreeProps) {
  return (
    <div className="rounded-lg border border-border bg-surface-raised/30 overflow-hidden">
      {title && (
        <div className="border-b border-border bg-surface-raised/50 px-3 py-1.5">
          <span className="text-xs font-semibold uppercase tracking-wide text-muted">{title}</span>
        </div>
      )}
      <div className="p-2 overflow-auto max-h-[400px]">
        {isObject(data) ? (
          Object.entries(data).map(([key, val]) => <TreeNode key={key} label={key} value={val} />)
        ) : isArray(data) ? (
          data.map((item, idx) => <TreeNode key={idx} label={String(idx)} value={item} />)
        ) : (
          <span className="text-muted">{formatValue(data)}</span>
        )}
      </div>
    </div>
  );
}
