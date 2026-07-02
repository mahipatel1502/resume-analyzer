export default function Footer() {
  return (
    <footer className="relative border-t border-ink-700/60 bg-ink-900/50 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-8 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <p className="font-mono text-[11px] uppercase tracking-wider text-ink-400">
          Resume.Analyzer — ATS Diagnostic Engine
        </p>
        <p className="font-mono text-[11px] text-ink-500">
          React · FastAPI · ML · Tailwind
        </p>
      </div>
    </footer>
  );
}
