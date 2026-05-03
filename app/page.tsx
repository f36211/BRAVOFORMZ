"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useStore } from "@/lib/store"

export default function RootPage() {
  const router = useRouter()
  const { username, hydrated } = useStore()

  useEffect(() => {
    if (!hydrated) return
    router.replace(username ? "/dashboard" : "/login")
  }, [hydrated, username, router])

  return (
    <div className="min-h-svh grid place-items-center text-muted-foreground">
      <div className="flex items-center gap-3 text-sm">
        <span className="size-2 rounded-full bg-foreground animate-pulse" />
        Loading BravoFormz…
      </div>
    </div>
  )
}
