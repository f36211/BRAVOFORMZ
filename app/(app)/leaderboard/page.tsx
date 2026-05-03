"use client"

import { useState, useEffect } from "react"
import { motion } from "motion/react"
import { Trophy, Medal, Crown, User, TrendingUp, Target, Clock, Check, Heart, MessageCircle } from "lucide-react"
import { AnimatePresence } from "motion/react"
import { appData } from "@/lib/data"
import { useStore } from "@/lib/store"
import useSWR from "swr"

type LeaderboardEntry = {
  rank: number
  username: string
  score: number
  correct_answers: number
  total_questions: number
  subjects_attempted?: number
  topics_completed?: number
  created_at?: string
}

const fetcher = (url: string) => fetch(url).then(res => res.json())

function RankBadge({ rank }: { rank: number }) {
  if (rank === 1) {
    return (
      <div className="size-8 rounded-lg bg-amber-500/20 text-amber-600 grid place-items-center">
        <Crown className="size-4" />
      </div>
    )
  }
  if (rank === 2) {
    return (
      <div className="size-8 rounded-lg bg-slate-400/20 text-slate-500 grid place-items-center">
        <Medal className="size-4" />
      </div>
    )
  }
  if (rank === 3) {
    return (
      <div className="size-8 rounded-lg bg-orange-400/20 text-orange-500 grid place-items-center">
        <Medal className="size-4" />
      </div>
    )
  }
  return (
    <div className="size-8 rounded-lg bg-muted text-muted-foreground grid place-items-center font-mono text-xs">
      {rank}
    </div>
  )
}

