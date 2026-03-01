"use client";

import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";
import { AnimatePresence, animate, motion } from "framer-motion";
import Sidebar from "@/components/Sidebar";
import PipelineLoader from "@/components/PipelineLoader";
import FraudResultCard from "@/components/FraudResultCard";
import ExplainabilityCard from "@/components/ExplainabilityCard";
import IdentityVerificationCard from "@/components/IdentityVerificationCard";
import {
  fetchAssessments,
  runAssessment,
  uploadDocument,
  type AssessmentHistoryItem,
  type AssessmentInput,
  type OcrResponse,
  type PredictResponse,
} from "@/lib/api";

type RiskResult = {
  score: number;
  approvalProbability: number;
  riskBand: "Low" | "Medium" | "High";
  model: string;
  confidence: number;
  factors: { name: string; impact: number }[];
  fraudProbability: number;
  assessmentStatus: "PRELIMINARY" | "VERIFIED";
  verificationStatus: "PENDING" | "COMPLETED";
  fraudFlags: string[];
  trustScore?: number;
  identityStatus?: "VERIFIED" | "SUSPICIOUS" | "FAILED";
  verificationReasons?: string[];
};

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

type HistoryItem = {
  timestamp: string;
  score: number;
  approvalProbability: number;
  fraudProbability: number;
  riskBand: string;
};

type FeedItem = {
  id: string;
  message: string;
  time: string;
};

const employmentOptions: AssessmentInput["employment_type"][] = [
  "Full-time",
  "Part-time",
  "Self-employed",
  "Unemployed",
  "Student",
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
      duration: 1,
      ease: "easeOut",
      onUpdate(latest) {
        if (ref.current) {
          ref.current.textContent = `${latest.toFixed(decimals)}${suffix ?? ""}`;
        }
      },
    });
    return () => controls.stop();
  }, [value, suffix, decimals]);

  return <span ref={ref} className={className} />;
}

