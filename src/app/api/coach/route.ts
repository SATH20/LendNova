import { NextResponse } from "next/server";

const MODELS = [
  "gemini-2.0-flash-lite",
  "gemini-1.5-flash-8b",
  "gemini-1.5-flash",
];
const BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models";

async function callGemini(key: string, model: string, prompt: string) {
  const resp = await fetch(`${BASE_URL}/${model}:generateContent?key=${key}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.75, maxOutputTokens: 350, topP: 0.95 },
    }),
  });
  return { status: resp.status, data: resp.ok ? await resp.json() : null };
}

export async function POST(request: Request) {
  const GEMINI_API_KEY = process.env.GEMINI_API_KEY ?? "";

  try {
    const { message, context } = await request.json();

    const prompt = `You are an expert AI Credit Coach in LendNova, an AI credit platform for first-time borrowers in India.

User's profile:
- Credit Score: ${context.credit_score} (${context.risk_band} risk)
- Decision: ${context.decision}
- Eligible Loan: ₹${Number(context.eligible_amount || 0).toLocaleString("en-IN")}
- Disposable Income: ₹${Number(context.disposable_income || 0).toLocaleString("en-IN")}/month
- Savings Ratio: ${context.savings_ratio}
- Employment: ${context.employment_type}
- Key Areas to Improve: ${Array.isArray(context.improvement_areas) ? context.improvement_areas.join(", ") : "None"}

Instructions: Answer in 2-4 warm, conversational sentences. Reference actual numbers. Use **bold** for key figures. No bullet points or headers.

User asks: ${message}`;

    const noKey =
      !GEMINI_API_KEY ||
      GEMINI_API_KEY === "your_gemini_api_key_here" ||
      GEMINI_API_KEY.length < 20;

    if (!noKey) {
      for (const model of MODELS) {
        try {
          const { status, data } = await callGemini(GEMINI_API_KEY, model, prompt);

          if (status === 429) {
            console.warn(`[Coach] ${model} → 429 rate limited`);
            continue;
          }
          if (status === 400) {
            console.warn(`[Coach] ${model} → 400 bad request`);
            continue;
          }
          if (status !== 200 || !data) {
            console.warn(`[Coach] ${model} → ${status}`);
            continue;
          }

          const text = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim();
          if (text && text.length > 10) {
            console.log(`[Coach] ✓ Served by ${model}`);
            return NextResponse.json({ reply: text });
          }
        } catch (e) {
          console.error(`[Coach] ${model} fetch failed:`, e);
          continue;
        }
      }
      console.warn("[Coach] All models failed — using smart fallback.");
    }

    return NextResponse.json({ reply: generateSmartFallback(message, context) });
  } catch (err) {
    console.error("[Coach] Error:", err);
    return NextResponse.json({
      reply: "I'm having a brief connection issue. Please ask again in a moment!",
    });
  }
}

function generateSmartFallback(
  message: string,
  ctx: Record<string, unknown>
): string {
  const m = (message || "").toLowerCase();
  const score = Number(ctx.credit_score) || 0;
  const eligible = Number(ctx.eligible_amount) || 0;
  const disposable = Number(ctx.disposable_income) || 0;
  const decision = String(ctx.decision || "REVIEW");
  const savings = String(ctx.savings_ratio || "0%");
  const band = String(ctx.risk_band || "Medium");

  // Greetings
  if (/^(hi|hello|hey|howdy|sup|good)/.test(m)) {
    return `Hello! 👋 I'm your AI Credit Coach. Your current score is **${score}** (${band} risk) and you're eligible for **₹${eligible.toLocaleString("en-IN")}**. What would you like to know — how to improve your score, understand your eligibility, or plan your next steps?`;
  }

  // Score improvement
  if (m.includes("improve") || m.includes("boost") || m.includes("increase score") || m.includes("better score")) {
    return `To improve your **${score}** score, the most impactful action is uploading verified documents — a genuine payslip or bank statement can unlock up to **50% more eligibility** because verified data carries more weight than self-declared figures. Beyond that, bringing your savings ratio above **30%** and maintaining stable employment for 2+ years will steadily push your score higher.`;
  }

  // Eligibility question
  if (m.includes("eligible") || m.includes("how much") || m.includes("loan amount") || m.includes("borrow")) {
    return `Your current eligible loan amount is **₹${eligible.toLocaleString("en-IN")}**, calculated from your monthly disposable income of **₹${disposable.toLocaleString("en-IN")}**. The best way to increase this is to either verify your documents via OCR upload or use the **What-If Sliders** tab to model how reducing expenses or raising income affects your eligibility in real time.`;
  }

  // Timeline
  if (m.includes("how long") || m.includes("when") || m.includes("qualify") || m.includes("time")) {
    if (decision === "APPROVED") {
      return `Great news — you're already approved! You can apply right now for up to **₹${eligible.toLocaleString("en-IN")}**. If you want a higher amount, uploading your payslip can switch your income from "declared" to "OCR-verified", which significantly increases the ceiling.`;
    }
    return `With your disposable income of **₹${disposable.toLocaleString("en-IN")}**/month, if you upload verification documents and reduce your expense ratio, you could qualify within **1–3 months**. The key is getting your savings ratio above 25% and having your income verified via payslip.`;
  }

  // DTI / ratio questions
  if (m.includes("dti") || m.includes("debt-to-income") || m.includes("ratio") || m.includes("what is")) {
    return `Debt-to-Income (DTI) ratio is what percentage of your monthly income goes toward debt repayments — lenders want this below 40–50%. Your savings ratio of **${savings}** is essentially the opposite metric: the higher it is, the more you can afford to repay, and the more you can borrow. Reducing expenses is the fastest way to improve your DTI.`;
  }

  // Expense reduction
  if (m.includes("expense") || m.includes("spending") || m.includes("cut") || m.includes("reduce")) {
    return `Reducing expenses has a powerful multiplier effect on eligibility. Every **₹1,000** you cut from monthly expenses can add **₹6,000–₹12,000** to your loan eligibility. Start with subscriptions, entertainment, and discretionary spending — then use the **What-If Sliders** tab to immediately see the impact on your eligible amount.`;
  }

  // Income increase
  if (m.includes("income") || m.includes("salary") || m.includes("earn") || m.includes("side")) {
    return `Increasing your income is the other big lever. With your employment type, every extra **₹1,000/month** you earn can unlock roughly **₹10,000–₹15,000** more in loan eligibility. Verified side income — through freelancing, consulting, or part-time work — counts as long as it shows up consistently in your bank statements.`;
  }

  // Document / OCR
  if (m.includes("document") || m.includes("payslip") || m.includes("upload") || m.includes("ocr") || m.includes("verify")) {
    return `Uploading documents is the single fastest way to improve your assessment. When your income is **OCR-verified** from a payslip or bank statement, it carries far more weight than self-declared figures, and it unlocks **100% of your eligibility** (unverified profiles are capped). Upload a clear, recent payslip or 3 months of bank statements on the Overview tab.`;
  }

  // How score is calculated
  if (m.includes("calculat") || m.includes("how does") || m.includes("how is") || m.includes("work")) {
    return `Your score of **${score}** is generated by our Gradient Boosting ML model, which weighs your income stability, expense ratio, employment tenure, and whether your data is OCR-verified. Verified document data always overrides self-declared numbers, which is why using the document upload feature can visibly shift your score and eligibility.`;
  }

  // Employment / job
  if (m.includes("employ") || m.includes("job") || m.includes("tenure") || m.includes("work")) {
    return `Employment stability is a key signal for the ML model. Longer job tenure (2+ years) triggers a **tenure bonus** that boosts your eligibility multiplier. If you've recently changed jobs, staying at your current employer for another 6–12 months will meaningfully improve your assessment score.`;
  }

  // Savings
  if (m.includes("saving") || m.includes("save") || m.includes("surplus")) {
    return `Your savings ratio of **${savings}** reflects the percentage of your income left after expenses. A ratio above **30%** is the threshold most lenders prefer — it signals financial discipline and confirms you can service a loan. If you're below that, reducing expenses rather than increasing income is usually the faster path to hitting 30%.`;
  }

  // Fraud / verification concern
  if (m.includes("fraud") || m.includes("flag") || m.includes("suspicious") || m.includes("discrepan")) {
    return `If any discrepancies were flagged, it usually means the declared values don't perfectly match your uploaded documents. The fix is simple: make sure the income and employer details you enter match your payslip exactly, and only upload original, unedited documents. Re-running the assessment after correcting these will resolve most flags.`;
  }

  // Generic smart response — varies based on their profile weakness
  const savingsNum = parseFloat(savings) / 100;
  if (savingsNum < 0.15) {
    return `Your savings ratio of **${savings}** is the most important thing to address — at under 15%, lenders see limited capacity to repay a loan. Aim to cut monthly expenses until you're saving at least **20–25%** of your income. Even small cuts compound quickly in your eligibility calculation.`;
  }
  if (eligible < 5000) {
    return `Your eligible amount of **₹${eligible.toLocaleString("en-IN")}** is currently limited by the combination of your income level and unverified data. Uploading your payslip is the single step that will have the biggest impact — it switches your income from declared to OCR-verified, which the model weights much more heavily.`;
  }
  return `Your credit score is **${score}** (${band} risk) and you're eligible for **₹${eligible.toLocaleString("en-IN")}**. Ask me anything specific — how your score is calculated, how to increase your eligibility, what affects your DTI, or what documents to upload. I'm here to help!`;
}
