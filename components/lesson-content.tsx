"use client"

import { useEffect, useMemo, useState } from "react"
import { Quote, Lightbulb } from "lucide-react"
import type { ContentBlock } from "@/lib/types"

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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_220px] gap-10">
      <article className="prose-custom max-w-none">
        {blocks.map((block, i) => (
          <Block key={i} block={block} index={i} />
        ))}
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
            {block.text}
          </h2>
        )
      if (lvl === 2)
        return (
          <h3 id={id} className="scroll-mt-24 text-lg font-medium tracking-tight mt-8 mb-2">
            {block.text}
          </h3>
        )
      return (
        <h4 id={id} className="scroll-mt-24 text-base font-medium tracking-tight mt-6 mb-2">
          {block.text}
        </h4>
      )
    }
    case "text":
      return (
        <p className="text-[15px] leading-relaxed text-foreground/90 my-4">{block.text}</p>
      )
    case "quote":
      return (
        <figure className="my-6 rounded-2xl border border-border bg-muted/40 p-5">
          <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.14em] text-muted-foreground">
            <Quote className="size-3.5" />
            {block.text}
          </div>
          {block.translation && (
            <blockquote className="mt-3 text-[15px] leading-relaxed italic text-foreground">
              &ldquo;{block.translation}&rdquo;
            </blockquote>
          )}
        </figure>
      )
    case "highlight":
      return (
        <aside className="my-6 rounded-2xl border-l-4 border-foreground bg-accent/60 px-5 py-4 flex gap-3">
          <Lightbulb className="size-4 mt-0.5 shrink-0" />
          <p className="text-sm leading-relaxed">{block.text}</p>
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
            <li key={i}>{it}</li>
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
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, ri) => (
                <tr key={ri} className="border-b border-border last:border-0">
                  {row.map((cell, ci) => (
                    <td key={ci} className="px-4 py-2.5">
                      {cell}
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
          className={`my-4 font-mono text-sm rounded-xl bg-muted/60 px-4 py-3 ${
            block.display ? "text-center text-base" : ""
          }`}
        >
          {block.tex}
        </div>
      )
    default:
      return null
  }
}
