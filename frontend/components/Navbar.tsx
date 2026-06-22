"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Microscope, FileCheck } from "lucide-react";
import { DATASET_PARAM, useActiveDataset, DEFAULT_DATASET } from "@/lib/datasets";
import DatasetSwitcher from "@/components/shell/DatasetSwitcher";
import { SURFACE_META, SURFACE_ORDER, SURFACE_TONE_ACTIVE } from "@/components/surface";

const navItems = SURFACE_ORDER.map((surface) => SURFACE_META[surface]);

export default function Navbar() {
  const pathname = usePathname();
  const datasetId = useActiveDataset();

  // Preserve the active dataset across surface navigation. Bare Gan URLs stay
  // bare so existing links keep working.
  const datasetQuery =
    datasetId === DEFAULT_DATASET ? "" : `?${DATASET_PARAM}=${datasetId}`;

  return (
    <nav className="shrink-0 border-b border-border bg-surface px-4 py-2 shadow-sm z-50">
      <div className="flex items-center justify-between gap-3">
        {/* Brand */}
        <Link href="/workbench" className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-deterministic/10">
            <Microscope className="h-3.5 w-3.5 text-deterministic" />
          </div>
          <span className="text-sm font-semibold text-foreground leading-none">
            Clinical Extraction Explorer
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1.5">
          {navItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.Icon;

            return (
              <Link
                key={item.href}
                href={`${item.href}${datasetQuery}`}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-medium transition-colors border ${
                  active
                    ? SURFACE_TONE_ACTIVE[item.tone]
                    : "text-muted border-transparent hover:bg-surface-raised hover:text-foreground"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {item.label}
              </Link>
            );
          })}
          <div className="w-px h-4 bg-border mx-1" />
          <Link
            href="/gold-audit"
            className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-[10px] font-medium transition-colors ${
              pathname === "/gold-audit"
                ? "text-success bg-success/10 border border-success/20"
                : "text-muted border-transparent hover:text-foreground hover:bg-surface-raised"
            }`}
          >
            <FileCheck className="h-3 w-3" />
            Audit
          </Link>

          {/* Sticky dataset context selector */}
          <div className="w-px h-4 bg-border mx-1" />
          <DatasetSwitcher />
        </div>
      </div>
    </nav>
  );
}
