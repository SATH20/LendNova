"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import AnimatedValue from "@/components/AnimatedValue";
import ModelComparisonCard from "@/components/ModelComparisonCard";
import { fetchAssessments, type AssessmentHistoryItem } from "@/lib/api";

const modelData = [
  { model: "Logistic Regression", accuracy: 0.78, explainability: 0.86 },
  { model: "Random Forest", accuracy: 0.84, explainability: 0.62 },
  { model: "Gradient Boosting", accuracy: 0.89, explainability: 0.74 },
];

type Stats = {
  total: number;
  avgScore: number;
  avgApproval: number;
  approvedCount: number;
  highRisk: number;
  mediumRisk: number;
  lowRisk: number;
};

export default function AdminPage() {
  const [assessments, setAssessments] = useState<AssessmentHistoryItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssessments(1, 50)
      .then((res) => {
        const a = res.assessments;
        setAssessments(a);
        if (a.length > 0) {
          const avgScore = a.reduce((s, i) => s + i.credit_score, 0) / a.length;
          const avgApproval = a.reduce((s, i) => s + i.approval_probability, 0) / a.length;
          const approvedCount = a.filter((i) => i.approval_probability > 0.6).length;
          const lowRisk = a.filter((i) => i.risk_band === "Low").length;
          const mediumRisk = a.filter((i) => i.risk_band === "Medium").length;
          const highRisk = a.filter((i) => i.risk_band === "High").length;
          setStats({ total: a.length, avgScore, avgApproval, approvedCount, highRisk, mediumRisk, lowRisk });
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const statCards = stats
    ? [
        { label: "Total Evaluations", value: stats.total, suffix: "", decimals: 0 },
        { label: "Avg Credit Score", value: Math.round(stats.avgScore), suffix: "", decimals: 0 },
        { label: "Approval Rate", value: +(stats.avgApproval * 100).toFixed(1), suffix: "%", decimals: 1 },
        { label: "High Risk Cases", value: stats.highRisk, suffix: "", decimals: 0 },
      ]
    : [];

  return (
    <div className="relative min-h-screen bg-[#0A0F1F]">
      <div className="mesh-bg pointer-events-none absolute inset-0 opacity-50" />
      <div className="relative z-10 mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-5 py-8">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#4F7FFF] via-[#7D7BFF] to-[#9B6BFF] p-[2px]">
                <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#0A0F1F] text-sm font-semibold">LN</div>
              </div>
              <div>
                <p className="text-sm font-semibold tracking-[0.2em] text-[#9B6BFF]">LENDNOVA</p>
                <p className="text-xs text-muted">Underwriter Console</p>
              </div>
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-[#2EE59D]/20 px-3 py-1 text-xs font-semibold text-[#2EE59D]">Admin View</span>
            <Link href="/assistant" className="ripple rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:bg-white/10">
              Run Assessment
            </Link>
          </div>
        </motion.div>

        {/* Title */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="glass glow-border rounded-3xl p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-muted">Underwriter Dashboard</p>
          <h1 className="mt-2 text-2xl font-semibold text-white">Risk Console — Macro View</h1>
          <p className="mt-2 text-sm text-muted">Aggregated metrics, risk band distribution, and model performance across all submitted assessments.</p>
        </motion.div>

        {/* Loading */}
        {loading && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="shimmer rounded-2xl h-24" />
            ))}
          </div>
        )}

        {/* Stat cards */}
        {stats && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {statCards.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.05 }}
                whileHover={{ y: -4 }}
                className="glass rounded-2xl p-4 text-center"
              >
                <p className="text-[10px] uppercase tracking-[0.25em] text-muted">{s.label}</p>
                <p className="mt-2 text-2xl font-semibold text-white">
                  <AnimatedValue value={s.value} suffix={s.suffix} decimals={s.decimals} />
                </p>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Risk distribution + Model */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Risk Band Distribution */}
          {stats && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass rounded-3xl p-6">
              <p className="text-xs uppercase tracking-[0.3em] text-muted">Risk Distribution</p>
              <h2 className="mt-2 text-lg font-semibold text-white">Portfolio Risk Bands</h2>
              <div className="mt-6 space-y-4">
                {[
                  { label: "Low Risk", count: stats.lowRisk, total: stats.total, color: "#2EE59D" },
                  { label: "Medium Risk", count: stats.mediumRisk, total: stats.total, color: "#9B6BFF" },
                  { label: "High Risk", count: stats.highRisk, total: stats.total, color: "#FF5C5C" },
                ].map((band) => {
                  const pct = stats.total > 0 ? (band.count / stats.total) * 100 : 0;
                  return (
                    <div key={band.label}>
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-muted">{band.label}</span>
                        <span className="font-semibold text-white">{band.count} <span className="text-muted font-normal text-xs">({pct.toFixed(0)}%)</span></span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-white/8">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.8 }}
                          className="h-full rounded-full"
                          style={{ background: band.color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-muted">
                <span className="font-semibold text-white">{stats.approvedCount}</span> of{" "}
                <span className="font-semibold text-white">{stats.total}</span> assessments have an approval probability above 60%.
              </div>
            </motion.div>
          )}

          {/* Model Performance */}
          <ModelComparisonCard data={modelData} recommended="Gradient Boosting" />
        </div>

        {/* Recent Assessments Table */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass rounded-3xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">Assessment Log</p>
              <h2 className="mt-2 text-lg font-semibold text-white">Recent Evaluations</h2>
            </div>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted">
              {assessments.length} records
            </span>
          </div>

          {loading ? (
            <div className="mt-4 space-y-2">
              {[0, 1, 2, 3].map((i) => <div key={i} className="shimmer h-12 rounded-xl" />)}
            </div>
          ) : assessments.length === 0 ? (
            <p className="mt-6 text-sm text-muted">No assessments yet. Run one from the Risk Console.</p>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-[0.25em] text-muted border-b border-white/8">
                    <th className="pb-3 pr-4">ID</th>
                    <th className="pb-3 pr-4">Score</th>
                    <th className="pb-3 pr-4">Approval</th>
                    <th className="pb-3 pr-4">Risk</th>
                    <th className="pb-3 pr-4">Model</th>
                    <th className="pb-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {assessments.slice(0, 15).map((a) => (
                    <tr key={a.id} className="text-muted transition hover:bg-white/3">
                      <td className="py-3 pr-4 text-white font-medium">#{a.id}</td>
                      <td className="py-3 pr-4 text-white font-semibold">{a.credit_score}</td>
                      <td className="py-3 pr-4">{(a.approval_probability * 100).toFixed(1)}%</td>
                      <td className="py-3 pr-4">
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                          a.risk_band === "Low" ? "bg-[#2EE59D]/20 text-[#2EE59D]"
                            : a.risk_band === "Medium" ? "bg-[#9B6BFF]/20 text-[#9B6BFF]"
                            : "bg-[#FF5C5C]/20 text-[#FF5C5C]"
                        }`}>
                          {a.risk_band}
                        </span>
                      </td>
                      <td className="py-3 pr-4">{a.model_used}</td>
                      <td className="py-3 text-xs">{new Date(a.timestamp).toLocaleString("en-IN")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>

        {/* System health */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass rounded-3xl p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-muted">System Status</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {[
              { label: "ML Model", status: "Operational", ok: true },
              { label: "OCR Engine", status: "Operational", ok: true },
              { label: "Fraud Detection", status: "Operational", ok: true },
            ].map((s) => (
              <div key={s.label} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span className="text-sm text-muted">{s.label}</span>
                <div className="flex items-center gap-2">
                  <span className={`h-2 w-2 rounded-full ${s.ok ? "bg-[#2EE59D]" : "bg-[#FF5C5C]"}`} />
                  <span className={`text-xs font-semibold ${s.ok ? "text-[#2EE59D]" : "text-[#FF5C5C]"}`}>{s.status}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <p className="text-center text-xs text-muted pb-4">
          © 2026 LendNova · Admin Console · Built by Rajavarapu Sathwik
        </p>
      </div>
    </div>
  );
}
