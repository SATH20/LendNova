import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="glass glow-border sticky top-0 z-40 w-full">
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
        <div className="hidden items-center gap-8 text-sm text-muted md:flex">
          <a href="#pipeline" className="transition text-[#E8EBF3] hover:text-white">
            Pipeline
          </a>
          <a
            href="#capabilities"
            className="transition text-[#E8EBF3] hover:text-white"
          >
            Capabilities
          </a>
          <a
            href="#models"
            className="transition text-[#E8EBF3] hover:text-white"
          >
            Models
          </a>
          <a
            href="#security"
            className="transition text-[#E8EBF3] hover:text-white"
          >
            Security
          </a>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/assistant"
            className="ripple rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:border-white/30 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60"
          >
            Run Assessment
          </Link>
          <a
            href="#architecture"
            className="ripple hidden rounded-full bg-gradient-to-r from-[#4F7FFF] to-[#9B6BFF] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white shadow-lg shadow-[#4F7FFF]/30 transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-[#4F7FFF]/60 md:inline-flex"
          >
            View Architecture
          </a>
        </div>
      </div>
    </nav>
  );
}
