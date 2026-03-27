"use client";

import { motion } from "framer-motion";
import AnimatedValue from "./AnimatedValue";

type IdentityVerification = {
  trustScore: number;
  identityStatus: "VERIFIED" | "SUSPICIOUS" | "FAILED";
  verificationReasons: string[];
};

type Props = {
  data: IdentityVerification;
};

const statusConfig = {
  VERIFIED: {
    color: "bg-[#2EE59D]/20 text-[#2EE59D]",
    label: "Verified",
    gradientClass: "bg-gradient-to-r from-[#2EE59D] to-[#4F7FFF]",
    description: "All identity checks passed successfully.",
  },
  SUSPICIOUS: {
    color: "bg-[#9B6BFF]/20 text-[#9B6BFF]",
    label: "Suspicious",
    gradientClass: "bg-gradient-to-r from-[#9B6BFF] to-[#4F7FFF]",
    description: "Some verification checks need review.",
  },
  FAILED: {
    color: "bg-[#FF5C5C]/20 text-[#FF5C5C]",
    label: "Failed",
    gradientClass: "bg-gradient-to-r from-[#FF5C5C] to-[#9B6BFF]",
    description: "Identity verification did not pass.",
  },
};

const verificationSteps = [
  "OCR Extraction",
  "Identity Consistency",
  "Document Authenticity",
  "Data Plausibility",
];

export default function IdentityVerificationCard({ data }: Props) {
  const config = statusConfig[data.identityStatus];
  const trustPercentage = data.trustScore * 100;

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
          <p className="text-xs uppercase tracking-[0.3em] text-muted">Trust Score</p>
          <p className="mt-3 text-3xl font-semibold text-white">
            <AnimatedValue value={trustPercentage} suffix="%" decimals={1} />
          </p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${config.color}`}>
          {config.label}
        </span>
      </div>

      <div className="mt-6">
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${trustPercentage}%` }}
            transition={{ duration: 0.8 }}
            className={`h-full rounded-full ${config.gradientClass}`}
          />
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 text-xs">
        {verificationSteps.map((step) => (
          <div key={step} className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2">
            <span className="text-[#2EE59D]">✓</span>
            <span className="text-muted">{step}</span>
          </div>
        ))}
      </div>

      {data.verificationReasons.length > 0 && (
        <div className="mt-5">
          <p className="text-xs uppercase tracking-[0.3em] text-muted">Findings</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {data.verificationReasons.map((reason, i) => (
              <span
                key={i}
                className={`rounded-full border px-3 py-1 text-xs ${
                  data.identityStatus === "VERIFIED"
                    ? "border-[#2EE59D]/30 bg-[#2EE59D]/10 text-[#2EE59D]"
                    : data.identityStatus === "SUSPICIOUS"
                    ? "border-[#9B6BFF]/30 bg-[#9B6BFF]/10 text-[#9B6BFF]"
                    : "border-[#FF5C5C]/30 bg-[#FF5C5C]/10 text-[#FF5C5C]"
                }`}
              >
                {reason}
              </span>
            ))}
          </div>
        </div>
      )}

      <p className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-muted">
        {config.description}
      </p>
    </motion.div>
  );
}
