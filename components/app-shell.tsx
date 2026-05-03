"use client"

import { useEffect, useState, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { useStore } from "@/lib/store"
import { Sidebar } from "@/components/sidebar"
import { Topbar } from "@/components/topbar"
import { SearchModal } from "@/components/search-modal"

export default function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { username, hydrated } = useStore()
  const [searchOpen, setSearchOpen] = useState(false)

  useEffect(() => {
    if (hydrated && !username) router.replace("/login")
  }, [hydrated, username, router])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        setSearchOpen((o) => !o)
      }
      if (e.key === "Escape") setSearchOpen(false)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  if (!hydrated || !username) {
    return (
      <div className="min-h-svh grid place-items-center text-muted-foreground text-sm">
        <div className="flex items-center gap-3">
          <span className="size-2 rounded-full bg-foreground animate-pulse" />
          Loading BravoFormz…
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-svh bg-background">
      <Sidebar />
      <div className="md:pl-[260px]">
        <Topbar onOpenSearch={() => setSearchOpen(true)} />
        <main className="px-4 md:px-8 py-6 md:py-8 max-w-6xl mx-auto">{children}</main>
      </div>
      <SearchModal open={searchOpen} onOpenChange={setSearchOpen} />
    </div>
  )
}
