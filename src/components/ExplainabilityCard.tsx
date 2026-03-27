"use client";

import { motion } from "framer-motion";

type Factor = {
  name: string;
  impact: number;
};

type Props = {
  factors: Factor[];
};

// Human-readable descriptions for known factor names
function getFactorInsight(name: string, impact: number): string {
  const positive = impact >= 0;
  const n = name.toLowerCase();
  if (n.includes("income") || n.includes("salary")) return positive ? "Your income level is a strong positive indicator." : "Your income level is limiting your score.";
  if (n.includes("expense") || n.includes("spending")) return positive ? "Your expense-to-income ratio is healthy." : "High expenses relative to income are pulling your score down.";
  if (n.includes("tenure") || n.includes("employment")) return positive ? "Your job stability is building lender confidence." : "Short employment history is a risk factor.";
  if (n.includes("savings")) return positive ? "A healthy savings ratio signals financial discipline." : "Low savings suggest financial strain.";
  if (n.includes("fraud") || n.includes("trust")) return positive ? "No fraud signals detected — data looks authentic." : "Some data inconsistencies were flagged.";
  if (n.includes("verification") || n.includes("ocr")) return positive ? "Verified documents boost your credibility." : "Unverified documents reduce your score.";
  if (n.includes("stability")) return positive ? "Consistent income patterns are a strong signal." : "Irregular income patterns introduce risk.";
  if (n.includes("cash") || n.includes("flow")) return positive ? "Your cash flow looks healthy." : "Cash flow is tighter than ideal.";
  return positive ? "This factor is positively contributing to your score." : "This factor is negatively impacting your score.";
}

export default function ExplainabilityCard({ factors }: Props) {
  const positive = factors.filter((f) => f.impact >= 0).sort((a, b) => b.impact - a.impact);
  const negative = factors.filter((f) => f.impact < 0).sort((a, b) => a.impact - b.impact);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col gap-4"
    >
      {/* Header card */}
      <div className="glass glow-border rounded-3xl p-6">
        <p className="text-xs uppercase tracking-[0.3em] text-muted">Why This Score</p>
        <h3 className="mt-2 text-lg font-semibold text-white">What drove your credit decision</h3>
        <p className="mt-2 text-sm text-muted">
          Your score is determined by a Gradient Boosting model. Here are the top factors, explained in plain language.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Positive factors */}
        <div className="flex flex-col gap-3">
          <p className="px-1 text-xs uppercase tracking-[0.25em] text-[#2EE59D]">
            ↑ Working in your favour
          </p>
          {positive.length === 0 && (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
              No strong positive factors detected yet.
            </div>
          )}
          {positive.map((f, i) => (
            <motion.div
              key={f.name}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07 }}
              className="rounded-2xl border border-[#2EE59D]/20 bg-[#2EE59D]/5 p-4"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">{f.name}</p>
                <span className="rounded-full bg-[#2EE59D]/20 px-2 py-0.5 text-[10px] font-bold text-[#2EE59D]">
                  +{(f.impact * 100).toFixed(0)}pts
                </span>
              </div>
              <p className="mt-1.5 text-xs text-muted">{getFactorInsight(f.name, f.impact)}</p>
              {/* Impact bar */}
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(f.impact) * 150, 100)}%` }}
                  transition={{ duration: 0.8, delay: i * 0.07 }}
                  className="h-full rounded-full bg-gradient-to-r from-[#2EE59D]/40 to-[#2EE59D]"
                />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Negative factors */}
        <div className="flex flex-col gap-3">
          <p className="px-1 text-xs uppercase tracking-[0.25em] text-[#FF5C5C]">
            ↓ Working against you
          </p>
          {negative.length === 0 && (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
              No significant negative factors. ✓
            </div>
          )}
          {negative.map((f, i) => (
            <motion.div
              key={f.name}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.07 }}
              className="rounded-2xl border border-[#FF5C5C]/20 bg-[#FF5C5C]/5 p-4"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-white">{f.name}</p>
                <span className="rounded-full bg-[#FF5C5C]/20 px-2 py-0.5 text-[10px] font-bold text-[#FF5C5C]">
                  {(f.impact * 100).toFixed(0)}pts
                </span>
              </div>
              <p className="mt-1.5 text-xs text-muted">{getFactorInsight(f.name, f.impact)}</p>
              {/* Impact bar */}
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.abs(f.impact) * 150, 100)}%` }}
                  transition={{ duration: 0.8, delay: i * 0.07 }}
                  className="h-full rounded-full bg-gradient-to-r from-[#FF5C5C]/40 to-[#FF5C5C]"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Bottom takeaway */}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
        <span className="font-semibold text-white">Quick takeaway: </span>
        {positive.length > negative.length
          ? "Your profile has more positive signals than negatives. Focus on the risk factors above to improve further."
          : "There are a few areas dragging your score down. The suggestions on the Loan Eligibility tab can guide you."}
      </div>
    </motion.div>
  );
}
