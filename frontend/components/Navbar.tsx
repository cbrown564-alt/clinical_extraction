"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Microscope, FileCheck } from "lucide-react";

const navItems = [
  { href: "/workbench", label: "Example Explorer", color: "deterministic" },
  { href: "/exectv2", label: "ExECTv2", color: "hybrid" },
  { href: "/observatory", label: "Aggregate Performance", color: "llm" },
  { href: "/laboratory", label: "Component Impact", color: "deterministic-alt" },
  { href: "/gallery", label: "Error Gallery", color: "error" },
] as const;

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="shrink-0 border-b border-border bg-surface px-4 py-2 shadow-sm z-50">
      <div className="flex items-center justify-between">
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
            const colorClass =
              item.color === "deterministic"
                ? "bg-deterministic/10 text-deterministic border-deterministic/20"
                : item.color === "llm"
                ? "bg-llm/10 text-llm border-llm/20"
                : item.color === "deterministic-alt"
                ? "bg-deterministic-alt/10 text-deterministic-alt border-deterministic-alt/20"
                : item.color === "hybrid"
                ? "bg-hybrid/10 text-hybrid border-hybrid/20"
                : item.color === "error"
                ? "bg-error/10 text-error border-error/20"
                  : "bg-muted/10 text-muted border-muted/20";

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-colors border ${
                  active
                    ? colorClass
                    : "text-muted border-transparent hover:bg-surface-raised hover:text-foreground"
                }`}
              >
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
        </div>
      </div>
    </nav>
  );
}
