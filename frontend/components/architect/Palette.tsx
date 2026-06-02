"use client";

import { GitBranch, Layers, Settings2, Wrench, Award } from "lucide-react";
import type { ArchitectNodeType, NodeFamily } from "@/lib/types";

interface PaletteItem {
  type: ArchitectNodeType;
  label: string;
  icon: React.ReactNode;
  defaultFamily: NodeFamily;
}

const items: PaletteItem[] = [
  { type: "extractor", label: "Extractor", icon: <GitBranch className="h-4 w-4" />, defaultFamily: "rules_only" },
  { type: "normaliser", label: "Normaliser", icon: <Layers className="h-4 w-4" />, defaultFamily: "rules_only" },
  { type: "selector", label: "Selector", icon: <Settings2 className="h-4 w-4" />, defaultFamily: "hybrid" },
  { type: "repair", label: "Repair", icon: <Wrench className="h-4 w-4" />, defaultFamily: "rules_only" },
  { type: "scorer", label: "Scorer", icon: <Award className="h-4 w-4" />, defaultFamily: "rules_only" },
];

const familyBadges: Record<NodeFamily, string> = {
  rules_only: "bg-deterministic/10 text-deterministic border-deterministic/20",
  llm_only: "bg-llm/10 text-llm border-llm/20",
  hybrid: "bg-hybrid/10 text-hybrid border-hybrid/20",
};

export default function Palette() {
  const onDragStart = (event: React.DragEvent, item: PaletteItem) => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify(item)
    );
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className="w-56 border-r border-border bg-surface flex flex-col h-full">
      <div className="border-b border-border px-4 py-3">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Palette
        </h3>
        <p className="text-[10px] text-muted mt-0.5">Drag nodes to the canvas</p>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {items.map((item) => (
          <div
            key={item.type}
            draggable
            onDragStart={(e) => onDragStart(e, item)}
            className="cursor-grab active:cursor-grabbing rounded-lg border border-border bg-surface-raised p-3 shadow-sm transition-all hover:shadow-md hover:border-deterministic/30"
          >
            <div className="flex items-center gap-2">
              <div className="text-muted">{item.icon}</div>
              <span className="text-xs font-medium text-foreground">{item.label}</span>
            </div>
            <div className="mt-1.5 flex items-center gap-1.5">
              <span
                className={`inline-flex rounded px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide border ${familyBadges[item.defaultFamily]}`}
              >
                {item.defaultFamily.replace("_", " ")}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
