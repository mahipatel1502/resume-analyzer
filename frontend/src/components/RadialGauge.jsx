import { useEffect, useState } from "react";
import { useTheme } from "../context/ThemeContext";

const toneColors = {
  signal: "var(--t-signal-500)",
  cyan: "var(--t-cyan-signal)",
  amber: "var(--t-amber-signal)",
  rose: "var(--t-rose-signal)",
};

function getToneForScore(score) {
  if (score >= 75) return "signal";
  if (score >= 50) return "cyan";
  if (score >= 30) return "amber";
  return "rose";
}

export default function RadialGauge({
  score = 0,
  label,
  sublabel,
  size = 168,
  toneOverride,
}) {
  const { isDark } = useTheme();
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const target = Math.max(0, Math.min(100, score));
    const duration = 900;
    const start = performance.now();

    let frame;
    const step = (now) => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(target * eased);
      if (progress < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [score]);

  const tone = toneOverride || getToneForScore(score);
  const color = toneColors[tone];

  const isCompact = size <= 96;
  const strokeWidth = isCompact ? 7 : 9;
  const radius = size / 2 - strokeWidth - 5;
  const circumference = 2 * Math.PI * radius;
  const sweep = (animatedScore / 100) * circumference * 0.999;
  const tickCount = isCompact ? 32 : 40;
  const tickLengthMajor = isCompact ? 10 : 12;
  const tickLengthMinor = isCompact ? 7 : 9;

  return (
    <div className="flex flex-col items-center" style={{ width: size }}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90 overflow-visible">
          {Array.from({ length: tickCount }).map((_, i) => {
            const angle = (i / tickCount) * 360;
            const isMajor = i % 4 === 0;
            return (
              <line
                key={i}
                x1={size / 2}
                y1={6}
                x2={size / 2}
                y2={isMajor ? tickLengthMajor : tickLengthMinor}
                stroke="var(--gauge-tick)"
                strokeWidth={isMajor ? 1.4 : 0.9}
                transform={`rotate(${angle} ${size / 2} ${size / 2})`}
              />
            );
          })}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--gauge-track)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${sweep} ${circumference}`}
            style={{
              filter: isDark ? `drop-shadow(0 0 8px ${color})` : "none",
              transition: "stroke 0.4s ease",
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center leading-none">
          <span
            className={`font-mono font-bold tabular-nums ${isCompact ? "text-2xl" : "text-3xl"}`}
            style={{ color }}
          >
            {Math.round(animatedScore)}
          </span>
          <span className={`font-mono uppercase tracking-wider text-ink-400 ${isCompact ? "text-[9px] mt-0.5" : "text-[10px]"}`}>
            / 100
          </span>
        </div>
      </div>
      {label && (
        <p className="mt-3 font-display text-sm font-semibold text-ink-100">{label}</p>
      )}
      {sublabel && (
        <p className="font-mono text-[11px] uppercase tracking-wider text-ink-400">{sublabel}</p>
      )}
    </div>
  );
}
