"use client";

import { useEffect, useRef, useState } from "react";
import { animate, motion } from "framer-motion";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import ModelComparisonCard from "@/components/ModelComparisonCard";

const pipelineSteps = [
  {
    title: "User Data",
    detail: "Consent-driven bank, wallet, and utility signals.",
  },
  {
    title: "Feature Engineering",
    detail: "Affordability ratios and stability vectors for thin files.",
  },
  {
    title: "ML Model",
    detail: "Gradient boosting with fairness guardrails.",
  },
  {
    title: "Fraud Detection",
    detail: "OCR integrity, document tamper checks, and ID matching.",
  },
  {
    title: "Decision",
    detail: "Score, confidence, and policy-aligned recommendation.",
  },
];

const metrics = [
  { label: "Credit Risk Score", value: 812, suffix: "" },
  { label: "Approval Probability", value: 88, suffix: "%" },
  { label: "Fraud Likelihood", value: 4, suffix: "%" },
];

const capabilities = [
  "Alternative Data Engine",
  "Bias-Reduced Scoring",
  "OCR Fraud Detection",
  "Explainable AI",
  "Secure Data Pipeline",
];

const securityItems = [
  "Encrypted Data Processing",
  "No Raw ID Storage",
  "Privacy-First Controls",
  "Secure APIs + Audit Trails",
];

const techStack = ["Next.js", "Python", "Flask", "Scikit-learn", "OCR", "Database"];

