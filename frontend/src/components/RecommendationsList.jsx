import { Lightbulb } from "lucide-react";

export default function RecommendationsList({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <p className="font-mono text-[12px] text-ink-500">
        No specific recommendations — your resume aligns well with this role.
      </p>
    );
  }

  return (
    <ol className="space-y-3">
      {recommendations.map((rec, i) => (
        <li
          key={i}
          className="flex gap-3 rounded-lg border border-ink-700 bg-ink-800/50 p-4"
        >
          <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-ink-700 font-mono text-[11px] font-semibold text-signal-500">
            {i + 1}
          </span>
          <p className="font-body text-[13.5px] leading-relaxed text-ink-200">{rec}</p>
        </li>
      ))}
    </ol>
  );
}
