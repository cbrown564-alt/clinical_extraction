"use client";

import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode,
  type SelectHTMLAttributes,
} from "react";
import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import {
  adjacentPickerValue,
  filterPickerItems,
  highlightedPickerIndex,
  type PickerItem,
} from "@/lib/controlPicker";

/**
 * The control bar both example explorers wear directly under the header.
 *
 * Owns the one row where you pick *which specimen* and *which variant* you are
 * looking at: Gan picks a split + row and a pipeline family; ExECTv2 picks a
 * letter and an architecture. `left` carries the specimen/context pickers,
 * `right` carries the variant picker and actions, with a flexible spacer
 * between – so both datasets read as "the same bar with different selects".
 */
export function ControlBar({
  left,
  right,
}: {
  left?: ReactNode;
  right?: ReactNode;
}) {
  return (
    <div className="relative z-20 shrink-0 border-b border-border bg-surface">
      <div className="flex flex-wrap items-center gap-3 px-4 py-2">
        {left}
        <div className="flex-1" />
        {right}
      </div>
    </div>
  );
}

/** Inline uppercase label + control, the shared shape for every picker. */
export function ControlField({
  label,
  icon,
  htmlFor,
  children,
}: {
  label?: ReactNode;
  icon?: ReactNode;
  htmlFor?: string;
  children: ReactNode;
}) {
  return (
    <div className="flex w-full min-w-0 flex-wrap items-center gap-1.5 sm:w-auto sm:flex-nowrap">
      {icon}
      {label &&
        (htmlFor ? (
          <label htmlFor={htmlFor} className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            {label}
          </label>
        ) : (
          <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">{label}</span>
        ))}
      {children}
    </div>
  );
}

