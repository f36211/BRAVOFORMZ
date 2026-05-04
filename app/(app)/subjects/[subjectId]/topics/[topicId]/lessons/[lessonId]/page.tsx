"use client"

import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { useEffect } from "react"
import { motion } from "motion/react"
import { ArrowLeft, ArrowRight, Clock, Layers, ListChecks } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"
import { LessonContent } from "@/components/lesson-content"

export default function LessonPage() {
  const { subjectId, topicId, lessonId } = useParams<{
    subjectId: string
    topicId: string
    lessonId: string
  }>()
  const subject = appData.subjects.find((s) => s.id === subjectId)
  const topic = subject?.topics.find((t) => t.id === topicId)
  const lesson = topic?.lessons.find((l) => l.id === lessonId)
  const { setProgress } = useStore()

  useEffect(() => {
    if (!subject || !topic) return
    // Mark some progress on view
    const idx = topic.lessons.findIndex((l) => l.id === lessonId)
    const pct = Math.round(((idx + 1) / Math.max(1, topic.lessons.length)) * 70)
    setProgress(subject.id, topic.id, pct)
  }, [subject, topic, lessonId, setProgress])

  if (!subject || !topic || !lesson) return notFound()

  const idx = topic.lessons.findIndex((l) => l.id === lesson.id)
  const prev = topic.lessons[idx - 1]
  const next = topic.lessons[idx + 1]

  // Find next topic if this is the last lesson
  const topicIdx = subject.topics.findIndex((t) => t.id === topic.id)
  const nextTopic = subject.topics[topicIdx + 1]

  return (
    <div className="space-y-8">
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="space-y-3"
      >
        <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
          <Link href={`/subjects/${subject.id}`} className="hover:text-foreground">
            {subject.name}
          </Link>
          <span>·</span>
          <Link href={`/subjects/${subject.id}/topics/${topic.id}`} className="hover:text-foreground">
            {topic.title}
          </Link>
        </div>
        <h1 className="text-3xl md:text-4xl font-medium tracking-tight text-balance">
          {lesson.title}
        </h1>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <Clock className="size-3.5" />
            {lesson.estMinutes ?? 5} min read
          </span>
          <span>·</span>
          <span className="font-mono">
            Lesson {idx + 1} of {topic.lessons.length}
          </span>
        </div>
      </motion.header>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.05 }}
      >
        <LessonContent blocks={lesson.content} />
      </motion.div>

      {/* Bottom nav */}
      <div className="border-t border-border pt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
        {prev ? (
          <Link
            href={`/subjects/${subject.id}/topics/${topic.id}/lessons/${prev.id}`}
            className="flex items-center gap-3 rounded-xl border border-border px-4 py-3 hover:bg-accent/50 transition-colors group"
          >
            <ArrowLeft className="size-4 text-muted-foreground group-hover:-translate-x-0.5 group-hover:text-foreground transition-all" />
            <div className="min-w-0">
              <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
                Previous
              </div>
              <div className="text-sm font-medium truncate">{prev.title}</div>
            </div>
          </Link>
        ) : (
          <div />
        )}
        {next ? (
          <Link
            href={`/subjects/${subject.id}/topics/${topic.id}/lessons/${next.id}`}
            className="flex items-center gap-3 rounded-xl border border-border px-4 py-3 hover:bg-accent/50 transition-colors group justify-end text-right"
          >
            <div className="min-w-0">
              <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
                Next
              </div>
              <div className="text-sm font-medium truncate">{next.title}</div>
            </div>
            <ArrowRight className="size-4 text-muted-foreground group-hover:translate-x-0.5 group-hover:text-foreground transition-all" />
          </Link>
        ) : (
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
            {nextTopic && (
              <Link
                href={`/subjects/${subject.id}/topics/${nextTopic.id}`}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
              >
                Next Topic: {nextTopic.title}
                <ArrowRight className="size-4" />
              </Link>
            )}
            <Link
              href={`/subjects/${subject.id}/topics/${topic.id}/flashcards`}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-foreground text-background px-4 py-3 text-sm font-medium hover:bg-foreground/90 transition-colors"
            >
              <Layers className="size-4" />
              Practice flashcards
            </Link>
            <Link
              href={`/subjects/${subject.id}/topics/${topic.id}/quiz`}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border px-4 py-3 text-sm font-medium hover:bg-accent transition-colors"
            >
              <ListChecks className="size-4" />
              Take quiz
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
