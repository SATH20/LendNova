import type { Metadata } from "next";
import { Inter, Manrope } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LENDNOVA | AI Creditworthiness",
  description:
    "AI-Based Creditworthiness Prediction System for First-Time Borrowers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${manrope.variable} min-h-screen bg-[#0A0F1F] text-[#E8EBF3] antialiased`}
      >
        {children}
        <footer className="border-t border-white/5 bg-[#0A0F1F]/80 backdrop-blur-sm">
          <div className="mx-auto max-w-7xl px-6 py-4">
            <div className="flex flex-col items-center justify-between gap-2 text-xs text-muted sm:flex-row">
              <p>© 2026 LendNova. Built by Rajavarapu Sathwik</p>
              <div className="flex items-center gap-4">
                <a
                  href="https://www.instagram.com/_sathwikkkk_?igsh=MWcyc3lwbWd0eWJkcQ=="
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition hover:text-white"
                >
                  Instagram
                </a>
                <span className="text-white/20">•</span>
                <a
                  href="https://github.com/SATH20/LendNova"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition hover:text-white"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
