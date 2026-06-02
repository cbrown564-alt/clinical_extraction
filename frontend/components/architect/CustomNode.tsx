"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import type { NodeFamily } from "@/lib/types";
import { useArchitectStore } from "@/lib/stores";

const familyColors: Record<NodeFamily, { bg: string; border: string; text: string; ring: string }> = {
  rules_only: {
    bg: "bg-deterministic/10",
    border: "border-deterministic",
    text: "text-deterministic",
    ring: "ring-deterministic/30",
  },
  llm_only: {
    bg: "bg-llm/10",
    border: "border-llm",
    text: "text-llm",
    ring: "ring-llm/30",
  },
  hybrid: {
    bg: "bg-hybrid/10",
    border: "border-hybrid",
    text: "text-hybrid",
    ring: "ring-hybrid/30",
  },
};

interface CustomNodeData extends Record<string, unknown> {
  family: NodeFamily;
  label: string;
}

type CustomNodeType = Node<CustomNodeData, "custom">;

function CustomNodeComponent({ id, data, selected }: NodeProps<CustomNodeType>) {
  const setSelectedNodeId = useArchitectStore((s) => s.setSelectedNodeId);
  const colors = familyColors[(data.family as NodeFamily) ?? "rules_only"];

  return (
    <div
      className={`relative rounded-xl border-2 px-5 py-3 min-w-[140px] text-center shadow-sm transition-all cursor-pointer
        ${colors.bg} ${colors.border} ${selected ? `ring-2 ${colors.ring}` : "hover:shadow-md"}
      `}
      onClick={() => setSelectedNodeId(id)}
    >
      <Handle type="target" position={Position.Left} className="!bg-muted !w-2.5 !h-2.5" />
      <div className={`text-[11px] font-semibold uppercase tracking-wider ${colors.text}`}>
        {data.label as string}
      </div>
      <div className="mt-1 text-[10px] text-muted font-mono capitalize">
        {(data.family as string).replace("_", " ")}
      </div>
      {/* Activity ring indicator */}
      <div className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-surface border border-border shadow-sm">
        <div className={`h-2 w-2 rounded-full ${(data.family as string) === "rules_only" ? "bg-deterministic" : (data.family as string) === "llm_only" ? "bg-llm" : "bg-hybrid"}`} />
      </div>
      <Handle type="source" position={Position.Right} className="!bg-muted !w-2.5 !h-2.5" />
    </div>
  );
}

export default memo(CustomNodeComponent);
