"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, animate, motion } from "framer-motion";
import Sidebar from "@/components/Sidebar";
import PipelineLoader from "@/components/PipelineLoader";
import QuickChips from "@/components/QuickChips";
import RiskResultCard from "@/components/RiskResultCard";
import FraudResultCard from "@/components/FraudResultCard";
import ExplainabilityCard from "@/components/ExplainabilityCard";
import ModelComparisonCard from "@/components/ModelComparisonCard";
import type { FraudResult, ModelMetric, RiskResult } from "@/lib/mockEngine";

type HistoryItem = {
  timestamp: string;
  score: number;
  approvalProbability: number;
  fraudProbability: number;
  riskBand: string;
};

type FeedItem = {
  id: string;
  message: string;
  time: string;
};

const actions = [
  "Run Risk Score",
  "OCR Extract",
  "Fraud Check",
  "Explain Decision",
  "Compare Models",
  "Generate Report",
];

const chips = [
  { label: "Income", value: "Income: $4,500/mo" },
  { label: "Expenses", value: "Expenses: $1,900/mo" },
  { label: "Employment", value: "Employment: Full-time" },
  { label: "Tenure", value: "Tenure: 2.5 years" },
  { label: "Upload Payslip", value: "Upload Payslip: yes" },
  { label: "Upload ID", value: "Upload ID: yes" },
  { label: "Run Risk", value: "Run risk score with latest cash-flow data." },
  { label: "Fraud Check", value: "Run OCR fraud check on uploaded documents." },
  { label: "Explain", value: "Explain the decision for the latest assessment." },
];

const defaultInput =
  "Income: $4,200/mo, Expenses: $1,700/mo, Employment: Full-time, Tenure: 3 years.";

function AnimatedValue({
  value,
  suffix,
  decimals = 0,
  className,
}: {
  value: number;
  suffix?: string;
  decimals?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1,
      ease: "easeOut",
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = `${latest.toFixed(decimals)}${suffix ?? ""}`;
        }
      },
    });
    return () => controls.stop();
  }, [value, suffix, decimals]);

  return <span ref={ref} className={className} />;
}

