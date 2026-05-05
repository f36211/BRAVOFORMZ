"use client"

import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { motion } from "motion/react"
import { Bookmark, BookmarkCheck, ChevronRight, Layers, FileText, ListChecks } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"

export default function SubjectPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const subject = appData.subjects.find((s) => s.id === subjectId)
  const { isBookmarked, toggleBookmark, progress } = useStore()

  if (!subject) return notFound()

  return (
    <div className="space-y-8">
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative overflow-hidden rounded-3xl border border-border bg-card p-6 md:p-10 flex flex-col md:flex-row gap-8 items-center md:items-start"
      >
        {subject.image && (
          <div className="absolute inset-0 opacity-5 pointer-events-none">
            <img src={subject.image} alt="" className="size-full object-cover blur-2xl" />
          </div>
        )}

        {subject.image && (
          <div className="size-32 md:size-40 rounded-2xl border border-border overflow-hidden shrink-0 shadow-xl relative z-10">
            <img src={subject.image} alt={subject.name} className="size-full object-cover" />
          </div>
        )}

        <div className="flex-1 space-y-2 relative z-10 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            <span>Subject</span>
            <span>·</span>
            <span>Grade {subject.grade?.join(", ") || "-"}</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-medium tracking-tight">{subject.name}</h1>
          <p className="text-sm md:text-lg text-muted-foreground max-w-2xl text-pretty mx-auto md:mx-0">
            {subject.description}
          </p>
        </div>
      </motion.header>

      <section>
        <div className="flex items-end justify-between mb-4">
          <div>
            <h2 className="text-lg font-medium tracking-tight">Topics</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              {subject.topics.length} topics · click to expand
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {subject.topics.map((t, i) => {
            const bookmarked = isBookmarked(subject.id, t.id)
            const pct = progress[`${subject.id}:${t.id}`] ?? 0
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
                className="rounded-2xl border border-border bg-card overflow-hidden"
              >
                <div className="p-5">
                  <div className="flex items-start gap-4">
                    <div className="size-10 rounded-xl bg-muted grid place-items-center shrink-0">
                      <Layers className="size-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/subjects/${subject.id}/topics/${t.id}`}
                          className="text-base font-medium tracking-tight hover:underline underline-offset-4"
                        >
                          {t.title}
                        </Link>
                        <span className="text-[10px] font-mono text-muted-foreground">
                          {pct}%
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-0.5">{t.description}</p>

                      <div className="mt-3 h-1 rounded-full bg-muted overflow-hidden">
                        <div className="h-full bg-foreground" style={{ width: `${pct}%` }} />
                      </div>

                      <div className="mt-4 flex flex-wrap items-center gap-2">
                        <Link
                          href={`/subjects/${subject.id}/topics/${t.id}`}
                          className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-foreground text-background hover:bg-foreground/90 transition-colors"
                        >
                          Open <ChevronRight className="size-3" />
                        </Link>
                        <Link
                          href={`/subjects/${subject.id}/topics/${t.id}/flashcards`}
                          className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-border hover:bg-accent transition-colors"
                        >
                          <Layers className="size-3" />
                          {t.flashcards.length} flashcards
                        </Link>
                        <Link
                          href={`/subjects/${subject.id}/topics/${t.id}/quiz`}
                          className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-border hover:bg-accent transition-colors"
                        >
                          <ListChecks className="size-3" />
                          {t.quiz.questions.length} quiz
                        </Link>
                        <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-border text-muted-foreground">
                          <FileText className="size-3" />
                          {t.lessons.length} lessons
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => toggleBookmark(subject.id, t.id)}
                      aria-label={bookmarked ? "Remove bookmark" : "Add bookmark"}
                      className="size-9 grid place-items-center rounded-lg border border-border hover:bg-accent transition-colors shrink-0"
                    >
                      {bookmarked ? (
                        <BookmarkCheck className="size-4 fill-foreground" />
                      ) : (
                        <Bookmark className="size-4" />
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
