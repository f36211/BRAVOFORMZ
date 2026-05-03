"use client"

import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { useCallback, useEffect, useState } from "react"
import { AnimatePresence, motion } from "motion/react"
import { ArrowLeft, ArrowRight, RotateCcw, X, Check } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"

export default function FlashcardsPage() {
  const { subjectId, topicId } = useParams<{ subjectId: string; topicId: string }>()
  const subject = appData.subjects.find((s) => s.id === subjectId)
  const topic = subject?.topics.find((t) => t.id === topicId)
  const { setProgress, settings } = useStore()

  const [idx, setIdx] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [done, setDone] = useState<{ correct: number; wrong: number } | null>(null)
  const [stats, setStats] = useState({ correct: 0, wrong: 0 })

  const cards = topic?.flashcards ?? []
  const card = cards[idx]
  const total = cards.length

  const next = useCallback(
    (mark?: "correct" | "wrong") => {
      if (mark === "correct") setStats((s) => ({ ...s, correct: s.correct + 1 }))
      if (mark === "wrong") setStats((s) => ({ ...s, wrong: s.wrong + 1 }))

      if (idx >= total - 1) {
        setDone({
          correct: stats.correct + (mark === "correct" ? 1 : 0),
          wrong: stats.wrong + (mark === "wrong" ? 1 : 0),
        })
        if (subject && topic) setProgress(subject.id, topic.id, 100)
      } else {
        setIdx((i) => i + 1)
        setFlipped(false)
      }
    },
    [idx, total, stats, subject, topic, setProgress],
  )

  const prev = useCallback(() => {
    if (idx > 0) {
      setIdx((i) => i - 1)
      setFlipped(false)
    }
  }, [idx])

  const toggle = useCallback(() => setFlipped((f) => !f), [])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (done) return
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault()
        toggle()
      } else if (e.key === "ArrowRight") {
        e.preventDefault()
        next()
      } else if (e.key === "ArrowLeft") {
        e.preventDefault()
        prev()
      } else if (e.key.toLowerCase() === "j") next("wrong")
      else if (e.key.toLowerCase() === "k") next("correct")
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [next, prev, toggle, done])

  if (!subject || !topic) return notFound()
  if (cards.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border p-10 text-center">
        <p className="text-sm text-muted-foreground">No flashcards in this topic yet.</p>
      </div>
    )
  }

  function reset() {
    setIdx(0)
    setFlipped(false)
    setStats({ correct: 0, wrong: 0 })
    setDone(null)
  }

  if (done) {
    const accuracy = Math.round((done.correct / Math.max(1, done.correct + done.wrong)) * 100)
    return (
      <div className="min-h-[70vh] grid place-items-center">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md text-center"
        >
          <div className="text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            Session complete
          </div>
          <h1 className="mt-3 text-3xl font-medium tracking-tight">Nice work.</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {topic.title} · {total} cards reviewed
          </p>

          <div className="mt-8 grid grid-cols-3 gap-3">
            <Stat value={done.correct} label="Got it" />
            <Stat value={done.wrong} label="Missed" />
            <Stat value={`${accuracy}%`} label="Accuracy" />
          </div>

          <div className="mt-8 flex flex-col sm:flex-row gap-2 justify-center">
            <button
              onClick={reset}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-foreground text-background px-4 py-2.5 text-sm font-medium hover:bg-foreground/90 transition-colors"
            >
              <RotateCcw className="size-4" />
              Run again
            </button>
            <Link
              href={`/subjects/${subject.id}/topics/${topic.id}`}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border px-4 py-2.5 text-sm font-medium hover:bg-accent transition-colors"
            >
              Back to topic
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  const progress = ((idx + 1) / total) * 100

  return (
    <div className="min-h-[80vh] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 mb-6">
        <Link
          href={`/subjects/${subject.id}/topics/${topic.id}`}
          aria-label="Exit flashcards"
          className="size-9 grid place-items-center rounded-lg border border-border hover:bg-accent transition-colors"
        >
          <X className="size-4" />
        </Link>
        <div className="flex-1 max-w-md">
          <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground mb-1.5">
            <span>{topic.title}</span>
            <span>
              {idx + 1} / {total}
            </span>
          </div>
          <div className="h-1 rounded-full bg-muted overflow-hidden">
            <motion.div
              className="h-full bg-foreground"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono">
          <span className="text-muted-foreground">{stats.correct}</span>
          <span className="text-muted-foreground">·</span>
          <span className="text-muted-foreground">{stats.wrong}</span>
        </div>
      </div>

      {/* Card */}
      <div className="flex-1 grid place-items-center">
        <div className="w-full max-w-2xl" style={{ perspective: "1500px" }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={card.id}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.25 }}
            >
              <button
                onClick={toggle}
                aria-label="Flip card"
                className="relative w-full aspect-[16/10] cursor-pointer focus:outline-none"
                style={{ transformStyle: "preserve-3d" }}
              >
                <motion.div
                  className="absolute inset-0"
                  style={{ transformStyle: "preserve-3d" }}
                  animate={{ rotateY: flipped ? 180 : 0 }}
                  transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                >
                  {/* Front */}
                  <div
                    className="absolute inset-0 rounded-3xl border border-border bg-card p-8 md:p-12 flex flex-col"
                    style={{ backfaceVisibility: "hidden" }}
                  >
                    <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
                      Question
                    </div>
                    <div className="flex-1 grid place-items-center">
                      <p className="text-2xl md:text-4xl font-medium tracking-tight text-balance text-center">
                        {card.question}
                      </p>
                    </div>
                    <div className="text-[11px] font-mono text-muted-foreground text-center">
                      tap or press <kbd className="rounded border border-border bg-muted px-1 py-px">space</kbd> to flip
                    </div>
                  </div>
                  {/* Back */}
                  <div
                    className="absolute inset-0 rounded-3xl border border-foreground bg-foreground text-background p-8 md:p-12 flex flex-col"
                    style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
                  >
                    <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-background/60">
                      Answer
                    </div>
                    <div className="flex-1 grid place-items-center">
                      <p className="text-2xl md:text-4xl font-medium tracking-tight text-balance text-center">
                        {card.answer}
                      </p>
                    </div>
                    <div className="text-[11px] font-mono text-background/60 text-center">
                      How well did you know it?
                    </div>
                  </div>
                </motion.div>
              </button>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Controls */}
      <div className="mt-6 flex items-center justify-center gap-2">
        <button
          onClick={prev}
          disabled={idx === 0}
          aria-label="Previous"
          className="size-11 grid place-items-center rounded-xl border border-border hover:bg-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowLeft className="size-4" />
        </button>

        {flipped ? (
          <>
            <button
              onClick={() => next("wrong")}
              className="inline-flex items-center gap-2 rounded-xl border border-border px-5 h-11 text-sm font-medium hover:bg-accent transition-colors"
            >
              <X className="size-4" />
              Missed
            </button>
            <button
              onClick={() => next("correct")}
              className="inline-flex items-center gap-2 rounded-xl bg-foreground text-background px-5 h-11 text-sm font-medium hover:bg-foreground/90 transition-colors"
            >
              <Check className="size-4" />
              Got it
            </button>
          </>
        ) : (
          <button
            onClick={toggle}
            className="inline-flex items-center gap-2 rounded-xl bg-foreground text-background px-6 h-11 text-sm font-medium hover:bg-foreground/90 transition-colors"
          >
            Show answer
          </button>
        )}

        <button
          onClick={() => next()}
          aria-label="Next"
          className="size-11 grid place-items-center rounded-xl border border-border hover:bg-accent transition-colors"
        >
          <ArrowRight className="size-4" />
        </button>
      </div>

      {settings.showKeyboardHints && (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3 text-[10px] font-mono text-muted-foreground">
          <span>
            <kbd className="rounded border border-border bg-muted px-1 py-px">space</kbd> flip
          </span>
          <span>
            <kbd className="rounded border border-border bg-muted px-1 py-px">←</kbd>{" "}
            <kbd className="rounded border border-border bg-muted px-1 py-px">→</kbd> nav
          </span>
          <span>
            <kbd className="rounded border border-border bg-muted px-1 py-px">j</kbd> miss
          </span>
          <span>
            <kbd className="rounded border border-border bg-muted px-1 py-px">k</kbd> got it
          </span>
        </div>
      )}
    </div>
  )
}

function Stat({ value, label }: { value: number | string; label: string }) {
  return (
    <div className="rounded-xl border border-border bg-card py-4">
      <div className="text-2xl font-medium tracking-tight">{value}</div>
      <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground mt-1">
        {label}
      </div>
    </div>
  )
}