export default function AssistantPage() {
  const [input, setInput] = useState(defaultInput);
  const [action, setAction] = useState(actions[0]);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [riskResult, setRiskResult] = useState<RiskResult | null>(null);
  const [fraudResult, setFraudResult] = useState<FraudResult | null>(null);
  const [modelMetrics, setModelMetrics] = useState<ModelMetric[] | null>(null);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    if (typeof window === "undefined") {
      return [];
    }
    const stored = window.localStorage.getItem("lendnova_history");
    return stored ? JSON.parse(stored) : [];
  });

  useEffect(() => {
    window.localStorage.setItem("lendnova_history", JSON.stringify(history));
  }, [history]);

  const statusChips = useMemo(
    () => ["Secure", "Model: Gradient Boosting", "v1.0", "Live"],
    []
  );
  const showSkeleton =
    loading && !riskResult && !fraudResult && !modelMetrics;
  const [simIncome, setSimIncome] = useState(4200);
  const [simExpenses, setSimExpenses] = useState(1700);
  const [simTenure, setSimTenure] = useState(36);

  const simScore = useMemo(() => {
    const base = riskResult?.score ?? 720;
    const incomeBoost = (simIncome - 4200) / 40;
    const expenseImpact = (simExpenses - 1700) / 35;
    const tenureBoost = (simTenure - 36) / 2;
    const score = base + incomeBoost - expenseImpact + tenureBoost;
    return Math.max(580, Math.min(820, Math.round(score)));
  }, [riskResult, simIncome, simExpenses, simTenure]);

  const simApproval = useMemo(() => {
    const normalized = (simScore - 580) / 240;
    return Math.max(0.45, Math.min(0.95, 0.45 + normalized * 0.5));
  }, [simScore]);

  const addFeed = (message: string) => {
    setFeed((prev) => [
      {
        id: `${Date.now()}-${prev.length}`,
        message,
        time: new Date().toLocaleTimeString(),
      },
      ...prev.slice(0, 7),
    ]);
  };

  const handleRun = async (overrideAction?: string) => {
    setLoading(true);
    setActiveStep(0);
    addFeed("Assessment workflow initialized with secure session token.");
    const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
    let latestRisk: RiskResult | null = null;
    let latestFraud: FraudResult | null = null;
    const activeAction = overrideAction ?? action;

    const runPredict = async () => {
      setActiveStep(1);
      await wait(180);
      setActiveStep(2);
      addFeed("Risk model inference started using Gradient Boosting v1.0.");
      const response = await fetch("/api/predict", { method: "POST" });
      const data = await response.json();
      setRiskResult(data.risk);
      setModelMetrics(data.modelMetrics);
      latestRisk = data.risk as RiskResult;
      addFeed(`Risk score generated at ${data.risk.score} with ${(data.risk.confidence * 100).toFixed(1)}% confidence.`);
      return latestRisk;
    };

    const runFraud = async () => {
      setActiveStep(3);
      addFeed("OCR fraud screening triggered with document integrity checks.");
      const response = await fetch("/api/fraud-check", { method: "POST" });
      const data = await response.json();
      setFraudResult(data.fraud);
      latestFraud = data.fraud as FraudResult;
      addFeed(`Fraud likelihood assessed at ${(data.fraud.probability * 100).toFixed(2)}%.`);
      return latestFraud;
    };

    if (activeAction === "Run Risk Score") {
      await wait(300);
      await runPredict();
    }

    if (activeAction === "OCR Extract") {
      setActiveStep(1);
      addFeed("OCR extraction running on uploaded identity artifacts.");
      await wait(300);
      const response = await fetch("/api/ocr-extract", { method: "POST" });
      const data = await response.json();
      setFraudResult((prev) =>
        prev
          ? { ...prev, fields: { ...prev.fields, ...data.ocr } }
          : {
              probability: 0.05,
              flags: ["Document Scan Verified"],
              fields: {
                name: data.ocr.name,
                idNumber: data.ocr.idNumber,
                employer: data.ocr.employer,
                income: data.ocr.income,
              },
            }
      );
    }

    if (activeAction === "Fraud Check") {
      await wait(300);
      await runFraud();
    }

    if (activeAction === "Explain Decision") {
      const risk = riskResult ?? (await runPredict());
      latestRisk = risk;
      addFeed("Explainability factors compiled for audit-ready decision trail.");
    }

    if (activeAction === "Compare Models") {
      if (!modelMetrics) {
        await runPredict();
      }
      addFeed("Model benchmarking snapshot updated for governance review.");
    }

    if (activeAction === "Generate Report") {
      await wait(300);
      const risk = await runPredict();
      const fraud = await runFraud();
      setHistory((prev) => [
        {
          timestamp: new Date().toLocaleString(),
          score: risk.score,
          approvalProbability: risk.approvalProbability,
          fraudProbability: fraud.probability,
          riskBand: risk.riskBand,
        },
        ...prev.slice(0, 4),
      ]);
    }

    if (activeAction === "Run Risk Score") {
      const risk = latestRisk ?? riskResult;
      if (risk) {
        setHistory((prev) => [
          {
            timestamp: new Date().toLocaleString(),
            score: risk.score,
            approvalProbability: risk.approvalProbability,
            fraudProbability: (latestFraud ?? fraudResult)?.probability ?? 0.04,
            riskBand: risk.riskBand,
          },
          ...prev.slice(0, 4),
        ]);
      }
    }

    setActiveStep(4);
    addFeed("Decision package sealed with audit hash and policy rationale.");
    await wait(200);
    setLoading(false);
  };

  const handleAssessment = async () => {
    await handleRun("Generate Report");
  };

  return (
    <div className="relative min-h-screen bg-[#0A0F1F]">
      <div className="mesh-bg pointer-events-none absolute inset-0 opacity-60" />
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 flex min-h-screen flex-col gap-6 px-6 py-8 lg:flex-row"
      >
        <div className="w-full lg:w-[280px]">
          <Sidebar />
        </div>
        <main className="flex-1 space-y-6">
          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-muted">
                  LendNova Risk Assistant
                </p>
                <h1 className="mt-3 text-2xl font-semibold text-white">
                  Execute credit scoring, fraud verification, and explainable AI decisions.
                </h1>
              </div>
              <div className="flex flex-wrap gap-2">
                {statusChips.map((chip, index) => (
                  <motion.span
                    key={chip}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted"
                  >
                    {chip}
                  </motion.span>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              AI Command Console
            </p>
            <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_220px_180px]">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Type borrower details (income, expenses, job tenure) or choose an action…"
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
              />
              <select
                value={action}
                onChange={(event) => setAction(event.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
              >
                {actions.map((item) => (
                  <option key={item} value={item} className="bg-[#0A0F1F]">
                    {item}
                  </option>
                ))}
              </select>
              <button
                onClick={handleAssessment}
                className="ripple rounded-2xl bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
              >
                Run Assessment
              </button>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <button
                onClick={() => handleRun()}
                className="ripple rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
              >
                {action}
              </button>
              <QuickChips chips={chips} onSelect={(value) => setInput(value)} />
            </div>
          </motion.div>

          <PipelineLoader activeStep={activeStep} loading={loading} />

          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <motion.div
              whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
              transition={{ type: "spring", stiffness: 120, damping: 16 }}
              className="glass glow-border rounded-3xl p-6"
            >
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                What-If Simulator
              </p>
              <h2 className="mt-3 text-lg font-semibold text-white">
                Adjust borrower signals to preview underwriting impact.
              </h2>
              <div className="mt-6 grid gap-4">
                <div>
                  <div className="flex items-center justify-between text-xs text-muted">
                    <span>Monthly Income</span>
                    <span className="text-white">${simIncome}</span>
                  </div>
                  <input
                    type="range"
                    min={2800}
                    max={8500}
                    step={100}
                    value={simIncome}
                    onChange={(event) => setSimIncome(Number(event.target.value))}
                    className="mt-3 w-full accent-[#4F7FFF]"
                  />
                </div>
                <div>
                  <div className="flex items-center justify-between text-xs text-muted">
                    <span>Monthly Expenses</span>
                    <span className="text-white">${simExpenses}</span>
                  </div>
                  <input
                    type="range"
                    min={800}
                    max={4200}
                    step={100}
                    value={simExpenses}
                    onChange={(event) => setSimExpenses(Number(event.target.value))}
                    className="mt-3 w-full accent-[#9B6BFF]"
                  />
                </div>
                <div>
                  <div className="flex items-center justify-between text-xs text-muted">
                    <span>Employment Tenure</span>
                    <span className="text-white">{simTenure} months</span>
                  </div>
                  <input
                    type="range"
                    min={6}
                    max={96}
                    step={3}
                    value={simTenure}
                    onChange={(event) => setSimTenure(Number(event.target.value))}
                    className="mt-3 w-full accent-[#2EE59D]"
                  />
                </div>
              </div>
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                    Simulated Score
                  </p>
                  <p className="mt-2 text-3xl font-semibold text-white">
                    <AnimatedValue value={simScore} className="text-3xl font-semibold text-white" />
                  </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                    Approval Probability
                  </p>
                  <p className="mt-2 text-3xl font-semibold text-white">
                    <AnimatedValue value={simApproval * 100} suffix="%" decimals={1} className="text-3xl font-semibold text-white" />
                  </p>
                </div>
              </div>
              <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-white/10">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${simApproval * 100}%` }}
                  transition={{ duration: 0.8 }}
                  className="h-full rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF]"
                />
              </div>
            </motion.div>

            <motion.div
              whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
              transition={{ type: "spring", stiffness: 120, damping: 16 }}
              className="glass glow-border rounded-3xl p-6"
            >
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                Activity Feed
              </p>
              <p className="mt-3 text-sm text-muted">
                Live underwriting telemetry captured for audit readiness.
              </p>
              <div className="mt-5 space-y-3">
                <AnimatePresence initial={false}>
                  {feed.map((item) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -6 }}
                      className="rounded-2xl border border-white/10 bg-white/5 p-4"
                    >
                      <p className="text-sm text-white">{item.message}</p>
                      <p className="mt-2 text-[11px] text-muted">{item.time}</p>
                    </motion.div>
                  ))}
                </AnimatePresence>
                {feed.length === 0 && (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
                    No audit events yet. Launch an assessment to capture underwriting logs.
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {showSkeleton && (
              <>
                {[0, 1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="glass glow-border rounded-3xl p-6"
                  >
                    <div className="h-4 w-1/3 rounded-full bg-white/10" />
                    <div className="mt-6 h-6 w-1/2 rounded-full bg-white/10" />
                    <div className="mt-6 h-2 w-full rounded-full bg-white/10" />
                    <div className="mt-3 h-2 w-5/6 rounded-full bg-white/10" />
                    <div className="mt-6 grid gap-3 sm:grid-cols-2">
                      <div className="h-16 rounded-2xl bg-white/5" />
                      <div className="h-16 rounded-2xl bg-white/5" />
                    </div>
                  </div>
                ))}
              </>
            )}
            {riskResult && (
              <RiskResultCard
                data={riskResult}
                onExplain={() => handleRun("Explain Decision")}
                onCompare={() => handleRun("Compare Models")}
              />
            )}
            {fraudResult && <FraudResultCard data={fraudResult} />}
            {riskResult && <ExplainabilityCard factors={riskResult.factors} />}
            {modelMetrics && (
              <ModelComparisonCard
                data={modelMetrics}
                recommended="Gradient Boosting"
              />
            )}
          </div>

          {history.length > 0 && (
            <motion.div
              whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
              transition={{ type: "spring", stiffness: 120, damping: 16 }}
              className="glass glow-border rounded-3xl p-6"
            >
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                Recent Assessments
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {history.map((item) => (
                  <div
                    key={item.timestamp}
                    className="rounded-2xl border border-white/10 bg-white/5 p-4"
                  >
                    <p className="text-sm font-semibold text-white">
                      Score {item.score} • {item.riskBand} Risk
                    </p>
                    <p className="mt-2 text-xs text-muted">
                      Approval {(item.approvalProbability * 100).toFixed(1)}% • Fraud{" "}
                      {(item.fraudProbability * 100).toFixed(2)}% • Policy ready
                    </p>
                    <p className="mt-2 text-xs text-muted">{item.timestamp}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </main>
      </motion.div>
    </div>
  );
}
