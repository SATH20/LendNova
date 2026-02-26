import { NextResponse } from "next/server";
import { generateRiskResult, getModelMetrics } from "@/lib/mockEngine";

export async function POST() {
  const risk = generateRiskResult();
  const modelMetrics = getModelMetrics();

  return NextResponse.json({
    risk,
    modelMetrics,
  });
}
