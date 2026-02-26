"use client";

import { useEffect, useRef } from "react";
import { animate, motion } from "framer-motion";

type FraudResult = {
  probability: number;
  flags: string[];
  fields: {
    name: string;
    idNumber: string;
    employer: string;
    income: string;
  };
};

type Props = {
  data: FraudResult;
};

function AnimatedNumber({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: 0.9,
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = `${latest.toFixed(2)}%`;
        }
      },
    });
    return () => controls.stop();
  }, [value]);

  return <span ref={ref} />;
}

export default function FraudResultCard({ data }: Props) {
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
            Fraud Probability
          </p>
          <p className="mt-3 text-3xl font-semibold text-white">
            <AnimatedNumber value={data.probability * 100} />
          </p>
        </div>
        <span className="rounded-full bg-[#FF5C5C]/20 px-3 py-1 text-xs font-semibold text-[#FF5C5C]">
          OCR Screening
        </span>
      </div>
      <div className="mt-5 grid gap-3 text-xs text-muted sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
            Name
          </p>
          <p className="mt-2 text-sm font-semibold text-white">{data.fields.name}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
            ID
          </p>
          <p className="mt-2 text-sm font-semibold text-white">
            {data.fields.idNumber}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
            Employer
          </p>
          <p className="mt-2 text-sm font-semibold text-white">
            {data.fields.employer}
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
            Income
          </p>
          <p className="mt-2 text-sm font-semibold text-white">
            {data.fields.income}
          </p>
        </div>
      </div>
      <div className="mt-5">
        <p className="text-xs uppercase tracking-[0.3em] text-muted">
          Risk Flags
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {data.flags.map((flag) => (
            <span
              key={flag}
              className="rounded-full border border-[#FF5C5C]/30 bg-[#FF5C5C]/10 px-3 py-1 text-xs text-[#FF5C5C]"
            >
              {flag}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
