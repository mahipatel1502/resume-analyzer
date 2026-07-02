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

  const radius = size / 2 - 14;
  const circumference = 2 * Math.PI * radius;
  const sweep = (animatedScore / 100) * circumference * 0.999;

  return (
    <div className="flex flex-col items-center" style={{ width: size }}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {Array.from({ length: 40 }).map((_, i) => {
            const angle = (i / 40) * 360;
            const isMajor = i % 5 === 0;
            return (
              <line
                key={i}
                x1={size / 2}
                y1={6}
                x2={size / 2}
                y2={isMajor ? 12 : 9}
                stroke="var(--gauge-tick)"
                strokeWidth={isMajor ? 1.5 : 1}
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
            strokeWidth={9}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={9}
            strokeLinecap="round"
            strokeDasharray={`${sweep} ${circumference}`}
            style={{
              filter: isDark ? `drop-shadow(0 0 8px ${color})` : "none",
              transition: "stroke 0.4s ease",
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-3xl font-bold tabular-nums" style={{ color }}>
            {Math.round(animatedScore)}
          </span>
          <span className="font-mono text-[10px] uppercase tracking-wider text-ink-400">/ 100</span>
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
