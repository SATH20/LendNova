export type Factor = {
  name: string;
  impact: number;
};

export type RiskResult = {
  score: number;
  approvalProbability: number;
  riskBand: "Low" | "Medium" | "High";
  model: string;
  confidence: number;
  factors: Factor[];
};

export type FraudResult = {
  probability: number;
  flags: string[];
  fields: {
    name: string;
    idNumber: string;
    employer: string;
    income: string;
  };
};

export type OcrResult = {
  name: string;
  idNumber: string;
  employer: string;
  income: string;
  docId: string;
};

export type ModelMetric = {
  model: string;
  accuracy: number;
  explainability: number;
};

const factorPool = [
  "Cash Flow Stability",
  "Employment Tenure",
  "Rent Payment History",
  "Utility Bill Regularity",
  "Merchant Diversity",
  "Savings Momentum",
  "Gig Income Consistency",
  "Device Trust Score",
  "Location Consistency",
  "Account Age",
];

const fraudFlags = [
  "Document Edge Mismatch",
  "Image Compression Artifact",
  "Metadata Timestamp Drift",
  "Name Spacing Anomaly",
  "Signature Variance",
  "ID Font Irregularity",
];

const models: ModelMetric[] = [
  { model: "Logistic Regression", accuracy: 0.78, explainability: 0.86 },
  { model: "Random Forest", accuracy: 0.84, explainability: 0.62 },
  { model: "Gradient Boosting", accuracy: 0.89, explainability: 0.74 },
];

const names = ["Ava Patel", "Leo Martin", "Mia Santos", "Noah Ali", "Iris Chen"];
const employers = ["Vertex Microfinance", "Beacon Logistics", "Nova Health", "DeltaWorks"];

const randomBetween = (min: number, max: number) =>
  Math.random() * (max - min) + min;

const randomPick = <T,>(arr: T[]) => arr[Math.floor(Math.random() * arr.length)];

export function generateRiskResult(): RiskResult {
  const score = Math.round(randomBetween(580, 820));
  const approvalProbability = Number(randomBetween(0.45, 0.92).toFixed(2));
  const riskBand = score > 740 ? "Low" : score > 660 ? "Medium" : "High";
  const confidence = Number(randomBetween(0.72, 0.94).toFixed(2));
  const factors = Array.from({ length: 5 }).map(() => ({
    name: randomPick(factorPool),
    impact: Number(randomBetween(-0.45, 0.6).toFixed(2)),
  }));

  return {
    score,
    approvalProbability,
    riskBand,
    model: "Gradient Boosting",
    confidence,
    factors,
  };
}

export function generateFraudResult(): FraudResult {
  return {
    probability: Number(randomBetween(0.01, 0.35).toFixed(2)),
    flags: Array.from({ length: 3 }).map(() => randomPick(fraudFlags)),
    fields: {
      name: `${randomPick(names).split(" ")[0]} ${randomPick(["K.", "R.", "M."])}`,
      idNumber: `****-${Math.floor(randomBetween(1200, 9900))}`,
      employer: randomPick(employers),
      income: `$${Math.floor(randomBetween(3200, 7200)).toLocaleString()}/mo`,
    },
  };
}

export function generateOcrResult(): OcrResult {
  return {
    name: randomPick(names),
    idNumber: `ID-${Math.floor(randomBetween(100000, 999999))}`,
    employer: randomPick(employers),
    income: `$${Math.floor(randomBetween(3200, 7200)).toLocaleString()}/mo`,
    docId: `DOC-${Math.floor(randomBetween(10000, 99999))}`,
  };
}

export function getModelMetrics(): ModelMetric[] {
  return models.map((item) => ({
    ...item,
    accuracy: Number((item.accuracy + randomBetween(-0.02, 0.02)).toFixed(2)),
    explainability: Number(
      (item.explainability + randomBetween(-0.02, 0.02)).toFixed(2)
    ),
  }));
}
