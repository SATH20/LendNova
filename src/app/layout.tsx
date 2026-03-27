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
      </body>
    </html>
  );
}
