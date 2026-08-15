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
  stepPickerIndex,
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

/** Native `<select>` styling, kept for short ungrouped pickers. */
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

export type ControlComboboxProps = {
  id: string;
  items: readonly PickerItem[];
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
  /** Singular noun used in aria labels and empty/search copy (`letter`, `method`). */
  noun?: string;
  title?: string;
};

/**
 * Searchable catalog picker with prev/next.
 *
 * Native `<select>` menus are OS-drawn and crop against the chrome when the
 * catalog is long. This combobox opens a scrollable panel under the trigger
 * and lets you jump by typing. Prev/next walk the full catalog in order,
 * skip disabled items, and stop at the ends.
 */
export function ControlCombobox({
  id,
  items,
  value,
  onChange,
  disabled = false,
  placeholder,
  className = "",
  noun = "item",
  title,
}: ControlComboboxProps) {
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
  const closedPlaceholder = placeholder ?? `${noun.charAt(0).toUpperCase()}${noun.slice(1)}…`;
  const nounPlural = `${noun}s`;
  const nounLabel = noun.charAt(0).toUpperCase() + noun.slice(1);

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
    const item = items.find((entry) => entry.value === next);
    if (!item || item.disabled) return;
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
      setHighlighted((index) => stepPickerIndex(filtered, index, 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlighted((index) => stepPickerIndex(filtered, index, -1));
    } else if (event.key === "Home") {
      event.preventDefault();
      setHighlighted(highlightedPickerIndex(filtered, ""));
    } else if (event.key === "End") {
      event.preventDefault();
      setHighlighted(stepPickerIndex(filtered, filtered.length, -1));
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
        aria-label={`Previous ${noun}`}
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
        title={title}
        aria-label={selected ? `${nounLabel} ${selected.label}` : `Choose ${noun}`}
      >
        <span className={`min-w-0 flex-1 truncate ${selected ? "" : "text-muted"}`}>
          {selected?.label ?? (value || closedPlaceholder)}
        </span>
        <ChevronDown
          className={`h-3 w-3 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      <button
        type="button"
        aria-label={`Next ${noun}`}
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
              placeholder={`Search ${nounPlural}…`}
              aria-label={`Search ${nounPlural}`}
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
            aria-label={nounLabel}
            className="max-h-[min(22rem,50vh)] overflow-y-auto"
          >
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-[11px] text-muted">No {nounPlural} match</div>
            ) : (
              filtered.map((item, index) => {
                const showGroup = Boolean(item.group) && item.group !== filtered[index - 1]?.group;
                return (
                  <div key={item.value}>
                    {showGroup && (
                      <div className="px-2.5 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wide text-muted">
                        {item.group}
                      </div>
                    )}
                    <button
                      ref={(node) => {
                        optionRefs.current[index] = node;
                      }}
                      type="button"
                      role="option"
                      id={optionId(index)}
                      tabIndex={-1}
                      disabled={item.disabled}
                      aria-disabled={item.disabled || undefined}
                      aria-selected={item.value === value}
                      onMouseEnter={() => setHighlighted(index)}
                      onClick={() => choose(item.value)}
                      className={`flex w-full px-2.5 py-1.5 text-left text-xs ${
                        item.disabled
                          ? "cursor-not-allowed text-muted opacity-50"
                          : index === highlighted
                            ? "bg-deterministic/8 text-foreground"
                            : "text-foreground hover:bg-surface-raised"
                      } ${!item.disabled && item.value === value ? "font-medium" : ""}`}
                    >
                      {item.label}
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/** Letter catalog picker. Same control as methods, with letter copy. */
export function LetterPicker(props: Omit<ControlComboboxProps, "noun">) {
  return <ControlCombobox {...props} noun="letter" />;
}
