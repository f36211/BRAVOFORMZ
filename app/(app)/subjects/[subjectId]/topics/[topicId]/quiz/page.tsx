"use client"

import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { useState, useEffect, useRef } from "react"
import { AnimatePresence, motion } from "motion/react"
import { Check, X, ArrowRight, RotateCcw, Trophy, Medal, Clock } from "lucide-react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"

export default function QuizPage() {
  const { subjectId, topicId } = useParams<{ subjectId: string; topicId: string }>()
  const subject = appData.subjects.find((s) => s.id === subjectId)
  const topic = subject?.topics.find((t) => t.id === topicId)
  const { setProgress, username } = useStore()

  const [idx, setIdx] = useState(0)
  const [picked, setPicked] = useState<number | null>(null)
  const [answers, setAnswers] = useState<number[]>([])
  const [done, setDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [rank, setRank] = useState<number | null>(null)
  const [startTime] = useState(() => Date.now())
  const timeRef = useRef(0)

  if (!subject || !topic) return notFound()
  const questions = topic.quiz.questions
  if (questions.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border p-10 text-center">
        <p className="text-sm text-muted-foreground">No quiz available for this topic.</p>
      </div>
    )
  }

  const q = questions[idx]
  const total = questions.length
  const correct = answers.reduce((n, a, i) => (a === questions[i].answer ? n + 1 : n), 0)

  function pick(i: number) {
    if (picked !== null) return
    setPicked(i)
  }

  async function submitToLeaderboard(finalCorrect: number, timeTaken: number) {
    if (!username) return
    
    setSubmitting(true)
    try {
      const response = await fetch('/api/leaderboard/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          subjectId: subject.id,
          topicId: topic.id,
          score: Math.round((finalCorrect / total) * 100),
          correctAnswers: finalCorrect,
          totalQuestions: total,
          timeTakenSeconds: Math.round(timeTaken / 1000),
        }),
      })
      
      const data = await response.json()
      if (data.success && data.data.rank) {
        setRank(data.data.rank)
      }
    } catch (error) {
      console.error('[v0] Failed to submit score:', error)
    } finally {
      setSubmitting(false)
    }
  }

  function nextQ() {
    const newAnswers = [...answers, picked ?? -1]
    setAnswers(newAnswers)
    setPicked(null)
    if (idx >= total - 1) {
      setDone(true)
      const finalCorrect = newAnswers.reduce(
        (n, a, i) => (a === questions[i].answer ? n + 1 : n),
        0,
      )
      setProgress(subject.id, topic.id, Math.round((finalCorrect / total) * 100))
      
      // Calculate time taken and submit to leaderboard
      timeRef.current = Date.now() - startTime
      submitToLeaderboard(finalCorrect, timeRef.current)
    } else {
      setIdx((i) => i + 1)
    }
  }

  function reset() {
    setIdx(0)
    setPicked(null)
    setAnswers([])
    setDone(false)
    setRank(null)
  }

  if (done) {
    const score = Math.round((correct / total) * 100)
    const timeTaken = Math.round(timeRef.current / 1000)
    const minutes = Math.floor(timeTaken / 60)
    const seconds = timeTaken % 60

    return (
      <div className="min-h-[70vh] grid place-items-center">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-lg text-center"
        >
          <div className="mx-auto size-14 rounded-2xl bg-foreground text-background grid place-items-center">
            <Trophy className="size-6" />
          </div>
          <div className="mt-5 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            Quiz complete
          </div>
          <h1 className="mt-2 text-4xl font-medium tracking-tight">{score}%</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            You got <span className="font-medium text-foreground">{correct}</span> of {total} correct.
          </p>

          {/* Time and Rank */}
          <div className="mt-4 flex items-center justify-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Clock className="size-4" />
              <span>{minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`}</span>
            </div>
            {rank !== null && (
              <div className="flex items-center gap-1.5">
                <Medal className="size-4" />
                <span>Rank #{rank}</span>
              </div>
            )}
            {submitting && (
              <span className="text-xs">Submitting...</span>
            )}
          </div>

          {/* Leaderboard link */}
          {username && (
            <div className="mt-4">
              <Link 
                href="/leaderboard" 
                className="text-sm text-muted-foreground hover:text-foreground underline underline-offset-4"
              >
                View full leaderboard
              </Link>
            </div>
          )}

          {/* Review */}
          <div className="mt-8 text-left space-y-2">
            {questions.map((qq, i) => {
              const a = answers[i]
              const ok = a === qq.answer
              return (
                <div
                  key={qq.id}
                  className="rounded-xl border border-border bg-card p-4"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`size-6 grid place-items-center rounded-md text-xs ${
                        ok ? "bg-foreground text-background" : "bg-muted text-foreground"
                      }`}
                    >
                      {ok ? <Check className="size-3" /> : <X className="size-3" />}
                    </div>
                    <div className="flex-1 text-left">
                      <div className="text-sm font-medium">{qq.question}</div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        Your answer:{" "}
                        <span className={ok ? "text-foreground" : "line-through"}>
                          {qq.options[a] ?? "—"}
                        </span>
                        {!ok && (
                          <>
                            {" · Correct: "}
                            <span className="text-foreground">{qq.options[qq.answer]}</span>
                          </>
                        )}
                      </div>
                      {qq.explanation && (
                        <div className="mt-2 text-xs italic text-muted-foreground">
                          {qq.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="mt-8 flex flex-col sm:flex-row gap-2 justify-center">
            <button
              onClick={reset}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-foreground text-background px-4 py-2.5 text-sm font-medium hover:bg-foreground/90 transition-colors"
            >
              <RotateCcw className="size-4" />
              Try again
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

  const progress = ((idx + (picked === null ? 0 : 1)) / total) * 100

  return (
    <div className="min-h-[70vh]">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 mb-8">
        <Link
          href={`/subjects/${subject.id}/topics/${topic.id}`}
          className="size-9 grid place-items-center rounded-lg border border-border hover:bg-accent transition-colors"
          aria-label="Exit quiz"
        >
          <X className="size-4" />
        </Link>
        <div className="flex-1 max-w-md">
          <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground mb-1.5">
            <span>{topic.title} · Quiz</span>
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
        <div className="text-[11px] font-mono text-muted-foreground w-10 text-right">
          {correct}/{idx}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={q.id}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.25 }}
          className="max-w-2xl mx-auto"
        >
          <div className="text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            Question {idx + 1}
          </div>
          <h2 className="mt-2 text-2xl md:text-3xl font-medium tracking-tight text-balance">
            {q.question}
          </h2>

          <div className="mt-6 space-y-2">
            {q.options.map((opt, i) => {
              const isPicked = picked === i
              const isCorrect = i === q.answer
              const showResult = picked !== null
              const variant = !showResult
                ? isPicked
                  ? "border-foreground"
                  : "border-border hover:border-foreground/40 hover:bg-accent/40"
                : isCorrect
                  ? "border-foreground bg-foreground text-background"
                  : isPicked
                    ? "border-border bg-muted text-muted-foreground line-through"
                    : "border-border opacity-60"
              return (
                <button
                  key={i}
                  onClick={() => pick(i)}
                  disabled={picked !== null}
                  className={`w-full text-left rounded-xl border px-4 py-3.5 transition-all flex items-center gap-3 ${variant}`}
                >
                  <span
                    className={`size-6 grid place-items-center rounded-md font-mono text-[11px] shrink-0 ${
                      showResult && isCorrect
                        ? "bg-background text-foreground"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    {String.fromCharCode(65 + i)}
                  </span>
                  <span className="text-sm flex-1">{opt}</span>
                  {showResult && isCorrect && <Check className="size-4" />}
                  {showResult && !isCorrect && isPicked && <X className="size-4" />}
                </button>
              )
            })}
          </div>

          {picked !== null && q.explanation && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 rounded-xl border border-border bg-muted/40 p-4 text-sm"
            >
              <span className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
                Explanation
              </span>
              <p className="mt-1 leading-relaxed">{q.explanation}</p>
            </motion.div>
          )}

          <div className="mt-8 flex justify-end">
            <button
              onClick={nextQ}
              disabled={picked === null}
              className="inline-flex items-center gap-2 rounded-xl bg-foreground text-background px-5 h-11 text-sm font-medium hover:bg-foreground/90 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              {idx >= total - 1 ? "Finish quiz" : "Next question"}
              <ArrowRight className="size-4" />
            </button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
