"use client";

import {
  FileText,
  type LucideIcon,
} from "lucide-react";
import type { DatasetTone, ExplorerSurface } from "@/lib/datasets";

export interface SurfaceMeta {
  surface: ExplorerSurface;
  label: string;
  href: string;
  tone: DatasetTone;
  Icon: LucideIcon;
}

export const SURFACE_META: Record<ExplorerSurface, SurfaceMeta> = {
  workbench: {
    surface: "workbench",
    label: "Workbench",
    href: "/workbench",
    tone: "deterministic",
    Icon: FileText,
  },
};

export const SURFACE_ORDER: ExplorerSurface[] = ["workbench"];

export const SURFACE_TONE_ACTIVE: Record<DatasetTone, string> = {
  deterministic: "bg-deterministic/10 text-deterministic border-deterministic/20",
  "deterministic-alt":
    "bg-deterministic-alt/10 text-deterministic-alt border-deterministic-alt/20",
  llm: "bg-llm/10 text-llm border-llm/20",
  hybrid: "bg-hybrid/10 text-hybrid border-hybrid/20",
  success: "bg-success/10 text-success border-success/20",
  error: "bg-error/10 text-error border-error/20",
  muted: "bg-muted/10 text-muted border-muted/20",
};

export const SURFACE_TONE_ICON: Record<DatasetTone, string> = {
  deterministic: "bg-deterministic/10 text-deterministic",
  "deterministic-alt": "bg-deterministic-alt/10 text-deterministic-alt",
  llm: "bg-llm/10 text-llm",
  hybrid: "bg-hybrid/10 text-hybrid",
  success: "bg-success/10 text-success",
  error: "bg-error/10 text-error",
  muted: "bg-muted/10 text-muted",
};
