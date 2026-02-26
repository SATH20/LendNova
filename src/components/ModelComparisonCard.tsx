"use client";

import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type ModelMetric = {
  model: string;
  accuracy: number;
  explainability: number;
};

type Props = {
  data: ModelMetric[];
  recommended: string;
};

export default function ModelComparisonCard({ data, recommended }: Props) {
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
            Model Comparison
          </p>
          <p className="mt-3 text-2xl font-semibold text-white">
            Accuracy vs Explainability
          </p>
        </div>
        <span className="rounded-full bg-[#4F7FFF]/20 px-3 py-1 text-xs font-semibold text-[#4F7FFF]">
          Recommended: {recommended}
        </span>
      </div>
      <div className="mt-6 h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={12}>
            <XAxis dataKey="model" tick={{ fill: "#8A8FA3", fontSize: 11 }} />
            <YAxis tick={{ fill: "#8A8FA3", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "rgba(12,18,38,0.9)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
                color: "#E8EBF3",
              }}
            />
            <Legend />
            <Bar dataKey="accuracy" fill="#4F7FFF" radius={[10, 10, 0, 0]} animationDuration={900} />
            <Bar dataKey="explainability" fill="#9B6BFF" radius={[10, 10, 0, 0]} animationDuration={900} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
