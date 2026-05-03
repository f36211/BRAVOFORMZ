"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Search, ChevronRight } from "lucide-react"
import { useStore } from "@/lib/store"
import { appData } from "@/lib/data"

function getCrumbs(pathname: string) {
  const parts = pathname.split("/").filter(Boolean)
  const crumbs: { label: string; href: string }[] = []
  if (parts[0] === "subjects" && parts[1]) {
    const subj = appData.subjects.find((s) => s.id === parts[1])
    if (subj) {
      crumbs.push({ label: "Subjects", href: "/dashboard" })
      crumbs.push({ label: subj.name, href: `/subjects/${subj.id}` })
      if (parts[2] === "topics" && parts[3]) {
        const topic = subj.topics.find((t) => t.id === parts[3])
        if (topic) {
          crumbs.push({
            label: topic.title,
            href: `/subjects/${subj.id}/topics/${topic.id}`,
          })
          if (parts[4] === "lessons" && parts[5]) {
            const lesson = topic.lessons.find((l) => l.id === parts[5])
            if (lesson)
              crumbs.push({
                label: lesson.title,
                href: `/subjects/${subj.id}/topics/${topic.id}/lessons/${lesson.id}`,
              })
          } else if (parts[4] === "flashcards") {
            crumbs.push({
              label: "Flashcards",
              href: `/subjects/${subj.id}/topics/${topic.id}/flashcards`,
            })
          } else if (parts[4] === "quiz") {
            crumbs.push({
              label: "Quiz",
              href: `/subjects/${subj.id}/topics/${topic.id}/quiz`,
            })
          }
        }
      }
    }
  } else if (parts[0]) {
    crumbs.push({
      label: parts[0].charAt(0).toUpperCase() + parts[0].slice(1),
      href: `/${parts[0]}`,
    })
  }
  return crumbs
}

export function Topbar({ onOpenSearch }: { onOpenSearch: () => void }) {
  const { username } = useStore()
  const pathname = usePathname()
  const crumbs = getCrumbs(pathname)
  const initial = (username ?? "?").charAt(0).toUpperCase()

  return (
    <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="h-14 px-4 md:px-8 flex items-center gap-4">
        <nav
          aria-label="Breadcrumb"
          className="hidden md:flex items-center gap-1.5 text-sm min-w-0 flex-1"
        >
          {crumbs.length === 0 ? (
            <span className="text-muted-foreground">Dashboard</span>
          ) : (
            crumbs.map((c, i) => (
              <span key={c.href} className="flex items-center gap-1.5 min-w-0">
                {i > 0 && <ChevronRight className="size-3.5 text-muted-foreground shrink-0" />}
                <Link
                  href={c.href}
                  className={
                    i === crumbs.length - 1
                      ? "text-foreground font-medium truncate"
                      : "text-muted-foreground hover:text-foreground truncate"
                  }
                >
                  {c.label}
                </Link>
              </span>
            ))
          )}
        </nav>

        <div className="md:hidden flex-1 pl-10" />

        <button
          onClick={onOpenSearch}
          className="flex items-center gap-2 h-9 px-3 rounded-lg border border-border bg-card hover:bg-accent transition-colors text-sm text-muted-foreground min-w-[180px] md:min-w-[280px]"
        >
          <Search className="size-3.5" />
          <span className="flex-1 text-left">Search…</span>
          <kbd className="hidden md:inline-flex font-mono text-[10px] text-muted-foreground border border-border rounded px-1 py-px bg-muted">
            ⌘K
          </kbd>
        </button>

        <div className="flex items-center gap-2 pl-2 border-l border-border">
          <div className="hidden md:block text-right leading-tight">
            <div className="text-xs font-medium">{username}</div>
            <div className="text-[10px] text-muted-foreground font-mono">student</div>
          </div>
          <div className="size-8 rounded-full bg-foreground text-background grid place-items-center text-xs font-medium">
            {initial}
          </div>
        </div>
      </div>
    </header>
  )
}
