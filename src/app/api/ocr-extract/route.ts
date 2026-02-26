import { NextResponse } from "next/server";
import { generateOcrResult } from "@/lib/mockEngine";

export async function POST() {
  const ocr = generateOcrResult();
  return NextResponse.json({ ocr });
}
