"use client";

import { motion } from "framer-motion";
import AnimatedValue from "./AnimatedValue";

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

export default function FraudResultCard({ data }: Props) {
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
          <p className="text-xs uppercase tracking-[0.3em] text-muted">
            Fraud Probability
          </p>
          <p className="mt-3 text-3xl font-semibold text-white">
            <AnimatedValue value={data.probability * 100} suffix="%" decimals={2} />
          </p>
        </div>
        <span className="rounded-full bg-[#FF5C5C]/20 px-3 py-1 text-xs font-semibold text-[#FF5C5C]">
          OCR Screening
        </span>
      </div>
      <div className="mt-5 grid gap-3 text-xs text-muted sm:grid-cols-2">
        {[
          { label: "Name", value: data.fields.name },
          { label: "Document ID", value: data.fields.idNumber },
          { label: "Employer", value: data.fields.employer },
          { label: "Income", value: data.fields.income },
        ].map((field) => (
          <div key={field.label} className="rounded-2xl border border-white/10 bg-white/5 p-3">
            <p className="text-[10px] uppercase tracking-[0.25em] text-muted">{field.label}</p>
            <p className="mt-2 text-sm font-semibold text-white">{field.value}</p>
          </div>
        ))}
      </div>
      {data.flags.length > 0 && (
        <div className="mt-5">
          <p className="text-xs uppercase tracking-[0.3em] text-muted">Risk Flags</p>
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
      )}
    </motion.div>
  );
}
