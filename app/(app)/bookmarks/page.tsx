"use client"

import Link from "next/link"
import { motion } from "motion/react"
import { Bookmark, BookmarkX, ArrowRight } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"

export default function BookmarksPage() {
  const { bookmarks, toggleBookmark } = useStore()

  const items = bookmarks
    .map((b) => {
      const [sid, tid] = b.split(":")
      const subject = appData.subjects.find((s) => s.id === sid)
      const topic = subject?.topics.find((t) => t.id === tid)
      if (!subject || !topic) return null
      return { subject, topic }
    })
    .filter(Boolean) as { subject: (typeof appData.subjects)[number]; topic: (typeof appData.subjects)[number]["topics"][number] }[]

  return (
    <div className="space-y-8">
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="space-y-2"
      >
        <div className="text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
          Saved
        </div>
        <h1 className="text-3xl md:text-4xl font-medium tracking-tight">Bookmarks</h1>
        <p className="text-sm text-muted-foreground max-w-xl">
          Topics you&apos;ve saved for quick access. Toggle the bookmark icon on any topic to
          add or remove it here.
        </p>
      </motion.header>

      {items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <div className="mx-auto size-10 rounded-xl border border-border bg-card grid place-items-center mb-4">
            <Bookmark className="size-4 text-muted-foreground" />
          </div>
          <h2 className="text-base font-medium">No bookmarks yet</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Open any topic and tap the bookmark icon to save it here.
          </p>
          <Link
            href="/dashboard"
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-foreground text-background px-4 py-2.5 text-sm font-medium hover:bg-foreground/90"
          >
            Browse subjects <ArrowRight className="size-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {items.map(({ subject, topic }, i) => (
            <motion.div
              key={`${subject.id}:${topic.id}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.04 }}
              className="rounded-2xl border border-border bg-card p-5 flex items-start gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
                  {subject.name}
                </div>
                <Link
                  href={`/subjects/${subject.id}/topics/${topic.id}`}
                  className="mt-1 block text-base font-medium tracking-tight hover:underline underline-offset-4"
                >
                  {topic.title}
                </Link>
                <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                  {topic.description}
                </p>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Link
                    href={`/subjects/${subject.id}/topics/${topic.id}`}
                    className="text-[11px] font-medium px-2.5 py-1 rounded-md bg-foreground text-background hover:bg-foreground/90 transition-colors"
                  >
                    Open
                  </Link>
                  <Link
                    href={`/subjects/${subject.id}/topics/${topic.id}/flashcards`}
                    className="text-[11px] font-medium px-2.5 py-1 rounded-md border border-border hover:bg-accent transition-colors"
                  >
                    Flashcards
                  </Link>
                </div>
              </div>
              <button
                onClick={() => toggleBookmark(subject.id, topic.id)}
                aria-label="Remove bookmark"
                className="size-8 grid place-items-center rounded-lg border border-border hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
              >
                <BookmarkX className="size-4" />
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
