import type { AssessmentInput, PredictResponse } from "./api";

export type RiskResult = {
  score: number;
  approvalProbability: number;
  riskBand: "Low" | "Medium" | "High";
  model: string;
  confidence: number;
  factors: { name: string; impact: number }[];
  fraudProbability: number;
  assessmentStatus: "PRELIMINARY" | "VERIFIED" | "PARTIAL";
  assessmentStage: "PRELIMINARY" | "VERIFIED" | "PARTIAL";
  verificationStatus: "PENDING" | "COMPLETED" | "INCOMPLETE" | "VERIFIED" | "PARTIAL" | "FAILED";
  fraudFlags: string[];
  verificationFlags: string[];
  trustScore?: number;
  identityStatus?: "VERIFIED" | "SUSPICIOUS" | "FAILED";
  verificationReasons?: string[];
  declaredIncome?: number;
  verifiedIncome?: number;
  declaredExpense?: number;
  verifiedExpense?: number;
  verificationMethod?: string;
  incomeStabilityScore?: number;
  expensePatternScore?: number;
};

export type FraudResult = {
  probability: number;
  flags: string[];
  fields: { name: string; idNumber: string; employer: string; income: string };
};

export type HistoryItem = {
  timestamp: string;
  score: number;
  approvalProbability: number;
  fraudProbability: number;
  riskBand: string;
};

export type FeedItem = {
  id: string;
  message: string;
  time: string;
};

export const employmentOptions: AssessmentInput["employment_type"][] = [
  "Full-time",
  "Part-time",
  "Self-employed",
  "Unemployed",
  "Student",
];

export const formatFactorName = (name: string) => {
  const cleaned = name.replace(/^(num__|cat__)/, "").replace(/_/g, " ");
  return cleaned.replace(/\b\w/g, (char) => char.toUpperCase());
};

export const mapPredictResponse = (response: PredictResponse): RiskResult => ({
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
  assessmentStage: response.assessment_stage ?? response.assessment_status,
  verificationStatus: response.verification_status,
  fraudFlags: response.fraud_flags ?? [],
  verificationFlags: response.verification_flags ?? [],
  trustScore: response.trust_score ?? undefined,
  identityStatus: response.identity_status ?? undefined,
  verificationReasons: response.verification_reasons ?? [],
  declaredIncome: response.declared_income ?? undefined,
  verifiedIncome: response.verified_income ?? undefined,
  declaredExpense: response.declared_expense ?? undefined,
  verifiedExpense: response.verified_expense ?? undefined,
  verificationMethod: response.verification_method ?? undefined,
  incomeStabilityScore: response.income_stability_score ?? undefined,
  expensePatternScore: response.expense_pattern_score ?? undefined,
});

export const getDocumentRequirements = (employmentType: string) => {
  const empType = employmentType.toLowerCase();
  const fullTimeTypes = ["full-time", "fulltime"];
  const selfEmployedTypes = ["self-employed", "selfemployed"];
  const partTimeTypes = ["part-time", "parttime"];
  
  if (fullTimeTypes.includes(empType)) {
    return {
      payslip: { required: true, label: "Payslip" },
      bankStatement: { required: true, label: "Bank Statement" },
    };
  } else if (selfEmployedTypes.includes(empType) || partTimeTypes.includes(empType)) {
    return {
      payslip: { required: false, label: "Payslip" },
      bankStatement: { required: true, label: "Bank Statement" },
    };
  }
  return {
    payslip: { required: false, label: "Payslip" },
    bankStatement: { required: false, label: "Bank Statement" },
  };
};

export const parseNumber = (value: string) => {
  const cleaned = value.replace(/,/g, "");
  const parsed = Number(cleaned);
  return Number.isFinite(parsed) ? parsed : null;
};
