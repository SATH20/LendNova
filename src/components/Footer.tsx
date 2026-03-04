export default function Footer() {
  return (
    <footer className="mt-auto border-t border-white/5 bg-[#0A0F1F]/80 backdrop-blur-sm">
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
  );
}
