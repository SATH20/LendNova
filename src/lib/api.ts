export type AssessmentInput = {
  income: number;
  expenses: number;
  employment_type: "Full-time" | "Part-time" | "Self-employed" | "Unemployed" | "Student";
  job_tenure: number;
};

export type PredictResponse = {
  id?: number;
  credit_score: number;
  approval_probability: number;
  risk_band: "Low" | "Medium" | "High";
  model_used: string;
  confidence_score: number;
  assessment_status: "PRELIMINARY" | "VERIFIED" | "PARTIAL";
  assessment_stage: "PRELIMINARY" | "VERIFIED" | "PARTIAL";
  verification_status: "PENDING" | "COMPLETED" | "INCOMPLETE" | "VERIFIED" | "PARTIAL" | "FAILED";
  fraud_probability?: number | null;
  fraud_flags?: string[];
  verification_flags?: string[];
  trust_score?: number | null;
  identity_status?: "VERIFIED" | "SUSPICIOUS" | "FAILED" | null;
  verification_reasons?: string[];
  declared_income?: number | null;
  verified_income?: number | null;
  declared_expense?: number | null;
  verified_expense?: number | null;
  verification_method?: string | null;
  income_stability_score?: number | null;
  expense_pattern_score?: number | null;
  top_factors: { factor: string; impact: number }[];
};

export type OcrResponse = {
  name: string | null;
  income: number | null;
  employer: string | null;
  extracted_text: string;
  document_id: number;
  assessment?: PredictResponse;
  fraud_probability?: number;
  fraud_flags?: string[];
  verification_flags?: string[];
  trust_score?: number | null;
  identity_status?: "VERIFIED" | "SUSPICIOUS" | "FAILED" | null;
  verification_reasons?: string[];
  verified_income?: number | null;
  verified_expense?: number | null;
  verification_method?: string | null;
  verification_status?: string | null;
  assessment_stage?: string | null;
  income_stability_score?: number | null;
  expense_pattern_score?: number | null;
};

export type FraudResponse = {
  fraud_probability: number;
  flags: string[];
};

export type AssessmentHistoryItem = {
  id: number;
  timestamp: string;
  credit_score: number;
  approval_probability: number;
  risk_band: string;
  model_used: string;
  confidence_score: number;
  fraud_probability?: number;
};

export type AssessmentHistoryResponse = {
  assessments: AssessmentHistoryItem[];
  total: number;
  pages: number;
  current_page: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";

async function fetchWithTimeout(input: RequestInfo | URL, init: RequestInit = {}, timeoutMs = 12000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(input, { ...init, signal: controller.signal });
    return response;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    throw error;
  } finally {
    clearTimeout(id);
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();
  if (!response.ok) {
    const message =
      typeof payload === "string"
        ? payload
        : payload?.error || payload?.message || "Request failed";
    throw new Error(message);
  }
  return payload as T;
}

export async function runAssessment(data: AssessmentInput): Promise<PredictResponse> {
  const response = await fetchWithTimeout(`${API_URL}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return parseResponse<PredictResponse>(response);
}

export async function uploadDocument(
  file: File,
  documentType?: string,
  assessmentId?: number,
  formValues?: AssessmentInput & { name?: string; employer?: string; mobile?: string }
): Promise<OcrResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (documentType) {
    formData.append("document_type", documentType);
  }
  if (assessmentId) {
    formData.append("assessment_id", String(assessmentId));
  }
  if (formValues) {
    formData.append("income", String(formValues.income));
    formData.append("expenses", String(formValues.expenses));
    formData.append("employment_type", formValues.employment_type);
    formData.append("job_tenure", String(formValues.job_tenure));
    if (formValues.name) {
      formData.append("name", formValues.name);
    }
    if (formValues.employer) {
      formData.append("employer", formValues.employer);
    }
    if (formValues.mobile) {
      formData.append("mobile", formValues.mobile);
    }
  }
  const response = await fetchWithTimeout(`${API_URL}/api/ocr-extract`, {
    method: "POST",
    body: formData,
  });
  return parseResponse<OcrResponse>(response);
}

export async function runFraudCheck(params: {
  form_data: AssessmentInput;
  ocr_data: {
    name: string | null;
    income: number | null;
    employer: string | null;
    extracted_text: string;
  };
  assessment_id?: number;
}): Promise<FraudResponse> {
  const response = await fetchWithTimeout(`${API_URL}/api/fraud-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return parseResponse<FraudResponse>(response);
}

export async function fetchAssessments(page = 1, perPage = 6): Promise<AssessmentHistoryResponse> {
  const response = await fetchWithTimeout(
    `${API_URL}/api/assessments?page=${page}&per_page=${perPage}`,
    { method: "GET" }
  );
  return parseResponse<AssessmentHistoryResponse>(response);
}
