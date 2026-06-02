"use client";

import { useState } from "react";
import { Download, Check, Copy } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";

export default function ConfigExporter() {
  const nodes = useArchitectStore((s) => s.nodes);
  const [copied, setCopied] = useState(false);

  const exportJson = () => {
    const payload = {
      name: `architecture-${new Date().toISOString().slice(0, 10)}`,
      version: "1.0",
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        label: n.label,
        family: n.family,
        pipelineFamily: n.pipelineFamily,
        ablationConfig: n.ablationConfig,
      })),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${payload.name}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    const payload = {
      name: `architecture-${new Date().toISOString().slice(0, 10)}`,
      version: "1.0",
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        label: n.label,
        family: n.family,
        pipelineFamily: n.pipelineFamily,
        ablationConfig: n.ablationConfig,
      })),
    };
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={copyToClipboard}
        className="flex items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-2 text-xs font-medium text-foreground shadow-sm transition-all hover:bg-surface-raised hover:shadow"
        title="Copy config JSON"
      >
        {copied ? <Check className="h-3.5 w-3.5 text-success" /> : <Copy className="h-3.5 w-3.5 text-muted" />}
        <span>{copied ? "Copied" : "Copy JSON"}</span>
      </button>
      <button
        onClick={exportJson}
        className="flex items-center gap-1.5 rounded-lg bg-deterministic px-3 py-2 text-xs font-medium text-white shadow-sm transition-all hover:bg-deterministic/90 hover:shadow active:scale-[0.98]"
      >
        <Download className="h-3.5 w-3.5" />
        <span>Export Config</span>
      </button>
    </div>
  );
}
