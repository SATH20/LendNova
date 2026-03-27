import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const {
      credit_score, risk_band, decision, approval_probability,
      eligible_amount, monthly_emi, disposable_income, savings_ratio,
      employment_type, income_used, expense_used,
      positive_factors = [], risk_factors = [],
      improvement_suggestions = [],
      timestamp, assessment_id,
    } = body;

    const date = timestamp ? new Date(timestamp).toLocaleString("en-IN") : new Date().toLocaleString("en-IN");
    const decisionColor = decision === "APPROVED" ? "#2EE59D" : decision === "REJECTED" ? "#FF5C5C" : "#9B6BFF";

    const formatAmt = (n: number) => {
      if (n >= 100000) return `₹${(n / 100000).toFixed(2)}L`;
      return `₹${n.toLocaleString("en-IN")}`;
    };

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>LendNova Credit Assessment Report</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; background: #0A0F1F; color: #E8EBF3; padding: 40px; }
    .page { max-width: 760px; margin: 0 auto; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 32px; border-bottom: 1px solid rgba(255,255,255,0.08); }
    .logo { display: flex; align-items: center; gap: 12px; }
    .logo-box { width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #4F7FFF, #9B6BFF); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
    .logo-text p:first-child { font-weight: 700; letter-spacing: 0.15em; color: #9B6BFF; }
    .logo-text p:last-child { font-size: 11px; color: #8A8FA3; }
    .header-right { text-align: right; font-size: 11px; color: #8A8FA3; }
    .section-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.3em; color: #8A8FA3; margin-bottom: 12px; }
    .score-section { margin-top: 32px; display: flex; align-items: flex-start; justify-content: space-between; }
    .score-big { font-size: 72px; font-weight: 700; line-height: 1; background: linear-gradient(135deg, #4F7FFF, #9B6BFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .decision-badge { padding: 6px 16px; border-radius: 999px; font-size: 12px; font-weight: 700; color: ${decisionColor}; background: ${decisionColor}22; border: 1px solid ${decisionColor}44; letter-spacing: 0.1em; }
    .grid { display: grid; gap: 16px; margin-top: 24px; }
    .grid-2 { grid-template-columns: 1fr 1fr; }
    .grid-3 { grid-template-columns: 1fr 1fr 1fr; }
    .card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px; }
    .card-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.2em; color: #8A8FA3; }
    .card-value { font-size: 20px; font-weight: 600; color: #fff; margin-top: 8px; }
    .card-sub { font-size: 11px; color: #8A8FA3; margin-top: 4px; }
    .tag { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 10px; font-weight: 600; margin-right: 6px; margin-top: 6px; }
    .tag-green { background: #2EE59D22; color: #2EE59D; border: 1px solid #2EE59D33; }
    .tag-orange { background: #FF9F4322; color: #FF9F43; border: 1px solid #FF9F4333; }
    .tag-red { background: #FF5C5C22; color: #FF5C5C; border: 1px solid #FF5C5C33; }
    .suggestion { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px; margin-top: 12px; }
    .suggestion-cat { font-size: 12px; font-weight: 600; color: #fff; }
    .suggestion-msg { font-size: 12px; color: #8A8FA3; margin-top: 4px; }
    .suggestion-priority { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 999px; float: right; }
    .p-critical { background: #FF5C5C22; color: #FF5C5C; }
    .p-high { background: #FF9F4322; color: #FF9F43; }
    .p-medium { background: #9B6BFF22; color: #9B6BFF; }
    .p-low { background: #4F7FFF22; color: #4F7FFF; }
    .p-info { background: #2EE59D22; color: #2EE59D; }
    .divider { height: 1px; background: rgba(255,255,255,0.06); margin: 28px 0; }
    .footer { text-align: center; font-size: 11px; color: #8A8FA3; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.06); }
    h2 { font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 4px; }
  </style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="logo">
      <div class="logo-box">LN</div>
      <div class="logo-text">
        <p>LENDNOVA</p>
        <p>AI Credit Assessment Report</p>
      </div>
    </div>
    <div class="header-right">
      <p>Report Date: ${date}</p>
      ${assessment_id ? `<p style="margin-top:4px">Assessment ID: #${assessment_id}</p>` : ""}
      <p style="margin-top:4px">Confidential Document</p>
    </div>
  </div>

  <div class="score-section">
    <div>
      <div class="section-label">Credit Score</div>
      <div class="score-big">${credit_score}</div>
      <div style="font-size:13px;color:#8A8FA3;margin-top:8px">${risk_band} Risk · ${(approval_probability * 100).toFixed(1)}% Approval Probability</div>
    </div>
    <div style="text-align:right">
      <div class="decision-badge">${decision}</div>
      <div style="font-size:11px;color:#8A8FA3;margin-top:10px">Employment: ${employment_type}</div>
    </div>
  </div>

  <div class="divider"></div>

  <div class="section-label">Loan Eligibility</div>
  <div class="grid grid-3">
    <div class="card">
      <div class="card-label">Eligible Amount</div>
      <div class="card-value">${formatAmt(eligible_amount)}</div>
      <div class="card-sub">Based on verified data</div>
    </div>
    <div class="card">
      <div class="card-label">Monthly EMI</div>
      <div class="card-value">${formatAmt(monthly_emi)}</div>
      <div class="card-sub">Estimated 12-month</div>
    </div>
    <div class="card">
      <div class="card-label">Disposable Income</div>
      <div class="card-value">${formatAmt(disposable_income)}</div>
      <div class="card-sub">Monthly surplus</div>
    </div>
  </div>

  <div class="grid grid-2" style="margin-top:16px">
    <div class="card">
      <div class="card-label">Savings Ratio</div>
      <div class="card-value">${(savings_ratio * 100).toFixed(1)}%</div>
      <div class="card-sub">Target: 30%+</div>
    </div>
    <div class="card">
      <div class="card-label">Data Source</div>
      <div style="margin-top:10px">
        <span class="tag ${income_used === 'verified' ? 'tag-green' : 'tag-orange'}">Income: ${income_used === 'verified' ? 'OCR Verified' : 'Declared'}</span>
        <span class="tag ${expense_used === 'verified' ? 'tag-green' : 'tag-orange'}">Expenses: ${expense_used === 'verified' ? 'OCR Verified' : 'Declared'}</span>
      </div>
    </div>
  </div>

  ${improvement_suggestions.length > 0 ? `
  <div class="divider"></div>
  <div class="section-label">Improvement Suggestions</div>
  ${improvement_suggestions.slice(0, 4).map((s: { priority: string; category: string; message: string }) => `
  <div class="suggestion">
    <span class="suggestion-priority p-${(s.priority || "info").toLowerCase()}">${s.priority}</span>
    <div class="suggestion-cat">${s.category}</div>
    <div class="suggestion-msg">${s.message}</div>
  </div>`).join("")}
  ` : ""}

  <div class="divider"></div>
  <div class="footer">
    <p>This report was generated by LendNova AI Underwriting Platform. For educational and illustrative purposes only.</p>
    <p style="margin-top:4px">© 2026 LendNova · Built by Rajavarapu Sathwik · github.com/SATH20/LendNova</p>
  </div>
</div>
</body>
</html>`;

    return new NextResponse(html, {
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Disposition": `attachment; filename="lendnova-report-${assessment_id ?? Date.now()}.html"`,
      },
    });
  } catch (err) {
    return NextResponse.json({ error: "Failed to generate report" }, { status: 500 });
  }
}
