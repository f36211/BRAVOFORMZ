"use client"

import { useEffect, useMemo, useState, useRef } from "react"
import { Quote, Lightbulb, Sparkles, Zap, AlertCircle } from "lucide-react"
import type { ContentBlock } from "@/lib/types"
import { MathJax, MathJaxContext } from "better-react-mathjax"
import confetti from "canvas-confetti"
import { motion, AnimatePresence } from "framer-motion"
import { 
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from "recharts"

const mathjaxConfig = {
  loader: { load: ["[tex]/ams"] },
  tex: {
    packages: { "[+]": ["ams"] },
    inlineMath: [["$", "$"], ["\\(", "\\)"]],
    displayMath: [["$$", "$$"], ["\\[", "\\]"]],
  }
}

export function LessonContent({ blocks }: { blocks: ContentBlock[] }) {
  // Build TOC of headings
  const headings = useMemo(
    () =>
      blocks
        .map((b, i) => ({ b, i }))
        .filter((x) => x.b.type === "heading")
        .map((x) => {
          const h = x.b as Extract<ContentBlock, { type: "heading" }>
          return {
            id: `h-${x.i}`,
            text: h.text,
            level: h.level ?? 1,
          }
        }),
    [blocks],
  )

  const [active, setActive] = useState(headings[0]?.id)

  useEffect(() => {
    const els = headings.map((h) => document.getElementById(h.id)).filter(Boolean) as HTMLElement[]
    if (!els.length) return
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible[0]) setActive(visible[0].target.id)
      },
      { rootMargin: "-80px 0px -70% 0px", threshold: 0 },
    )
    els.forEach((el) => obs.observe(el))
    return () => obs.disconnect()
  }, [headings])

  const handleFinish = () => {
    confetti({
      particleCount: 150,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#000000", "#666666", "#ffffff"]
    })
  }

  return (
    <MathJaxContext config={mathjaxConfig}>
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_220px] gap-10">
        <article className="prose-custom max-w-none">
          {blocks.map((block, i) => (
            <Block key={i} block={block} index={i} />
          ))}
          
          <div className="mt-16 pt-8 border-t border-border flex justify-center">
            <button
              onClick={handleFinish}
              className="flex items-center gap-2 px-6 py-3 rounded-full bg-foreground text-background font-medium hover:scale-105 transition-transform active:scale-95"
            >
              <Sparkles className="size-4" />
              Selesaikan Pelajaran
            </button>
          </div>
        </article>

        {headings.length > 0 && (
          <aside className="hidden lg:block">
            <div className="sticky top-20">
              <div className="text-[10px] uppercase tracking-[0.14em] font-mono text-muted-foreground mb-3">
                On this page
              </div>
              <ul className="space-y-1.5 border-l border-border">
                {headings.map((h) => (
                  <li key={h.id} style={{ paddingLeft: 12 + (h.level - 1) * 8 }}>
                    <a
                      href={`#${h.id}`}
                      className={`block text-xs transition-colors -ml-px border-l-2 pl-3 py-0.5 ${
                        active === h.id
                          ? "border-foreground text-foreground"
                          : "border-transparent text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {h.text}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </aside>
        )}
      </div>
    </MathJaxContext>
  )
}

function LazyMathJax({ children, inline = false, display = false }: { children: React.ReactNode, inline?: boolean, display?: boolean }) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(entry.target)
        }
      },
      { rootMargin: "200px" } // Start rendering 200px before it comes into view
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [])

  return (
    <div ref={ref} className={display ? "w-full" : "inline-block min-w-[10px]"}>
      {isVisible ? (
        <MathJax inline={inline}>{children}</MathJax>
      ) : (
        <span className="opacity-0">{children}</span>
      )}
    </div>
  )
}

function Block({ block, index }: { block: ContentBlock; index: number }) {
  switch (block.type) {
    case "heading": {
      const lvl = block.level ?? 1
      const id = `h-${index}`
      if (lvl === 1)
        return (
          <h2 id={id} className="scroll-mt-24 text-2xl md:text-3xl font-medium tracking-tight mt-10 first:mt-0 mb-3">
            <LazyMathJax inline>{block.text}</LazyMathJax>
          </h2>
        )
      if (lvl === 2)
        return (
          <h3 id={id} className="scroll-mt-24 text-lg font-medium tracking-tight mt-8 mb-2">
            <LazyMathJax inline>{block.text}</LazyMathJax>
          </h3>
        )
      return (
        <h4 id={id} className="scroll-mt-24 text-base font-medium tracking-tight mt-6 mb-2">
          <LazyMathJax inline>{block.text}</LazyMathJax>
        </h4>
      )
    }
    case "text":
      return (
        <div className="text-[15px] leading-relaxed text-foreground/90 my-4">
          <LazyMathJax inline>{block.text}</LazyMathJax>
        </div>
      )
    case "quote":
      return (
        <figure className="my-6 rounded-2xl border border-border bg-muted/40 p-5">
          <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            <Quote className="size-3.5" />
            <LazyMathJax inline>{block.text}</LazyMathJax>
          </div>
          {block.translation && (
            <blockquote className="mt-3 text-[15px] leading-relaxed italic text-foreground">
              &ldquo;<LazyMathJax inline>{block.translation}</LazyMathJax>&rdquo;
            </blockquote>
          )}
        </figure>
      )
    case "highlight":
      return (
        <aside className="my-6 rounded-2xl border-l-4 border-foreground bg-accent/60 px-5 py-4 flex gap-3">
          <Lightbulb className="size-4 mt-0.5 shrink-0" />
          <div className="text-sm leading-relaxed">
            <LazyMathJax inline>{block.text}</LazyMathJax>
          </div>
        </aside>
      )
    case "list": {
      const Tag = block.ordered ? "ol" : "ul"
      return (
        <Tag
          className={`my-4 space-y-1.5 text-[15px] leading-relaxed ${
            block.ordered ? "list-decimal" : "list-disc"
          } pl-5`}
        >
          {block.items.map((it, i) => (
            <li key={i}>
              <LazyMathJax inline>{it}</LazyMathJax>
            </li>
          ))}
        </Tag>
      )
    }
    case "table":
      return (
        <div className="my-6 overflow-x-auto rounded-2xl border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted/60">
              <tr>
                {block.headers.map((h, i) => (
                  <th
                    key={i}
                    className="text-left font-medium px-4 py-2.5 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground border-b border-border"
                  >
                    <LazyMathJax inline>{h}</LazyMathJax>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, ri) => (
                <tr key={ri} className="border-b border-border last:border-0">
                  {row.map((cell, ci) => (
                    <td key={ci} className="px-4 py-2.5">
                      <LazyMathJax inline>{String(cell)}</LazyMathJax>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    case "math":
      return (
        <div
          className={`my-4 font-mono text-sm rounded-xl bg-muted/60 px-4 py-3 flex justify-center overflow-x-auto ${
            block.display ? "text-base py-6" : ""
          }`}
        >
          <LazyMathJax display>{`\\(${block.tex}\\)`}</LazyMathJax>
        </div>
      )
    case "chart": {
      if (!block.data || !Array.isArray(block.data) || block.data.length === 0) {
        return (
          <div className="my-8 p-8 rounded-2xl border border-dashed border-border flex items-center justify-center text-xs text-muted-foreground font-mono">
            [Chart data empty or invalid]
          </div>
        )
      }
      const Chart = 
        block.chartType === "bar" ? BarChart :
        block.chartType === "line" ? LineChart : AreaChart
      const DataComp = 
        block.chartType === "bar" ? Bar :
        block.chartType === "line" ? Line : Area

      return (
        <div className="my-8 h-[300px] w-full p-4 rounded-2xl border border-border bg-card">
          <ResponsiveContainer width="100%" height="100%">
            <Chart data={block.data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
              <XAxis 
                dataKey="name" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: "var(--muted-foreground)" }}
              />
              <YAxis 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                tick={{ fill: "var(--muted-foreground)" }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "var(--card)", 
                  borderColor: "var(--border)",
                  borderRadius: "12px",
                  fontSize: "12px"
                }}
              />
              <DataComp 
                type="monotone" 
                dataKey="value" 
                fill="var(--foreground)" 
                stroke="var(--foreground)" 
                strokeWidth={2}
                radius={[4, 4, 0, 0]}
              />
            </Chart>
          </ResponsiveContainer>
        </div>
      )
    }
    case "simulation": {
      switch (block.simType) {
        case "atom": return <AtomSimulation />
        case "cells": return <CellsSimulation />
        case "newton": return <NewtonSimulation />
        case "circuit": return <CircuitSimulation />
        case "magnet": return <MagnetSimulation />
        case "wave": return <WaveSimulation />
        case "piston": return <PistonSimulation />
        case "geometry": return <GeometrySimulation />
        default: return <AtomSimulation />
      }
    }
    case "image":
      return (
        <figure className="my-8 overflow-hidden rounded-2xl border border-border bg-muted/30">
          <img 
            src={block.url} 
            alt={block.caption || "Illustration"} 
            className="w-full h-auto object-cover max-h-[500px]"
          />
          {block.caption && (
            <figcaption className="p-4 text-center text-xs text-muted-foreground italic border-t border-border bg-background/50">
              <LazyMathJax inline>{block.caption}</LazyMathJax>
            </figcaption>
          )}
        </figure>
      )
    default:
      return null
  }
}

function NewtonSimulation() {
  const [force, setForce] = useState(50)
  return (
    <div className="my-8 p-4 md:p-8 rounded-2xl border border-border bg-muted/30 flex flex-col items-center gap-8 relative overflow-hidden min-h-[300px]">
      <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Hukum Newton II (F = m.a)
      </div>
      
      <div className="w-full h-24 border-b-2 border-foreground/20 flex items-end justify-start relative px-4">
        <motion.div 
          className="size-12 md:size-16 bg-foreground rounded-lg flex items-center justify-center text-background font-bold text-[10px] md:text-xs"
          animate={{ x: force * 1.5 }}
          transition={{ type: "spring", stiffness: 50 }}
        >
          10kg
        </motion.div>
        {/* Force Arrow */}
        <motion.div 
          className="absolute h-1 bg-primary origin-left"
          style={{ bottom: 32, left: 16 }}
          animate={{ width: force }}
        />
      </div>

      <div className="w-full max-w-[280px] md:max-w-xs space-y-4">
        <div className="flex justify-between text-[10px] md:text-xs font-mono uppercase tracking-tighter">
          <span>Gaya (F): {force} N</span>
        </div>
        <input 
          type="range" 
          min="0" max="100" 
          value={force} 
          onChange={(e) => setForce(Number(e.target.value))}
          className="w-full accent-foreground cursor-pointer"
        />
      </div>
    </div>
  )
}

function CircuitSimulation() {
  const [isOn, setIsOn] = useState(false)
  return (
    <div className="my-8 p-4 md:p-8 rounded-2xl border border-border bg-muted/30 flex flex-col items-center justify-center min-h-[300px] relative">
      <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Simple Electric Circuit
      </div>

      <div className="relative w-full max-w-[240px] md:max-w-[256px] h-40 border-4 border-muted-foreground/20 rounded-xl flex items-center justify-center">
        {/* Wire paths */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div 
            className="w-full h-1 bg-yellow-400/50 absolute"
            initial={{ opacity: 0 }}
            animate={{ opacity: isOn ? 1 : 0 }}
          />
        </div>

        {/* Bulb */}
        <motion.div 
          className={`size-14 md:size-16 rounded-full border-2 flex items-center justify-center cursor-pointer transition-colors ${isOn ? "bg-yellow-400 border-yellow-500 shadow-[0_0_40px_rgba(250,204,21,0.5)]" : "bg-muted border-muted-foreground/30"}`}
          onClick={() => setIsOn(!isOn)}
        >
          <Zap className={`size-6 md:size-8 ${isOn ? "text-yellow-900" : "text-muted-foreground/50"}`} />
        </motion.div>

        {/* Battery */}
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 bg-foreground text-background text-[8px] md:text-[10px] px-2 md:px-3 py-1 rounded font-bold whitespace-nowrap">
          BATTERY 9V
        </div>
      </div>

      <button 
        onClick={() => setIsOn(!isOn)}
        className="mt-12 px-6 py-2 rounded-full border border-border hover:bg-muted active:bg-muted/80 transition-colors text-[10px] md:text-xs font-mono uppercase tracking-widest"
      >
        {isOn ? "MATIKAN SAKLAR" : "NYALAKAN SAKLAR"}
      </button>
    </div>
  )
}

function MagnetSimulation() {
  const [distance, setDistance] = useState(100)
  return (
    <div className="my-8 p-4 md:p-8 rounded-2xl border border-border bg-muted/30 flex flex-col items-center justify-center min-h-[350px] relative overflow-hidden">
      <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Magnetic Field Interaction
      </div>

      <div className="flex flex-col md:flex-row items-center gap-8 md:gap-4 relative w-full justify-center">
        {/* Fixed Magnet */}
        <div className="w-28 md:w-32 h-10 md:h-12 flex rounded-md overflow-hidden shadow-lg z-10 shrink-0">
          <div className="w-1/2 bg-red-600 flex items-center justify-center text-white font-bold text-xs md:text-sm">N</div>
          <div className="w-1/2 bg-blue-600 flex items-center justify-center text-white font-bold text-xs md:text-sm">S</div>
        </div>

        {/* Magnetic Field Lines (CSS Visual) - Hidden on small mobile to avoid clutter */}
        <div className="absolute inset-0 hidden md:flex items-center justify-center pointer-events-none opacity-20">
          {[1, 2, 3].map(i => (
            <div key={i} className="absolute border-2 border-dashed border-foreground rounded-full" 
                 style={{ width: 100 + i*60, height: 60 + i*30 }} />
          ))}
        </div>

        {/* Movable Magnet */}
        <motion.div 
          className="w-28 md:w-32 h-10 md:h-12 flex rounded-md overflow-hidden shadow-lg cursor-grab active:cursor-grabbing shrink-0"
          animate={{ x: distance }}
          drag="x"
          dragConstraints={{ left: -50, right: 200 }}
          onDrag={(e, info) => setDistance(info.offset.x)}
        >
          <div className="w-1/2 bg-red-600 flex items-center justify-center text-white font-bold text-xs md:text-sm">N</div>
          <div className="w-1/2 bg-blue-600 flex items-center justify-center text-white font-bold text-xs md:text-sm">S</div>
        </motion.div>
      </div>

      <p className="mt-16 text-[8px] md:text-[10px] text-muted-foreground font-mono text-center">Geser magnet untuk merasakan interaksi (visual saja).</p>
    </div>
  )
}

function WaveSimulation() {
  return (
    <div className="my-8 p-4 md:p-8 rounded-2xl border border-border bg-muted/30 flex flex-col items-center justify-center min-h-[300px] relative overflow-hidden">
       <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Wave Propagation
      </div>

      <div className="flex gap-0.5 md:gap-1 items-end h-24 md:h-32 w-full justify-center">
        {Array.from({ length: 30 }).map((_, i) => (
          <motion.div
            key={i}
            className="w-1 md:w-1.5 bg-foreground/40 rounded-full"
            animate={{ 
              height: ["20%", "80%", "20%"],
              backgroundColor: ["#ffffff20", "#ffffff", "#ffffff20"]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              delay: i * 0.05,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>
      <p className="mt-8 text-[8px] md:text-[10px] text-muted-foreground font-mono italic">Visualisasi gelombang transversal.</p>
    </div>
  )
}

function PistonSimulation() {
  return (
    <div className="my-8 p-4 md:p-8 rounded-2xl border border-border bg-muted/30 flex flex-col items-center justify-center min-h-[350px] relative">
      <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Piston Movement (Thermodynamics)
      </div>

      <div className="w-32 md:w-40 h-56 md:h-64 border-x-4 border-b-4 border-foreground/20 relative rounded-b-xl bg-background/50 overflow-hidden">
        {/* Gas Particles (Visual) */}
        <div className="absolute inset-0 opacity-10">
          {Array.from({ length: 15 }).map((_, i) => (
            <motion.div 
              key={i}
              className="size-1 bg-foreground rounded-full absolute"
              style={{ top: `${Math.random()*100}%`, left: `${Math.random()*100}%` }}
              animate={{ 
                x: [0, Math.random()*20-10, 0],
                y: [0, Math.random()*20-10, 0]
              }}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
          ))}
        </div>

        {/* Piston Head */}
        <motion.div 
          className="absolute top-0 left-0 w-full h-6 md:h-8 bg-foreground flex items-center justify-center shadow-lg"
          animate={{ top: [20, 160, 20] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        >
          <div className="w-1 h-16 md:h-20 bg-foreground absolute bottom-full" />
        </motion.div>
      </div>
    </div>
  )
}

function GeometrySimulation() {
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="my-8 p-4 md:p-8 rounded-2xl border border-border bg-muted/30 flex flex-col items-center justify-center min-h-[350px] relative">
      <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> 3D Geometry Visualizer
      </div>

      <div className="relative size-32 md:size-48">
        {/* CSS Cube */}
        <motion.div 
          className="size-full relative"
          style={{ transformStyle: "preserve-3d" }}
          animate={{ rotateY: 360, rotateX: 360 }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        >
          {["front", "back", "left", "right", "top", "bottom"].map((face) => {
            const translateVal = mounted && window.innerWidth < 768 ? "64px" : "96px";
            const styles: Record<string, string> = {
              front: `translateZ(${translateVal})`,
              back: `rotateY(180deg) translateZ(${translateVal})`,
              left: `rotateY(-90deg) translateZ(${translateVal})`,
              right: `rotateY(90deg) translateZ(${translateVal})`,
              top: `rotateX(90deg) translateZ(${translateVal})`,
              bottom: `rotateX(-90deg) translateZ(${translateVal})`,
            }
            return (
              <div 
                key={face}
                className="absolute inset-0 border-2 border-foreground/30 bg-foreground/5 flex items-center justify-center text-[6px] md:text-[8px] font-mono uppercase tracking-tighter"
                style={{ transform: styles[face] }}
              >
                {face}
              </div>
            )
          })}
        </motion.div>
      </div>
      <p className="mt-12 text-[8px] md:text-[10px] text-muted-foreground font-mono">Visualisasi Bangun Ruang (Kubus).</p>
    </div>
  )
}

function AtomSimulation() {
  return (
    <div className="my-8 flex flex-col items-center justify-center p-12 rounded-2xl border border-border bg-muted/30 overflow-hidden relative min-h-[400px]">
      <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Interactive Atom Model
      </div>
      
      {/* Nucleus */}
      <motion.div 
        className="size-12 rounded-full bg-foreground flex items-center justify-center z-10 shadow-xl"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="size-4 rounded-full bg-background/20 blur-sm" />
      </motion.div>

      {/* Electron Orbits */}
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          className="absolute border border-muted-foreground/20 rounded-full"
          style={{
            width: 120 + i * 60,
            height: 120 + i * 60,
            rotateX: 60 + i * 10,
            rotateY: i * 30,
          }}
          animate={{ rotateZ: 360 }}
          transition={{ duration: 5 + i * 2, repeat: Infinity, ease: "linear" }}
        >
          {/* Electron */}
          <motion.div 
            className="size-3 rounded-full bg-foreground absolute -top-1.5 left-1/2"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        </motion.div>
      ))}

      <div className="mt-auto pt-12 text-center">
        <p className="text-xs text-muted-foreground italic">Gunakan imajinasimu untuk memvisualisasikan struktur atom.</p>
      </div>
    </div>
  )
}

function CellsSimulation() {
  return (
    <div className="my-8 p-12 rounded-2xl border border-border bg-muted/30 overflow-hidden min-h-[400px] flex flex-col items-center justify-center relative">
       <div className="absolute top-4 left-4 flex items-center gap-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground">
        <Zap className="size-3" /> Cell Division Preview
      </div>

      <div className="flex gap-12">
        <motion.div 
          className="size-32 rounded-3xl border-2 border-foreground/50 bg-background/50 relative flex items-center justify-center"
          animate={{ 
            borderRadius: ["24px", "48px", "24px"],
            scale: [1, 1.05, 1]
          }}
          transition={{ duration: 4, repeat: Infinity }}
        >
          <motion.div 
            className="size-12 rounded-full bg-foreground/20"
            animate={{ scale: [0.8, 1.2, 0.8] }}
            transition={{ duration: 3, repeat: Infinity }}
          />
        </motion.div>

        <div className="flex items-center text-muted-foreground">
          <motion.div
            animate={{ x: [0, 10, 0] }}
            transition={{ duration: 1, repeat: Infinity }}
          >
            →
          </motion.div>
        </div>

        <div className="flex flex-col gap-4">
          {[1, 2].map((i) => (
            <motion.div 
              key={i}
              className="size-16 rounded-2xl border-2 border-foreground/50 bg-background/50 flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.5 }}
            >
               <div className="size-6 rounded-full bg-foreground/10" />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
