import { Check, X } from "lucide-react";

export function SkillTag({ skill, variant = "found" }) {
  const isFound = variant === "found";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 font-mono text-[12px] ${
        isFound
          ? "border-signal-600/40 bg-signal-500/10 text-signal-400"
          : "border-rose-signal/30 bg-rose-signal/10 text-rose-signal"
      }`}
    >
      {isFound ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
      {skill}
    </span>
  );
}

export function SkillTagGrid({ skills, variant }) {
  if (!skills || skills.length === 0) {
    return (
      <p className="font-mono text-[12px] text-ink-500">
        {variant === "found" ? "No matched skills detected." : "No gaps detected — nice work."}
      </p>
    );
  }
  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill) => (
        <SkillTag key={skill} skill={skill} variant={variant} />
      ))}
    </div>
  );
}
