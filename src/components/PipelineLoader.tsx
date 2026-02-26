"use client";

import { motion } from "framer-motion";

const steps = [
  {
    title: "User Data",
    detail: "Bank signals, cash flow, and consented alternative data feeds.",
  },
  {
    title: "Features",
    detail: "Stability, affordability, and repayment proxy engineering.",
  },
  {
    title: "Model",
    detail: "Gradient boosting risk inference with fairness constraints.",
  },
  {
    title: "Fraud",
    detail: "OCR integrity checks and identity mismatch detection.",
  },
  {
    title: "Decision",
    detail: "Explainable score, confidence, and underwriting recommendation.",
  },
];

type Props = {
  activeStep: number;
  loading: boolean;
};

export default function PipelineLoader({ activeStep, loading }: Props) {
  return (
    <motion.div
      whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="glass glow-border rounded-3xl px-6 py-5"
    >
      <div className="flex flex-wrap items-center gap-3">
        {steps.map((step, index) => {
          const isActive = loading && index <= activeStep;
          const isCurrent = loading && index === activeStep;
          return (
            <div key={step.title} className="flex items-center gap-3">
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.06 }}
                className={`group relative flex items-center gap-2 rounded-full border px-4 py-2 text-xs uppercase tracking-[0.2em] ${
                  isActive
                    ? "border-[#4F7FFF]/70 bg-[#4F7FFF]/15 text-white shadow-[0_0_25px_rgba(79,127,255,0.3)]"
                    : "border-white/10 bg-white/5 text-muted"
                } ${isCurrent ? "neon-ring" : ""}`}
              >
                <span className="h-2 w-2 rounded-full bg-current" />
                {step.title}
                <div className="pointer-events-none absolute left-1/2 top-[120%] w-56 -translate-x-1/2 rounded-2xl border border-white/10 bg-[#0B1022]/95 px-4 py-3 text-[11px] normal-case tracking-normal text-muted opacity-0 transition group-hover:opacity-100">
                  {step.detail}
                </div>
              </motion.div>
              {index < steps.length - 1 && (
                <motion.span
                  initial={{ width: 0, opacity: 0.4 }}
                  animate={{
                    width: isActive ? 28 : 16,
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
      {loading && (
        <div className="mt-4 space-y-3">
          <div className="h-4 w-full rounded-full bg-white/5" />
          <div className="h-4 w-5/6 rounded-full bg-white/5" />
          <div className="h-4 w-2/3 rounded-full bg-white/5" />
        </div>
      )}
    </motion.div>
  );
}
