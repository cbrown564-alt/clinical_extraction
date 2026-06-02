"use client";

import { ChevronDown, ChevronRight } from "lucide-react";
import * as Collapsible from "@radix-ui/react-collapsible";
import type { ActiveStage } from "@/lib/types";

interface StageCardProps {
  stage: ActiveStage;
  label: string;
  description: string;
  isActive: boolean;
  isExpanded: boolean;
  onActivate: () => void;
  onToggleExpand: () => void;
  children?: React.ReactNode;
  badge?: string;
  badgeColor?: string;
}

const stageDotColor: Record<ActiveStage, string> = {
  raw: "bg-muted",
  extract: "bg-deterministic",
  normalise: "bg-deterministic-alt",
  select: "bg-hybrid",
  score: "bg-success",
};

export default function StageCard({
  stage,
  label,
  description,
  isActive,
  isExpanded,
  onActivate,
  onToggleExpand,
  children,
  badge,
  badgeColor,
}: StageCardProps) {
  return (
    <Collapsible.Root
      open={isExpanded}
      onOpenChange={(open) => {
        if (open !== isExpanded) onToggleExpand();
      }}
    >
      <div
        className={`rounded-xl border transition-all duration-200 ${
          isActive
            ? "border-deterministic/30 bg-surface shadow-md"
            : "border-border bg-surface/40 shadow-sm hover:shadow"
        }`}
      >
        <button
          onClick={() => {
            onActivate();
            if (!isExpanded) onToggleExpand();
          }}
          className="flex w-full items-center gap-3 p-3 text-left"
        >
          <span
            className={`h-2.5 w-2.5 rounded-full ${stageDotColor[stage]} shrink-0 ${
              isActive ? "ring-2 ring-offset-1 ring-deterministic/20" : ""
            }`}
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold uppercase tracking-wide text-foreground">
                {label}
              </span>
              {badge && (
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium truncate max-w-[140px] ${
                    badgeColor ?? "bg-surface-raised text-muted border border-border"
                  }`}
                >
                  {badge}
                </span>
              )}
            </div>
            <p className="text-[11px] text-muted mt-0.5">{description}</p>
          </div>
          <Collapsible.Trigger
            asChild
            onClick={(e) => {
              e.stopPropagation();
              onToggleExpand();
            }}
          >
            <button className="rounded-lg p-1.5 hover:bg-surface-raised transition-colors shrink-0">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-muted" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted" />
              )}
            </button>
          </Collapsible.Trigger>
        </button>
        <Collapsible.Content>
          <div className="border-t border-border px-3 pb-3 pt-2">{children}</div>
        </Collapsible.Content>
      </div>
    </Collapsible.Root>
  );
}
