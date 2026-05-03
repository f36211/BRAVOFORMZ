"use client"

import dynamic from "next/dynamic"
import type { ReactNode } from "react"

const AppShell = dynamic(() => import("@/components/app-shell"), {
  ssr: false,
  loading: () => (
    <div className="min-h-svh grid place-items-center text-muted-foreground text-sm">
      <div className="flex items-center gap-3">
        <span className="size-2 rounded-full bg-foreground animate-pulse" />
        Loading BravoFormz…
      </div>
    </div>
  ),
})

export default function AppLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>
}
