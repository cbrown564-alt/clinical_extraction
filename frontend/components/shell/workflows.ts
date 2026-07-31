import type { LucideIcon } from "lucide-react";
import {
  AlertTriangle,
  BarChart3,
  Boxes,
  ClipboardCheck,
  FileCheck,
  FileText,
  GalleryHorizontalEnd,
  Gauge,
  Search,
  ShieldCheck,
} from "lucide-react";

export type WorkflowId = "inspect" | "evaluate" | "assure";
export type DestinationScope = "dataset" | "exectv2" | "cross-project";

export interface AppDestination {
  href: string;
  label: string;
  scope: DestinationScope;
  Icon: LucideIcon;
}

export interface AppWorkflow {
  id: WorkflowId;
  label: string;
  href: string;
  Icon: LucideIcon;
  destinations: AppDestination[];
}

export const APP_WORKFLOWS: AppWorkflow[] = [
  {
    id: "inspect",
    label: "Inspect",
    href: "/workbench",
    Icon: Search,
    destinations: [
      { href: "/workbench", label: "Examples", scope: "dataset", Icon: FileText },
      { href: "/gallery", label: "Errors", scope: "dataset", Icon: GalleryHorizontalEnd },
      { href: "/exectv2-sf-inspection", label: "SF deep dive", scope: "exectv2", Icon: Gauge },
    ],
  },
  {
    id: "evaluate",
    label: "Evaluate",
    href: "/observatory",
    Icon: BarChart3,
    destinations: [
      { href: "/observatory", label: "Runs", scope: "dataset", Icon: BarChart3 },
      { href: "/laboratory", label: "Components", scope: "dataset", Icon: Boxes },
      {
        href: "/reliability-scorecard",
        label: "Reliability",
        scope: "dataset",
        Icon: ShieldCheck,
      },
    ],
  },
  {
    id: "assure",
    label: "Assure",
    href: "/gold-audit",
    Icon: ShieldCheck,
    destinations: [
      { href: "/gold-audit", label: "Gold audit", scope: "dataset", Icon: FileCheck },
      {
        href: "/clinical-review",
        label: "Clinical review",
        scope: "exectv2",
        Icon: ClipboardCheck,
      },
      {
        href: "/gold-noise",
        label: "Gold evidence",
        scope: "cross-project",
        Icon: AlertTriangle,
      },
    ],
  },
];

export function workflowForPath(pathname: string): AppWorkflow {
  if (["/clinical-review", "/qualified-review", "/semantic-support-review"].includes(pathname)) {
    return APP_WORKFLOWS.find((workflow) => workflow.id === "assure") ?? APP_WORKFLOWS[0];
  }
  return (
    APP_WORKFLOWS.find((workflow) =>
      workflow.destinations.some((destination) => destination.href === pathname)
    ) ?? APP_WORKFLOWS[0]
  );
}

export function destinationForPath(pathname: string): AppDestination | undefined {
  return APP_WORKFLOWS.flatMap((workflow) => workflow.destinations).find(
    (destination) => destination.href === pathname
  );
}
