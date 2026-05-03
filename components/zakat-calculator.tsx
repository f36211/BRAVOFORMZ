"use client"

import { useState } from "react"
import { motion } from "motion/react"
import { Calculator, Info, Coins, Wheat, Calculator as CalcIcon } from "lucide-react"

type ZakatType = "fitrah" | "emas" | "profesi" | "niaga" | "tani"

export function ZakatCalculator() {
  const [type, setType] = useState<ZakatType>("fitrah")
  const [val, setVal] = useState<string>("")
  const [price, setPrice] = useState<string>("1000000") // Emas price fallback

  const calculate = () => {
    const amount = parseFloat(val) || 0
    const goldPrice = parseFloat(price) || 0

    switch (type) {
      case "fitrah":
        return { 
          result: amount * 2.5, 
          unit: "kg Beras", 
          desc: "Jumlah Orang x 2.5 kg" 
        }
      case "emas":
        const isNishab = amount >= 85
        return { 
          result: isNishab ? (amount * goldPrice * 0.025) : 0, 
          unit: "Rupiah", 
          desc: isNishab ? "Berat x Harga x 2.5%" : "Belum mencapai nishab (85g)"
        }
      case "profesi":
        return { 
          result: amount * 0.025, 
          unit: "Rupiah", 
          desc: "Penghasilan x 2.5%" 
        }
      case "niaga":
        return { 
          result: amount * 0.025, 
          unit: "Rupiah", 
          desc: "Aset x 2.5%" 
        }
      case "tani":
        return { 
          result: amount * 0.05, 
          unit: "kg Beras", 
          desc: "Hasil Panen x 5% (Irigasi)" 
        }
      default:
        return { result: 0, unit: "", desc: "" }
    }
  }

  const { result, unit, desc } = calculate()

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6">
        <div className="size-10 rounded-xl bg-foreground text-background grid place-items-center">
          <CalcIcon className="size-5" />
        </div>
        <div>
          <h3 className="font-medium">Kalkulator Zakat Interaktif</h3>
          <p className="text-xs text-muted-foreground">Visualisasi rumus dalam angka nyata</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 mb-6">
        {(["fitrah", "emas", "profesi", "niaga", "tani"] as ZakatType[]).map((t) => (
          <button
            key={t}
            onClick={() => { setType(t); setVal(""); }}
            className={`px-3 py-2 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-all border ${
              type === t 
                ? "bg-foreground text-background border-foreground shadow-md" 
                : "bg-muted text-muted-foreground border-transparent hover:bg-accent"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-1.5 block">
            {type === "fitrah" ? "Jumlah Orang" : type === "emas" ? "Berat Emas (gram)" : "Total Harta / Hasil (Rp/kg)"}
          </label>
          <input
            type="number"
            value={val}
            onChange={(e) => setVal(e.target.value)}
            placeholder="Masukkan angka..."
            className="w-full bg-muted border-none rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-foreground/10 outline-none transition-all"
          />
        </div>

        {type === "emas" && (
          <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}>
            <label className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground mb-1.5 block">
              Harga Emas per Gram (Rp)
            </label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full bg-muted border-none rounded-xl px-4 py-3 text-sm outline-none"
            />
          </motion.div>
        )}

        <div className="pt-4 border-t border-border">
          <div className="flex items-end justify-between">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Hasil Zakat</span>
              <div className="text-2xl font-medium tracking-tight mt-1">
                {type === "emas" || type === "profesi" || type === "niaga" 
                  ? new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(result)
                  : `${result} ${unit}`
                }
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Rumus</span>
              <div className="text-[11px] font-medium text-muted-foreground mt-1">{desc}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
