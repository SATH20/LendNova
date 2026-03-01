import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";

export async function POST(request: Request) {
  const formData = await request.formData();
  const response = await fetch(`${API_URL}/api/ocr-extract`, {
    method: "POST",
    body: formData,
  });
  const payload = await response.json();
  return NextResponse.json(payload, { status: response.status });
}