function ReactionPicker({ toUser, fromUser }: { toUser: string, fromUser: string | null }) {
  const [isOpen, setIsOpen] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const emojis = ["🔥", "👏", "🙌", "⭐", "🚀"]

  const sendEmoji = async (emoji: string) => {
    if (!fromUser || isSending) return
    setIsSending(true)
    try {
      await fetch('/api/leaderboard/react', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fromUser, toUser, emoji })
      })
      setIsOpen(false)
    } catch (e) {
      console.error(e)
    } finally {
      setIsSending(false)
    }
  }

  if (toUser === fromUser) return null

  return (
    <div className="relative">
      <button 
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          setIsOpen(!isOpen)
        }}
        className="p-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors relative z-10"
      >
        <Heart className={`size-4 ${isOpen ? "fill-red-500 text-red-500" : ""}`} />
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <>
            <div 
              className="fixed inset-0 z-40" 
              onClick={() => setIsOpen(false)} 
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 5 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 5 }}
              className="absolute right-0 bottom-full mb-2 p-1.5 rounded-xl border border-border bg-card shadow-2xl flex gap-1 z-50 min-w-[160px] justify-center"
            >
              {emojis.map(e => (
                <button
                  key={e}
                  onClick={(event) => {
                    event.preventDefault()
                    event.stopPropagation()
                    sendEmoji(e)
                  }}
                  disabled={isSending}
                  className="size-9 grid place-items-center hover:bg-muted rounded-lg transition-colors text-xl active:scale-90"
                >
                  {e}
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

function LeaderboardTable({ 
  data, 
  loading, 
  currentUser 
}: { 
  data: LeaderboardEntry[] | undefined
  loading: boolean
  currentUser: string | null 
}) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 rounded-xl bg-muted/50 animate-pulse" />
        ))}
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border p-10 text-center">
        <Trophy className="size-8 mx-auto text-muted-foreground/50" />
        <p className="mt-3 text-sm text-muted-foreground">
          No scores yet. Be the first to complete a quiz!
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {data.map((entry, i) => {
        const isCurrentUser = entry.username === currentUser
        return (
          <motion.div
            key={`${entry.username}-${i}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className={`flex items-center gap-4 rounded-xl border p-4 transition-colors ${
              isCurrentUser 
                ? "border-foreground/30 bg-foreground/5" 
                : "border-border bg-card hover:bg-accent/30"
            }`}
          >
            <RankBadge rank={entry.rank} />
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium truncate">
                  {entry.username}
                </span>
                {isCurrentUser && (
                  <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                    You
                  </span>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2 mt-1.5">
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  {entry.subjects_attempted !== undefined && (
                    <span>{entry.subjects_attempted} subjects</span>
                  )}
                  {entry.topics_completed !== undefined && (
                    <span>{entry.topics_completed} topics</span>
                  )}
                </div>
                
                {/* Emoji Reactions Display */}
                {entry.reactions && entry.reactions.length > 0 && (
                  <div className="flex flex-wrap gap-1 items-center">
                    <span className="text-muted-foreground mx-1">·</span>
                    {entry.reactions.map((r, ri) => (
                      <span 
                        key={ri} 
                        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-muted/50 border border-border/50 text-[10px]"
                        title={`${r.count} orang memberikan ${r.emoji}`}
                      >
                        <span>{r.emoji}</span>
                        <span className="font-mono font-medium">{r.count}</span>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-lg font-medium tabular-nums">{entry.score}%</div>
                <div className="text-[10px] text-muted-foreground font-mono">AVG SCORE</div>
              </div>
              <ReactionPicker toUser={entry.username} fromUser={currentUser} />
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

function UserStats({ username }: { username: string }) {
  const { data, isLoading } = useSWR(
    username ? `/api/leaderboard/user/${encodeURIComponent(username)}` : null,
    fetcher
  )

  if (isLoading || !data?.data) {
    return null
  }

  const stats = data.data

  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <div className="size-10 rounded-xl border border-border bg-background grid place-items-center">
          <User className="size-5 text-muted-foreground" />
        </div>
        <div>
          <h2 className="text-lg font-medium tracking-tight">{username}</h2>
          <p className="text-xs text-muted-foreground">Statistik Kamu</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Stat label="Rata-rata" value={stats.average_score ?? 0} unit="%" icon={Target} />
        <Stat label="Terbaik" value={stats.highest_score ?? 0} unit="%" icon={TrendingUp} />
        <Stat label="Topik" value={stats.topics_completed ?? 0} icon={Trophy} />
        <Stat label="Benar" value={stats.total_correct ?? 0} total={stats.total_questions ?? 0} icon={Check} />
      </div>
    </div>
  )
}

function Stat({ 
  label, 
  value, 
  unit,
  total,
  icon: Icon 
}: { 
  label: string; 
  value: number; 
  unit?: string;
  total?: number;
  icon: any 
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-3">
      <div className="flex items-center justify-between text-muted-foreground mb-2">
        <span className="text-[10px] font-mono uppercase tracking-[0.14em]">{label}</span>
        <Icon className="size-3.5" />
      </div>
      <div className="flex items-baseline gap-0.5">
        <span className="text-2xl font-medium tracking-tight tabular-nums">{value}</span>
        {unit && <span className="text-xs text-muted-foreground font-medium">{unit}</span>}
        {total !== undefined && (
          <span className="text-xs text-muted-foreground font-medium ml-1">/ {total}</span>
        )}
      </div>
    </div>
  )
}

export default function LeaderboardPage() {
  const { username } = useStore()
  const [subjectFilter, setSubjectFilter] = useState<"global" | string>("global")
  const [topicFilter, setTopicFilter] = useState<string>("all")
  
  const subjects = appData.subjects
  const selectedSubject = subjects.find(s => s.id === subjectFilter)
  const topics = selectedSubject?.topics || []

  // Reset topic filter when subject changes
  useEffect(() => {
    setTopicFilter("all")
  }, [subjectFilter])

  const apiUrl = subjectFilter === "global" 
    ? "/api/leaderboard?limit=20" 
    : topicFilter === "all"
      ? `/api/leaderboard?subjectId=${subjectFilter}&limit=20`
      : `/api/leaderboard?subjectId=${subjectFilter}&topicId=${topicFilter}&limit=20`

  const { data, isLoading } = useSWR(apiUrl, fetcher)

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="size-12 rounded-2xl border border-border bg-card grid place-items-center">
          <Trophy className="size-6 text-foreground" />
        </div>
        <div>
          <h1 className="text-2xl font-medium tracking-tight">Papan Peringkat</h1>
          <p className="text-sm text-muted-foreground">Prestasi terbaik di semua kuis</p>
        </div>
      </div>

      {/* User Stats */}
      {username && <UserStats username={username} />}

      {/* Filters */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide">
          <button
            onClick={() => setSubjectFilter("global")}
            className={`shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              subjectFilter === "global"
                ? "bg-foreground text-background shadow-sm"
                : "bg-muted text-muted-foreground hover:bg-accent/70"
            }`}
          >
            Global
          </button>
          {subjects.map((subject) => (
            <button
              key={subject.id}
              onClick={() => setSubjectFilter(subject.id)}
              className={`shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                subjectFilter === subject.id
                  ? "bg-foreground text-background shadow-sm"
                  : "bg-muted text-muted-foreground hover:bg-accent/70"
              }`}
            >
              {subject.name}
            </button>
          ))}
        </div>

        {/* Topic Filter - Only show when a subject is selected */}
        {subjectFilter !== "global" && topics.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide"
          >
            <button
              onClick={() => setTopicFilter("all")}
              className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                topicFilter === "all"
                  ? "border-foreground bg-foreground/5 text-foreground"
                  : "border-border bg-muted/30 text-muted-foreground hover:text-foreground"
              }`}
            >
              Semua Topik
            </button>
            {topics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => setTopicFilter(topic.id)}
                className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  topicFilter === topic.id
                    ? "border-foreground bg-foreground/5 text-foreground"
                    : "border-border bg-muted/30 text-muted-foreground hover:text-foreground"
                }`}
              >
                {topic.title}
              </button>
            ))}
          </motion.div>
        )}
      </div>

      {/* Leaderboard Table */}
      <div className="relative">
        <LeaderboardTable 
          data={data?.data} 
          loading={isLoading} 
          currentUser={username} 
        />
      </div>
    </div>
  )
}
