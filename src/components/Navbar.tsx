"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

const navLinks = [
  { href: "#pipeline", label: "Pipeline" },
  { href: "#capabilities", label: "Capabilities" },
  { href: "#models", label: "Models" },
  { href: "#security", label: "Security" },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav id="main-nav" className="glass glow-border sticky top-0 z-40 w-full">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#4F7FFF] via-[#7D7BFF] to-[#9B6BFF] p-[2px]">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#0A0F1F] text-sm font-semibold">
              LN
            </div>
          </div>
          <div>
            <p className="text-sm font-semibold tracking-[0.2em] text-[#9B6BFF]">
              LENDNOVA
            </p>
            <p className="text-xs text-muted">AI Underwriting Suite</p>
          </div>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden items-center gap-8 text-sm text-muted md:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="transition text-[#E8EBF3] hover:text-white"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/admin"
            id="nav-admin"
            className="hidden rounded-full border border-[#9B6BFF]/40 bg-[#9B6BFF]/10 px-4 py-2 text-xs font-semibold text-[#9B6BFF] transition hover:bg-[#9B6BFF]/20 md:inline-flex"
          >
            Admin
          </Link>
          <Link
            href="/assistant"
            id="nav-run-assessment"
            className="ripple rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
          >
            Run Assessment
          </Link>

          {/* Mobile hamburger  */}
          <button
            id="mobile-menu-toggle"
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 md:hidden"
            aria-label="Toggle menu"
          >
            <motion.span
              animate={mobileOpen ? { rotate: 45 } : { rotate: 0 }}
              className="relative block h-[2px] w-4 bg-white transition"
              style={{ transformOrigin: "center" }}
            >
              <motion.span
                animate={mobileOpen ? { rotate: -90, y: 0 } : { rotate: 0, y: -5 }}
                className="absolute left-0 block h-[2px] w-4 bg-white"
              />
              <motion.span
                animate={mobileOpen ? { opacity: 0 } : { opacity: 1, y: 5 }}
                className="absolute left-0 block h-[2px] w-4 bg-white"
              />
            </motion.span>
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-white/5 md:hidden"
          >
            <div className="flex flex-col gap-1 px-6 py-4">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-xl px-4 py-3 text-sm text-muted transition hover:bg-white/5 hover:text-white"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
