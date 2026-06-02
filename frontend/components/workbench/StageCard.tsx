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
    <Collapsible.Root open={isExpanded} onOpenChange={(open) => {
      if (open !== isExpanded) onToggleExpand();
    }}>
      <div
        className={`rounded-lg border transition-colors ${
          isActive
            ? "border-deterministic/40 bg-surface shadow-sm"
            : "border-border bg-surface/50"
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
            className={`h-2.5 w-2.5 rounded-full ${stageDotColor[stage]} ${
              isActive ? "ring-2 ring-offset-1 ring-deterministic/30" : ""
            }`}
          />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold uppercase tracking-wide text-foreground">
                {label}
              </span>
              {badge && (
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    badgeColor ?? "bg-surface-raised text-muted"
                  }`}
                >
                  {badge}
                </span>
              )}
            </div>
            <p className="text-xs text-muted">{description}</p>
          </div>
          <Collapsible.Trigger asChild onClick={(e) => { e.stopPropagation(); onToggleExpand(); }}>
            <button className="rounded p-1 hover:bg-surface-raised">
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
