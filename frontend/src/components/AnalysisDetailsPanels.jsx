import Card from "./Card";

function statusColor(status) {
  if (status === "good") return "text-signal-400";
  if (status === "missing") return "text-rose-signal";
  return "text-amber-signal";
}

export default function ATSDetailsPanel({ atsDetails }) {
  if (!atsDetails) return null;

  const { sections = {}, missing_sections = [], weak_content = [], formatting_issues = [], suggestions = [] } = atsDetails;

  return (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(sections).map(([name, section]) => (
          <div key={name} className="rounded-lg border border-ink-600 bg-ink-800/40 p-4">
            <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-ink-400">
              {name.replace(/_/g, " ")}
            </p>
            <p className="font-display text-lg font-semibold text-ink-100">
              {section.score}/{section.max_score}
            </p>
            <p className={`mt-1 font-mono text-[11px] capitalize ${statusColor(section.status)}`}>
              {section.status?.replace(/_/g, " ")}
            </p>
            {section.issues?.length > 0 && (
              <ul className="mt-2 space-y-1">
                {section.issues.map((issue) => (
                  <li key={issue} className="font-body text-[12px] text-ink-400">• {issue}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>

      {missing_sections.length > 0 && (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-rose-signal">Missing Sections</p>
          <div className="flex flex-wrap gap-2">
            {missing_sections.map((s) => (
              <span key={s} className="rounded-md border border-rose-signal/30 bg-rose-signal/10 px-2 py-1 font-mono text-[11px] text-rose-signal">{s}</span>
            ))}
          </div>
        </div>
      )}

      {formatting_issues.length > 0 && (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-amber-signal">Formatting Issues</p>
          <ul className="space-y-1">
            {formatting_issues.map((issue) => (
              <li key={issue} className="font-body text-[13px] text-ink-300">• {issue}</li>
            ))}
          </ul>
        </div>
      )}

      {weak_content.length > 0 && (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-amber-signal">Weak Content</p>
          <ul className="space-y-1">
            {weak_content.map((item) => (
              <li key={item} className="font-body text-[13px] text-ink-300">• {item}</li>
            ))}
          </ul>
        </div>
      )}

      {suggestions.length > 0 && (
        <div>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">ATS Suggestions</p>
          <ul className="space-y-1">
            {suggestions.map((s) => (
              <li key={s} className="font-body text-[13px] text-ink-300">• {s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function JobAnalysisPanel({ jobAnalysis }) {
  if (!jobAnalysis) return null;

  const lists = [
    { label: "Job Skills", items: jobAnalysis.job_skills, tone: "ink" },
    { label: "Resume Skills", items: jobAnalysis.resume_skills, tone: "ink" },
    { label: "Required Technologies", items: jobAnalysis.required_technologies, tone: "signal" },
    { label: "Experience Requirements", items: jobAnalysis.experience_requirements, tone: "amber" },
    { label: "Education Requirements", items: jobAnalysis.education_requirements, tone: "amber" },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {lists.map(({ label, items }) => (
        <div key={label}>
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">{label}</p>
          {items?.length > 0 ? (
            <ul className="space-y-1">
              {items.map((item) => (
                <li key={item} className="font-body text-[13px] text-ink-300">• {item}</li>
              ))}
            </ul>
          ) : (
            <p className="font-mono text-[12px] text-ink-500">None detected</p>
          )}
        </div>
      ))}
    </div>
  );
}

export function MLMatchPanel({ mlDetails, matchDetails }) {
  if (!mlDetails && !matchDetails) return null;

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {matchDetails && (
        <div className="rounded-lg border border-ink-600 bg-ink-800/40 p-4">
          <p className="font-mono text-[10px] uppercase tracking-wider text-ink-400">POST /match-resume</p>
          <p className="mt-2 font-display text-2xl font-bold text-ink-100">{matchDetails.match_score}%</p>
          <p className="font-body text-[13px] text-ink-300">Skill-based match score</p>
        </div>
      )}
      {mlDetails && (
        <div className="rounded-lg border border-ink-600 bg-ink-800/40 p-4">
          <p className="font-mono text-[10px] uppercase tracking-wider text-ink-400">POST /ml-match</p>
          <p className="mt-2 font-display text-2xl font-bold text-cyan-400">{mlDetails.ml_similarity}%</p>
          <p className="font-body text-[13px] text-ink-300">ML similarity (TF-IDF cosine)</p>
          <p className="mt-1 font-mono text-[11px] text-ink-500">Skill match: {mlDetails.skill_match}%</p>
        </div>
      )}
    </div>
  );
}
