"use client";

import { motion } from "framer-motion";
import type { LoanEligibility, ImprovementSuggestion, PotentialIncrease } from "@/lib/api";
import { formatCurrency, getPriorityColor, getPriorityBgColor } from "@/lib/assistantHelpers";
import { useEffect, useRef } from "react";
import { animate } from "framer-motion";

type Props = {
  eligibility: LoanEligibility;
  suggestions: ImprovementSuggestion[];
  potentialIncrease: Record<string, PotentialIncrease>;
  decision?: string;
};

function AnimatedAmount({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1.2,
      ease: "easeOut",
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = formatCurrency(Math.round(latest));
        }
      },
    });
    return () => controls.stop();
  }, [value]);
  return <span ref={ref} />;
}

export default function LoanEligibilityCard({ eligibility, suggestions, potentialIncrease, decision }: Props) {
  const hasEligibility = eligibility.eligible_loan_amount > 0;

  return (
    <div className="space-y-6">
      {/* Main Eligibility Card */}
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
              Loan Eligibility
            </p>
            <p className="mt-3 text-4xl font-semibold text-white">
              {hasEligibility ? <AnimatedAmount value={eligibility.eligible_loan_amount} /> : "₹0"}
            </p>
            <p className="mt-2 text-sm text-muted">
              {hasEligibility
                ? `Based on ${eligibility.income_used} income & ${eligibility.expense_used} expenses`
                : decision === "REJECTED"
                  ? "Not eligible — Application rejected"
                  : "Complete verification to unlock eligibility"
              }
            </p>
          </div>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
            hasEligibility
              ? "bg-[#2EE59D]/20 text-[#2EE59D]"
              : "bg-[#FF5C5C]/20 text-[#FF5C5C]"
          }`}>
            {hasEligibility ? "Eligible" : "Not Eligible"}
          </span>
        </div>

        {hasEligibility && (
          <div className="mt-6 grid gap-3 text-xs text-muted sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
              <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Monthly EMI</p>
              <p className="mt-2 text-sm font-semibold text-white">
                {formatCurrency(eligibility.monthly_emi_estimate)}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
              <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Disposable Income</p>
              <p className="mt-2 text-sm font-semibold text-white">
                {formatCurrency(eligibility.disposable_income)}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
              <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Savings Ratio</p>
              <p className="mt-2 text-sm font-semibold text-white">
                {(eligibility.savings_ratio * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        )}

        {/* Financial Breakdown */}
        <div className="mt-6 grid gap-3 text-xs text-muted sm:grid-cols-2">
          <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <span>Effective Income</span>
            <div className="flex items-center gap-2">
              <span className="text-white font-semibold">{formatCurrency(eligibility.effective_income)}</span>
              <span className={`rounded-full px-2 py-0.5 text-[10px] ${
                eligibility.income_used === "verified"
                  ? "bg-[#2EE59D]/20 text-[#2EE59D]"
                  : "bg-[#FF9F43]/20 text-[#FF9F43]"
              }`}>
                {eligibility.income_used}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <span>Effective Expense</span>
            <div className="flex items-center gap-2">
              <span className="text-white font-semibold">{formatCurrency(eligibility.effective_expense)}</span>
              <span className={`rounded-full px-2 py-0.5 text-[10px] ${
                eligibility.expense_used === "verified"
                  ? "bg-[#2EE59D]/20 text-[#2EE59D]"
                  : "bg-[#FF9F43]/20 text-[#FF9F43]"
              }`}>
                {eligibility.expense_used}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Potential Increase Section */}
      {Object.keys(potentialIncrease).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
          className="glass rounded-3xl p-6"
        >
          <p className="text-xs uppercase tracking-[0.3em] text-muted">What-If Scenarios</p>
          <h3 className="mt-3 text-lg font-semibold text-white">How to Increase Your Eligibility</h3>
          <div className="mt-4 space-y-3">
            {Object.entries(potentialIncrease).map(([key, scenario]) => (
              <div key={key} className="flex items-center justify-between rounded-2xl border border-[#4F7FFF]/20 bg-[#4F7FFF]/5 px-4 py-3 text-sm">
                <span className="text-muted">{scenario.description}</span>
                <div className="text-right">
                  <span className="font-semibold text-[#2EE59D]">
                    +{formatCurrency(scenario.increase_amount)}
                  </span>
                  <p className="text-[10px] text-muted">
                    New: {formatCurrency(scenario.new_eligible_amount)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Improvement Suggestions Section */}
      {suggestions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
          className="glass glow-border rounded-3xl p-6"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted">Actionable Insights</p>
              <h3 className="mt-3 text-lg font-semibold text-white">Improve Your Loan Eligibility</h3>
            </div>
            <span className="rounded-full bg-[#9B6BFF]/20 px-3 py-1 text-xs font-semibold text-[#9B6BFF]">
              {suggestions.length} Tips
            </span>
          </div>
          <div className="mt-4 space-y-4">
            {suggestions.map((suggestion, index) => (
              <motion.div
                key={suggestion.category}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + index * 0.05 }}
                className={`rounded-2xl border p-4 ${getPriorityBgColor(suggestion.priority)}`}
              >
                <div className="flex items-center justify-between">
                  <h4 className={`text-sm font-semibold ${getPriorityColor(suggestion.priority)}`}>
                    {suggestion.category}
                  </h4>
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${getPriorityColor(suggestion.priority)}`}>
                    {suggestion.priority}
                  </span>
                </div>
                <p className="mt-2 text-sm text-muted">{suggestion.message}</p>
                <p className="mt-1 text-xs text-white/60">Impact: {suggestion.impact}</p>
                {suggestion.action_items.length > 0 && (
                  <ul className="mt-3 space-y-1">
                    {suggestion.action_items.map((item, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-muted">
                        <span className="mt-1 h-1 w-1 flex-shrink-0 rounded-full bg-white/30" />
                        {item}
                      </li>
                    ))}
                  </ul>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
