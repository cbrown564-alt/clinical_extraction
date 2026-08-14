import type { LucideIcon } from "lucide-react";
import { CheckCircle2, FileCheck, FileText } from "lucide-react";

export type DestinationScope = "dataset" | "exectv2";

export interface AppDestination {
  href: string;
  label: string;
  scope: DestinationScope;
  Icon: LucideIcon;
}

export const APP_DESTINATIONS: AppDestination[] = [
  {
    href: "/workbench",
    label: "Workbench",
    scope: "dataset",
    Icon: FileText,
  },
  {
    href: "/gold-audit",
    label: "Gold audit",
    scope: "dataset",
    Icon: FileCheck,
  },
  {
    href: "/semantic-support-review",
    label: "Semantic support",
    scope: "exectv2",
    Icon: CheckCircle2,
  },
];

export function destinationForPath(pathname: string): AppDestination | undefined {
  if (pathname === "/clinical-review") {
    return APP_DESTINATIONS.find((dest) => dest.href === "/semantic-support-review");
  }
  return APP_DESTINATIONS.find((dest) => dest.href === pathname);
}

