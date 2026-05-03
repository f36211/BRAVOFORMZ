"use client"

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react"

type ProgressMap = Record<string, number> // key: `${subjectId}:${topicId}` -> 0..100

type Settings = {
  reducedMotion: boolean
  showKeyboardHints: boolean
  compactSidebar: boolean
}

type StoreState = {
  username: string | null
  setUsername: (name: string | null) => void
  bookmarks: string[] // `${subjectId}:${topicId}`
  toggleBookmark: (subjectId: string, topicId: string) => void
  isBookmarked: (subjectId: string, topicId: string) => boolean
  progress: ProgressMap
  setProgress: (subjectId: string, topicId: string, value: number) => void
  getSubjectProgress: (subjectId: string, topicIds: string[]) => number
  settings: Settings
  updateSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void
  hydrated: boolean
}

const StoreContext = createContext<StoreState | null>(null)

const STORAGE_KEY = "bravoformz-state-v1"

type Persisted = {
  username: string | null
  bookmarks: string[]
  progress: ProgressMap
  settings: Settings
}

const defaultSettings: Settings = {
  reducedMotion: false,
  showKeyboardHints: true,
  compactSidebar: false,
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [hydrated, setHydrated] = useState(false)
  const [username, setUsernameState] = useState<string | null>(null)
  const [bookmarks, setBookmarks] = useState<string[]>([])
  const [progress, setProgressState] = useState<ProgressMap>({})
  const [settings, setSettings] = useState<Settings>(defaultSettings)

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const parsed: Persisted = JSON.parse(raw)
        setUsernameState(parsed.username ?? null)
        setBookmarks(parsed.bookmarks ?? [])
        setProgressState(parsed.progress ?? {})
        setSettings({ ...defaultSettings, ...(parsed.settings ?? {}) })
      }
    } catch (e) {
      console.log("[v0] store hydrate error:", e)
    }
    setHydrated(true)
  }, [])

  useEffect(() => {
    if (!hydrated) return
    const data: Persisted = { username, bookmarks, progress, settings }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (e) {
      console.log("[v0] store persist error:", e)
    }
  }, [username, bookmarks, progress, settings, hydrated])

  const setUsername = (name: string | null) => setUsernameState(name)

  const key = (s: string, t: string) => `${s}:${t}`

  const toggleBookmark = useCallback((subjectId: string, topicId: string) => {
    const k = key(subjectId, topicId)
    setBookmarks((prev) => (prev.includes(k) ? prev.filter((b) => b !== k) : [...prev, k]))
  }, [])

  const isBookmarked = useCallback((subjectId: string, topicId: string) => bookmarks.includes(key(subjectId, topicId)), [bookmarks])

  const setProgress = useCallback((subjectId: string, topicId: string, value: number) => {
    const k = key(subjectId, topicId)
    setProgressState((prev) => ({ ...prev, [k]: Math.max(prev[k] ?? 0, Math.min(100, Math.round(value))) }))
  }, [])

  const getSubjectProgress = useCallback((subjectId: string, topicIds: string[]) => {
    if (topicIds.length === 0) return 0
    const sum = topicIds.reduce((acc, tid) => acc + (progress[key(subjectId, tid)] ?? 0), 0)
    return Math.round(sum / topicIds.length)
  }, [progress])

  const updateSetting = useCallback(<K extends keyof Settings>(k: K, v: Settings[K]) => {
    setSettings((prev) => ({ ...prev, [k]: v }))
  }, [])

  return (
    <StoreContext.Provider
      value={{
        username,
        setUsername,
        bookmarks,
        toggleBookmark,
        isBookmarked,
        progress,
        setProgress,
        getSubjectProgress,
        settings,
        updateSetting,
        hydrated,
      }}
    >
      {children}
    </StoreContext.Provider>
  )
}

export function useStore() {
  const ctx = useContext(StoreContext)
  if (!ctx) throw new Error("useStore must be used within StoreProvider")
  return ctx
}
