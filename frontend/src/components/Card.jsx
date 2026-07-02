export default function Card({ children, className = "", glow = false, hover = false }) {
  return (
    <div
      className={`relative rounded-2xl border border-ink-700/80 bg-ink-900/70 p-6 backdrop-blur-sm transition-all duration-300 ${
        glow
          ? "shadow-[var(--card-shadow)] ring-1 ring-signal-500/10"
          : "shadow-[var(--card-shadow)]"
      } ${
        hover ? "hover:-translate-y-0.5 hover:border-ink-500 hover:shadow-lg" : ""
      } ${className}`}
    >
      {glow && (
        <div className="pointer-events-none absolute -inset-px rounded-2xl bg-gradient-to-br from-signal-500/10 via-transparent to-cyan-signal/5" />
      )}
      <div className="relative">{children}</div>
    </div>
  );
}

export function CardHeader({ eyebrow, title, action }) {
  return (
    <div className="mb-5 flex items-start justify-between gap-3">
      <div>
        {eyebrow && (
          <p className="mb-1 font-mono text-[10.5px] uppercase tracking-wider text-ink-400">
            {eyebrow}
          </p>
        )}
        <h3 className="font-display text-lg font-semibold text-ink-100">{title}</h3>
      </div>
      {action}
    </div>
  );
}
