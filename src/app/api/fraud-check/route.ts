import { NextResponse } from "next/server";
import { generateFraudResult } from "@/lib/mockEngine";

export async function POST() {
  const fraud = generateFraudResult();
  return NextResponse.json({ fraud });
}
