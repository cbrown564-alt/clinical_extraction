"use client";

import { useMemo, useState, useRef, useEffect } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

/*
  Token types for regex syntax highlighting
*/
type TokenType =
  | "anchor"
  | "groupOpen"
  | "groupClose"
  | "namedGroup"
  | "charClass"
  | "quantifier"
  | "alternation"
  | "escape"
  | "literal"
  | "comment";

interface Token {
  type: TokenType;
  text: string;
  name?: string; // for named groups
}

const TOKEN_COLORS: Record<TokenType, string> = {
  anchor: "#9ca3af",        // gray
  groupOpen: "#7c3aed",     // purple
  groupClose: "#7c3aed",
  namedGroup: "#7c3aed",
  charClass: "#d97706",     // amber
  quantifier: "#2a6f6f",    // teal
  alternation: "#4a6fa5",   // slate blue
  escape: "#e07a5f",        // coral
  literal: "#1a1a1a",       // near-black
  comment: "#6b7280",
};

const TOKEN_BG: Record<TokenType, string | undefined> = {
  anchor: undefined,
  groupOpen: "rgba(124,58,237,0.06)",
  groupClose: "rgba(124,58,237,0.06)",
  namedGroup: "rgba(124,58,237,0.10)",
  charClass: "rgba(217,119,6,0.08)",
  quantifier: "rgba(42,111,111,0.08)",
  alternation: undefined,
  escape: undefined,
  literal: undefined,
  comment: undefined,
};

function tokenizeRegex(pattern: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;

  while (i < pattern.length) {
    const ch = pattern[i];

    if (ch === "(" && pattern.slice(i, i + 4) === "(?P<") {
      const nameMatch = pattern.slice(i + 4).match(/^([a-zA-Z_][a-zA-Z0-9_]*)>/);
      if (nameMatch) {
        const name = nameMatch[1];
        const len = 4 + name.length + 1;
        tokens.push({ type: "namedGroup", text: pattern.slice(i, i + len), name });
        i += len;
        continue;
      }
    }

    if (ch === "(" && pattern.slice(i, i + 3) === "(?:") {
      tokens.push({ type: "groupOpen", text: "(?:" });
      i += 3;
      continue;
    }

    if (ch === "(" && pattern[i + 1] === "?") {
      let j = i + 2;
      while (j < pattern.length && /[#:=!<>\-~]/.test(pattern[j])) j++;
      tokens.push({ type: "groupOpen", text: pattern.slice(i, j) });
      i = j;
      continue;
    }

    if (ch === "(") {
      tokens.push({ type: "groupOpen", text: "(" });
      i++;
      continue;
    }

    if (ch === ")") {
      tokens.push({ type: "groupClose", text: ")" });
      i++;
      continue;
    }

    if (ch === "[") {
      let j = i + 1;
      let escaped = false;
      while (j < pattern.length) {
        if (escaped) { escaped = false; j++; continue; }
        if (pattern[j] === "\\") { escaped = true; j++; continue; }
        if (pattern[j] === "]") { j++; break; }
        j++;
      }
      tokens.push({ type: "charClass", text: pattern.slice(i, j) });
      i = j;
      continue;
    }

    if (ch === "\\") {
      tokens.push({ type: "escape", text: pattern.slice(i, i + 2) });
      i += 2;
      continue;
    }

    if (ch === "{" ) {
      const match = pattern.slice(i).match(/^\{\d+(?:,\d*)?\}/);
      if (match) {
        tokens.push({ type: "quantifier", text: match[0] });
        i += match[0].length;
        continue;
      }
    }

    if (ch === "+" || ch === "*" || ch === "?") {
      tokens.push({ type: "quantifier", text: ch });
      i++;
      continue;
    }

    if (ch === "|") {
      tokens.push({ type: "alternation", text: "|" });
      i++;
      continue;
    }

    tokens.push({ type: "literal", text: ch });
    i++;
  }

  return tokens;
}

function extractNamedGroups(tokens: Token[]): Array<{ name: string; text: string }> {
  const groups: Array<{ name: string; text: string }> = [];
  for (const tok of tokens) {
    if (tok.type === "namedGroup" && tok.name) {
      groups.push({ name: tok.name, text: tok.text });
    }
  }
  return groups;
}

function countAlternations(tokens: Token[]): number {
  return tokens.filter((t) => t.type === "alternation").length;
}

interface RegexHighlighterProps {
  pattern: string;
  className?: string;
}

export default function RegexHighlighter({ pattern, className = "" }: RegexHighlighterProps) {
  const [expanded, setExpanded] = useState(false);
  const codeRef = useRef<HTMLElement>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);

  const { tokens, namedGroups, altCount } = useMemo(() => {
    const toks = tokenizeRegex(pattern);
    const groups = extractNamedGroups(toks);
    const alts = countAlternations(toks);
    return { tokens: toks, namedGroups: groups, altCount: alts };
  }, [pattern]);

  // Detect if content overflows the collapsed max-height
  useEffect(() => {
    const el = codeRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => {
      setIsOverflowing(el.scrollHeight > 80);
    });
    observer.observe(el);
    setIsOverflowing(el.scrollHeight > 80);
    return () => observer.disconnect();
  }, [pattern]);

  const needsCollapse = pattern.length > 120 || altCount > 6;

  return (
    <div className={`font-mono text-xs leading-relaxed ${className}`}>
      {/* Named group badges */}
      {namedGroups.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-1.5">
          {namedGroups.map((g) => (
            <span
              key={g.name}
              className="inline-flex items-center gap-0.5 rounded-md bg-hybrid/8 px-1.5 py-0.5 text-[11px] font-medium text-hybrid border border-hybrid/12"
              title={`Named capture group: ${g.name}`}
            >
              <span className="opacity-50">(?P&lt;</span>
              {g.name}
              <span className="opacity-50">&gt;</span>
            </span>
          ))}
        </div>
      )}

      {/* Regex body – natural wrap, no forced breaks at | */}
      <div className="relative">
        <code
          ref={codeRef}
          className={`block overflow-x-auto rounded-lg border border-border/50 bg-surface-raised/60 p-2.5 transition-colors duration-200 ${
            !expanded && needsCollapse ? "max-h-[80px] overflow-y-hidden" : "max-h-none"
          }`}
          style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}
        >
          {tokens.map((tok, idx) => {
            const color = TOKEN_COLORS[tok.type];
            const bg = TOKEN_BG[tok.type];
            return (
              <span
                key={idx}
                style={{
                  color,
                  backgroundColor: bg,
                  borderRadius: bg ? 3 : undefined,
                  padding: bg ? "0 2px" : undefined,
                }}
              >
                {tok.text}
              </span>
            );
          })}
        </code>

        {/* Fade overlay when collapsed */}
        {!expanded && isOverflowing && (
          <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-surface-raised/60 to-transparent pointer-events-none rounded-b-lg" />
        )}
      </div>

      {/* Expand / meta */}
      {needsCollapse && (
        <div className="flex items-center gap-3 mt-1">
          <button
            onClick={() => setExpanded(!expanded)}
            className="inline-flex items-center gap-1 text-[11px] text-deterministic hover:underline font-medium"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-3 w-3" />
                Collapse regex
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" />
                Show full regex
              </>
            )}
          </button>
          <span className="text-[11px] text-muted">
            {pattern.length} chars · {altCount} alt{altCount !== 1 ? "s" : ""}
          </span>
        </div>
      )}
    </div>
  );
}
