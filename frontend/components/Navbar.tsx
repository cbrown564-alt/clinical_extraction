"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Database, Microscope } from "lucide-react";
import { DATASET_PARAM, useActiveDataset, DEFAULT_DATASET } from "@/lib/datasets";
import DatasetSwitcher from "@/components/shell/DatasetSwitcher";
import {
  APP_DESTINATIONS,
  destinationForPath,
  type AppDestination,
} from "@/components/shell/workflows";

export default function Navbar() {
  const pathname = usePathname();
  const datasetId = useActiveDataset();

  // Preserve the active dataset across surface navigation. Bare Gan URLs stay
  // bare so existing links keep working.
  const datasetQuery =
    datasetId === DEFAULT_DATASET ? "" : `?${DATASET_PARAM}=${datasetId}`;
  const activeDestination = destinationForPath(pathname);

  function hrefFor(destination: Pick<AppDestination, "href" | "scope">) {
    return destination.scope === "dataset" ? `${destination.href}${datasetQuery}` : destination.href;
  }

  return (
    <header className="relative z-50 shrink-0 border-b border-border bg-surface">
      <div className="flex h-10 min-w-0 items-center gap-3 px-3 sm:px-4">
        <Link
          href={`/workbench${datasetQuery}`}
          className="flex min-w-0 shrink-0 items-center gap-1.5 rounded-md"
          aria-label="Clinical Extraction Explorer home"
        >
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-deterministic/10">
            <Microscope className="h-3.5 w-3.5 text-deterministic" />
          </div>
          <span className="hidden text-xs font-semibold text-foreground xl:block">
            Explorer
          </span>
        </Link>

        <span className="hidden h-4 w-px shrink-0 bg-border sm:block" aria-hidden />

        <nav
          aria-label="Main navigation"
          className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto"
        >
          {APP_DESTINATIONS.map((destination) => {
            const active = pathname === destination.href || activeDestination?.href === destination.href;
            const Icon = destination.Icon;
            return (
              <Link
                key={destination.href}
                href={hrefFor(destination)}
                aria-current={active ? "page" : undefined}
                className={`inline-flex min-h-7 shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                  active
                    ? "bg-deterministic/10 font-semibold text-deterministic"
                    : "text-muted hover:bg-surface-raised hover:text-foreground"
                }`}
              >
                <Icon className="h-3.5 w-3.5" aria-hidden />
                {destination.label}
              </Link>
            );
          })}
        </nav>

        <div className="shrink-0 border-l border-border pl-2">
          {activeDestination?.scope === "exectv2" ? (
            <ScopeBadge label="ExECTv2" />
          ) : (
            <DatasetSwitcher />
          )}
        </div>
      </div>
    </header>
  );
}

function ScopeBadge({ label }: { label: string }) {
  return (
    <div className="flex min-h-7 items-center gap-1.5 rounded-md px-2 py-1 text-xs">
      <Database className="h-3.5 w-3.5 shrink-0 text-muted" aria-hidden />
      <span className="hidden font-medium text-foreground sm:inline">{label}</span>
    </div>
  );
}

