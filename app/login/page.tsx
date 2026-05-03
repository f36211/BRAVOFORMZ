"use client"

import { useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"
import { motion } from "motion/react"
import { ArrowRight, Sparkles } from "lucide-react"
import { useStore } from "@/lib/store"
import { appData } from "@/lib/data"

export default function LoginPage() {
  const router = useRouter()
  const { setUsername } = useStore()
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    setLoading(true)
    setUsername(name.trim())
    setTimeout(() => router.push("/dashboard"), 250)
  }

  return (
    <div className="min-h-svh flex flex-col">
      <div className="absolute inset-0 -z-10 dot-bg opacity-40" />
      <header className="px-6 md:px-10 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="size-7 rounded-lg bg-foreground grid place-items-center text-background">
            <span className="font-mono text-[11px] tracking-tight">BF</span>
          </div>
          <span className="font-medium tracking-tight">BravoFormz</span>
        </div>
        <span className="text-xs text-muted-foreground font-mono">Class {appData.app.class}</span>
      </header>

      <main className="flex-1 grid place-items-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-sm"
        >
          <div className="mb-8 text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground mb-6">
              <Sparkles className="size-3" />
              Private study space
            </div>
            <h1 className="text-3xl md:text-4xl font-medium tracking-tight text-balance">
              Welcome back to <span className="italic">BravoFormz</span>
            </h1>
            <p className="mt-3 text-sm text-muted-foreground text-pretty">
              Enter your name to start revising. No password, no fuss.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <label htmlFor="username" className="sr-only">
              Your name
            </label>
            <div className="relative">
              <input
                id="username"
                name="username"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Abrar"
                autoFocus
                autoComplete="off"
                className="w-full h-12 rounded-xl border border-border bg-card px-4 pr-12 text-sm outline-none transition-colors focus:border-foreground placeholder:text-muted-foreground"
              />
              <button
                type="submit"
                disabled={!name.trim() || loading}
                aria-label="Continue"
                className="absolute right-1.5 top-1.5 grid size-9 place-items-center rounded-lg bg-foreground text-background transition-all hover:bg-foreground/90 disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ArrowRight className="size-4" />
              </button>
            </div>
            <p className="text-[11px] text-muted-foreground text-center font-mono">
              tip: press <kbd className="rounded border border-border bg-muted px-1.5 py-0.5">Enter</kbd> to continue
            </p>
          </form>
        </motion.div>
      </main>

      <footer className="px-6 md:px-10 py-6 text-xs text-muted-foreground flex items-center justify-between">
        <span>© BravoFormz</span>
        <span className="font-mono">v{appData.app.version}</span>
      </footer>
    </div>
  )
}
