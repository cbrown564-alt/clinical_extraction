"use client";

import React, { useState, useMemo } from "react";
import {
  Code,
  LayoutList,
  FolderTree,
  Clock,
  Sparkles,
  Quote,
  Tag,
  CheckCircle2,
} from "lucide-react";
import JsonTree from "@/components/architect/JsonTree";

interface FormattedPayloadViewerProps {
  label: string;
  raw: string;
}

export default function FormattedPayloadViewer({ label, raw }: FormattedPayloadViewerProps) {
  const [viewMode, setViewMode] = useState<"visual" | "tree" | "raw">("visual");

  // Attempt to parse JSON
  const parsedJson = useMemo(() => {
    if (!raw || typeof raw !== "string") return null;
    const trimmed = raw.trim();
    if (
      (trimmed.startsWith("{") && trimmed.endsWith("}")) ||
      (trimmed.startsWith("[") && trimmed.endsWith("]"))
    ) {
      try {
        return JSON.parse(trimmed);
      } catch {
        return null;
      }
    }
    return null;
  }, [raw]);

  // Clean string helper: strips redundant surrounding JSON quotes and escaping
  const cleanStr = (s: string) => {
    let res = s.trim();
    if (res.startsWith('"') && res.endsWith('"') && res.length >= 2) {
      res = res.slice(1, -1);
    }
    return res.replace(/\\"/g, '"');
  };

  // If not JSON, render plain string
  if (!parsedJson) {
    return (
      <div className="rounded-lg border border-border bg-surface overflow-hidden shadow-xs">
        <div className="flex items-center justify-between gap-3 border-b border-border bg-surface-raised px-3.5 py-2">
          <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-muted shrink-0">
            {label}
          </span>
          <span className="rounded bg-surface border border-border px-1.5 py-0.5 text-[9px] font-mono text-muted uppercase">
            plain text
          </span>
        </div>
        <pre className="p-3.5 font-mono text-[11px] text-foreground whitespace-pre-wrap break-all leading-relaxed max-h-48 overflow-y-auto">
          {raw}
        </pre>
      </div>
    );
  }

  // Extract structured events if present
  const events = Array.isArray(parsedJson)
    ? parsedJson
    : parsedJson.events || parsedJson.clinical_events || parsedJson.clinical_facts || null;

  const selection = parsedJson.selection || null;

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden shadow-xs">
      {/* Viewer Tab Bar */}
      <div className="flex items-center justify-between gap-3 border-b border-border bg-surface-raised px-3.5 py-2">
        <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-muted truncate min-w-0">
          {label}
        </span>
        <div className="flex items-center gap-0.5 rounded-md bg-surface p-0.5 border border-border shrink-0">
          <button
            onClick={() => setViewMode("visual")}
            className={`flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-semibold transition-all ${
              viewMode === "visual"
                ? "bg-surface-raised text-foreground shadow-2xs"
                : "text-muted hover:text-foreground"
            }`}
          >
            <LayoutList className="h-3 w-3" />
            <span>Cards</span>
          </button>
          <button
            onClick={() => setViewMode("tree")}
            className={`flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-semibold transition-all ${
              viewMode === "tree"
                ? "bg-surface-raised text-foreground shadow-2xs"
                : "text-muted hover:text-foreground"
            }`}
          >
            <FolderTree className="h-3 w-3" />
            <span>Tree</span>
          </button>
          <button
            onClick={() => setViewMode("raw")}
            className={`flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-semibold transition-all ${
              viewMode === "raw"
                ? "bg-surface-raised text-foreground shadow-2xs"
                : "text-muted hover:text-foreground"
            }`}
          >
            <Code className="h-3 w-3" />
            <span>Raw</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-h-56 overflow-y-auto p-3">
        {viewMode === "raw" && (
          <pre className="font-mono text-[11px] leading-relaxed text-foreground whitespace-pre-wrap break-all p-1 bg-surface-raised/40 rounded border border-border/50">
            {JSON.stringify(parsedJson, null, 2)}
          </pre>
        )}

        {viewMode === "tree" && <JsonTree data={parsedJson} />}

        {viewMode === "visual" && (
          <div className="space-y-2.5">
            {/* If Selection is present */}
            {selection && (
              <div className="rounded-md border border-amber-300 bg-amber-50/80 p-3 text-xs text-amber-950 shadow-2xs">
                <div className="flex items-center justify-between font-bold">
                  <span className="flex items-center gap-1.5 text-amber-900">
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Model Selection</span>
                  </span>
                  <span className="font-mono rounded bg-amber-200/90 px-2 py-0.5 text-[10px] font-bold text-amber-950">
                    {selection.final_label || selection.final_kind}
                  </span>
                </div>
                {selection.rationale && (
                  <p className="mt-1.5 text-[11px] text-amber-900/90 leading-snug">
                    {selection.rationale}
                  </p>
                )}
              </div>
            )}

            {/* If Events list is present */}
            {events && Array.isArray(events) && events.length > 0 ? (
              <div className="space-y-2">
                {events.map((item: unknown, i: number) => {
                  if (typeof item === "string") {
                    const cleaned = cleanStr(item);
                    // Match pattern like "evt_1: a focal seizure monthly"
                    const colonIdx = cleaned.indexOf(":");
                    let idBadge = "";
                    let mainText = cleaned;
                    if (colonIdx > 0 && colonIdx < 15) {
                      idBadge = cleaned.slice(0, colonIdx).trim();
                      mainText = cleaned.slice(colonIdx + 1).trim();
                    }

                    return (
                      <div
                        key={i}
                        className="rounded-md border border-border bg-surface-raised/50 p-2.5 text-xs hover:border-border/90 transition-colors shadow-2xs"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-mono font-bold text-foreground text-[11.5px] leading-tight">
                            {mainText}
                          </span>
                          {idBadge && (
                            <span className="rounded bg-sky-100 text-sky-900 font-mono text-[9.5px] font-bold px-1.5 py-0.5 shrink-0">
                              {idBadge}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  }

                  const evt = item as Record<string, unknown>;
                  const eventId = String(evt.event_id || evt.id || `evt_${i + 1}`);
                  const val = String(evt.raw_value || evt.text || evt.concept || evt.anchor_text || JSON.stringify(evt));
                  const evidence = String(evt.evidence || "");
                  const timeWindow = evt.time_window ? String(evt.time_window) : null;
                  const appliesTo = evt.applies_to ? String(evt.applies_to) : evt.family ? String(evt.family) : null;

                  return (
                    <div
                      key={i}
                      className="rounded-md border border-border bg-surface-raised/50 p-2.5 text-xs hover:border-border/90 transition-colors shadow-2xs"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono font-bold text-foreground text-[11.5px] leading-tight truncate">
                          {val}
                        </span>
                        <div className="flex items-center gap-1 shrink-0">
                          {appliesTo && (
                            <span className="rounded bg-surface border border-border px-1.5 py-0.5 font-mono text-[9px] font-semibold text-muted uppercase">
                              {appliesTo}
                            </span>
                          )}
                          <span className="rounded bg-sky-100 text-sky-900 font-mono text-[9.5px] font-bold px-1.5 py-0.5">
                            {eventId}
                          </span>
                        </div>
                      </div>

                      {timeWindow && (
                        <div className="mt-1.5 flex items-center gap-1.5 text-[10px] text-muted font-medium">
                          <Clock className="h-3 w-3 shrink-0" />
                          <span>Window: {timeWindow}</span>
                        </div>
                      )}

                      {evidence && (
                        <div className="mt-1.5 flex items-start gap-1.5 text-[10.5px] text-muted italic bg-surface p-1.5 rounded border border-border/40">
                          <Quote className="h-3 w-3 shrink-0 mt-0.5 opacity-50" />
                          <span className="line-clamp-2 leading-tight">{evidence}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              // Generic Key-Value summary for non-event objects
              <div className="space-y-1">
                {Object.entries(parsedJson).map(([k, v]) => (
                  <div
                    key={k}
                    className="flex items-baseline justify-between gap-2 rounded-md border border-border/50 bg-surface-raised/40 px-2.5 py-1.5 text-xs"
                  >
                    <span className="font-mono text-[10px] font-bold text-muted uppercase">
                      {k}:
                    </span>
                    <span className="font-mono text-[11px] font-medium text-foreground truncate max-w-[200px]">
                      {typeof v === "object" ? JSON.stringify(v) : String(v)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
