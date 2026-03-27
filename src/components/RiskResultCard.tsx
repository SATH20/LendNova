"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import AnimatedValue from "./AnimatedValue";

type Factor = {
  name: string;
  impact: number;
};

type RiskResult = {
  score: number;
  approvalProbability: number;
  riskBand: "Low" | "Medium" | "High";
  model: string;
  confidence: number;
  factors: Factor[];
};

type Props = {
  data: RiskResult;
  onExplain: () => void;
  onCompare: () => void;
};

export default function RiskResultCard({ data, onExplain, onCompare }: Props) {
  const riskColor = useMemo(() => {
    if (data.riskBand === "Low") return "bg-[#2EE59D]/20 text-[#2EE59D]";
    if (data.riskBand === "Medium") return "bg-[#9B6BFF]/20 text-[#9B6BFF]";
    return "bg-[#FF5C5C]/20 text-[#FF5C5C]";
  }, [data.riskBand]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="glass glow-border rounded-3xl p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-muted">
            Credit Score
          </p>
          <p className="mt-3 text-4xl font-semibold text-white">
            <AnimatedValue value={data.score} />
          </p>
          <p className="mt-2 text-sm text-muted">Model: {data.model}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${riskColor}`}>
          {data.riskBand} Risk
        </span>
      </div>
      <div className="mt-6">
        <div className="flex items-center justify-between text-xs text-muted">
          <span>Approval Probability</span>
          <span className="text-white font-semibold">
            {(data.approvalProbability * 100).toFixed(1)}%
          </span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${data.approvalProbability * 100}%` }}
            transition={{ duration: 0.8 }}
            className="h-full rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF]"
          />
        </div>
      </div>
      <div className="mt-6 grid gap-3 text-xs text-muted sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Confidence</p>
          <p className="mt-2 text-sm font-semibold text-white">
            {(data.confidence * 100).toFixed(1)}%
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Top Factor</p>
          <p className="mt-2 text-sm font-semibold text-white">
            {data.factors[0]?.name ?? "N/A"}
          </p>
        </div>
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <button
          id="explain-btn"
          onClick={onExplain}
          className="ripple rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/20"
        >
          Why This Score
        </button>
        <button
          id="eligibility-btn"
          onClick={onCompare}
          className="ripple rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110"
        >
          See Loan Eligibility
        </button>
      </div>
    </motion.div>
  );
}
