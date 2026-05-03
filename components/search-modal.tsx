"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { AnimatePresence, motion } from "motion/react"
import { Search, BookOpen, FileText, Layers, ArrowRight, X } from "lucide-react"
import { appData } from "@/lib/data"
import type { SearchResult } from "@/lib/types"

function buildIndex(): SearchResult[] {
  const out: SearchResult[] = []
  for (const s of appData.subjects) {
    out.push({
      kind: "subject",
      subjectId: s.id,
      title: s.name,
      subtitle: s.description,
    })
    for (const t of s.topics) {
      out.push({
        kind: "topic",
        subjectId: s.id,
        topicId: t.id,
        title: t.title,
        subtitle: `${s.name} · ${t.description}`,
      })
      for (const l of t.lessons) {
        const text = l.content
          .map((b) => ("text" in b ? b.text : "items" in b ? b.items.join(" ") : ""))
          .join(" ")
        out.push({
          kind: "lesson",
          subjectId: s.id,
          topicId: t.id,
          lessonId: l.id,
          title: l.title,
          subtitle: text.slice(0, 90),
        })
      }
      for (const f of t.flashcards) {
        out.push({
          kind: "flashcard",
          subjectId: s.id,
          topicId: t.id,
          flashcardId: f.id,
          title: f.question,
          subtitle: `${s.name} · ${t.title} · flashcard`,
        })
      }
    }
  }
  return out
}

const ICONS = {
  subject: BookOpen,
  topic: Layers,
  lesson: FileText,
  flashcard: Layers,
}

export function SearchModal({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (o: boolean) => void
}) {
  const router = useRouter()
  const [q, setQ] = useState("")
  const [active, setActive] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const index = useMemo(buildIndex, [])

  const results = useMemo(() => {
    const term = q.trim().toLowerCase()
    if (!term) return index.slice(0, 8)
    return index
      .filter(
        (r) =>
          r.title.toLowerCase().includes(term) || r.subtitle.toLowerCase().includes(term),
      )
      .slice(0, 12)
  }, [q, index])

  useEffect(() => {
    if (open) {
      setQ("")
      setActive(0)
      setTimeout(() => inputRef.current?.focus(), 30)
    }
  }, [open])

  useEffect(() => {
    setActive(0)
  }, [q])

  function go(r: SearchResult) {
    if (r.kind === "subject") router.push(`/subjects/${r.subjectId}`)
    else if (r.kind === "topic") router.push(`/subjects/${r.subjectId}/topics/${r.topicId}`)
    else if (r.kind === "lesson")
      router.push(`/subjects/${r.subjectId}/topics/${r.topicId}/lessons/${r.lessonId}`)
    else if (r.kind === "flashcard")
      router.push(`/subjects/${r.subjectId}/topics/${r.topicId}/flashcards`)
    onOpenChange(false)
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setActive((a) => Math.min(a + 1, results.length - 1))
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setActive((a) => Math.max(a - 1, 0))
    } else if (e.key === "Enter" && results[active]) {
      e.preventDefault()
      go(results[active])
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-foreground/20 backdrop-blur-sm"
            onClick={() => onOpenChange(false)}
          />
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
            className="relative w-full max-w-xl rounded-2xl border border-border bg-popover shadow-2xl overflow-hidden"
            role="dialog"
            aria-label="Search"
          >
            <div className="flex items-center gap-3 px-4 h-14 border-b border-border">
              <Search className="size-4 text-muted-foreground" />
              <input
                ref={inputRef}
                value={q}
                onChange={(e) => setQ(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Search subjects, topics, lessons, flashcards…"
                className="flex-1 h-full bg-transparent outline-none text-sm placeholder:text-muted-foreground"
              />
              <button
                onClick={() => onOpenChange(false)}
                aria-label="Close"
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="max-h-[50vh] overflow-y-auto scrollbar-thin py-1">
              {results.length === 0 ? (
                <div className="px-4 py-10 text-center text-sm text-muted-foreground">
                  No matches for &ldquo;{q}&rdquo;
                </div>
              ) : (
                <ul>
                  {results.map((r, i) => {
                    const Icon = ICONS[r.kind]
                    const activeRow = i === active
                    return (
                      <li key={`${r.kind}-${i}`}>
                        <button
                          onMouseEnter={() => setActive(i)}
                          onClick={() => go(r)}
                          className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${
                            activeRow ? "bg-accent" : ""
                          }`}
                        >
                          <div className="size-8 rounded-lg border border-border bg-card grid place-items-center shrink-0">
                            <Icon className="size-3.5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium truncate">{r.title}</div>
                            <div className="text-xs text-muted-foreground truncate">
                              {r.subtitle}
                            </div>
                          </div>
                          <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                            {r.kind}
                          </span>
                          {activeRow && (
                            <ArrowRight className="size-3.5 text-muted-foreground" />
                          )}
                        </button>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>

            <div className="border-t border-border px-4 py-2 flex items-center justify-between text-[10px] font-mono text-muted-foreground">
              <div className="flex items-center gap-3">
                <span>
                  <kbd className="rounded border border-border bg-muted px-1 py-px">↑↓</kbd> navigate
                </span>
                <span>
                  <kbd className="rounded border border-border bg-muted px-1 py-px">↵</kbd> open
                </span>
                <span>
                  <kbd className="rounded border border-border bg-muted px-1 py-px">esc</kbd> close
                </span>
              </div>
              <span>{results.length} results</span>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
