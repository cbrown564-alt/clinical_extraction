"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { FileText, Tag } from "lucide-react";
import LetterRenderer from "@/components/surface/LetterRenderer";
import {
  ControlBar,
  ControlField,
  ExplorerBody,
  LensStrip,
  LetterPicker,
  SurfaceError,
  SurfaceLayout,
  SurfaceLoading,
  type HighlightTone,
  type LensItem,
} from "@/components/surface";
import { EXECTV2_FAMILIES } from "@/lib/datasets";
import { fetchGanInventory } from "@/lib/api";
import { useLetter } from "@/lib/hooks";
import { preserveWorkbenchDataset } from "@/lib/architectUrl";
import {
  GAN_INVENTORY_VIEW,
  INVENTORY_DISPLAY_FAMILIES,
  compactInventoryFact,
  inventoryEvidenceSpans,
  isInventoryDisplayFamily,
  resolveInventoryRow,
  type GanInventoryDisplayFamily,
  type GanInventoryMention,
} from "@/lib/ganInventory";
import { mergeFamilyHighlights } from "@/lib/letterHighlights";
import { attributeRank, inventoryCardAttributeKeys } from "@/lib/attributeOrder";
import { useArchitectStore } from "@/lib/stores";

const FAMILY_TONE = Object.fromEntries(
  EXECTV2_FAMILIES.map((family) => [family.id, family.tone as HighlightTone])
) as Record<string, HighlightTone>;

type FamilyFilter = GanInventoryDisplayFamily | "all";

function familyTone(entity: string): HighlightTone {
  return FAMILY_TONE[entity] ?? "no-reference";
}

function familyLabel(family: string): string {
  return EXECTV2_FAMILIES.find((item) => item.id === family)?.label ?? family;
}

function familyToneName(family: string) {
  return EXECTV2_FAMILIES.find((item) => item.id === family)?.tone ?? "muted";
}

function familyTextClass(family: string): string {
  switch (familyToneName(family)) {
    case "deterministic":
      return "text-deterministic";
    case "deterministic-alt":
      return "text-deterministic-alt";
    case "llm":
      return "text-llm";
    case "success":
      return "text-success";
    case "hybrid":
      return "text-hybrid";
    default:
      return "text-foreground";
  }
}

function familyTint(family: string): string {
  switch (familyToneName(family)) {
    case "deterministic":
      return "border-deterministic/25 bg-deterministic/8";
    case "llm":
      return "border-llm/25 bg-llm/8";
    case "success":
      return "border-success/25 bg-success/10";
    case "deterministic-alt":
      return "border-deterministic-alt/25 bg-deterministic-alt/8";
    case "hybrid":
      return "border-hybrid/25 bg-hybrid/8";
    default:
      return "border-border bg-surface";
  }
}

