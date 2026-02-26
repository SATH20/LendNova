"use client";

import { motion } from "framer-motion";

const items = [
  "New Assessment",
  "Borrower Profile",
  "Upload Documents (OCR)",
  "Risk Dashboard",
  "Explainability",
  "Model Comparison",
  "Audit Logs",
  "Settings",
];

export default function Sidebar() {
  return (
    <aside className="glass glow-border h-full w-full max-w-xs px-6 py-8">
      <div className="flex items-center gap-3">
        <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-[#4F7FFF] via-[#7D7BFF] to-[#9B6BFF] p-[2px]">
          <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#0A0F1F] text-sm font-semibold">
            LN
          </div>
        </div>
        <div>
          <p className="text-sm font-semibold tracking-[0.2em] text-[#9B6BFF]">
            LENDNOVA
          </p>
          <p className="text-xs text-muted">Risk Console</p>
        </div>
      </div>
      <div className="mt-8 space-y-2">
        {items.map((item, index) => (
          <motion.button
            key={item}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="w-full rounded-xl border border-white/5 bg-white/5 px-4 py-3 text-left text-sm text-[#E8EBF3] transition hover:border-white/20 hover:bg-white/10"
          >
            {item}
          </motion.button>
        ))}
      </div>
    </aside>
  );
}
