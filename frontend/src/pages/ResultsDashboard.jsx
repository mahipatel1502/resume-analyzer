import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Download, RotateCcw, FileText, Briefcase } from "lucide-react";
import Card, { CardHeader } from "../components/Card";
import RadialGauge from "../components/RadialGauge";
import StepIndicator from "../components/StepIndicator";
import ProgressBar from "../components/ProgressBar";
import { SkillTagGrid } from "../components/SkillTag";
import RecommendationsList from "../components/RecommendationsList";
import ScoreBreakdownChart from "../components/ScoreBreakdownChart";
import SkillsDonut from "../components/SkillsDonut";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import { getAnalysisById } from "../api/endpoints";
import ATSDetailsPanel, { JobAnalysisPanel, MLMatchPanel } from "../components/AnalysisDetailsPanels";
import { useAnalysis } from "../context/AnalysisContext";

function scoreVerdict(score) {
  if (score >= 85) return { label: "Excellent", tone: "signal" };
  if (score >= 70) return { label: "Strong", tone: "signal" };
  if (score >= 50) return { label: "Needs Work", tone: "amber" };
  return { label: "At Risk", tone: "rose" };
}

export default function ResultsDashboard() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { result, resumeFilename, jobTitle, company, reset, setResult } = useAnalysis();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Allow deep-linking to a past analysis via /results?id=...
  useEffect(() => {
    const analysisId = searchParams.get("id");
    if (analysisId && !result) {
      setIsLoading(true);
      getAnalysisById(analysisId)
        .then(setResult)
        .catch((err) => setError(err.friendlyMessage || "Couldn't load that analysis."))
        .finally(() => setIsLoading(false));
    }
  }, [searchParams, result, setResult]);

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader message="Loading analysis…" size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-xl px-4 py-20">
        <ErrorBanner message={error} />
        <button
          onClick={() => navigate("/upload")}
          className="mt-6 inline-flex items-center gap-2 rounded-md bg-signal-500 px-5 py-2.5 font-display text-sm font-semibold text-ink-950 hover:bg-signal-400"
        >
          Start a new analysis
        </button>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="mx-auto max-w-xl px-4 py-24 text-center">
        <FileText className="mx-auto mb-4 h-10 w-10 text-ink-500" />
        <h1 className="font-display text-xl font-semibold text-ink-100">
          No results yet
        </h1>
        <p className="mt-2 font-body text-sm text-ink-300">
          Run an analysis first — upload a resume and a job description to
          generate a diagnostic.
        </p>
        <button
          onClick={() => navigate("/upload")}
          className="mt-6 inline-flex items-center gap-2 rounded-md bg-signal-500 px-5 py-2.5 font-display text-sm font-semibold text-ink-950 hover:bg-signal-400"
        >
          Start analysis
        </button>
      </div>
    );
  }

  const {
    ats_score = 0,
    match_score = 0,
    ml_score = 0,
    skills_found = [],
    missing_skills = [],
    recommendations = [],
    score_breakdown,
    job_analysis,
    ats_details,
    match_details,
    ml_details,
    resume_filename: resultResumeFilename,
    job_title: resultJobTitle,
    company: resultCompany,
  } = result;

  const displayFilename = resumeFilename || resultResumeFilename;
  const displayJobTitle = jobTitle || resultJobTitle;
  const displayCompany = company || resultCompany;

  const atsVerdict = scoreVerdict(ats_score);
  const matchVerdict = scoreVerdict(match_score);
  const mlVerdict = scoreVerdict(ml_score);

  const handleStartOver = () => {
    reset();
    navigate("/upload");
  };

  const handleExport = () => {
    window.print();
  };

  return (
    <div className="grid-texture min-h-[calc(100vh-4rem)] pb-20">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <StepIndicator current="results" />

        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
              Diagnostic Complete
            </p>
            <h1 className="font-display text-3xl font-bold text-ink-100">
              Results Dashboard
            </h1>
            <div className="mt-2 flex flex-wrap items-center gap-4 text-ink-400">
              {displayFilename && (
                <span className="inline-flex items-center gap-1.5 font-mono text-[12px]">
                  <FileText className="h-3.5 w-3.5" /> {displayFilename}
                </span>
              )}
              {displayJobTitle && (
                <span className="inline-flex items-center gap-1.5 font-mono text-[12px]">
                  <Briefcase className="h-3.5 w-3.5" /> {displayJobTitle}
                  {displayCompany ? ` @ ${displayCompany}` : ""}
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleExport}
              className="inline-flex items-center gap-2 rounded-md border border-ink-600 px-4 py-2.5 font-display text-[13px] font-semibold text-ink-200 transition-colors hover:border-ink-400"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              onClick={handleStartOver}
              className="inline-flex items-center gap-2 rounded-md bg-signal-500 px-4 py-2.5 font-display text-[13px] font-semibold text-ink-950 transition-colors hover:bg-signal-400"
            >
              <RotateCcw className="h-4 w-4" />
              New Analysis
            </button>
          </div>
        </div>

        {/* Top scores row */}
        <div className="mb-6 grid gap-5 lg:grid-cols-3">
          <Card glow>
            <div className="flex flex-col items-center gap-5">
              <RadialGauge score={ats_score} label="ATS Score" sublabel={atsVerdict.label} />
              <p className="text-center font-body text-[13px] leading-relaxed text-ink-300">
                How reliably an Applicant Tracking System can parse your
                resume's structure, headers, and contact details.
              </p>
            </div>
          </Card>
          <Card glow>
            <div className="flex flex-col items-center gap-5">
              <RadialGauge score={match_score} label="Match Score" sublabel={matchVerdict.label} toneOverride={match_score >= 75 ? "signal" : "cyan"} />
              <p className="text-center font-body text-[13px] leading-relaxed text-ink-300">
                Skill keyword overlap between your resume and this job
                description's extracted requirements.
              </p>
            </div>
          </Card>
          <Card glow>
            <div className="flex flex-col items-center gap-5">
              <RadialGauge score={ml_score} label="ML Score" sublabel={mlVerdict.label} toneOverride="cyan" />
              <p className="text-center font-body text-[13px] leading-relaxed text-ink-300">
                TF-IDF cosine similarity — how semantically close your resume
                text is to the job description.
              </p>
            </div>
          </Card>
        </div>

        {/* Score breakdown + skills donut */}
        <div className="mb-6 grid gap-5 lg:grid-cols-3">
          {score_breakdown && (
            <Card className="lg:col-span-2">
              <CardHeader eyebrow="Diagnostic Breakdown" title="Where points were gained or lost" />
              <ScoreBreakdownChart breakdown={score_breakdown} />
            </Card>
          )}
          <Card>
            <CardHeader eyebrow="Coverage" title="Skill Match Ratio" />
            <SkillsDonut foundCount={skills_found.length} missingCount={missing_skills.length} />
            <div className="mt-4 flex justify-center gap-5">
              <span className="flex items-center gap-1.5 font-mono text-[11px] text-ink-300">
                <span className="h-2 w-2 rounded-full bg-signal-500" /> Found ({skills_found.length})
              </span>
              <span className="flex items-center gap-1.5 font-mono text-[11px] text-ink-300">
                <span className="h-2 w-2 rounded-full bg-rose-signal" /> Missing ({missing_skills.length})
              </span>
            </div>
          </Card>
        </div>

        {/* Skills found / missing */}
        <div className="mb-6 grid gap-5 sm:grid-cols-2">
          <Card>
            <CardHeader eyebrow={`${skills_found.length} Matched`} title="Skills Found" />
            <SkillTagGrid skills={skills_found} variant="found" />
          </Card>
          <Card>
            <CardHeader eyebrow={`${missing_skills.length} Gaps`} title="Missing Skills" />
            <SkillTagGrid skills={missing_skills} variant="missing" />
          </Card>
        </div>

        {/* Recommendations */}
        <Card className="mb-6">
          <CardHeader eyebrow="Prioritized" title="Recommendations" />
          <RecommendationsList recommendations={recommendations} />
        </Card>

        {job_analysis && (
          <Card className="mb-6">
            <CardHeader eyebrow="POST /analyze-job" title="Job Requirements Breakdown" />
            <JobAnalysisPanel jobAnalysis={job_analysis} />
          </Card>
        )}

        {ats_details && (
          <Card className="mb-6">
            <CardHeader eyebrow="POST /ats-score" title="ATS Section Details" />
            <ATSDetailsPanel atsDetails={ats_details} />
          </Card>
        )}

        {(match_details || ml_details) && (
          <Card>
            <CardHeader eyebrow="Job Matching APIs" title="Match & ML Endpoints" />
            <MLMatchPanel matchDetails={match_details} mlDetails={ml_details} />
          </Card>
        )}
      </div>
    </div>
  );
}
