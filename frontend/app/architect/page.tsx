"use client";

import { Suspense } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Workflow, ArrowLeft } from "lucide-react";
import Palette from "@/components/architect/Palette";
import NodeDrawer from "@/components/architect/NodeDrawer";
import ConfigExporter from "@/components/architect/ConfigExporter";
import ComparisonBar from "@/components/architect/ComparisonBar";

// React Flow must be loaded client-side only
const PipelineCanvas = dynamic(
  () => import("@/components/architect/PipelineCanvas"),
  { ssr: false }
);

function ArchitectInner() {
  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-5 py-2.5 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-raised border border-border text-muted hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-hybrid/10">
            <Workflow className="h-4 w-4 text-hybrid" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground leading-tight">
              Clinical Extraction Observatory
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-muted border border-border">
                Architect
              </span>
              <span className="text-[10px] text-muted">
                Phase 2 — Pipeline Composer
              </span>
            </div>
          </div>
        </div>
        <ConfigExporter />
      </header>

      {/* Comparison bar */}
      <ComparisonBar />

      {/* Main workspace */}
      <div className="flex flex-1 overflow-hidden">
        <Palette />
        <PipelineCanvas />
        <NodeDrawer />
      </div>
    </div>
  );
}

export default function ArchitectPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading architect…</p>
          </div>
        </div>
      }
    >
      <ArchitectInner />
    </Suspense>
  );
}
