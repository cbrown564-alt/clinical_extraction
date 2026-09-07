"use client";

import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import { quoteSegments, type DemoCase } from "@/lib/viva";
import styles from "./demo.module.css";

export default function FullLetter({ current, showEvidence, onClose }: {
  current: DemoCase;
  showEvidence: boolean;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [highlights, setHighlights] = useState(showEvidence);
  const firstLineEnd = current.note.indexOf("\n");
  const heading = firstLineEnd < 0 ? "" : current.note.slice(0, firstLineEnd);
  const body = firstLineEnd < 0 ? current.note : current.note.slice(firstLineEnd);
  // Preserve the source whitespace while giving blank lines a smaller visual gap.
  function letterText(text: string) {
    return text.split(/(\n[ \t]*\n(?:[ \t]*\n)*)/).map((part, i) => /^\n[ \t]*\n/.test(part)
      ? <span key={i} className={styles.letterParagraphBreak}>{part}</span>
      : part);
  }

  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    const element = dialog.current!;
    element.showModal();
    return () => { element.close(); opener?.focus(); };
  }, []);

  return <dialog ref={dialog} className={styles.fullLetter} aria-labelledby="full-letter-title"
    onCancel={e => { e.preventDefault(); onClose(); }}
    onClick={e => {
      if (e.target !== e.currentTarget) return;
      const bounds = e.currentTarget.getBoundingClientRect();
      if (e.clientX < bounds.left || e.clientX > bounds.right || e.clientY < bounds.top || e.clientY > bounds.bottom) onClose();
    }}>
    <header className={styles.fullLetterToolbar}>
      <div><h2 id="full-letter-title">Full source letter <span>#{current.id}</span></h2><p>Synthetic development example</p></div>
      <div className={styles.fullLetterActions}>
        <button className={styles.evidenceSwitch} aria-pressed={highlights} onClick={() => setHighlights(!highlights)}>Evidence <span aria-hidden>{highlights ? "On" : "Off"}</span></button>
        <button className={styles.iconButton} onClick={onClose} aria-label="Close full letter"><X size={19} /></button>
      </div>
    </header>
    <div className={styles.fullLetterScroll}>
      <article className={styles.letterPage} aria-label="Original letter text">
        <div className={styles.letterOriginal}>
          {heading && <div className={styles.letterhead}>{heading}</div>}
          <div className={styles.letterPageText}>{quoteSegments(body, highlights ? current.record.events : []).map((segment, i) => segment.ids.length
            ? <mark key={i} title={`Evidence ${segment.ids.join(", ").toUpperCase()}`}>{letterText(segment.text)}</mark>
            : <span key={i}>{letterText(segment.text)}</span>)}</div>
        </div>
        <footer className={styles.letterPageFooter}>Gan 2026 · Letter {current.id}<span>Original wording</span></footer>
      </article>
    </div>
  </dialog>;
}
