"use client"

import Link from "next/link"
import { motion } from "motion/react"
import { ArrowUpRight, BookOpen, Bookmark, Layers, FileText, Sparkles } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"

function greeting() {
  const h = new Date().getHours()
  if (h < 5) return "Still up"
  if (h < 12) return "Good morning"
  if (h < 18) return "Good afternoon"
  return "Good evening"
}

export default function DashboardPage() {
  const { username, getSubjectProgress, bookmarks, progress } = useStore()

  const totalLessons = appData.subjects.reduce(
    (n, s) => n + s.topics.reduce((m, t) => m + t.lessons.length, 0),
    0,
  )
  const totalFlashcards = appData.subjects.reduce(
    (n, s) => n + s.topics.reduce((m, t) => m + t.flashcards.length, 0),
    0,
  )
  const studied = Object.values(progress).filter((v) => v > 0).length

  // Recent: topics with non-zero progress, fallback to first topics
  const recent: { subjectId: string; topicId: string; subject: string; topic: string }[] = []
  for (const s of appData.subjects)
    for (const t of s.topics)
      if (progress[`${s.id}:${t.id}`])
        recent.push({ subjectId: s.id, topicId: t.id, subject: s.name, topic: t.title })

  const quickFlashTopics = appData.subjects
    .flatMap((s) => s.topics.map((t) => ({ s, t })))
    .filter((x) => x.t.flashcards.length > 0)
    .slice(0, 4)

  return (
    <div className="space-y-8">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative overflow-hidden rounded-2xl border border-border bg-card p-6 md:p-8"
      >
        <div className="absolute inset-0 dot-bg opacity-50 pointer-events-none" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-background/60 px-2.5 py-1 text-[11px] text-muted-foreground mb-4">
            <Sparkles className="size-3" />
            <span>{greeting()}</span>
          </div>
          <h1 className="text-2xl md:text-4xl font-medium tracking-tight text-balance">
            Hello, <span className="italic">{username}</span>. Ready to revise?
          </h1>
          <p className="mt-2 text-sm md:text-base text-muted-foreground max-w-xl text-pretty">
            Pick a subject, run through flashcards, or take a quick quiz. Your class —{" "}
            <span className="font-mono">{appData.app.class}</span>.
          </p>

          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
            <Stat label="Subjects" value={appData.subjects.length} icon={BookOpen} />
            <Stat label="Lessons" value={totalLessons} icon={FileText} />
            <Stat label="Flashcards" value={totalFlashcards} icon={Layers} />
            <Stat label="Bookmarks" value={bookmarks.length} icon={Bookmark} />
          </div>
        </div>
      </motion.section>

      {/* Subjects grid */}
      <section>
        <SectionHeader title="Subjects" subtitle="Browse the full catalogue" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {appData.subjects.map((s, i) => {
            const topicIds = s.topics.map((t) => t.id)
            const pct = getSubjectProgress(s.id, topicIds)
            return (
              <motion.div
                key={s.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.04 }}
              >
                <Link
                  href={`/subjects/${s.id}`}
                  className="group block rounded-2xl border border-border bg-card p-5 transition-all hover:bg-accent/40 hover:scale-[1.01] active:scale-[0.99]"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
                        {s.topics.length} topics
                      </div>
                      <h3 className="mt-2 text-lg font-medium tracking-tight group-hover:text-primary transition-colors">{s.name}</h3>
                      <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                        {s.description}
                      </p>
                    </div>
                    {s.image ? (
                      <div className="size-16 rounded-xl border border-border overflow-hidden shrink-0">
                        <img src={s.image} alt={s.name} className="size-full object-cover transition-transform group-hover:scale-110" />
                      </div>
                    ) : (
                      <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                    )}
                  </div>

                  <div className="mt-5">
                    <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground mb-1.5">
                      <span>Progress</span>
                      <span>{pct}%</span>
                    </div>
                    <div className="h-1 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-foreground transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </section>

      {/* Two columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recently studied */}
        <section className="lg:col-span-2">
          <SectionHeader title="Recently studied" subtitle={`${studied} topics in progress`} />
          {recent.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border p-8 text-center">
              <p className="text-sm text-muted-foreground">
                No recent activity yet. Open any topic to start tracking progress.
              </p>
            </div>
          ) : (
            <div className="rounded-2xl border border-border bg-card divide-y divide-border">
              {recent.slice(0, 5).map((r) => {
                const pct = progress[`${r.subjectId}:${r.topicId}`] ?? 0
                return (
                  <Link
                    key={`${r.subjectId}:${r.topicId}`}
                    href={`/subjects/${r.subjectId}/topics/${r.topicId}`}
                    className="flex items-center gap-4 px-4 py-3 hover:bg-accent/50 transition-colors group"
                  >
                    <div className="size-9 rounded-lg border border-border bg-background grid place-items-center">
                      <FileText className="size-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{r.topic}</div>
                      <div className="text-[11px] text-muted-foreground font-mono">
                        {r.subject}
                      </div>
                    </div>
                    <div className="hidden sm:flex items-center gap-2 w-32">
                      <div className="flex-1 h-1 rounded-full bg-muted overflow-hidden">
                        <div className="h-full bg-foreground" style={{ width: `${pct}%` }} />
                      </div>
                      <span className="text-[11px] font-mono text-muted-foreground w-9 text-right">
                        {pct}%
                      </span>
                    </div>
                    <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-foreground" />
                  </Link>
                )
              })}
            </div>
          )}
        </section>

        {/* Quick flashcards */}
        <section>
          <SectionHeader title="Quick flashcards" subtitle="Drill in 60 seconds" />
          <div className="space-y-2">
            {quickFlashTopics.map(({ s, t }) => (
              <Link
                key={`${s.id}-${t.id}`}
                href={`/subjects/${s.id}/topics/${t.id}/flashcards`}
                className="flex items-center gap-3 rounded-xl border border-border bg-card px-3 py-2.5 hover:bg-accent/50 transition-colors group"
              >
                <div className="size-8 rounded-lg bg-foreground text-background grid place-items-center">
                  <Layers className="size-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{t.title}</div>
                  <div className="text-[11px] font-mono text-muted-foreground">
                    {s.name} · {t.flashcards.length} cards
                  </div>
                </div>
                <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-foreground" />
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

function SectionHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="flex items-end justify-between mb-4">
      <div>
        <h2 className="text-lg font-medium tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
      </div>
    </div>
  )
}

function Stat({
  label,
  value,
  icon: Icon,
}: {
  label: string
  value: number
  icon: React.ComponentType<{ className?: string }>
}) {
  return (
    <div className="rounded-xl border border-border bg-background/70 p-3">
      <div className="flex items-center justify-between text-muted-foreground">
        <span className="text-[10px] font-mono uppercase tracking-[0.14em]">{label}</span>
        <Icon className="size-3.5" />
      </div>
      <div className="mt-1 text-2xl font-medium tracking-tight">{value}</div>
    </div>
  )
}