const modelData = [
  { model: "Logistic Regression", accuracy: 0.78, explainability: 0.86 },
  { model: "Random Forest", accuracy: 0.84, explainability: 0.62 },
  { model: "Gradient Boosting", accuracy: 0.89, explainability: 0.74 },
];

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
      duration: 1.1,
      ease: "easeOut",
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = `${latest.toFixed(decimals)}${suffix ?? ""}`;
        }
      },
    });
    return () => controls.stop();
  }, [value, suffix, decimals]);
  return (
    <span ref={ref} className={className ?? "text-3xl font-semibold text-white"} />
  );
}

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
        className="relative z-10 mx-auto flex w-full max-w-6xl flex-col gap-24 px-6 pb-24 pt-16"
      >
        <section className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-[#9B6BFF]">
              AI-Based Underwriting
            </p>
            <h1 className="mt-4 text-4xl font-semibold text-white md:text-5xl">
              Intelligent Credit Scoring for First-Time Borrowers
            </h1>
            <p className="mt-6 text-lg text-muted">
              LENDNOVA merges cash-flow intelligence, verified OCR identity signals,
              and fairness-aware models to approve thin-file applicants with clarity.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                href="/assistant"
                className="ripple rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
              >
                Run Assessment
              </Link>
              <a
                href="#architecture"
                className="ripple rounded-full border border-white/15 bg-white/5 px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
              >
                View Architecture
              </a>
            </div>
          </div>
          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              Live Credit Signal
            </p>
            <AnimatedValue value={768} className="text-4xl font-semibold text-white" />
            <p className="mt-2 text-sm text-muted">
              Confidence index based on verified alternative data sources.
            </p>
            <div className="mt-6">
              <div className="flex items-center justify-between text-xs text-muted">
                <span>Model Confidence</span>
                <span className="text-white">
                  <AnimatedValue value={89} suffix="%" decimals={1} className="text-xs font-semibold text-white" />
                </span>
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
            <div className="mt-6 grid gap-3 text-xs text-muted sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                  OCR Integrity
                </p>
                <p className="mt-2 text-sm font-semibold text-white">
                  Document match score 98.4%
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
                <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                  Bias Monitor
                </p>
                <p className="mt-2 text-sm font-semibold text-white">
                  Fairness variance within 1.2%
                </p>
              </div>
            </div>
          </motion.div>
        </section>

        <section id="pipeline" className="glass glow-border rounded-3xl p-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                AI Pipeline
              </p>
              <h2 className="mt-3 text-2xl font-semibold text-white">
                Real-time decision orchestration across the underwriting stack
              </h2>
            </div>
            <a
              href="#architecture"
              className="ripple rounded-full border border-white/10 bg-white/5 px-5 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
            >
              View Architecture
            </a>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            {pipelineSteps.map((step, index) => {
              const isActive = index === activePipeline;
              return (
                <div key={step.title} className="flex items-center gap-3">
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.08 }}
                    className={`group relative rounded-full border px-4 py-2 text-xs uppercase tracking-[0.2em] ${
                      isActive
                        ? "border-[#4F7FFF]/70 bg-[#4F7FFF]/15 text-white shadow-[0_0_25px_rgba(79,127,255,0.35)]"
                        : "border-white/10 bg-white/5 text-muted"
                    }`}
                  >
                    {step.title}
                    <div className="pointer-events-none absolute left-1/2 top-[120%] w-56 -translate-x-1/2 rounded-2xl border border-white/10 bg-[#0B1022]/95 px-4 py-3 text-[11px] normal-case tracking-normal text-muted opacity-0 transition group-hover:opacity-100">
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
                      className="h-[2px] rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF]"
                    />
                  )}
                </div>
              );
            })}
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          {metrics.map((metric) => (
            <motion.div
              key={metric.label}
              whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
              transition={{ type: "spring", stiffness: 120, damping: 16 }}
              className="glass glow-border rounded-3xl p-6"
            >
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                {metric.label}
              </p>
              <div className="mt-4">
                <AnimatedValue value={metric.value} suffix={metric.suffix} />
              </div>
              <p className="mt-3 text-sm text-muted">
                Updated from live underwriting telemetry and policy constraints.
              </p>
            </motion.div>
          ))}
        </section>

        <section id="capabilities">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                Core Capabilities
              </p>
              <h2 className="mt-3 text-2xl font-semibold text-white">
                Bank-grade AI underwriting
              </h2>
            </div>
            <Link
              href="/assistant"
              className="ripple rounded-full border border-white/10 bg-white/5 px-5 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
            >
              Open Risk Console
            </Link>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((capability) => (
              <motion.div
                key={capability}
                whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
                transition={{ type: "spring", stiffness: 120, damping: 16 }}
                className="glass rounded-3xl p-5"
              >
                <p className="text-sm font-semibold text-white">{capability}</p>
                <p className="mt-3 text-sm text-muted">
                  Continuous policy monitoring aligns model outcomes with regulated
                  credit governance.
                </p>
              </motion.div>
            ))}
          </div>
        </section>

        <section id="models" className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              Model Comparison
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              Balanced accuracy with interpretability
            </h2>
            <p className="mt-4 text-sm text-muted">
              LENDNOVA benchmarks interpretable and high-lift learners to balance
              regulator-friendly explanations with underwriting performance.
            </p>
            <div className="mt-6 space-y-3 text-sm text-muted">
              <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span>Logistic Regression</span>
                <span className="text-[#9B6BFF]">High Interpretability</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span>Random Forest</span>
                <span className="text-[#4F7FFF]">Robust Non-Linearity</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <span>Gradient Boosting</span>
                <span className="text-[#2EE59D]">Recommended</span>
              </div>
            </div>
          </motion.div>
          <ModelComparisonCard data={modelData} recommended="Gradient Boosting" />
        </section>

        <section id="security" className="glass glow-border rounded-3xl p-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">
                Security
              </p>
              <h2 className="mt-3 text-2xl font-semibold text-white">
                Privacy-first decisioning
              </h2>
            </div>
            <span className="rounded-full bg-[#2EE59D]/20 px-4 py-2 text-xs font-semibold text-[#2EE59D]">
              SOC2-aligned controls
            </span>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {securityItems.map((item) => (
              <motion.div
                key={item}
                whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
                transition={{ type: "spring", stiffness: 120, damping: 16 }}
                className="rounded-3xl border border-white/10 bg-white/5 p-5"
              >
                <p className="text-sm font-semibold text-white">{item}</p>
                <p className="mt-3 text-sm text-muted">
                  Cryptographic controls enforce lender-grade privacy and auditability.
                </p>
              </motion.div>
            ))}
          </div>
        </section>

        <section id="architecture" className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              Tech Stack
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              Built for AI credit operations
            </h2>
            <p className="mt-4 text-sm text-muted">
              Built for regulated underwriting pipelines with resilient APIs and
              explainability services.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              {techStack.map((tech) => (
                <span
                  key={tech}
                  className="rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold text-white"
                >
                  {tech}
                </span>
              ))}
            </div>
          </motion.div>
          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass rounded-3xl p-6"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-muted">
              System Highlights
            </p>
            <div className="mt-4 space-y-3 text-sm text-muted">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Alternative-data ingestion with fairness diagnostics and drift alarms.
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                OCR-based fraud detection with masked identity field storage.
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Explainable AI decisions with auditable evidence trails.
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Secure API gateway for credit operations integrations.
              </div>
            </div>
          </motion.div>
        </section>

        <footer className="glass rounded-3xl p-6 text-xs text-muted">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-white">LENDNOVA</p>
              <p className="mt-2">
                © 2026 Built by Rajavarapu Sathwik • Ethical AI Lending Initiative
              </p>
            </div>
            <div className="flex items-center gap-4 text-right">
              <a
                href="https://www.instagram.com/_sathwikkkk_?igsh=MWcyc3lwbWd0eWJkcQ=="
                target="_blank"
                rel="noopener noreferrer"
                className="transition hover:text-white"
              >
                Instagram
              </a>
              <span className="text-white/20">•</span>
              <a
                href="https://github.com/SATH20/LendNova"
                target="_blank"
                rel="noopener noreferrer"
                className="transition hover:text-white"
              >
                GitHub
              </a>
            </div>
          </div>
        </footer>
      </motion.main>
    </div>
  );
}
