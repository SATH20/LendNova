"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

type ChatMessage = {
  id: string;
  role: "user" | "ai";
  text: string;
};

type Props = {
  creditScore: number;
  riskBand: string;
  decision: string;
  eligibleAmount: number;
  disposableIncome: number;
  savingsRatio: number;
  employmentType: string;
  improvements?: string[];
};

const STARTER_PROMPTS = [
  "How do I improve my score?",
  "How long to qualify for ₹50,000?",
  "What is a debt-to-income ratio?",
  "Should I reduce expenses or increase income first?",
];

export default function CreditCoach({
  creditScore, riskBand, decision, eligibleAmount,
  disposableIncome, savingsRatio, employmentType, improvements = [],
}: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "ai",
      text: `Hi! I'm your AI Credit Coach 👋\n\nYour current credit score is **${creditScore}** (${riskBand} risk) and you're eligible for up to **₹${eligibleAmount.toLocaleString("en-IN")}**.\n\nAsk me anything about your results or how to improve your eligibility!`,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const context = {
        credit_score: creditScore,
        risk_band: riskBand,
        decision,
        eligible_amount: eligibleAmount,
        disposable_income: disposableIncome,
        savings_ratio: `${(savingsRatio * 100).toFixed(1)}%`,
        employment_type: employmentType,
        improvement_areas: improvements.slice(0, 3),
      };

      const resp = await fetch("/api/coach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, context }),
      });

      const data = await resp.json();
      const aiMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "ai",
        text: data.reply || "I'm having trouble connecting. Please try again.",
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      setMessages((prev) => [...prev, {
        id: `err-${Date.now()}`,
        role: "ai",
        text: "Sorry, I couldn't reach the server. Please check your connection.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderText = (text: string) => {
    return text.split(/\*\*(.*?)\*\*/g).map((part, i) =>
      i % 2 === 1
        ? <strong key={i} className="text-white font-semibold">{part}</strong>
        : <span key={i}>{part}</span>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass glow-border flex flex-col rounded-3xl overflow-hidden"
      style={{ height: "520px" }}
    >
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-white/8 px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#4F7FFF] to-[#9B6BFF]">
          <span className="text-sm">🤖</span>
        </div>
        <div>
          <p className="text-sm font-semibold text-white">AI Credit Coach</p>
          <p className="text-xs text-muted">Powered by Gemini</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-[#2EE59D] animate-pulse" />
          <span className="text-xs text-[#2EE59D]">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === "user" ? "chat-user text-white" : "chat-ai text-[#E8EBF3]"}`}>
                {renderText(msg.text)}
              </div>
            </motion.div>
          ))}
          {loading && (
            <motion.div key="typing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="chat-ai rounded-2xl px-4 py-3">
                <div className="flex items-center gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <span key={i} className="typing-dot h-2 w-2 rounded-full bg-muted block" />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Starter prompts */}
      {messages.length <= 1 && (
        <div className="px-5 pb-3 flex flex-wrap gap-2">
          {STARTER_PROMPTS.map((p) => (
            <button
              key={p}
              onClick={() => send(p)}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-muted transition hover:border-[#4F7FFF]/50 hover:text-white"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-white/8 px-4 py-3">
        <div className="flex items-center gap-2">
          <input
            id="coach-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Ask about your score, eligibility, or how to improve..."
            className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white outline-none transition focus:border-[#4F7FFF]/60 focus:ring-1 focus:ring-[#4F7FFF]/30 placeholder:text-muted"
          />
          <button
            id="coach-send-btn"
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="ripple flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#4F7FFF] to-[#9B6BFF] text-white transition hover:brightness-110 disabled:opacity-40"
            aria-label="Send message"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
