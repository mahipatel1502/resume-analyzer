const toneMap = {
  signal: "bg-signal-500",
  cyan: "bg-cyan-signal",
  amber: "bg-amber-signal",
  rose: "bg-rose-signal",
};

export default function ProgressBar({
  value = 0,
  label,
  tone = "signal",
  showValue = true,
  size = "md",
}) {
  const clamped = Math.max(0, Math.min(100, value));
  const heightClass = size === "sm" ? "h-1.5" : "h-2.5";

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="mb-1.5 flex items-center justify-between">
          {label && (
            <span className="font-body text-[13px] text-ink-200">{label}</span>
          )}
          {showValue && (
            <span className="font-mono text-[12px] text-ink-300">
              {Math.round(clamped)}%
            </span>
          )}
        </div>
      )}
      <div className={`w-full overflow-hidden rounded-full bg-ink-700 ${heightClass}`}>
        <div
          className={`${heightClass} rounded-full ${toneMap[tone]} transition-[width] duration-700 ease-out`}
          style={{ width: `${clamped}%` }}
          role="progressbar"
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