export default function AssistantPage() {
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"input" | "processing" | "results">("input");
  const [activeTab, setActiveTab] = useState<"overview" | "explainability" | "fraud" | "history">(
    "overview"
  );
  const [activeStep, setActiveStep] = useState(0);
  const [riskResult, setRiskResult] = useState<RiskResult | null>(null);
  const [fraudResult, setFraudResult] = useState<FraudResult | null>(null);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [ocrResult, setOcrResult] = useState<OcrResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [assessmentId, setAssessmentId] = useState<number | null>(null);
  const [assessmentStatus, setAssessmentStatus] = useState<"PRELIMINARY" | "VERIFIED">(
    "PRELIMINARY"
  );
  const [verificationStatus, setVerificationStatus] = useState<"PENDING" | "COMPLETED">(
    "PENDING"
  );
  const [formData, setFormData] = useState({
    income: "4200",
    expenses: "1700",
    employmentType: "Full-time" as AssessmentInput["employment_type"],
    jobTenure: "3",
    name: "",
    employer: "",
    mobile: "",
  });

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetchAssessments();
        const items = response.assessments.map((item: AssessmentHistoryItem) => ({
          timestamp: new Date(item.timestamp).toLocaleString(),
          score: item.credit_score,
          approvalProbability: item.approval_probability,
          fraudProbability: item.fraud_probability ?? 0,
          riskBand: item.risk_band,
        }));
        setHistory(items);
      } catch {
        setHistory([]);
      }
    };
    loadHistory();
  }, []);

  useEffect(() => {
    if (verificationStatus !== "COMPLETED" && activeTab === "fraud") {
      setActiveTab("overview");
    }
  }, [verificationStatus, activeTab]);

  const statusChips = useMemo(
    () => ["Secure", `Model: ${riskResult?.model ?? "Gradient Boosting"}`, "v1.0", "Live"],
    [riskResult?.model]
  );
  const [simIncome, setSimIncome] = useState(4200);
  const [simExpenses, setSimExpenses] = useState(1700);
  const [simTenure, setSimTenure] = useState(36);

  const simScore = useMemo(() => {
    const base = riskResult?.score ?? 720;
    const incomeBoost = (simIncome - 4200) / 40;
    const expenseImpact = (simExpenses - 1700) / 35;
    const tenureBoost = (simTenure - 36) / 2;
    const score = base + incomeBoost - expenseImpact + tenureBoost;
    return Math.max(580, Math.min(820, Math.round(score)));
  }, [riskResult, simIncome, simExpenses, simTenure]);

  const simApproval = useMemo(() => {
    const normalized = (simScore - 580) / 240;
    return Math.max(0.45, Math.min(0.95, 0.45 + normalized * 0.5));
  }, [simScore]);

  const parseNumber = (value: string) => {
    const cleaned = value.replace(/,/g, "");
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : null;
  };

  const buildAssessmentInput = (): AssessmentInput => ({
    income: parseNumber(formData.income) ?? 0,
    expenses: parseNumber(formData.expenses) ?? 0,
    employment_type: formData.employmentType,
    job_tenure: parseNumber(formData.jobTenure) ?? 0,
  });

  const mapPredictResponse = (response: PredictResponse): RiskResult => ({
    score: response.credit_score,
    approvalProbability: response.approval_probability,
    riskBand: response.risk_band,
    model: response.model_used,
    confidence: response.confidence_score,
    factors: (response.top_factors ?? []).map((factor) => ({
      name: formatFactorName(factor.factor),
      impact: factor.impact,
    })),
    fraudProbability: response.fraud_probability ?? 0,
    assessmentStatus: response.assessment_status,
    verificationStatus: response.verification_status,
    fraudFlags: response.fraud_flags ?? [],
    trustScore: response.trust_score ?? undefined,
    identityStatus: response.identity_status ?? undefined,
    verificationReasons: response.verification_reasons ?? [],
  });

  const formatFactorName = (name: string) => {
    const cleaned = name.replace(/^(num__|cat__)/, "").replace(/_/g, " ");
    return cleaned.replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const addFeed = (message: string) => {
    setFeed((prev) => [
      {
        id: `${Date.now()}-${prev.length}`,
        message,
        time: new Date().toLocaleTimeString(),
      },
      ...prev.slice(0, 7),
    ]);
  };

  const runOcrVerification = async (assessmentInput: AssessmentInput) => {
    if (!selectedFile) {
      throw new Error("Upload a document before running OCR.");
    }
    setActiveStep(2);
    addFeed("OCR extraction running on uploaded documents.");
    const ocr = await uploadDocument(
      selectedFile,
      "payslip",
      assessmentId ?? undefined,
      {
        ...assessmentInput,
        name: formData.name,
        employer: formData.employer,
        mobile: formData.mobile,
      }
    );
    setOcrResult(ocr);
    addFeed("OCR extraction completed.");
    if (ocr.assessment) {
      const verifiedRisk = mapPredictResponse(ocr.assessment);
      setRiskResult(verifiedRisk);
      setAssessmentStatus(verifiedRisk.assessmentStatus);
      setVerificationStatus(verifiedRisk.verificationStatus);
    }
    if (ocr.fraud_probability !== undefined) {
      setFraudResult({
        probability: ocr.fraud_probability ?? 0,
        flags: ocr.fraud_flags?.length ? ocr.fraud_flags : ["No anomalies detected"],
        fields: {
          name: ocr.name ?? "Unavailable",
          idNumber: ocr.document_id ? `DOC-${ocr.document_id}` : "N/A",
          employer: ocr.employer ?? "Unavailable",
          income: ocr.income ? `$${Math.round(ocr.income).toLocaleString()}` : "Unavailable",
        },
      });
    }
    return ocr;
  };

  const handleAssessment = async () => {
    const assessmentInput = buildAssessmentInput();
    if (!assessmentInput.income || !assessmentInput.expenses || !assessmentInput.job_tenure) {
      setErrorMessage("Enter income, expenses, and job tenure to continue.");
      return;
    }
    setLoading(true);
    setMode("processing");
    setActiveTab("overview");
    setErrorMessage(null);
    setActiveStep(0);
    addFeed("Assessment workflow initialized with secure session token.");
    const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

    const runPredict = async () => {
      setActiveStep(1);
      await wait(120);
      addFeed("Risk model inference started using production ML pipeline.");
      const response = await runAssessment(assessmentInput);
      setAssessmentId(response.id ?? null);
      const risk = mapPredictResponse(response);
      setRiskResult(risk);
      setAssessmentStatus(risk.assessmentStatus);
      setVerificationStatus(risk.verificationStatus);
      addFeed(
        `Risk score generated at ${risk.score} with ${(risk.confidence * 100).toFixed(1)}% confidence.`
      );
      return risk;
    };


    try {
      const risk = await runPredict();
      setFraudResult(null);
      setHistory((prev) => [
        {
          timestamp: new Date().toLocaleString(),
          score: risk.score,
          approvalProbability: risk.approvalProbability,
          fraudProbability: fraudResult?.probability ?? 0,
          riskBand: risk.riskBand,
        },
        ...prev.slice(0, 4),
      ]);

      setActiveStep(4);
      addFeed("Decision package sealed with audit hash and policy rationale.");
      setMode("results");
      await wait(180);
      try {
        const refreshed = await fetchAssessments();
        const items = refreshed.assessments.map((item) => ({
          timestamp: new Date(item.timestamp).toLocaleString(),
          score: item.credit_score,
          approvalProbability: item.approval_probability,
          fraudProbability: item.fraud_probability ?? 0,
          riskBand: item.risk_band,
        }));
        setHistory(items);
      } catch {
        setHistory((prev) => prev);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Request failed.");
      setMode("input");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setSelectedFile(null);
      setOcrResult(null);
      setFraudResult(null);
      setAssessmentStatus("PRELIMINARY");
      setVerificationStatus("PENDING");
      return;
    }
    const allowed = ["image/png", "image/jpeg", "application/pdf"];
    if (!allowed.includes(file.type)) {
      setErrorMessage("Unsupported file type. Upload PNG, JPG, or PDF.");
      setSelectedFile(null);
      return;
    }
    setErrorMessage(null);
    setSelectedFile(file);
    setOcrResult(null);
    setFraudResult(null);
  };

  const handleVerify = async () => {
    if (!selectedFile) {
      setErrorMessage("Upload a document to verify.");
      return;
    }
    const assessmentInput = buildAssessmentInput();
    setLoading(true);
    setMode("processing");
    setErrorMessage(null);
    setActiveStep(2);
    addFeed("Verification workflow started with uploaded documents.");
    try {
      await runOcrVerification(assessmentInput);
      setActiveStep(4);
      addFeed("Verification completed and assessment updated.");
      setMode("results");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Verification failed.");
      setMode("results");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#0A0F1F]">
      <div className="mesh-bg pointer-events-none absolute inset-0 opacity-60" />
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 flex min-h-screen flex-col gap-6 px-6 py-8 lg:flex-row"
      >
        <div className="w-full lg:w-[280px]">
          <Sidebar />
        </div>
        <main className="flex-1 space-y-6">
          <motion.div
            whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
            transition={{ type: "spring", stiffness: 120, damping: 16 }}
            className="glass glow-border rounded-3xl p-6"
          >
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-muted">
                  LendNova Risk Assistant
                </p>
                <h1 className="mt-3 text-2xl font-semibold text-white">
                  Execute credit scoring, fraud verification, and explainable AI decisions.
                </h1>
              </div>
              <div className="flex flex-wrap gap-2">
                {statusChips.map((chip, index) => (
                  <motion.span
                    key={chip}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted"
                  >
                    {chip}
                  </motion.span>
                ))}
              </div>
            </div>
          </motion.div>

          {mode === "input" && (
            <motion.div
              whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
              transition={{ type: "spring", stiffness: 120, damping: 16 }}
              className="glass glow-border mx-auto w-full max-w-2xl rounded-3xl p-8"
            >
              <p className="text-xs uppercase tracking-[0.3em] text-muted">New Assessment</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">Run Credit Evaluation</h2>
              <div className="mt-6 grid gap-5">
                <div>
                  <label className="text-xs uppercase tracking-[0.25em] text-muted">
                    Monthly Income
                  </label>
                  <input
                    type="number"
                    min={0}
                    value={formData.income}
                    onChange={(event) =>
                      setFormData((prev) => ({ ...prev, income: event.target.value }))
                    }
                    className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                  />
                </div>
                <div>
                  <label className="text-xs uppercase tracking-[0.25em] text-muted">
                    Monthly Expenses
                  </label>
                  <input
                    type="number"
                    min={0}
                    value={formData.expenses}
                    onChange={(event) =>
                      setFormData((prev) => ({ ...prev, expenses: event.target.value }))
                    }
                    className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-muted">
                      Employment Type
                    </label>
                    <select
                      value={formData.employmentType}
                      onChange={(event) =>
                        setFormData((prev) => ({
                          ...prev,
                          employmentType: event.target.value as AssessmentInput["employment_type"],
                        }))
                      }
                      className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                    >
                      {employmentOptions.map((option) => (
                        <option key={option} value={option} className="bg-[#0A0F1F]">
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-muted">
                      Job Tenure (Years)
                    </label>
                    <input
                      type="number"
                      min={0}
                      step={0.5}
                      value={formData.jobTenure}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, jobTenure: event.target.value }))
                      }
                      className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                    />
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-muted">
                      Full Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, name: event.target.value }))
                      }
                      placeholder="John Doe"
                      className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-muted">
                      Employer (Optional)
                    </label>
                    <input
                      type="text"
                      value={formData.employer}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, employer: event.target.value }))
                      }
                      placeholder="Company Name"
                      className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-muted">
                      Mobile (Optional)
                    </label>
                    <input
                      type="tel"
                      value={formData.mobile}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, mobile: event.target.value }))
                      }
                      placeholder="+1234567890"
                      className="mt-3 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-[#4F7FFF]/70 focus:ring-2 focus:ring-[#4F7FFF]/30"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase tracking-[0.25em] text-muted">
                    Optional Document Upload
                  </label>
                  <label className="mt-3 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-muted">
                    <input
                      type="file"
                      accept="image/png,image/jpeg,application/pdf"
                      onChange={handleFileChange}
                      className="text-xs text-white file:mr-3 file:rounded-full file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-xs file:text-white"
                    />
                    {selectedFile ? selectedFile.name : "Attach payslip or ID"}
                  </label>
                </div>
              </div>
              {errorMessage && (
                <div className="mt-5 rounded-2xl border border-[#FF5C5C]/30 bg-[#FF5C5C]/10 px-4 py-3 text-xs text-[#FF5C5C]">
                  {errorMessage}
                </div>
              )}
              <button
                onClick={handleAssessment}
                disabled={loading}
                className="ripple mt-8 w-full rounded-2xl bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-6 py-4 text-sm font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
              >
                Run Assessment
              </button>
            </motion.div>
          )}

          {mode === "processing" && (
            <motion.div
              whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
              transition={{ type: "spring", stiffness: 120, damping: 16 }}
              className="glass glow-border mx-auto w-full max-w-3xl rounded-3xl p-8"
            >
              <p className="text-xs uppercase tracking-[0.3em] text-muted">Processing</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">AI Decision Pipeline</h2>
              <div className="mt-6">
                <PipelineLoader activeStep={activeStep} loading={loading} />
              </div>
              <motion.div
                initial={{ opacity: 0.4 }}
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 2.2, repeat: Infinity }}
                className="mt-6 text-center text-xs uppercase tracking-[0.4em] text-muted"
              >
                USER DATA → FEATURES → MODEL → FRAUD → DECISION
              </motion.div>
            </motion.div>
          )}

          {mode === "results" && riskResult && (
            <div className="space-y-6">
              <motion.div
                whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
                transition={{ type: "spring", stiffness: 120, damping: 16 }}
                className="glass glow-border rounded-3xl p-8"
              >
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <p className="text-xs uppercase tracking-[0.3em] text-muted">Assessment Summary</p>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-white">
                      {verificationStatus === "COMPLETED"
                        ? "🟢 Verified Assessment"
                        : "🟡 Preliminary Assessment"}
                    </span>
                  </div>
                  <button
                    onClick={() => setMode("input")}
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10"
                  >
                    New Assessment
                  </button>
                </div>
                <p className="mt-3 text-sm text-muted">
                  {verificationStatus === "COMPLETED"
                    ? "Document verification completed."
                    : "Upload documents to complete verification."}
                </p>
                <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Credit Score</p>
                    <p className="mt-2 text-3xl font-semibold text-white">
                      <AnimatedValue value={riskResult.score} className="text-3xl font-semibold text-white" />
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                      Approval Probability
                    </p>
                    <p className="mt-2 text-3xl font-semibold text-white">
                      <AnimatedValue
                        value={riskResult.approvalProbability * 100}
                        suffix="%"
                        decimals={1}
                        className="text-3xl font-semibold text-white"
                      />
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Risk Band</p>
                    <p className="mt-2 text-2xl font-semibold text-white">{riskResult.riskBand}</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                      Trust Score
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-white">
                      {verificationStatus === "COMPLETED" && riskResult.trustScore !== undefined
                        ? `${(riskResult.trustScore * 100).toFixed(1)}%`
                        : "N/A"}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                      Fraud Probability
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-white">
                      {verificationStatus === "COMPLETED" && fraudResult
                        ? `${(fraudResult.probability * 100).toFixed(2)}%`
                        : "N/A"}
                    </p>
                  </div>
                </div>
                {verificationStatus !== "COMPLETED" && (
                  <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_200px]">
                    <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-muted">
                      <input
                        type="file"
                        accept="image/png,image/jpeg,application/pdf"
                        onChange={handleFileChange}
                        className="text-xs text-white file:mr-3 file:rounded-full file:border-0 file:bg-white/10 file:px-3 file:py-1 file:text-xs file:text-white"
                      />
                      {selectedFile ? selectedFile.name : "Upload documents to verify"}
                    </label>
                    <button
                      onClick={handleVerify}
                      disabled={loading || !selectedFile}
                      className="ripple rounded-2xl bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-4 py-3 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
                    >
                      Upload Documents to Verify
                    </button>
                  </div>
                )}
              </motion.div>

              <div className="glass glow-border rounded-3xl p-6">
                <div className="flex flex-wrap gap-3">
                  {[
                    { key: "overview", label: "Overview" },
                    { key: "explainability", label: "Explainability" },
                    ...(verificationStatus === "COMPLETED"
                      ? [{ key: "fraud", label: "Fraud Analysis" }]
                      : []),
                    { key: "history", label: "History" },
                  ].map((tab) => (
                    <button
                      key={tab.key}
                      onClick={() =>
                        setActiveTab(tab.key as "overview" | "explainability" | "fraud" | "history")
                      }
                      className={`rounded-full px-4 py-2 text-xs font-semibold uppercase tracking-wide transition ${
                        activeTab === tab.key
                          ? "bg-white/15 text-white"
                          : "border border-white/10 bg-white/5 text-muted hover:border-white/30 hover:bg-white/10"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {activeTab === "overview" && (
                <motion.div
                  whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
                  transition={{ type: "spring", stiffness: 120, damping: 16 }}
                  className="glass glow-border rounded-3xl p-6"
                >
                  <p className="text-xs uppercase tracking-[0.3em] text-muted">Decision Overview</p>
                  <p className="mt-3 text-lg font-semibold text-white">
                    Model: {riskResult.model} • Confidence {(riskResult.confidence * 100).toFixed(1)}%
                  </p>
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
                      Latest assessment stored and audit-ready.
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
                      {assessmentStatus === "VERIFIED"
                        ? "Fraud checks completed with document verification."
                        : "Document verification pending for fraud checks."}
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
                      Explainability available for compliance review.
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === "explainability" && (
                <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
                  <ExplainabilityCard factors={riskResult.factors} />
                  <motion.div
                    whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
                    transition={{ type: "spring", stiffness: 120, damping: 16 }}
                    className="glass glow-border rounded-3xl p-6"
                  >
                    <p className="text-xs uppercase tracking-[0.3em] text-muted">
                      What-If Simulator
                    </p>
                    <h2 className="mt-3 text-lg font-semibold text-white">
                      Adjust borrower signals to preview underwriting impact.
                    </h2>
                    <div className="mt-6 grid gap-4">
                      <div>
                        <div className="flex items-center justify-between text-xs text-muted">
                          <span>Monthly Income</span>
                          <span className="text-white">${simIncome}</span>
                        </div>
                        <input
                          type="range"
                          min={2800}
                          max={8500}
                          step={100}
                          value={simIncome}
                          onChange={(event) => setSimIncome(Number(event.target.value))}
                          className="mt-3 w-full accent-[#4F7FFF]"
                        />
                      </div>
                      <div>
                        <div className="flex items-center justify-between text-xs text-muted">
                          <span>Monthly Expenses</span>
                          <span className="text-white">${simExpenses}</span>
                        </div>
                        <input
                          type="range"
                          min={800}
                          max={4200}
                          step={100}
                          value={simExpenses}
                          onChange={(event) => setSimExpenses(Number(event.target.value))}
                          className="mt-3 w-full accent-[#9B6BFF]"
                        />
                      </div>
                      <div>
                        <div className="flex items-center justify-between text-xs text-muted">
                          <span>Employment Tenure</span>
                          <span className="text-white">{simTenure} months</span>
                        </div>
                        <input
                          type="range"
                          min={6}
                          max={96}
                          step={3}
                          value={simTenure}
                          onChange={(event) => setSimTenure(Number(event.target.value))}
                          className="mt-3 w-full accent-[#2EE59D]"
                        />
                      </div>
                    </div>
                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                        <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                          Simulated Score
                        </p>
                        <p className="mt-2 text-3xl font-semibold text-white">
                          <AnimatedValue value={simScore} className="text-3xl font-semibold text-white" />
                        </p>
                      </div>
                      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                        <p className="text-[10px] uppercase tracking-[0.25em] text-muted">
                          Approval Probability
                        </p>
                        <p className="mt-2 text-3xl font-semibold text-white">
                          <AnimatedValue
                            value={simApproval * 100}
                            suffix="%"
                            decimals={1}
                            className="text-3xl font-semibold text-white"
                          />
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-white/10">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${simApproval * 100}%` }}
                        transition={{ duration: 0.8 }}
                        className="h-full rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF]"
                      />
                    </div>
                  </motion.div>
                </div>
              )}

              {activeTab === "fraud" && (
                <div className="space-y-6">
                  {riskResult.trustScore !== undefined &&
                    riskResult.identityStatus &&
                    riskResult.verificationReasons && (
                      <IdentityVerificationCard
                        data={{
                          trustScore: riskResult.trustScore,
                          identityStatus: riskResult.identityStatus,
                          verificationReasons: riskResult.verificationReasons,
                        }}
                      />
                    )}
                  <div className="grid gap-6 lg:grid-cols-2">
                    {fraudResult ? (
                      <FraudResultCard data={fraudResult} />
                    ) : (
                      <div className="glass glow-border rounded-3xl p-6 text-sm text-muted">
                        Upload a document to run OCR-driven fraud analysis.
                      </div>
                    )}
                    {ocrResult && (
                      <motion.div
                        whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
                        transition={{ type: "spring", stiffness: 120, damping: 16 }}
                        className="glass glow-border rounded-3xl p-6"
                      >
                        <p className="text-xs uppercase tracking-[0.3em] text-muted">OCR Preview</p>
                        <div className="mt-5 grid gap-3 text-xs text-muted">
                          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                            <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Name</p>
                            <p className="mt-2 text-sm text-white">{ocrResult.name ?? "Unavailable"}</p>
                          </div>
                          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                            <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Employer</p>
                            <p className="mt-2 text-sm text-white">{ocrResult.employer ?? "Unavailable"}</p>
                          </div>
                          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                            <p className="text-[10px] uppercase tracking-[0.25em] text-muted">Income</p>
                            <p className="mt-2 text-sm text-white">
                              {ocrResult.income ? `${Math.round(ocrResult.income).toLocaleString()}` : "Unavailable"}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                  {riskResult.verificationReasons && riskResult.verificationReasons.length > 0 && (
                    <motion.div
                      whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
                      transition={{ type: "spring", stiffness: 120, damping: 16 }}
                      className="glass glow-border rounded-3xl p-6"
                    >
                      <p className="text-xs uppercase tracking-[0.3em] text-muted">
                        Why Risk Increased
                      </p>
                      <p className="mt-3 text-lg font-semibold text-white">
                        Fraud Analysis Explanation
                      </p>
                      <div className="mt-5 space-y-3">
                        {riskResult.verificationReasons.map((reason, index) => (
                          <div
                            key={index}
                            className="rounded-2xl border border-white/10 bg-white/5 p-4"
                          >
                            <div className="flex items-start gap-3">
                              <span className="text-[#FF5C5C]">?</span>
                              <div>
                                <p className="text-sm font-semibold text-white">{reason}</p>
                                <p className="mt-2 text-xs text-muted">
                                  {reason.includes("mismatch")
                                    ? "Data inconsistency detected between user input and document verification."
                                    : reason.includes("confidence")
                                    ? "OCR extraction quality below acceptable threshold for reliable verification."
                                    : reason.includes("metadata")
                                    ? "Document metadata indicates potential tampering or non-authentic source."
                                    : reason.includes("income")
                                    ? "Income pattern analysis suggests potential data manipulation."
                                    : reason.includes("tenure")
                                    ? "Employment tenure inconsistent with reported income level."
                                    : reason.includes("submissions")
                                    ? "Behavioral pattern indicates potential fraudulent activity."
                                    : "Verification check flagged this item for manual review."}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>
              )}

              {activeTab === "history" && (
                <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
                  <motion.div
                    whileHover={{ y: -4, rotateX: 2, rotateY: -2 }}
                    transition={{ type: "spring", stiffness: 120, damping: 16 }}
                    className="glass glow-border rounded-3xl p-6"
                  >
                    <p className="text-xs uppercase tracking-[0.3em] text-muted">
                      Recent Assessments
                    </p>
                    <div className="mt-4 grid gap-3">
                      {history.length === 0 && (
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
                          No assessment history loaded yet.
                        </div>
                      )}
                      {history.map((item) => (
                        <div
                          key={item.timestamp}
                          className="rounded-2xl border border-white/10 bg-white/5 p-4"
                        >
                          <p className="text-sm font-semibold text-white">
                            Score {item.score} • {item.riskBand} Risk
                          </p>
                          <p className="mt-2 text-xs text-muted">
                            Approval {(item.approvalProbability * 100).toFixed(1)}% • Fraud{" "}
                            {(item.fraudProbability * 100).toFixed(2)}% • Policy ready
                          </p>
                          <p className="mt-2 text-xs text-muted">{item.timestamp}</p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                  <motion.div
                    whileHover={{ y: -4, rotateX: 2, rotateY: 2 }}
                    transition={{ type: "spring", stiffness: 120, damping: 16 }}
                    className="glass glow-border rounded-3xl p-6"
                  >
                    <p className="text-xs uppercase tracking-[0.3em] text-muted">Audit Feed</p>
                    <p className="mt-3 text-sm text-muted">
                      Live underwriting telemetry captured for audit readiness.
                    </p>
                    <div className="mt-5 space-y-3">
                      <AnimatePresence initial={false}>
                        {feed.map((item) => (
                          <motion.div
                            key={item.id}
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            className="rounded-2xl border border-white/10 bg-white/5 p-4"
                          >
                            <p className="text-sm text-white">{item.message}</p>
                            <p className="mt-2 text-[11px] text-muted">{item.time}</p>
                          </motion.div>
                        ))}
                      </AnimatePresence>
                      {feed.length === 0 && (
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
                          No audit events yet. Run an assessment to capture activity logs.
                        </div>
                      )}
                    </div>
                  </motion.div>
                </div>
              )}
            </div>
          )}
        </main>
      </motion.div>
    </div>
  );
}
