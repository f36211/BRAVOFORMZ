"use client"

import { useState, useEffect } from "react"
import { motion } from "motion/react"
import { Trophy, Medal, Crown, User, TrendingUp, Target, Clock } from "lucide-react"
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
              <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                {entry.subjects_attempted !== undefined && (
                  <span>{entry.subjects_attempted} subjects</span>
                )}
                {entry.topics_completed !== undefined && (
                  <span>{entry.topics_completed} topics</span>
                )}
                {entry.correct_answers !== undefined && entry.total_questions !== undefined && (
                  <span>{entry.correct_answers}/{entry.total_questions} correct</span>
                )}
              </div>
            </div>

            <div className="text-right">
              <div className="text-lg font-medium tabular-nums">{entry.score}%</div>
              <div className="text-[10px] text-muted-foreground font-mono">AVG SCORE</div>
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
    <div className="rounded-2xl border border-border bg-card p-6 mb-8">
      <div className="flex items-center gap-3 mb-4">
        <div className="size-10 rounded-xl bg-foreground text-background grid place-items-center">
          <User className="size-5" />
        </div>
        <div>
          <h2 className="font-medium">{username}</h2>
          <p className="text-xs text-muted-foreground">Your Statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-xl bg-muted/50 p-3">
          <Target className="size-4 text-muted-foreground mb-1" />
          <div className="text-xl font-medium tabular-nums">{stats.average_score ?? 0}%</div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase">Avg Score</div>
        </div>
        <div className="rounded-xl bg-muted/50 p-3">
          <TrendingUp className="size-4 text-muted-foreground mb-1" />
          <div className="text-xl font-medium tabular-nums">{stats.highest_score ?? 0}%</div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase">Best</div>
        </div>
        <div className="rounded-xl bg-muted/50 p-3">
          <Trophy className="size-4 text-muted-foreground mb-1" />
          <div className="text-xl font-medium tabular-nums">{stats.topics_completed ?? 0}</div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase">Topics</div>
        </div>
        <div className="rounded-xl bg-muted/50 p-3">
          <Clock className="size-4 text-muted-foreground mb-1" />
          <div className="text-xl font-medium tabular-nums">
            {stats.total_correct ?? 0}/{stats.total_questions ?? 0}
          </div>
          <div className="text-[10px] text-muted-foreground font-mono uppercase">Correct</div>
        </div>
      </div>
    </div>
  )
}

export default function LeaderboardPage() {
  const { username } = useStore()
  const [filter, setFilter] = useState<"global" | string>("global")
  
  const subjects = appData.subjects

  const apiUrl = filter === "global" 
    ? "/api/leaderboard?limit=20" 
    : `/api/leaderboard?subjectId=${filter}&limit=20`

  const { data, isLoading } = useSWR(apiUrl, fetcher)

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div className="size-12 rounded-2xl bg-foreground text-background grid place-items-center">
          <Trophy className="size-6" />
        </div>
        <div>
          <h1 className="text-2xl font-medium tracking-tight">Leaderboard</h1>
          <p className="text-sm text-muted-foreground">Top performers across all quizzes</p>
        </div>
      </div>

      {/* User Stats */}
      {username && <UserStats username={username} />}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
        <button
          onClick={() => setFilter("global")}
          className={`shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === "global"
              ? "bg-foreground text-background"
              : "bg-muted text-muted-foreground hover:text-foreground"
          }`}
        >
          Global
        </button>
        {subjects.map((subject) => (
          <button
            key={subject.id}
            onClick={() => setFilter(subject.id)}
            className={`shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === subject.id
                ? "bg-foreground text-background"
                : "bg-muted text-muted-foreground hover:text-foreground"
            }`}
          >
            {subject.name}
          </button>
        ))}
      </div>

      {/* Leaderboard */}
      <LeaderboardTable 
        data={data?.data} 
        loading={isLoading} 
        currentUser={username} 
      />
    </div>
  )
}
