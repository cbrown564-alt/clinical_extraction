"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Check, ChevronDown } from "lucide-react";
import { guidedCases, storyFor } from "@/lib/viva";
import styles from "./demo.module.css";

export default function CasePicker({ value, onChange }: { value: number; onChange: (id: number) => void }) {
  const [open, setOpen] = useState(false);
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const options = useRef<(HTMLButtonElement | null)[]>([]);
  const search = useRef({ text: "", time: 0 });
  const listId = useId();
  const items = guidedCases.map((c, index) => ({ id: c.id, title: storyFor(c).title, number: String(index + 1).padStart(2, "0") }));
  if (!items.some(c => c.id === value)) items.push({ id: value, title: `Batch · letter ${value}`, number: "↗" });
  const selected = items.findIndex(c => c.id === value);

  useEffect(() => {
    if (!open) return;
    options.current[selected]?.focus();
    function dismiss(event: PointerEvent) {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("pointerdown", dismiss);
    return () => document.removeEventListener("pointerdown", dismiss);
  }, [open, selected]);

  function close() {
    setOpen(false);
    trigger.current?.focus();
  }

  return <div className={styles.casePicker} ref={root} onBlur={e => {
    if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setOpen(false);
  }}>
    <button ref={trigger} className={styles.caseTrigger} aria-haspopup="listbox" aria-expanded={open}
      aria-controls={open ? listId : undefined} aria-label={`Case study: ${items[selected].title}`}
      onClick={() => setOpen(!open)} onKeyDown={e => {
        if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); setOpen(true); }
        if (e.key === "Escape") close();
      }}>
      <span className={styles.caseIndex}>{items[selected].number}</span>
      <span className={styles.caseTriggerText}><small>Case study</small><strong>{items[selected].title}</strong></span>
      <ChevronDown size={16} aria-hidden />
    </button>
    {open && <div className={styles.caseMenu}>
      <div className={styles.caseMenuHeading}>Explore the method <span>5 guided cases</span></div>
      <div id={listId} role="listbox" aria-label="Case study" onKeyDown={e => {
        const index = options.current.findIndex(el => el === document.activeElement);
        let next = index;
        if (e.key === "ArrowDown") next = (index + 1) % items.length;
        else if (e.key === "ArrowUp") next = (index - 1 + items.length) % items.length;
        else if (e.key === "Home") next = 0;
        else if (e.key === "End") next = items.length - 1;
        else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); return; }
        else if (e.key === "Tab") { close(); return; }
        else if (e.key.length === 1 && e.key !== " " && !e.ctrlKey && !e.metaKey && !e.altKey) {
          const now = e.timeStamp;
          search.current.text = (now - search.current.time < 600 ? search.current.text : "") + e.key.toLowerCase();
          search.current.time = now;
          const match = items.findIndex(c => c.title.toLowerCase().startsWith(search.current.text));
          if (match >= 0) next = match;
        } else return;
        e.preventDefault();
        options.current[next]?.focus();
      }}>
        {items.map((item, index) => <button key={item.id} ref={el => { options.current[index] = el; }}
          role="option" aria-selected={item.id === value} tabIndex={-1} className={styles.caseOption}
          onClick={() => { onChange(item.id); close(); }}>
          <span className={styles.caseOptionIndex} aria-hidden>{item.number}</span>
          <span>{item.title}</span>
          {item.id === value && <Check size={16} aria-hidden />}
        </button>)}
      </div>
    </div>}
  </div>;
}
