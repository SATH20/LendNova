"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import AnimatedValue from "@/components/AnimatedValue";
import ModelComparisonCard from "@/components/ModelComparisonCard";

const pipelineSteps = [
  { title: "User Data", detail: "Consent-driven bank, wallet, and utility signals." },
  { title: "OCR Engine", detail: "High-accuracy extraction from payslips & bank statements." },
  { title: "ML Model", detail: "Gradient boosting with fairness guardrails." },
  { title: "Decision", detail: "Score, loan eligibility, and actionable insights." },
];

const capabilities = [
  {
    title: "OCR-First Verification",
    description: "Extract and verify income through document intelligence — verified data always overrides declared values.",
  },
  {
    title: "Explainable AI",
    description: "Every credit decision comes with SHAP-powered explanations showing exactly why.",
  },
  {
    title: "Loan Eligibility",
    description: "Dynamic loan amount calculation based on verified financials, employment type, and behavioral metrics.",
  },
  {
    title: "Actionable Insights",
    description: "Personalized improvement suggestions — reduce expenses by X, increase tenure, verify documents.",
  },
  {
    title: "Fraud Detection",
    description: "OCR integrity checks, identity mismatch detection, and anomaly scoring with Isolation Forest.",
  },
  {
    title: "Privacy-First",
    description: "Encrypted processing, masked identity storage, and auditable evidence trails throughout.",
  },
];

const modelData = [
  { model: "Logistic Regression", accuracy: 0.78, explainability: 0.86 },
  { model: "Random Forest", accuracy: 0.84, explainability: 0.62 },
  { model: "Gradient Boosting", accuracy: 0.89, explainability: 0.74 },
];

