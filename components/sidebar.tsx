"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "motion/react"
import { Home, BookOpen, Bookmark, Settings, Trophy, Sparkles, Menu } from "lucide-react"
import { useState } from "react"
import { appData } from "@/lib/data"
import { cn } from "@/lib/utils"

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/bookmarks", label: "Bookmarks", icon: Bookmark },
  { href: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)

  const inner = (
    <>
      <div className="px-5 py-5 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2 group">
          <div className="size-7 rounded-lg bg-foreground grid place-items-center text-background">
            <span className="font-mono text-[11px] tracking-tight">BF</span>
          </div>
          <div className="leading-tight">
            <div className="text-sm font-medium tracking-tight">{appData.app.name}</div>
            <div className="text-[10px] text-muted-foreground font-mono">Class {appData.app.class}</div>
          </div>
        </Link>
      </div>

      <nav className="px-3 space-y-0.5">
        {NAV.map((item) => {
          const active =
            item.href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(item.href)
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.soon ? "#" : item.href}
              onClick={() => setMobileOpen(false)}
              aria-disabled={item.soon}
              className={cn(
                "relative flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors",
                active
                  ? "bg-accent text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/60",
                item.soon && "opacity-50 cursor-not-allowed",
              )}
            >
              {active && (
                <motion.span
                  layoutId="sb-active"
                  className="absolute inset-0 rounded-lg bg-accent -z-0"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <Icon className="size-4 relative z-10" />
              <span className="relative z-10">{item.label}</span>
              {item.soon && (
                <span className="ml-auto relative z-10 text-[10px] font-mono text-muted-foreground">
                  soon
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      <div className="px-5 mt-6 mb-2 flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-[0.14em] text-muted-foreground font-mono">
          Subjects
        </span>
        <span className="text-[10px] text-muted-foreground font-mono">{appData.subjects.length}</span>
      </div>

      <div className="px-3 space-y-0.5 overflow-y-auto scrollbar-thin">
        {appData.subjects.map((s) => {
          const href = `/subjects/${s.id}`
          const active = pathname.startsWith(href)
          return (
            <Link
              key={s.id}
              href={href}
              onClick={() => setMobileOpen(false)}
              className={cn(
                "flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-sm transition-colors",
                active
                  ? "bg-accent text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/60",
              )}
            >
              <span className="size-1.5 rounded-full bg-foreground/60" />
              <span className="truncate">{s.name}</span>
              <span className="ml-auto text-[10px] font-mono text-muted-foreground">
                {s.topics?.length || 0}
              </span>
            </Link>
          )
        })}
      </div>

      <div className="mt-auto p-3">
        <div className="rounded-xl border border-border bg-card p-3">
          <div className="flex items-center gap-2 text-xs">
            <Sparkles className="size-3.5" />
            <span className="font-medium">Tip</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground leading-relaxed">
            Press{" "}
            <kbd className="rounded border border-border bg-muted px-1 py-px font-mono text-[10px]">⌘K</kbd>{" "}
            to search anything.
          </p>
        </div>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(true)}
        aria-label="Open menu"
        className="md:hidden fixed top-3 left-3 z-40 size-9 grid place-items-center rounded-lg border border-border bg-card"
      >
        <Menu className="size-4" />
      </button>

      {/* Desktop sidebar */}
      <aside className="hidden md:flex fixed inset-y-0 left-0 w-[260px] flex-col border-r border-border bg-sidebar">
        {inner}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-foreground/20 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <motion.aside
            initial={{ x: -260 }}
            animate={{ x: 0 }}
            exit={{ x: -260 }}
            className="absolute inset-y-0 left-0 w-[260px] flex flex-col bg-sidebar border-r border-border"
          >
            {inner}
          </motion.aside>
        </div>
      )}
    </>
  )
}
