"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";

type Props = {
  baseIncome: number;
  baseExpenses: number;
  baseEligibleAmount: number;
  employmentType: string;
};

const EMPLOYMENT_MULTIPLIERS: Record<string, { income_factor: number; max_dti: number }> = {
  "full-time":     { income_factor: 15, max_dti: 0.50 },
  "self-employed": { income_factor: 10, max_dti: 0.40 },
  "part-time":     { income_factor: 8,  max_dti: 0.35 },
  "student":       { income_factor: 5,  max_dti: 0.25 },
  "unemployed":    { income_factor: 2,  max_dti: 0.15 },
};

function calcEligibility(income: number, expenses: number, empType: string): number {
  const key = empType.toLowerCase();
  const cfg = EMPLOYMENT_MULTIPLIERS[key] || { income_factor: 8, max_dti: 0.35 };
  const disposable = Math.max(0, income - expenses);
  const dtiAmount  = disposable * cfg.max_dti * 12;
  const incomeAmt  = income * cfg.income_factor;
  return Math.round(Math.min(dtiAmount, incomeAmt) / 100) * 100;
}

function formatNum(n: number): string {
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  if (n < 0) return `-₹${Math.abs(n).toLocaleString("en-IN")}`;
  return `₹${n.toLocaleString("en-IN")}`;
}

export default function WhatIfSliders({
  baseIncome, baseExpenses, baseEligibleAmount, employmentType,
}: Props) {
  const [income,   setIncome]   = useState(baseIncome);
  const [expenses, setExpenses] = useState(baseExpenses);

  const newEligibility = useMemo(
    () => calcEligibility(income, expenses, employmentType),
    [income, expenses, employmentType]
  );
  const diff        = newEligibility - baseEligibleAmount;
  const disposable  = Math.max(0, income - expenses);
  const savingsRatio = income > 0 ? disposable / income : 0;

  const incomeMin  = Math.max(500,  Math.round(baseIncome   * 0.4));
  const incomeMax  = Math.round(baseIncome   * 2.8);
  const expenseMin = Math.max(200,  Math.round(baseExpenses * 0.3));
  const expenseMax = Math.round(baseExpenses * 1.8);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass glow-border rounded-3xl p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-muted">What-If Simulator</p>
          <h3 className="mt-2 text-lg font-semibold text-white">Drag to explore your potential</h3>
        </div>
        <button
          onClick={() => { setIncome(baseIncome); setExpenses(baseExpenses); }}
          className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] font-semibold uppercase tracking-wide text-muted transition hover:text-white"
        >
          Reset
        </button>
      </div>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        {/* Income */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs uppercase tracking-[0.2em] text-muted">Monthly Income</label>
            <span className="text-sm font-semibold text-white">{formatNum(income)}</span>
          </div>
          <input
            id="income-slider"
            type="range"
            min={incomeMin} max={incomeMax} step={500}
            value={income}
            onChange={(e) => setIncome(Number(e.target.value))}
            aria-label="Income"
          />
          <div className="flex justify-between text-[10px] text-muted mt-1">
            <span>{formatNum(incomeMin)}</span>
            <span>{formatNum(incomeMax)}</span>
          </div>
        </div>

        {/* Expenses */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs uppercase tracking-[0.2em] text-muted">Monthly Expenses</label>
            <span className="text-sm font-semibold text-white">{formatNum(expenses)}</span>
          </div>
          <input
            id="expense-slider"
            type="range"
            min={expenseMin} max={expenseMax} step={200}
            value={expenses}
            onChange={(e) => setExpenses(Number(e.target.value))}
            aria-label="Expenses"
          />
          <div className="flex justify-between text-[10px] text-muted mt-1">
            <span>{formatNum(expenseMin)}</span>
            <span>{formatNum(expenseMax)}</span>
          </div>
        </div>
      </div>

      {/* Live mini stats */}
      <div className="mt-5 grid grid-cols-3 gap-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
          <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Disposable</p>
          <p className="mt-1 text-sm font-semibold text-white">{formatNum(disposable)}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
          <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Savings</p>
          <p className={`mt-1 text-sm font-semibold ${
            savingsRatio >= 0.3 ? "text-[#2EE59D]" : savingsRatio >= 0.15 ? "text-[#9B6BFF]" : "text-[#FF5C5C]"
          }`}>
            {(savingsRatio * 100).toFixed(0)}%
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
          <p className="text-[10px] uppercase tracking-[0.2em] text-muted">Change</p>
          <p className={`mt-1 text-sm font-semibold ${diff > 0 ? "text-[#2EE59D]" : diff < 0 ? "text-[#FF5C5C]" : "text-muted"}`}>
            {diff > 0 ? "+" : ""}{formatNum(diff)}
          </p>
        </div>
      </div>

      {/* Result */}
      <AnimatePresence mode="wait">
        <motion.div
          key={newEligibility}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 flex items-center justify-between rounded-2xl border border-[#4F7FFF]/25 bg-[#4F7FFF]/8 px-5 py-4"
        >
          <p className="text-sm text-muted">Simulated Loan Eligibility</p>
          <p className="text-xl font-semibold text-white">{formatNum(newEligibility)}</p>
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}