export function GanInventoryExplorer() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const sourceRowIndex = useArchitectStore((state) => state.sourceRowIndex);
  const setSourceRowIndex = useArchitectStore((state) => state.setSourceRowIndex);
  const workbenchView = useArchitectStore((state) => state.workbenchView);
  const setWorkbenchView = useArchitectStore((state) => state.setWorkbenchView);
  const [activeFamily, setActiveFamily] = useState<FamilyFilter>("all");
  const panelQuery = useQuery({
    queryKey: ["paper", "gan", "inventory"],
    queryFn: fetchGanInventory,
    staleTime: Infinity,
  });

  const sampled = panelQuery.data?.selected_source_row_indices ?? [];
  const fallback =
    panelQuery.data?.illustration_source_row_indices[0] ?? sampled[0] ?? 2748;
  const selectedRow = resolveInventoryRow(sourceRowIndex, sampled, fallback);
  const letterRecord = panelQuery.data?.letters.find(
    (letter) => letter.source_row_index === selectedRow
  );
  const noteQuery = useLetter("gan2026", sampled.length ? String(selectedRow) : null);

  useEffect(() => {
    if (!sampled.length) return;
    if (sourceRowIndex !== selectedRow) {
      setSourceRowIndex(selectedRow);
    }
  }, [sampled.length, selectedRow, setSourceRowIndex, sourceRowIndex]);

  useEffect(() => {
    if (workbenchView !== "inventory") return;
    if (!sampled.length) return;
    const params = new URLSearchParams();
    preserveWorkbenchDataset(params, searchParams);
    params.set("view", GAN_INVENTORY_VIEW);
    params.set("row", String(selectedRow));
    const next = `${pathname}?${params.toString()}`;
    const current = `${pathname}?${searchParams.toString()}`;
    if (next !== current) {
      router.replace(next, { scroll: false });
    }
  }, [pathname, router, sampled.length, searchParams, selectedRow, workbenchView]);

  const mentions = useMemo(() => {
    const visible = (letterRecord?.mentions ?? []).filter((mention) =>
      isInventoryDisplayFamily(mention.entity)
    );
    if (activeFamily === "all") return visible;
    return visible.filter((mention) => mention.entity === activeFamily);
  }, [activeFamily, letterRecord]);

  const noteText = noteQuery.data?.note_text ?? "";
  const highlights = useMemo(
    () =>
      mergeFamilyHighlights(inventoryEvidenceSpans(mentions, noteText), noteText).map(
        (span) => ({
          start: span.start,
          end: span.end,
          kind: familyTone(span.entity),
          label: span.label,
        })
      ),
    [mentions, noteText]
  );

  const letterItems = useMemo(
    () =>
      sampled.map((index) => ({
        value: String(index),
        label: String(index),
      })),
    [sampled]
  );

  const lensItems = useMemo((): LensItem[] => {
    const visible = (letterRecord?.mentions ?? []).filter((mention) =>
      isInventoryDisplayFamily(mention.entity)
    );
    return [
      {
        id: "all",
        label: "All families",
        count: visible.length,
        tone: "foreground",
        fixed: true,
      },
      ...INVENTORY_DISPLAY_FAMILIES.map((familyId) => {
        const family = EXECTV2_FAMILIES.find((item) => item.id === familyId);
        return {
          id: familyId,
          label: family?.label ?? familyId,
          count: visible.filter((mention) => mention.entity === familyId).length,
          tone: family?.tone ?? "muted",
        };
      }),
    ];
  }, [letterRecord]);

  if (panelQuery.isLoading) {
    return <SurfaceLoading message="Loading the 100-letter inventory…" />;
  }
  if (panelQuery.error || !panelQuery.data) {
    return (
      <SurfaceError
        title="Inventory panel failed to load"
        detail={String(panelQuery.error ?? "The frozen 100-letter artifact is not available.")}
      />
    );
  }

  return (
    <SurfaceLayout variant="fill">
      <ControlBar
        left={
          <>
            <ControlField label="Letter" htmlFor="gan-inventory-row" icon={<FileText className="h-3 w-3 text-muted" />}>
              <LetterPicker
                id="gan-inventory-row"
                items={letterItems}
                value={String(selectedRow)}
                onChange={(next) => setSourceRowIndex(next ? Number(next) : selectedRow)}
                placeholder="Letter…"
                className="min-w-0 flex-1 sm:min-w-[160px] sm:flex-none"
              />
            </ControlField>
            <p className="max-w-xl text-[11px] leading-4 text-muted">
              {panelQuery.data.claim_boundary}
            </p>
          </>
        }
        right={
          <button
            type="button"
            onClick={() => {
              setWorkbenchView("frequency");
              const params = new URLSearchParams();
              preserveWorkbenchDataset(params, searchParams);
              params.set("row", String(selectedRow));
              router.replace(`${pathname}?${params.toString()}`, { scroll: false });
            }}
            className="inline-flex min-h-8 items-center rounded-md border border-border bg-surface px-2.5 text-xs font-medium text-foreground hover:bg-surface-raised"
          >
            Frequency extraction
          </button>
        }
      />
      <LensStrip
        items={lensItems}
        activeId={activeFamily}
        onSelect={(id) => setActiveFamily(id as FamilyFilter)}
      />
      <ExplorerBody
        sourceLabel="Letter"
        sourceMeta={
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-muted uppercase tracking-wide">dev750</span>
            <span className="rounded border border-border bg-surface-raised px-1 py-0 font-mono text-[11px] text-muted">
              letter {selectedRow}
            </span>
            {noteQuery.data?.gold_label && (
              <span className="flex items-center gap-1 text-[11px] text-gold-ghost">
                <Tag className="h-3 w-3" />
                Frequency gold · {noteQuery.data.gold_label}
              </span>
            )}
            <span className="text-[11px] text-muted">
              {panelQuery.data.sample_size} sampled letters · emitted facts only
            </span>
          </div>
        }
        source={
          noteQuery.isLoading ? (
            <p className="text-sm text-muted">Loading letter…</p>
          ) : (
            <LetterRenderer text={noteText} highlights={highlights} />
          )
        }
        inspector={
          <InventoryInspector mentions={mentions} activeFamily={activeFamily} />
        }
      />
    </SurfaceLayout>
  );
}

