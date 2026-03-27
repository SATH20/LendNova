"use client";

import { useEffect, useState, useCallback, type ChangeEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import PipelineLoader from "@/components/PipelineLoader";
import RiskResultCard from "@/components/RiskResultCard";
import FraudResultCard from "@/components/FraudResultCard";
import ExplainabilityCard from "@/components/ExplainabilityCard";
import IdentityVerificationCard from "@/components/IdentityVerificationCard";
import LoanEligibilityCard from "@/components/LoanEligibilityCard";
import WhatIfSliders from "@/components/WhatIfSliders";
import CreditCoach from "@/components/CreditCoach";
import DocumentUpload from "@/components/DocumentUpload";
import AssessmentForm from "@/components/AssessmentForm";
import {
  fetchAssessments,
  runAssessment,
  uploadDocument,
  type AssessmentHistoryItem,
  type AssessmentInput,
} from "@/lib/api";
import {
  type RiskResult,
  type FraudResult,
  type HistoryItem,
  type FeedItem,
  mapPredictResponse,
  getDocumentRequirements,
  parseNumber,
  formatCurrency,
} from "@/lib/assistantHelpers";

// ─── State hook ─────────────────────────────────────────────────
function useAssessment() {
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"input" | "processing" | "results">("input");
  const [activeStep, setActiveStep] = useState(0);
  const [riskResult, setRiskResult] = useState<RiskResult | null>(null);
  const [fraudResult, setFraudResult] = useState<FraudResult | null>(null);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [assessmentId, setAssessmentId] = useState<number | null>(null);
  const [payslipFile, setPayslipFile] = useState<File | null>(null);
  const [bankStatementFile, setBankStatementFile] = useState<File | null>(null);
  const [payslipUploaded, setPayslipUploaded] = useState(false);
  const [bankStatementUploaded, setBankStatementUploaded] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState("PENDING");
  const [formData, setFormData] = useState({
    income: "4200",
    expenses: "1700",
    employmentType: "Full-time" as AssessmentInput["employment_type"],
    jobTenure: "3",
    name: "",
    employer: "",
    mobile: "",
  });

  const addFeed = (message: string) =>
    setFeed((prev) => [
      { id: `${Date.now()}-${prev.length}`, message, time: new Date().toLocaleTimeString() },
      ...prev.slice(0, 5),
    ]);

  const buildInput = (): AssessmentInput => ({
    income: parseNumber(formData.income) ?? 0,
    expenses: parseNumber(formData.expenses) ?? 0,
    employment_type: formData.employmentType,
    job_tenure: parseNumber(formData.jobTenure) ?? 0,
  });

  const refreshHistory = useCallback(() => {
    fetchAssessments()
      .then((res) =>
        setHistory(
          res.assessments.map((item: AssessmentHistoryItem) => ({
            timestamp: new Date(item.timestamp).toLocaleString(),
            score: item.credit_score,
            approvalProbability: item.approval_probability,
            fraudProbability: item.fraud_probability ?? 0,
            riskBand: item.risk_band,
          }))
        )
      )
      .catch(() => setHistory([]));
  }, []);

  const reset = () => {
    setMode("input");
    setRiskResult(null);
    setFraudResult(null);
    setPayslipFile(null);
    setBankStatementFile(null);
    setPayslipUploaded(false);
    setBankStatementUploaded(false);
    setVerificationStatus("PENDING");
    setAssessmentId(null);
    setErrorMessage(null);
    setFeed([]);
  };

  return {
    loading, setLoading, mode, setMode, activeStep, setActiveStep,
    riskResult, setRiskResult, fraudResult, setFraudResult,
    feed, addFeed, history, refreshHistory,
    errorMessage, setErrorMessage, assessmentId, setAssessmentId,
    payslipFile, setPayslipFile, bankStatementFile, setBankStatementFile,
    payslipUploaded, setPayslipUploaded, bankStatementUploaded, setBankStatementUploaded,
    verificationStatus, setVerificationStatus, formData, setFormData,
    buildInput, reset,
  };
}

// ─── Page ───────────────────────────────────────────────────────
export default function AssistantPage() {
  const state = useAssessment();
  const [activeTab, setActiveTab] = useState<"overview" | "eligibility" | "coach" | "explain" | "fraud" | "history">("overview");
  const [downloadingReport, setDownloadingReport] = useState(false);

  useEffect(() => { state.refreshHistory(); }, []);

  // ── Assessment ──
  const handleAssessment = async () => {
    const input = state.buildInput();
    if (!input.income || !input.expenses || !input.job_tenure) {
      state.setErrorMessage("Enter income, expenses, and job tenure.");
      return;
    }
    state.setLoading(true);
    state.setMode("processing");
    setActiveTab("overview");
    state.setErrorMessage(null);
    state.setActiveStep(0);
    state.addFeed("Assessment initialized.");
    try {
      state.setActiveStep(1);
      state.addFeed("Running ML pipeline...");
      const response = await runAssessment(input);
      state.setAssessmentId(response.id ?? null);
      const risk = mapPredictResponse(response);
      state.setRiskResult(risk);
      state.setVerificationStatus(risk.verificationStatus);
      state.addFeed(`Score: ${risk.score} · Confidence: ${(risk.confidence * 100).toFixed(0)}%`);
      if (risk.loanEligibility) {
        state.addFeed(`Eligible: ${formatCurrency(risk.loanEligibility.eligible_loan_amount)}`);
      }
      state.setFraudResult(null);
      state.setActiveStep(4);
      state.setMode("results");
      state.refreshHistory();
    } catch (error) {
      state.setErrorMessage(error instanceof Error ? error.message : "Request failed.");
      state.setMode("input");
    } finally {
      state.setLoading(false);
    }
  };

  // ── File change ──
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>, type: "payslip" | "bank_statement") => {
    const file = event.target.files?.[0];
    if (!file) { type === "payslip" ? state.setPayslipFile(null) : state.setBankStatementFile(null); return; }
    if (!["image/png", "image/jpeg", "application/pdf"].includes(file.type)) {
      state.setErrorMessage("Unsupported file. Upload PNG, JPG, or PDF.");
      return;
    }
    state.setErrorMessage(null);
    type === "payslip" ? state.setPayslipFile(file) : state.setBankStatementFile(file);
  };

  // ── Verify ──
  const handleVerify = async () => {
    const reqs = getDocumentRequirements(state.formData.employmentType);
    if (reqs.payslip.required && !state.payslipFile && !state.payslipUploaded) {
      state.setErrorMessage("Payslip is required for this employment type.");
      return;
    }
    if (!state.payslipFile && !state.bankStatementFile) {
      state.setErrorMessage("Upload at least one document.");
      return;
    }
    const input = state.buildInput();
    state.setLoading(true);
    state.setMode("processing");
    state.setErrorMessage(null);
    state.setActiveStep(2);
    state.addFeed("Verifying documents via OCR...");
    try {
      const opts = { ...input, name: state.formData.name, employer: state.formData.employer, mobile: state.formData.mobile };
      if (state.payslipFile && !state.payslipUploaded) {
        state.addFeed("Processing payslip...");
        const ocr = await uploadDocument(state.payslipFile, "payslip", state.assessmentId ?? undefined, opts);
        state.setPayslipUploaded(true);
        if (ocr.assessment) {
          const risk = mapPredictResponse(ocr.assessment);
          state.setRiskResult(risk);
          state.setVerificationStatus(risk.verificationStatus);
        }
        if (ocr.fraud_probability !== undefined) {
          state.setFraudResult({
            probability: ocr.fraud_probability ?? 0,
            flags: ocr.fraud_flags?.length ? ocr.fraud_flags : ["No anomalies detected"],
            fields: {
              name: ocr.name ?? "N/A",
              idNumber: ocr.document_id ? `DOC-${ocr.document_id}` : "N/A",
              employer: ocr.employer ?? "N/A",
              income: ocr.income ? `₹${Math.round(ocr.income).toLocaleString()}` : "N/A",
            },
          });
        }
        state.addFeed("Payslip verified ✓");
      }
      if (state.bankStatementFile && !state.bankStatementUploaded) {
        state.addFeed("Processing bank statement...");
        const ocr = await uploadDocument(state.bankStatementFile, "bank_statement", state.assessmentId ?? undefined, opts);
        state.setBankStatementUploaded(true);
        if (ocr.assessment) {
          const risk = mapPredictResponse(ocr.assessment);
          state.setRiskResult(risk);
          state.setVerificationStatus(risk.verificationStatus);
        }
        state.addFeed("Bank statement verified ✓");
      }
      state.setActiveStep(4);
      state.addFeed("Risk re-evaluated with verified data.");
      state.setMode("results");
    } catch (error) {
      state.setErrorMessage(error instanceof Error ? error.message : "Verification failed.");
      state.setMode("results");
    } finally {
      state.setLoading(false);
    }
  };

  // ── Download report ──
  const handleDownloadReport = async () => {
    if (!state.riskResult) return;
    setDownloadingReport(true);
    try {
      const el = state.riskResult.loanEligibility;
      const body = {
        credit_score: state.riskResult.score,
        risk_band: state.riskResult.riskBand,
        decision: state.riskResult.decision ?? state.riskResult.riskBand,
        approval_probability: state.riskResult.approvalProbability,
        eligible_amount: el?.eligible_loan_amount ?? 0,
        monthly_emi: el?.monthly_emi_estimate ?? 0,
        disposable_income: el?.disposable_income ?? 0,
        savings_ratio: el?.savings_ratio ?? 0,
        employment_type: state.formData.employmentType,
        income_used: el?.income_used ?? "declared",
        expense_used: el?.expense_used ?? "declared",
        improvement_suggestions: state.riskResult.improvementSuggestions ?? [],
        assessment_id: state.assessmentId,
        timestamp: new Date().toISOString(),
      };
      const resp = await fetch("/api/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `lendnova-report-${state.assessmentId ?? Date.now()}.html`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silently fail
    } finally {
      setDownloadingReport(false);
    }
  };

  // ── Tabs ──
  const tabs = [
    { id: "overview" as const, label: "Overview" },
    { id: "eligibility" as const, label: "Eligibility" },
    { id: "coach" as const, label: "AI Coach 🤖" },
    { id: "explain" as const, label: "Why This Score" },
    ...(state.fraudResult ? [{ id: "fraud" as const, label: "Verification" }] : []),
    { id: "history" as const, label: "History" },
  ];

  return (
    <div className="relative min-h-screen bg-[#0A0F1F]">
      <div className="mesh-bg pointer-events-none absolute inset-0 opacity-60" />
      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col gap-6 px-5 py-8">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#4F7FFF] via-[#7D7BFF] to-[#9B6BFF] p-[2px]">
              <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#0A0F1F] text-sm font-semibold">LN</div>
            </div>
            <div>
              <p className="text-sm font-semibold tracking-[0.2em] text-[#9B6BFF]">LENDNOVA</p>
              <p className="text-xs text-muted">Risk Console</p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            {["Secure", "Live", "v1.0"].map((chip) => (
              <span key={chip} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted">{chip}</span>
            ))}
            <Link href="/admin" className="rounded-full border border-[#9B6BFF]/40 bg-[#9B6BFF]/10 px-3 py-1 text-xs font-semibold text-[#9B6BFF] transition hover:bg-[#9B6BFF]/20">
              Admin
            </Link>
          </div>
        </motion.div>

        {/* Modes */}
        <AnimatePresence mode="wait">
          {/* ── Input ── */}
          {state.mode === "input" && (
            <motion.div key="input" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.3 }}>
              <AssessmentForm
                formData={state.formData}
                setFormData={state.setFormData}
                payslipFile={state.payslipFile}
                bankStatementFile={state.bankStatementFile}
                onFileChange={handleFileChange}
                errorMessage={state.errorMessage}
                loading={state.loading}
                onSubmit={handleAssessment}
              />
            </motion.div>
          )}

          {/* ── Processing ── */}
          {state.mode === "processing" && (
            <motion.div key="processing" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.98 }} className="glass glow-border mx-auto w-full max-w-2xl rounded-3xl p-8">
              <p className="text-xs uppercase tracking-[0.3em] text-muted">Processing</p>
              <h2 className="mt-3 text-xl font-semibold text-white">AI Decision Pipeline</h2>
              <div className="mt-6">
                <PipelineLoader activeStep={state.activeStep} loading={state.loading} />
              </div>
              <motion.p animate={{ opacity: [0.4, 1, 0.4] }} transition={{ duration: 2.2, repeat: Infinity }} className="mt-6 text-center text-xs uppercase tracking-[0.3em] text-muted">
                OCR → VERIFY → MODEL → SCORE → ELIGIBILITY
              </motion.p>
            </motion.div>
          )}

          {/* ── Results ── */}
          {state.mode === "results" && state.riskResult && (
            <motion.div key="results" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="flex flex-col gap-5">

              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  { label: "Score", value: String(state.riskResult.score) },
                  {
                    label: "Decision",
                    value: state.riskResult.decision ?? state.riskResult.riskBand,
                    color: state.riskResult.decision === "APPROVED" ? "text-[#2EE59D]" : state.riskResult.decision === "REJECTED" ? "text-[#FF5C5C]" : "text-[#9B6BFF]",
                  },
                  { label: "Approval", value: `${(state.riskResult.approvalProbability * 100).toFixed(0)}%` },
                  {
                    label: "Eligible",
                    value: state.riskResult.loanEligibility ? formatCurrency(state.riskResult.loanEligibility.eligible_loan_amount) : "—",
                    color: "text-[#2EE59D]",
                  },
                ].map((s) => (
                  <div key={s.label} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-center">
                    <p className="text-[10px] uppercase tracking-[0.25em] text-muted">{s.label}</p>
                    <p className={`mt-1 text-lg font-semibold ${s.color ?? "text-white"}`}>{s.value}</p>
                  </div>
                ))}
              </div>

              {/* Action row */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                {/* Tab navigation */}
                <div className="flex flex-wrap gap-2">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      id={`tab-${tab.id}`}
                      onClick={() => setActiveTab(tab.id)}
                      className={`rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-wide transition ${
                        activeTab === tab.id
                          ? "border border-[#4F7FFF]/70 bg-[#4F7FFF]/15 text-white shadow-[0_0_20px_rgba(79,127,255,0.25)]"
                          : "border border-white/10 bg-white/5 text-muted hover:bg-white/10"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* Download report */}
                <button
                  id="download-report-btn"
                  onClick={handleDownloadReport}
                  disabled={downloadingReport}
                  className="ripple flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold text-white transition hover:bg-white/10 disabled:opacity-40"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  {downloadingReport ? "Generating..." : "Download Report"}
                </button>
              </div>

              {/* Tab content */}
              <AnimatePresence mode="wait">
                {/* ── Overview ── */}
                {activeTab === "overview" && (
                  <motion.div key="overview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col gap-5">
                    <RiskResultCard
                      data={state.riskResult}
                      onExplain={() => setActiveTab("explain")}
                      onCompare={() => setActiveTab("eligibility")}
                    />

                    {/* Data source banner */}
                    {state.riskResult.dataSource && (
                      <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-muted">
                        <span>Data Source:</span>
                        {(["income", "expense"] as const).map((key) => {
                          const src = state.riskResult!.dataSource?.[key];
                          return (
                            <span key={key} className={`rounded-full px-3 py-1 text-[10px] font-semibold ${src === "verified" ? "bg-[#2EE59D]/20 text-[#2EE59D]" : "bg-[#FF9F43]/20 text-[#FF9F43]"}`}>
                              {key}: {src === "verified" ? "OCR Verified" : "Declared"}
                            </span>
                          );
                        })}
                      </div>
                    )}

                    {/* Verify documents */}
                    {state.verificationStatus !== "VERIFIED" && (
                      <div className="glass rounded-3xl p-5">
                        <p className="text-xs uppercase tracking-[0.3em] text-muted">Verify Documents</p>
                        <p className="mt-1.5 text-sm text-muted">Upload documents to unlock full eligibility. Verified data overrides declared values.</p>
                        <div className="mt-4 grid gap-3 sm:grid-cols-2">
                          <DocumentUpload label="Payslip" required={getDocumentRequirements(state.formData.employmentType).payslip.required} file={state.payslipFile} uploaded={state.payslipUploaded} onChange={(e) => handleFileChange(e, "payslip")} />
                          <DocumentUpload label="Bank Statement" required={getDocumentRequirements(state.formData.employmentType).bankStatement.required} file={state.bankStatementFile} uploaded={state.bankStatementUploaded} onChange={(e) => handleFileChange(e, "bank_statement")} />
                        </div>
                        {state.errorMessage && (
                          <div className="mt-3 rounded-2xl border border-[#FF5C5C]/30 bg-[#FF5C5C]/10 px-4 py-2 text-xs text-[#FF5C5C]">{state.errorMessage}</div>
                        )}
                        <button id="verify-btn" onClick={handleVerify} disabled={state.loading || (!state.payslipFile && !state.bankStatementFile)} className="ripple mt-4 w-full rounded-2xl bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-6 py-3 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 disabled:opacity-40">
                          Verify & Recalculate
                        </button>
                      </div>
                    )}

                    {/* Activity feed */}
                    {state.feed.length > 0 && (
                      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                        <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Activity</p>
                        <div className="mt-3 space-y-1.5">
                          {state.feed.slice(0, 4).map((item) => (
                            <div key={item.id} className="flex items-start gap-2 text-xs text-muted">
                              <span className="mt-1 h-1 w-1 flex-shrink-0 rounded-full bg-[#4F7FFF]" />
                              <span className="flex-1">{item.message}</span>
                              <span className="text-white/20">{item.time}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* ── Eligibility ── */}
                {activeTab === "eligibility" && (
                  <motion.div key="eligibility" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col gap-5">
                    {state.riskResult.loanEligibility && (
                      <>
                        <LoanEligibilityCard
                          eligibility={state.riskResult.loanEligibility}
                          suggestions={state.riskResult.improvementSuggestions ?? []}
                          potentialIncrease={state.riskResult.potentialIncrease ?? {}}
                          decision={state.riskResult.decision}
                        />
                        <WhatIfSliders
                          baseIncome={state.riskResult.loanEligibility.effective_income}
                          baseExpenses={state.riskResult.loanEligibility.effective_expense}
                          baseEligibleAmount={state.riskResult.loanEligibility.eligible_loan_amount}
                          employmentType={state.formData.employmentType}
                        />
                      </>
                    )}
                    {!state.riskResult.loanEligibility && (
                      <div className="glass rounded-3xl p-8 text-center text-muted">
                        Eligibility data not available. Try running the assessment again.
                      </div>
                    )}
                  </motion.div>
                )}

                {/* ── AI Coach ── */}
                {activeTab === "coach" && (
                  <motion.div key="coach" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <CreditCoach
                      creditScore={state.riskResult.score}
                      riskBand={state.riskResult.riskBand}
                      decision={state.riskResult.decision ?? state.riskResult.riskBand}
                      eligibleAmount={state.riskResult.loanEligibility?.eligible_loan_amount ?? 0}
                      disposableIncome={state.riskResult.loanEligibility?.disposable_income ?? 0}
                      savingsRatio={state.riskResult.loanEligibility?.savings_ratio ?? 0}
                      employmentType={state.formData.employmentType}
                      improvements={state.riskResult.improvementSuggestions?.map((s) => s.category) ?? []}
                    />
                  </motion.div>
                )}

                {/* ── Explainability ── */}
                {activeTab === "explain" && (
                  <motion.div key="explain" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <ExplainabilityCard factors={state.riskResult.factors} />
                  </motion.div>
                )}

                {/* ── Fraud ── */}
                {activeTab === "fraud" && state.fraudResult && (
                  <motion.div key="fraud" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col gap-5">
                    <FraudResultCard data={state.fraudResult} />
                    {state.riskResult.trustScore !== undefined && state.riskResult.identityStatus && (
                      <IdentityVerificationCard
                        data={{
                          trustScore: state.riskResult.trustScore,
                          identityStatus: state.riskResult.identityStatus,
                          verificationReasons: state.riskResult.verificationReasons ?? [],
                        }}
                      />
                    )}
                  </motion.div>
                )}

                {/* ── History ── */}
                {activeTab === "history" && (
                  <motion.div key="history" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="glass rounded-3xl p-6">
                    <p className="text-xs uppercase tracking-[0.3em] text-muted">History</p>
                    <h3 className="mt-2 text-lg font-semibold text-white">Recent Evaluations</h3>
                    {state.history.length === 0 ? (
                      <p className="mt-4 text-sm text-muted">No previous assessments.</p>
                    ) : (
                      <div className="mt-4 space-y-2">
                        {state.history.map((item, i) => (
                          <div key={i} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm">
                            <div>
                              <p className="font-semibold text-white">Score: {item.score}</p>
                              <p className="text-xs text-muted">{item.timestamp}</p>
                            </div>
                            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.riskBand === "Low" ? "bg-[#2EE59D]/20 text-[#2EE59D]" : item.riskBand === "Medium" ? "bg-[#9B6BFF]/20 text-[#9B6BFF]" : "bg-[#FF5C5C]/20 text-[#FF5C5C]"}`}>
                              {item.riskBand}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* New assessment */}
              <div className="flex justify-center pt-1">
                <button id="new-assessment-btn" onClick={state.reset} className="rounded-full border border-white/10 bg-white/5 px-6 py-2.5 text-xs font-semibold uppercase tracking-wide text-white transition hover:bg-white/10">
                  New Assessment
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
