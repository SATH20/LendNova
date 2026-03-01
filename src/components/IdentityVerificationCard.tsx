"use client";

import { useEffect, useRef } from "react";
import { animate, motion } from "framer-motion";

type IdentityVerification = {
  trustScore: number;
  identityStatus: "VERIFIED" | "SUSPICIOUS" | "FAILED";
  verificationReasons: string[];
};

type Props = {
  data: IdentityVerification;
};

function AnimatedNumber({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: 0.9,
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = `${latest.toFixed(1)}`;
        }
      },
    });
    return () => controls.stop();
  }, [value]);

  return <span ref={ref} />;
}

export default function IdentityVerificationCard({ data }: Props) {
  const statusConfig = {
    VERIFIED: {
      color: "bg-[#2EE59D]/20 text-[#2EE59D]",
      icon: "🟢",
      label: "Verified Identity",
      description: "All identity checks passed successfully",
    },
    SUSPICIOUS: {
      color: "bg-[#9B6BFF]/20 text-[#9B6BFF]",
      icon: "🟡",
      label: "Suspicious Identity",
      description: "Some verification checks require review",
    },
    FAILED: {
      color: "bg-[#FF5C5C]/20 text-[#FF5C5C]",
      icon: "🔴",
      label: "Verification Failed",
      description: "Identity verification did not meet requirements",
    },
  };

  const config = statusConfig[data.identityStatus];
  const trustPercentage = data.trustScore * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
      transition={{ type: "spring", stiffness: 120, damping: 16 }}
      className="glass glow-border rounded-3xl p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-muted">
            Identity Verification
          </p>
          <p className="mt-3 text-3xl font-semibold text-white">
            <AnimatedNumber value={trustPercentage} />%
          </p>
          <p className="mt-2 text-sm text-muted">Trust Score</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${config.color}`}>
          {config.icon} {config.label}
        </span>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between text-xs text-muted">
          <span>Trust Level</span>
          <span className="text-white">{trustPercentage.toFixed(1)}%</span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${trustPercentage}%` }}
            transition={{ duration: 0.8 }}
            className={`h-full rounded-full ${
              data.identityStatus === "VERIFIED"
                ? "bg-gradient-to-r from-[#2EE59D] to-[#4F7FFF]"
                : data.identityStatus === "SUSPICIOUS"
                ? "bg-gradient-to-r from-[#9B6BFF] to-[#4F7FFF]"
                : "bg-gradient-to-r from-[#FF5C5C] to-[#9B6BFF]"
            }`}
          />
        </div>
      </div>

      <div className="mt-5">
        <p className="text-xs uppercase tracking-[0.3em] text-muted">
          Verification Pipeline
        </p>
        <div className="mt-3 grid gap-2 text-xs">
          <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-3">
            <span className="text-[#2EE59D]">✓</span>
            <span className="text-muted">OCR Extraction</span>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-3">
            <span className="text-[#2EE59D]">✓</span>
            <span className="text-muted">Identity Consistency Check</span>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-3">
            <span className="text-[#2EE59D]">✓</span>
            <span className="text-muted">Document Authenticity Check</span>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-3">
            <span className="text-[#2EE59D]">✓</span>
            <span className="text-muted">Data Plausibility Validation</span>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-3">
            <span className="text-[#2EE59D]">✓</span>
            <span className="text-muted">Behavioral Risk Analysis</span>
          </div>
        </div>
      </div>

      {data.verificationReasons.length > 0 && (
        <div className="mt-5">
          <p className="text-xs uppercase tracking-[0.3em] text-muted">
            Verification Findings
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {data.verificationReasons.map((reason, index) => (
              <span
                key={index}
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

      <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
        <p className="text-sm text-muted">{config.description}</p>
      </div>
    </motion.div>
  );
}
