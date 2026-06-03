"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Microscope, FlaskConical, LayoutGrid } from "lucide-react";

const navItems = [
  { href: "/workbench", label: "Workbench", color: "deterministic" },
  { href: "/architect", label: "Architect", color: "hybrid" },
  { href: "/observatory", label: "Observatory", color: "llm" },
  { href: "/laboratory", label: "Laboratory", color: "deterministic-alt" },
  { href: "/gallery", label: "Gallery", color: "error" },
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
            Clinical Extraction Observatory
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1.5">
          {navItems.map((item) => {
            const active = pathname === item.href;
            const colorClass =
              item.color === "deterministic"
                ? "bg-deterministic/10 text-deterministic border-deterministic/20"
                : item.color === "hybrid"
                ? "bg-hybrid/10 text-hybrid border-hybrid/20"
                : item.color === "llm"
                ? "bg-llm/10 text-llm border-llm/20"
                : item.color === "deterministic-alt"
                ? "bg-deterministic-alt/10 text-deterministic-alt border-deterministic-alt/20"
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
        </div>
      </div>
    </nav>
  );
}
