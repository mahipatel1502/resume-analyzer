import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  FileSearch,
  Target,
  ListChecks,
  Sparkles,
  ScanLine,
  Wifi,
  WifiOff,
  Brain,
} from "lucide-react";
import RadialGauge from "../components/RadialGauge";
import Card from "../components/Card";
import { checkApiHealth } from "../api/endpoints";

const features = [
  {
    icon: FileSearch,
    title: "ATS Compatibility",
    description: "Measures how cleanly an ATS parser can read your formatting, structure, and section headers.",
  },
  {
    icon: Target,
    title: "Job Match Score",
    description: "Skill keyword overlap between your resume and the job description's extracted requirements.",
  },
  {
    icon: Brain,
    title: "ML Similarity",
    description: "TF-IDF cosine similarity — semantic closeness between resume text and job description.",
  },
  {
    icon: ListChecks,
    title: "Skill Gap Detection",
    description: "Surfaces matched skills and the exact gaps standing between you and the role.",
  },
  {
    icon: Sparkles,
    title: "Recommendations",
    description: "Specific, actionable edits ranked by likely impact on your score.",
  },
];

const steps = [
  { n: "01", title: "Upload your resume", desc: "PDF only. We parse text, structure, skills, education, and experience." },
  { n: "02", title: "Paste the job description", desc: "We extract requirements, technologies, and keywords to grade against." },
  { n: "03", title: "Read the diagnostic", desc: "ATS, match, and ML scores — plus gaps and prioritized fixes." },
];

export default function Home() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    checkApiHealth()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <div className="grid-texture">
      <section className="relative overflow-hidden border-b border-ink-700/60">
        <div className="hero-orb hero-orb--primary left-1/4 top-10 h-[28rem] w-[28rem] -translate-x-1/2" />
        <div className="hero-orb hero-orb--secondary right-0 top-1/3 h-72 w-72" />
        <div className="absolute inset-0 bg-gradient-to-b from-ink-900/30 via-transparent to-ink-950" />

        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
          <div className="grid items-center gap-14 lg:grid-cols-2">
            <div className="animate-tick">
              <div className="mb-6 flex flex-wrap items-center gap-3">
                <div className="inline-flex items-center gap-2 rounded-full border border-ink-600 bg-ink-900/80 px-3.5 py-1.5 shadow-sm backdrop-blur-sm">
                  <ScanLine className="h-3.5 w-3.5 text-signal-500" />
                  <span className="font-mono text-[11px] uppercase tracking-wider text-ink-300">
                    ATS Diagnostic Engine
                  </span>
                </div>
                <div
                  className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-wider ${
                    apiStatus === "online"
                      ? "border-signal-600/40 bg-signal-500/10 text-signal-500"
                      : apiStatus === "offline"
                        ? "border-rose-signal/30 bg-rose-signal/10 text-rose-signal"
                        : "border-ink-600 text-ink-400"
                  }`}
                >
                  {apiStatus === "online" ? (
                    <Wifi className="h-3 w-3" />
                  ) : apiStatus === "offline" ? (
                    <WifiOff className="h-3 w-3" />
                  ) : null}
                  API {apiStatus === "checking" ? "…" : apiStatus}
                </div>
              </div>

              <h1 className="font-display text-4xl font-bold leading-[1.08] tracking-tight text-ink-100 text-balance sm:text-5xl lg:text-[3.25rem]">
                Know exactly why your resume gets{" "}
                <span className="bg-gradient-to-r from-signal-500 to-cyan-signal bg-clip-text text-transparent">
                  filtered out
                </span>
                .
              </h1>
              <p className="mt-6 max-w-xl font-body text-base leading-relaxed text-ink-300 sm:text-lg">
                Upload a resume and job description. Get ATS readability, skill match,
                ML similarity, and the precise gaps between you and an interview.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-4">
                <Link to="/upload" className="btn-primary group px-6 py-3">
                  Analyze My Resume
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
                <Link to="/history" className="btn-secondary px-6 py-3">
                  View History
                </Link>
              </div>
              <p className="mt-5 font-mono text-[11px] text-ink-500">
                JWT-authenticated workspace · PDF up to 5MB · Dark & light mode
              </p>
            </div>

            <div className="relative animate-float">
              <Card className="mx-auto max-w-md" glow>
                <p className="mb-5 font-mono text-[10.5px] uppercase tracking-wider text-ink-400">
                  Live Sample Readout
                </p>
                <div className="grid grid-cols-3 gap-3">
                  <RadialGauge score={88} label="ATS" sublabel="Strong" size={120} />
                  <RadialGauge score={72} label="Match" sublabel="Good" size={120} toneOverride="cyan" />
                  <RadialGauge score={65} label="ML" sublabel="Fair" size={120} toneOverride="cyan" />
                </div>
                <div className="mt-6 flex flex-wrap gap-2">
                  {["Python", "FastAPI", "Docker"].map((s) => (
                    <span
                      key={s}
                      className="rounded-md border border-signal-600/40 bg-signal-500/10 px-2.5 py-1 font-mono text-[11px] text-signal-500"
                    >
                      {s}
                    </span>
                  ))}
                  {["Kubernetes", "AWS"].map((s) => (
                    <span
                      key={s}
                      className="rounded-md border border-rose-signal/30 bg-rose-signal/10 px-2.5 py-1 font-mono text-[11px] text-rose-signal"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="mb-12 max-w-2xl">
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
            What the engine measures
          </p>
          <h2 className="font-display text-2xl font-bold text-ink-100 sm:text-3xl">
            Five readings, one diagnostic.
          </h2>
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {features.map((f) => (
            <Card key={f.title} hover className="group">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-ink-600 bg-ink-800/80 transition-colors group-hover:border-signal-500/40 group-hover:bg-signal-500/10">
                <f.icon className="h-5 w-5 text-signal-500" strokeWidth={2} />
              </div>
              <h3 className="mb-2 font-display text-[15px] font-semibold text-ink-100">{f.title}</h3>
              <p className="font-body text-[13px] leading-relaxed text-ink-300">{f.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="border-t border-ink-700/60 bg-ink-900/40">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="mb-12 max-w-2xl">
            <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
              The process
            </p>
            <h2 className="font-display text-2xl font-bold text-ink-100 sm:text-3xl">
              Three steps, in order.
            </h2>
          </div>
          <div className="grid gap-8 sm:grid-cols-3">
            {steps.map((step, i) => (
              <div
                key={step.n}
                className="relative rounded-2xl border border-ink-700/60 bg-ink-900/50 p-6 transition-all hover:border-ink-500 hover:shadow-[var(--card-shadow)]"
              >
                <span className="font-mono text-4xl font-bold text-ink-700">{step.n}</span>
                <h3 className="mt-3 font-display text-base font-semibold text-ink-100">{step.title}</h3>
                <p className="mt-2 font-body text-[13px] leading-relaxed text-ink-300">{step.desc}</p>
                {i < steps.length - 1 && (
                  <div className="absolute -right-4 top-1/2 hidden h-px w-8 bg-gradient-to-r from-ink-600 to-transparent sm:block" />
                )}
              </div>
            ))}
          </div>
          <div className="mt-12">
            <Link to="/upload" className="btn-primary px-6 py-3">
              Start the diagnostic
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
