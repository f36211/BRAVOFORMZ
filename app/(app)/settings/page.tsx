"use client"

import { useRouter } from "next/navigation"
import { motion } from "motion/react"
import { LogOut } from "lucide-react"
import { useStore } from "@/lib/store"
import { appData } from "@/lib/data"

export default function SettingsPage() {
  const router = useRouter()
  const { username, setUsername, settings, updateSetting, bookmarks, progress } = useStore()

  const studied = Object.values(progress).filter((v) => v > 0).length

  function logout() {
    setUsername(null)
    router.push("/login")
  }

  function clearProgress() {
    if (confirm("Reset all progress and bookmarks? This cannot be undone.")) {
      try {
        localStorage.removeItem("bravoformz-state-v1")
      } catch (e) {
        console.log("[v0] clear error:", e)
      }
      window.location.reload()
    }
  }

  return (
    <div className="space-y-8 max-w-2xl">
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
          Preferences
        </div>
        <h1 className="mt-1 text-3xl md:text-4xl font-medium tracking-tight">Settings</h1>
      </motion.header>

      {/* Profile */}
      <Section title="Profile">
        <Row label="Display name" desc="Shown across the app">
          <input
            value={username ?? ""}
            onChange={(e) => setUsername(e.target.value)}
            className="h-9 rounded-lg border border-border bg-card px-3 text-sm outline-none focus:border-foreground transition-colors w-44"
          />
        </Row>
        <Row label="Class" desc="Read-only">
          <span className="font-mono text-xs text-muted-foreground">{appData.app.class}</span>
        </Row>
      </Section>

      {/* Preferences */}
      <Section title="UI Preferences">
        <Row
          label="Reduce motion"
          desc="Minimize animations and transitions"
        >
          <Toggle
            checked={settings.reducedMotion}
            onChange={(v) => updateSetting("reducedMotion", v)}
          />
        </Row>
        <Row
          label="Show keyboard hints"
          desc="Display shortcut hints in flashcards"
        >
          <Toggle
            checked={settings.showKeyboardHints}
            onChange={(v) => updateSetting("showKeyboardHints", v)}
          />
        </Row>
        <Row label="Compact sidebar" desc="Use a denser sidebar layout">
          <Toggle
            checked={settings.compactSidebar}
            onChange={(v) => updateSetting("compactSidebar", v)}
          />
        </Row>
      </Section>

      {/* Stats */}
      <Section title="Your activity">
        <Row label="Topics in progress">
          <span className="font-mono text-sm">{studied}</span>
        </Row>
        <Row label="Bookmarks">
          <span className="font-mono text-sm">{bookmarks.length}</span>
        </Row>
      </Section>

      {/* Danger */}
      <Section title="Account">
        <Row label="Reset all data" desc="Clears progress, bookmarks, and session">
          <button
            onClick={clearProgress}
            className="text-xs font-medium px-3 py-1.5 rounded-lg border border-border hover:bg-accent transition-colors"
          >
            Reset
          </button>
        </Row>
        <Row label="Sign out" desc="Return to the login screen">
          <button
            onClick={logout}
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-foreground text-background hover:bg-foreground/90 transition-colors"
          >
            <LogOut className="size-3" />
            Log out
          </button>
        </Row>
      </Section>

      <p className="pt-4 text-[11px] font-mono text-muted-foreground">
        BravoFormz v{appData.app.version}
      </p>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-[10px] font-mono uppercase tracking-[0.14em] text-muted-foreground mb-2">
        {title}
      </h2>
      <div className="rounded-2xl border border-border bg-card divide-y divide-border overflow-hidden">
        {children}
      </div>
    </section>
  )
}

function Row({
  label,
  desc,
  children,
}: {
  label: string
  desc?: string
  children: React.ReactNode
}) {
  return (
    <div className="px-4 py-3.5 flex items-center justify-between gap-4">
      <div className="min-w-0">
        <div className="text-sm font-medium">{label}</div>
        {desc && <div className="text-xs text-muted-foreground mt-0.5">{desc}</div>}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  )
}

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative h-6 w-10 rounded-full transition-colors ${
        checked ? "bg-foreground" : "bg-muted border border-border"
      }`}
    >
      <span
        className={`absolute top-0.5 size-5 rounded-full bg-background shadow-sm transition-transform ${
          checked ? "translate-x-[18px]" : "translate-x-0.5"
        }`}
      />
    </button>
  )
}
