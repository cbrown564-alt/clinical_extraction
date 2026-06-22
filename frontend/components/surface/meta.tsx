"use client";

import {
  FileText,
  BarChart3,
  Boxes,
  GalleryHorizontalEnd,
  type LucideIcon,
} from "lucide-react";
import type { DatasetTone, ExplorerSurface } from "@/lib/datasets";

/**
 * Single source of truth for the four review surfaces.
 *
 * The Navbar, the shared {@link SurfaceHeader}, and any cross-surface link pill
 * all read from here so a surface's name, icon, and accent tone never drift
 * between the chrome and the page. Datasets supply their own description copy;
 * everything structural lives in this registry.
 */
export interface SurfaceMeta {
  surface: ExplorerSurface;
  /** Human label, identical to the Navbar tab text. */
  label: string;
  /** Route segment (with leading slash). */
  href: string;
  /** Accent tone that tints the icon and active states. */
  tone: DatasetTone;
  Icon: LucideIcon;
}

export const SURFACE_META: Record<ExplorerSurface, SurfaceMeta> = {
  workbench: {
    surface: "workbench",
    label: "Example Explorer",
    href: "/workbench",
    tone: "deterministic",
    Icon: FileText,
  },
  observatory: {
    surface: "observatory",
    label: "Aggregate Performance",
    href: "/observatory",
    tone: "llm",
    Icon: BarChart3,
  },
  laboratory: {
    surface: "laboratory",
    label: "Component Impact",
    href: "/laboratory",
    tone: "deterministic-alt",
    Icon: Boxes,
  },
  gallery: {
    surface: "gallery",
    label: "Error Gallery",
    href: "/gallery",
    tone: "error",
    Icon: GalleryHorizontalEnd,
  },
};

/** Surfaces in canonical app-shell order. */
export const SURFACE_ORDER: ExplorerSurface[] = [
  "workbench",
  "observatory",
  "laboratory",
  "gallery",
];

/**
 * Active-state classes for a surface chip/tab (border + tinted bg + text).
 * Fixed per-tone strings so Tailwind can statically extract them.
 */
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

/** Icon-tile tint (soft tinted square) for a tone. */
export const SURFACE_TONE_ICON: Record<DatasetTone, string> = {
  deterministic: "bg-deterministic/10 text-deterministic",
  "deterministic-alt": "bg-deterministic-alt/10 text-deterministic-alt",
  llm: "bg-llm/10 text-llm",
  hybrid: "bg-hybrid/10 text-hybrid",
  success: "bg-success/10 text-success",
  error: "bg-error/10 text-error",
  muted: "bg-muted/10 text-muted",
};
