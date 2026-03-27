import { NextResponse } from "next/server";

const GEMINI_API_KEY = process.env.GEMINI_API_KEY ?? "";
const GEMINI_URL =
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

export async function POST(request: Request) {
  try {
    const { message, context } = await request.json();

    const systemPrompt = `You are an expert AI Credit Coach embedded in LendNova, an AI-powered credit underwriting platform for first-time borrowers in India.

The user's current financial profile:
- Credit Score: ${context.credit_score} (${context.risk_band} risk)
- Decision: ${context.decision}
- Eligible Loan Amount: ₹${context.eligible_amount?.toLocaleString("en-IN")}
- Disposable Income: ₹${context.disposable_income?.toLocaleString("en-IN")}/month
- Savings Ratio: ${context.savings_ratio}
- Employment Type: ${context.employment_type}
- Key Improvement Areas: ${context.improvement_areas?.join(", ") || "None"}

Your role:
- Answer questions about credit scores, loan eligibility, and the LendNova assessment in plain, friendly language
- Give specific, actionable advice tailored to their profile
- Be concise — keep answers to 3-5 sentences unless they ask for detail
- Use ₹ for Indian Rupee amounts and reference their actual numbers
- Bold important numbers or key takeaways using **bold**
- Never make up specific timelines unless you can calculate them from their data
- If you don't know something, say so honestly

Respond only in plain text with **bold** for emphasis. Do NOT use markdown headers or bullet lists with dashes.`;

    if (!GEMINI_API_KEY) {
      // Fallback: deterministic smart replies if no API key
      const fallback = generateFallback(message, context);
      return NextResponse.json({ reply: fallback });
    }

    const response = await fetch(`${GEMINI_URL}?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: systemPrompt }] },
        contents: [{ role: "user", parts: [{ text: message }] }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 300,
          topP: 0.9,
        },
      }),
    });

    if (!response.ok) {
      const fallback = generateFallback(message, context);
      return NextResponse.json({ reply: fallback });
    }

    const data = await response.json();
    const reply =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ??
      generateFallback(message, context);

    return NextResponse.json({ reply });
  } catch {
    return NextResponse.json(
      { reply: "I'm having trouble connecting right now. Please try again shortly." },
      { status: 200 }
    );
  }
}

// Smart fallback replies when no Gemini key is configured
function generateFallback(message: string, context: Record<string, unknown>): string {
  const msg = message.toLowerCase();
  const score = Number(context.credit_score) || 0;
  const eligible = Number(context.eligible_amount) || 0;
  const disposable = Number(context.disposable_income) || 0;
  const decision = String(context.decision || "");
  const savings = String(context.savings_ratio || "0%");

  if (msg.includes("improve") || msg.includes("better") || msg.includes("increase")) {
    return `To improve your **${score}** score, focus on three things: reduce your monthly expenses to increase your savings ratio above 30%, upload verified payslip and bank statement documents (this alone can raise eligibility by up to 50%), and maintain stable employment for at least 2+ years. Your biggest quick win is document verification.`;
  }
  if (msg.includes("how long") || msg.includes("qualify") || msg.includes("when")) {
    if (decision === "APPROVED") return `Great news — you're already approved! Your current profile qualifies you for up to **₹${eligible.toLocaleString("en-IN")}**. You can apply now. To increase the limit further, try reducing expenses or uploading verified documents.`;
    return `Based on your profile, if you focus on reducing expenses to bring your savings ratio above 25% and upload valid documents, you could qualify for a loan within **2-3 months**. Your disposable income of **₹${disposable.toLocaleString("en-IN")}** is the main factor to work on.`;
  }
  if (msg.includes("dti") || msg.includes("debt") || msg.includes("ratio")) {
    return `DTI (Debt-to-Income ratio) is the percentage of your monthly income that goes toward debt payments. Lenders want this below 35-50%. Your current savings ratio is **${savings}** — a higher savings ratio means a lower DTI, which means you can borrow more. Reducing expenses is the fastest way to improve your DTI.`;
  }
  if (msg.includes("income") || msg.includes("expense") || msg.includes("first")) {
    return `For your profile, **reducing expenses first** will have the faster impact. Increasing income takes longer (salary raises, new jobs) while cutting subscriptions and discretionary spending can happen this month. Every **₹1,000** reduction in monthly expenses can increase your loan eligibility by **₹6,000–₹12,000** depending on your employment type.`;
  }
  if (msg.includes("score") || msg.includes("credit")) {
    return `Your score of **${score}** is calculated using your income, expenses, employment stability, and verified document data. The ML model weighs verified OCR data highest. Uploading a recent payslip and bank statement is the single most impactful thing you can do right now to boost your score.`;
  }
  return `Based on your credit score of **${score}** and eligible amount of **₹${eligible.toLocaleString("en-IN")}**, here's my advice: your savings ratio of **${savings}** is the key metric to focus on. Aim to keep expenses below 70% of your income. Feel free to ask me anything specific about your assessment!`;
}