export default function Home() {
  const [activePipeline, setActivePipeline] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActivePipeline((prev) => (prev + 1) % pipelineSteps.length);
    }, 2200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh-bg pointer-events-none absolute inset-0 opacity-70" />
      <Navbar />
      <motion.main
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 mx-auto flex w-full max-w-6xl flex-col gap-20 px-6 pb-20 pt-16"
      >
        {/* ── Hero ── */}
        <section className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-[#9B6BFF]">
              AI-Based Underwriting
            </p>
            <h1 className="mt-4 text-4xl font-semibold text-white md:text-5xl">
              Intelligent Credit Scoring for First-Time Borrowers
            </h1>
            <p className="mt-6 text-lg text-muted">
              LendNova merges OCR-verified data, cash-flow intelligence, and
              fairness-aware models to approve thin-file applicants with full
              transparency.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                href="/assistant"
                id="hero-run-assessment"
                className="ripple rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
              >
                Run Assessment
              </Link>
              <a
                href="#pipeline"
                className="ripple rounded-full border border-white/15 bg-white/5 px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10 focus:outline-none"
              >
                How It Works
              </a>
            </div>
          </div>

          {/* Live Signal Card */}
          <motion.div
            whileHover={{ y: -4 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              Live Credit Signal
            </p>
            <div className="mt-3">
              <AnimatedValue value={768} className="text-4xl font-semibold text-white" />
            </div>
            <p className="mt-2 text-sm text-muted">
              Based on verified alternative data sources.
            </p>
            <div className="mt-6">
              <div className="flex items-center justify-between text-xs text-muted">
                <span>Model Confidence</span>
                <span className="text-white font-semibold">89%</span>
              </div>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-white/10">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "89%" }}
                  transition={{ duration: 1.2 }}
                  className="h-full rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF]"
                />
              </div>
            </div>
          </motion.div>
        </section>

        {/* ── Pipeline ── */}
        <section id="pipeline">
          <p className="text-xs uppercase tracking-[0.3em] text-muted">Pipeline</p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            How the decision engine works
          </h2>
          <div className="mt-6 flex flex-wrap gap-3">
            {pipelineSteps.map((step, index) => {
              const isActive = index === activePipeline;
              return (
                <div key={step.title} className="flex items-center gap-3">
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.08 }}
                    className={`group relative rounded-full border px-4 py-2 text-xs uppercase tracking-[0.2em] transition-all duration-300 ${
                      isActive
                        ? "border-[#4F7FFF]/70 bg-[#4F7FFF]/15 text-white shadow-[0_0_25px_rgba(79,127,255,0.35)]"
                        : "border-white/10 bg-white/5 text-muted"
                    }`}
                  >
                    {step.title}
                    <div className="pointer-events-none absolute left-1/2 top-[120%] z-20 w-48 -translate-x-1/2 rounded-2xl border border-white/10 bg-[#0B1022]/95 px-4 py-3 text-[11px] normal-case tracking-normal text-muted opacity-0 transition group-hover:opacity-100">
                      {step.detail}
                    </div>
                  </motion.div>
                  {index < pipelineSteps.length - 1 && (
                    <motion.span
                      initial={{ width: 0, opacity: 0.4 }}
                      animate={{
                        width: isActive ? 26 : 16,
                        opacity: isActive ? 0.9 : 0.4,
                      }}
                      transition={{ duration: 0.6 }}
                      className="hidden h-[2px] rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] sm:block"
                    />
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {/* ── Capabilities ── */}
        <section id="capabilities">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                Core Capabilities
              </p>
              <h2 className="mt-3 text-2xl font-semibold text-white">
                What makes LendNova different
              </h2>
            </div>
            <Link
              href="/assistant"
              className="ripple rounded-full border border-white/10 bg-white/5 px-5 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10"
            >
              Try It Now
            </Link>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((cap, i) => (
              <motion.div
                key={cap.title}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                whileHover={{ y: -4 }}
                className="glass rounded-3xl p-5"
              >
                <p className="text-sm font-semibold text-white">{cap.title}</p>
                <p className="mt-3 text-sm text-muted">{cap.description}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── Models ── */}
        <section id="models" className="grid gap-6 lg:grid-cols-2">
          <div className="glass glow-border rounded-3xl p-6">
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              Model Comparison
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              Accuracy vs Explainability
            </h2>
            <p className="mt-4 text-sm text-muted">
              LendNova benchmarks interpretable and high-lift learners to balance
              explanations with performance.
            </p>
            <div className="mt-6 space-y-3 text-sm text-muted">
              {[
                { name: "Logistic Regression", tag: "High Interpretability", color: "text-[#9B6BFF]" },
                { name: "Random Forest", tag: "Robust Non-Linearity", color: "text-[#4F7FFF]" },
                { name: "Gradient Boosting", tag: "Recommended", color: "text-[#2EE59D]" },
              ].map((m) => (
                <div key={m.name} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <span>{m.name}</span>
                  <span className={m.color}>{m.tag}</span>
                </div>
              ))}
            </div>
          </div>
          <ModelComparisonCard data={modelData} recommended="Gradient Boosting" />
        </section>

        {/* ── Security ── */}
        <section id="security" className="glass glow-border rounded-3xl p-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">Security</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">
                Privacy-first decisioning
              </h2>
            </div>
            <span className="rounded-full bg-[#2EE59D]/20 px-4 py-2 text-xs font-semibold text-[#2EE59D]">
              SOC2-Aligned
            </span>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {[
              "Encrypted Data Processing",
              "No Raw ID Storage",
              "Privacy-First Controls",
              "Secure APIs + Audit Trails",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-semibold text-white">{item}</p>
                <p className="mt-2 text-sm text-muted">
                  Cryptographic controls enforce lender-grade privacy and auditability.
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="glass rounded-3xl p-6 text-xs text-muted">
          <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
            <div>
              <p className="text-sm font-semibold text-white">LENDNOVA</p>
              <p className="mt-1">© 2026 Built by Rajavarapu Sathwik</p>
            </div>
            <div className="flex items-center gap-4">
              <a href="https://www.instagram.com/_sathwikkkk_?igsh=MWcyc3lwbWd0eWJkcQ==" target="_blank" rel="noopener noreferrer" className="transition hover:text-white">Instagram</a>
              <span className="text-white/20">•</span>
              <a href="https://github.com/SATH20/LendNova" target="_blank" rel="noopener noreferrer" className="transition hover:text-white">GitHub</a>
            </div>
          </div>
        </footer>
      </motion.main>
    </div>
  );
}
