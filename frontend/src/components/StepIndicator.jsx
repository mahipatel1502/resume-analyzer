import { Check } from "lucide-react";

const steps = [
  { key: "upload", label: "Upload" },
  { key: "jd", label: "Job Description" },
  { key: "results", label: "Results" },
];

export default function StepIndicator({ current }) {
  const currentIndex = steps.findIndex((s) => s.key === current);

  return (
    <div className="mx-auto mb-10 flex max-w-lg items-center justify-between rounded-2xl border border-ink-700/60 bg-ink-900/50 p-4 backdrop-blur-sm">
      {steps.map((step, i) => {
        const isComplete = i < currentIndex;
        const isCurrent = i === currentIndex;
        return (
          <div key={step.key} className="flex flex-1 items-center last:flex-none">
            <div className="flex flex-col items-center gap-2">
              <div
                className={`flex h-9 w-9 items-center justify-center rounded-full border-2 font-mono text-[12px] font-semibold transition-all ${
                  isComplete
                    ? "border-signal-500 bg-signal-500 text-ink-950 shadow-[0_0_16px_-2px_var(--hero-glow)]"
                    : isCurrent
                      ? "border-signal-500 bg-signal-500/10 text-signal-500"
                      : "border-ink-600 text-ink-400"
                }`}
              >
                {isComplete ? <Check className="h-4 w-4" /> : i + 1}
              </div>
              <span
                className={`whitespace-nowrap font-mono text-[10px] uppercase tracking-wider ${
                  isCurrent ? "text-signal-500" : "text-ink-400"
                }`}
              >
                {step.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={`mx-2 h-0.5 flex-1 rounded-full transition-colors ${
                  isComplete ? "bg-signal-500" : "bg-ink-600"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
