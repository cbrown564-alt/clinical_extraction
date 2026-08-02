"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Database, Microscope } from "lucide-react";
import { DATASET_PARAM, useActiveDataset, DEFAULT_DATASET, datasetSupports } from "@/lib/datasets";
import DatasetSwitcher from "@/components/shell/DatasetSwitcher";
import {
  APP_WORKFLOWS,
  destinationForPath,
  workflowForPath,
  type AppDestination,
} from "@/components/shell/workflows";

export default function Navbar() {
  const pathname = usePathname();
  const datasetId = useActiveDataset();

  // Preserve the active dataset across surface navigation. Bare Gan URLs stay
  // bare so existing links keep working.
  const datasetQuery =
    datasetId === DEFAULT_DATASET ? "" : `?${DATASET_PARAM}=${datasetId}`;
  const activeWorkflow = workflowForPath(pathname);
  const activeDestination = destinationForPath(pathname);

  function hrefFor(destination: Pick<AppDestination, "href" | "scope">) {
    return destination.scope === "dataset" ? `${destination.href}${datasetQuery}` : destination.href;
  }

  return (
    <header className="relative z-50 shrink-0 border-b border-border bg-surface shadow-sm">
      <div className="flex h-12 min-w-0 items-center gap-3 px-3 sm:px-4">
        <Link
          href={`/workbench${datasetQuery}`}
          className="flex min-w-0 shrink-0 items-center gap-2 rounded-md"
          aria-label="Clinical Extraction Explorer home"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-deterministic/10">
            <Microscope className="h-4 w-4 text-deterministic" />
          </div>
          <span className="hidden max-w-44 text-sm font-semibold leading-tight text-foreground lg:block">
            Clinical Extraction Explorer
          </span>
        </Link>

        <nav aria-label="Primary workflows" className="flex min-w-0 flex-1 items-center gap-1">
          {APP_WORKFLOWS.map((workflow) => {
            const active = workflow.id === activeWorkflow.id;
            const Icon = workflow.Icon;

            return (
              <Link
                key={workflow.id}
                href={`${workflow.href}${datasetQuery}`}
                aria-label={`${workflow.label} workflow`}
                aria-current={active ? "location" : undefined}
                className={`inline-flex min-h-9 items-center gap-1.5 rounded-md border px-2.5 py-2 text-xs font-semibold transition-colors sm:px-3 ${
                  active
                    ? "border-deterministic/25 bg-deterministic/10 text-deterministic"
                    : "border-transparent text-muted hover:bg-surface-raised hover:text-foreground"
                }`}
              >
                <Icon className="h-3.5 w-3.5" aria-hidden />
                <span className="hidden sm:inline">{workflow.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="shrink-0 border-l border-border pl-3">
          {activeDestination?.scope === "exectv2" ? (
            <ScopeBadge label="ExECTv2" detail="fixed" />
          ) : activeDestination?.scope === "cross-project" ? (
            <ScopeBadge label="Cross-project" detail="scope" />
          ) : (
            <DatasetSwitcher />
          )}
        </div>
      </div>

      <nav
        aria-label={`${activeWorkflow.label} tools`}
        className="flex h-10 min-w-0 items-center gap-1 overflow-x-auto border-t border-border/70 bg-surface-raised/45 px-3 sm:px-4"
      >
        <span className="mr-1 hidden shrink-0 text-[11px] font-semibold uppercase tracking-[0.08em] text-muted sm:inline">
          {activeWorkflow.label}
        </span>
        <span className="mr-1 hidden h-4 w-px shrink-0 bg-border sm:block" aria-hidden />
        {activeWorkflow.destinations
          .filter(
            (destination) =>
              destination.href !== "/laboratory" ||
              datasetSupports(datasetId, "laboratory")
          )
          .map((destination) => {
          const active = pathname === destination.href;
          const Icon = destination.Icon;
          return (
            <Link
              key={destination.href}
              href={hrefFor(destination)}
              aria-current={active ? "page" : undefined}
              className={`inline-flex min-h-8 shrink-0 items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-xs font-medium transition-colors ${
                active
                  ? "border-foreground/15 bg-surface text-foreground"
                  : "border-transparent text-muted hover:bg-surface hover:text-foreground"
              }`}
            >
              <Icon className="h-3.5 w-3.5" aria-hidden />
              {destination.label}
              {destination.scope === "exectv2" && (
                <span className="font-mono text-[11px] text-muted">ExECTv2</span>
              )}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}

function ScopeBadge({ label, detail }: { label: string; detail: string }) {
  return (
    <div className="flex min-h-9 items-center gap-2 rounded-md border border-border bg-surface-raised px-2.5 py-1.5">
      <Database className="h-3.5 w-3.5 shrink-0 text-muted" aria-hidden />
      <div className="hidden leading-tight sm:block">
        <span className="block text-[11px] font-semibold text-foreground">{label}</span>
        <span className="hidden text-[11px] text-muted sm:block">{detail}</span>
      </div>
    </div>
  );
}