function InventoryInspector({
  mentions,
  activeFamily,
}: {
  mentions: GanInventoryMention[];
  activeFamily: FamilyFilter;
}) {
  const [form, setForm] = useState<"schema" | "simple">("schema");
  const families =
    activeFamily === "all" ? INVENTORY_DISPLAY_FAMILIES : [activeFamily];
  const grouped = families.map((family) => ({
    family,
    items: mentions.filter((mention) => mention.entity === family),
  }));

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-start justify-between gap-3 border-b border-border px-4 py-2">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Emitted inventory
          </p>
          <p className="mt-1 text-[11px] leading-4 text-muted">
            Frozen ExECT-style program. These facts are not scored and have no
            inventory reference labels.
          </p>
        </div>
        <div className="flex shrink-0 items-center rounded-md border border-border bg-surface-raised p-0.5 text-[11px]">
          <button
            type="button"
            onClick={() => setForm("schema")}
            className={`rounded px-2 py-0.5 font-medium transition-colors ${
              form === "schema"
                ? "bg-surface font-semibold text-foreground shadow-xs"
                : "text-muted hover:text-foreground"
            }`}
          >
            Schema
          </button>
          <button
            type="button"
            onClick={() => setForm("simple")}
            className={`rounded px-2 py-0.5 font-medium transition-colors ${
              form === "simple"
                ? "bg-surface font-semibold text-foreground shadow-xs"
                : "text-muted hover:text-foreground"
            }`}
          >
            Simple
          </button>
        </div>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {grouped.map(({ family, items }) => (
          <section
            key={family}
            className={`overflow-hidden rounded-md border ${familyTint(family)}`}
          >
            <header className="flex items-center justify-between border-b border-border/60 bg-surface px-3 py-2">
              <h3 className="text-xs font-semibold text-foreground">{familyLabel(family)}</h3>
              <span className="font-mono text-[11px] text-muted">{items.length}</span>
            </header>
            {items.length === 0 ? (
              <p className="bg-surface/50 py-3 text-center text-xs text-muted">
                No emitted facts
              </p>
            ) : form === "simple" ? (
              <ul className="divide-y divide-border/50 bg-surface">
                {items.map((mention, index) => (
                  <li key={`${family}:${index}:${mention.text}`}>
                    <InventorySimpleRow mention={mention} />
                  </li>
                ))}
              </ul>
            ) : (
              <div className="space-y-2 bg-surface/50 p-3">
                {items.map((mention, index) => (
                  <InventoryFactCard
                    key={`${family}:${index}:${mention.text}`}
                    mention={mention}
                  />
                ))}
              </div>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}

function InventorySimpleRow({ mention }: { mention: GanInventoryMention }) {
  const fact = compactInventoryFact(mention);
  return (
    <div className="px-3 py-2">
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
        <span className="text-xs font-semibold text-foreground">{fact.identity}</span>
        {fact.clinical && (
          <span className={`text-xs font-medium ${familyTextClass(mention.entity)}`}>
            {fact.clinical}
          </span>
        )}
      </div>
      <p className="mt-0.5 line-clamp-2 text-[11px] italic leading-snug text-muted">
        {fact.evidence}
      </p>
    </div>
  );
}

function InventoryFactCard({ mention }: { mention: GanInventoryMention }) {
  const keys = inventoryCardAttributeKeys(mention.attributes, mention.entity);
  return (
    <article className="rounded-md border border-border bg-surface p-3">
      <h4 className="text-xs font-semibold text-foreground">
        {mention.text || mention.subtype || "Blank mention"}
      </h4>
      <p className="mt-1 text-[11px] italic leading-snug text-muted">
        {mention.evidence || "No evidence text"}
      </p>
      {keys.length > 0 && (
        <div className="mt-2.5 overflow-hidden rounded border border-border/70 bg-surface-raised/40 text-[11px]">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-border/70 bg-surface-raised font-mono text-[10px] uppercase tracking-wider text-muted">
                <th className="px-2 py-1 font-medium">Attribute</th>
                <th className="px-2 py-1 font-medium">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 font-mono">
              {keys.map((key) => {
                const value = mention.attributes[key];
                const rank = attributeRank(key, mention.entity);
                const primary = rank === "primary";
                return (
                  <tr key={key} className={primary ? familyTint(mention.entity) : undefined}>
                    <td
                      className={`px-2 py-1 ${
                        primary
                          ? `${familyTextClass(mention.entity)} font-medium`
                          : "text-muted/70"
                      }`}
                    >
                      {key}
                    </td>
                    <td
                      className={`px-2 py-1 ${
                        primary
                          ? `${familyTextClass(mention.entity)} font-medium`
                          : "text-foreground"
                      }`}
                    >
                      {value}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}