/** The single `<select>` styling both explorers use, so pickers never drift. */
export function ControlSelect({
  className = "",
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={`max-w-full rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-deterministic disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}

const controlButtonClass =
  "rounded-md border border-border bg-surface px-1 py-1 text-muted outline-none hover:bg-surface-raised hover:text-foreground focus:border-deterministic disabled:opacity-30";

/**
 * Searchable letter picker with prev/next.
 *
 * Native `<select>` menus are OS-drawn and crop against the chrome when the
 * catalog is long. This combobox opens a scrollable panel under the trigger
 * and lets you jump by typing an id. Prev/next walk the full catalog in order
 * and stop at the ends.
 */
export function LetterPicker({
  id,
  items,
  value,
  onChange,
  disabled = false,
  placeholder = "Letter…",
  className = "",
}: {
  id: string;
  items: readonly PickerItem[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlighted, setHighlighted] = useState(-1);
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const optionRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const listboxId = useId();
  const catalogKey = items.map((item) => item.value).join("\0");
  const catalogKeyRef = useRef(catalogKey);

  const filtered = useMemo(
    () => filterPickerItems(items, query),
    [items, query]
  );
  const selected = items.find((item) => item.value === value);
  const prevValue = disabled ? null : adjacentPickerValue(items, value, -1);
  const nextValue = disabled ? null : adjacentPickerValue(items, value, 1);

  useEffect(() => {
    if (catalogKeyRef.current === catalogKey) return;
    catalogKeyRef.current = catalogKey;
    setOpen(false);
    setQuery("");
  }, [catalogKey]);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    searchRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!open || highlighted < 0) return;
    optionRefs.current[highlighted]?.scrollIntoView({ block: "nearest" });
  }, [open, highlighted]);

  function close() {
    setOpen(false);
    setQuery("");
  }

  function openMenu() {
    setQuery("");
    setHighlighted(highlightedPickerIndex(items, value));
    setOpen(true);
  }

  function choose(next: string) {
    onChange(next);
    close();
    triggerRef.current?.focus();
  }

  function onTriggerKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (!open) openMenu();
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      if (prevValue) onChange(prevValue);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      if (nextValue) onChange(nextValue);
    } else if (event.key === "Escape" && open) {
      event.preventDefault();
      close();
    }
  }

  function onSearchKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      if (filtered.length === 0) return;
      setHighlighted((index) =>
        index < 0 ? 0 : Math.min(index + 1, filtered.length - 1)
      );
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      if (filtered.length === 0) return;
      setHighlighted((index) =>
        index < 0 ? filtered.length - 1 : Math.max(index - 1, 0)
      );
    } else if (event.key === "Home") {
      event.preventDefault();
      if (filtered.length > 0) setHighlighted(0);
    } else if (event.key === "End") {
      event.preventDefault();
      if (filtered.length > 0) setHighlighted(filtered.length - 1);
    } else if (event.key === "Enter") {
      event.preventDefault();
      const item = highlighted >= 0 ? filtered[highlighted] : undefined;
      if (item) choose(item.value);
    } else if (event.key === "Escape") {
      event.preventDefault();
      close();
      triggerRef.current?.focus();
    }
  }

  function onQueryChange(nextQuery: string) {
    setQuery(nextQuery);
    setHighlighted(
      highlightedPickerIndex(filterPickerItems(items, nextQuery), value)
    );
  }

  function optionId(index: number) {
    return `${listboxId}-opt-${index}`;
  }

  return (
    <div ref={rootRef} className={`relative flex min-w-0 items-center gap-0.5 ${className}`}>
      <button
        type="button"
        aria-label="Previous letter"
        disabled={!prevValue}
        onClick={() => prevValue && onChange(prevValue)}
        className={controlButtonClass}
      >
        <ChevronLeft className="h-3.5 w-3.5" />
      </button>

      <button
        id={id}
        ref={triggerRef}
        type="button"
        disabled={disabled}
        onClick={() => (open ? close() : openMenu())}
        onKeyDown={onTriggerKeyDown}
        className="flex min-w-0 flex-1 items-center gap-1 rounded-md border border-border bg-surface px-2 py-1 text-left text-xs text-foreground outline-none focus:border-deterministic disabled:opacity-50"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listboxId : undefined}
        aria-label={selected ? `Letter ${selected.label}` : "Choose letter"}
      >
        <span className={`min-w-0 flex-1 truncate ${selected ? "" : "text-muted"}`}>
          {selected?.label ?? (value || placeholder)}
        </span>
        <ChevronDown
          className={`h-3 w-3 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      <button
        type="button"
        aria-label="Next letter"
        disabled={!nextValue}
        onClick={() => nextValue && onChange(nextValue)}
        className={controlButtonClass}
      >
        <ChevronRight className="h-3.5 w-3.5" />
      </button>

      {open && (
        <div className="absolute left-0 top-full z-40 mt-1 w-max min-w-full max-w-sm overflow-hidden rounded-md border border-border bg-surface shadow-lg">
          <div className="border-b border-border p-1.5">
            <input
              ref={searchRef}
              value={query}
              onChange={(event) => onQueryChange(event.target.value)}
              onKeyDown={onSearchKeyDown}
              placeholder="Search letters…"
              aria-label="Search letters"
              role="combobox"
              aria-autocomplete="list"
              aria-expanded="true"
              aria-controls={listboxId}
              aria-activedescendant={
                highlighted >= 0 ? optionId(highlighted) : undefined
              }
              className="w-full rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground placeholder:text-muted outline-none focus:border-deterministic"
            />
          </div>
          <div
            id={listboxId}
            role="listbox"
            aria-label="Letters"
            className="max-h-[min(22rem,50vh)] overflow-y-auto"
          >
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-[11px] text-muted">No letters match</div>
            ) : (
              filtered.map((item, index) => (
                <button
                  key={item.value}
                  ref={(node) => {
                    optionRefs.current[index] = node;
                  }}
                  type="button"
                  role="option"
                  id={optionId(index)}
                  tabIndex={-1}
                  aria-selected={item.value === value}
                  onMouseEnter={() => setHighlighted(index)}
                  onClick={() => choose(item.value)}
                  className={`flex w-full px-2.5 py-1.5 text-left text-xs ${
                    index === highlighted ? "bg-deterministic/8" : "hover:bg-surface-raised"
                  } ${item.value === value ? "font-medium text-foreground" : "text-foreground"}`}
                >
                  {item.label}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
