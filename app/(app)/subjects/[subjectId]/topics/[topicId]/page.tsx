"use client"

import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { motion } from "motion/react"
import { Bookmark, BookmarkCheck, FileText, Layers, ListChecks, Clock, ArrowRight } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"

export default function TopicPage() {
  const { subjectId, topicId } = useParams<{ subjectId: string; topicId: string }>()
  const subject = appData.subjects.find((s) => s.id === subjectId)
  const topic = subject?.topics.find((t) => t.id === topicId)
  const { isBookmarked, toggleBookmark, progress } = useStore()

  if (!subject || !topic) return notFound()
  const bookmarked = isBookmarked(subject.id, topic.id)
  const pct = progress[`${subject.id}:${topic.id}`] ?? 0

  return (
    <div className="space-y-8">
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-start justify-between gap-4"
      >
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            <Link href={`/subjects/${subject.id}`} className="hover:text-foreground">
              {subject.name}
            </Link>
            <span>·</span>
            <span>Topic</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-medium tracking-tight">{topic.title}</h1>
          <p className="text-sm md:text-base text-muted-foreground max-w-2xl text-pretty">
            {topic.description}
          </p>
          <div className="flex items-center gap-3 pt-1">
            <div className="flex items-center gap-2 text-xs">
              <span className="font-mono text-muted-foreground">{pct}%</span>
              <div className="w-32 h-1 rounded-full bg-muted overflow-hidden">
                <div className="h-full bg-foreground" style={{ width: `${pct}%` }} />
              </div>
            </div>
          </div>
        </div>
        <button
          onClick={() => toggleBookmark(subject.id, topic.id)}
          aria-label={bookmarked ? "Remove bookmark" : "Add bookmark"}
          className="size-10 grid place-items-center rounded-xl border border-border hover:bg-accent transition-colors shrink-0"
        >
          {bookmarked ? (
            <BookmarkCheck className="size-4 fill-foreground" />
          ) : (
            <Bookmark className="size-4" />
          )}
        </button>
      </motion.header>

      {/* Action grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <ActionCard
          href={`/subjects/${subject.id}/topics/${topic.id}/flashcards`}
          title="Flashcards"
          desc={`${topic.flashcards.length} cards · drill mode`}
          icon={Layers}
          primary
        />
        <ActionCard
          href={`/subjects/${subject.id}/topics/${topic.id}/quiz`}
          title="Take quiz"
          desc={`${topic.quiz.questions.length} questions · multiple choice`}
          icon={ListChecks}
        />
        <ActionCard
          href={topic.lessons[0] ? `/subjects/${subject.id}/topics/${topic.id}/lessons/${topic.lessons[0].id}` : "#"}
          title="Read first lesson"
          desc={topic.lessons[0]?.title ?? "No lessons"}
          icon={FileText}
          disabled={!topic.lessons[0]}
        />
      </section>

      {/* Lessons */}
      <section>
        <div className="flex items-end justify-between mb-4">
          <div>
            <h2 className="text-lg font-medium tracking-tight">Lessons</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              {topic.lessons.length} lessons in this topic
            </p>
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-card divide-y divide-border overflow-hidden">
          {topic.lessons.map((l, i) => (
            <Link
              key={l.id}
              href={`/subjects/${subject.id}/topics/${topic.id}/lessons/${l.id}`}
              className="flex items-center gap-4 px-5 py-4 hover:bg-accent/50 transition-colors group"
            >
              <span className="font-mono text-xs text-muted-foreground w-6 text-right">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium tracking-tight">{l.title}</div>
                <div className="text-[11px] text-muted-foreground flex items-center gap-2 mt-0.5">
                  <Clock className="size-3" />
                  {l.estMinutes ?? 5} min read · {l.content.length} sections
                </div>
              </div>
              <ArrowRight className="size-4 text-muted-foreground group-hover:translate-x-0.5 group-hover:text-foreground transition-all" />
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}

function ActionCard({
  href,
  title,
  desc,
  icon: Icon,
  primary,
  disabled,
}: {
  href: string
  title: string
  desc: string
  icon: React.ComponentType<{ className?: string }>
  primary?: boolean
  disabled?: boolean
}) {
  const cls = primary
    ? "bg-foreground text-background border-foreground"
    : "bg-card text-foreground border-border hover:bg-accent/50"
  if (disabled)
    return (
      <div className="rounded-2xl border border-dashed border-border p-5 opacity-50 cursor-not-allowed">
        <Icon className="size-5" />
        <div className="mt-4 text-sm font-medium">{title}</div>
        <div className="text-xs text-muted-foreground mt-0.5">{desc}</div>
      </div>
    )
  return (
    <Link
      href={href}
      className={`group rounded-2xl border p-5 transition-colors flex flex-col gap-3 ${cls}`}
    >
      <div className="flex items-center justify-between">
        <Icon className="size-5" />
        <ArrowRight className="size-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
      </div>
      <div>
        <div className="text-sm font-medium">{title}</div>
        <div className={`text-xs mt-0.5 ${primary ? "text-background/70" : "text-muted-foreground"}`}>
          {desc}
        </div>
      </div>
    </Link>
  )
}
