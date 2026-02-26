"use client";

import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Factor = {
  name: string;
  impact: number;
};

type Props = {
  factors: Factor[];
};

export default function ExplainabilityCard({ factors }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="glass glow-border rounded-3xl p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-muted">
            Explainable AI
          </p>
          <p className="mt-3 text-2xl font-semibold text-white">
            Decision Drivers
          </p>
        </div>
        <span className="rounded-full bg-[#2EE59D]/20 px-3 py-1 text-xs font-semibold text-[#2EE59D]">
          Interpretable
        </span>
      </div>
      <div className="mt-6 h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={factors} layout="vertical" margin={{ left: 12 }}>
            <XAxis type="number" hide />
            <YAxis
              dataKey="name"
              type="category"
              width={110}
              tick={{ fill: "#8A8FA3", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(12,18,38,0.9)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
                color: "#E8EBF3",
              }}
            />
            <Bar dataKey="impact" fill="#4F7FFF" radius={[8, 8, 8, 8]} animationDuration={900} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 space-y-3 text-sm text-muted">
        {factors.map((factor, index) => {
          const isPositive = factor.impact >= 0;
          const magnitude = Math.min(Math.abs(factor.impact) * 120, 100);
          return (
            <div key={factor.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <span>{factor.name}</span>
                <span className={isPositive ? "text-[#2EE59D]" : "text-[#FF5C5C]"}>
                  {isPositive ? "+" : ""}
                  {factor.impact.toFixed(2)}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${magnitude}%` }}
                  transition={{ duration: 0.8, delay: index * 0.05 }}
                  className={`h-full rounded-full ${
                    isPositive
                      ? "bg-gradient-to-r from-[#2EE59D]/40 to-[#2EE59D]"
                      : "bg-gradient-to-r from-[#FF5C5C]/40 to-[#FF5C5C]"
                  }`}
                />
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-muted">
        Gradient Boosting emphasizes stable cash flow, recent employment, and
        verified OCR identity signals. Short credit history introduces moderate
        risk but is offset by consistent repayment behavior in alternative data.
      </div>
    </motion.div>
  );
}
