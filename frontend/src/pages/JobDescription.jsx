import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, ArrowLeft, FileWarning } from "lucide-react";
import Card from "../components/Card";
import StepIndicator from "../components/StepIndicator";
import ErrorBanner from "../components/ErrorBanner";
import Loader from "../components/Loader";
import { submitJobDescription, analyzeResume } from "../api/endpoints";
import { useAnalysis } from "../context/AnalysisContext";

const MIN_DESCRIPTION_LENGTH = 30;

export default function JobDescription() {
  const navigate = useNavigate();
  const { resumeId, setJobDescription, setResult } = useAnalysis();

  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [descriptionText, setDescriptionText] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const charCount = descriptionText.length;
  const isTooShort = charCount > 0 && charCount < MIN_DESCRIPTION_LENGTH;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resumeId) {
      setError("Upload a resume first — we need it to run the comparison.");
      return;
    }
    if (descriptionText.trim().length < MIN_DESCRIPTION_LENGTH) {
      setError(`Add a bit more detail — at least ${MIN_DESCRIPTION_LENGTH} characters helps us extract real requirements.`);
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      const jdData = await submitJobDescription({
        resume_id: resumeId,
        job_title: jobTitle,
        company,
        description_text: descriptionText,
      });
      setJobDescription(jdData.jd_id, { jobTitle, company, descriptionText });

      const result = await analyzeResume({ resumeId, jdId: jdData.jd_id });
      setResult(result);
      navigate("/results");
    } catch (err) {
      setError(err.friendlyMessage || "Couldn't process the job description. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="grid-texture min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 lg:px-8">
        <StepIndicator current="jd" />

        <div className="mb-8 text-center">
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
            Step 2
          </p>
          <h1 className="font-display text-3xl font-bold text-ink-100">
            Paste the job description
          </h1>
          <p className="mt-2 font-body text-sm text-ink-300">
            We'll extract required skills and compare them against your resume.
          </p>
        </div>

        {!resumeId && (
          <div className="mb-6">
            <ErrorBanner
              message={
                <>
                  No resume on file yet.{" "}
                  <button
                    onClick={() => navigate("/upload")}
                    className="underline hover:text-rose-signal"
                  >
                    Upload one first
                  </button>
                  .
                </>
              }
            />
          </div>
        )}

        {isSubmitting ? (
          <Card>
            <Loader message="Comparing resume against job description…" size="lg" />
          </Card>
        ) : (
          <Card>
            {error && (
              <div className="mb-5">
                <ErrorBanner message={error} onDismiss={() => setError(null)} />
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="jobTitle" className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-ink-400">
                    Job Title
                  </label>
                  <input
                    id="jobTitle"
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Machine Learning Engineer"
                    className="w-full rounded-md border border-ink-600 bg-ink-800 px-3.5 py-2.5 font-body text-sm text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label htmlFor="company" className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-ink-400">
                    Company <span className="text-ink-600">(optional)</span>
                  </label>
                  <input
                    id="company"
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="e.g. Acme Corp"
                    className="w-full rounded-md border border-ink-600 bg-ink-800 px-3.5 py-2.5 font-body text-sm text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <div className="mb-1.5 flex items-center justify-between">
                  <label htmlFor="description" className="font-mono text-[11px] uppercase tracking-wider text-ink-400">
                    Job Description
                  </label>
                  <span className={`font-mono text-[11px] ${isTooShort ? "text-amber-signal" : "text-ink-500"}`}>
                    {charCount} chars
                  </span>
                </div>
                <textarea
                  id="description"
                  value={descriptionText}
                  onChange={(e) => setDescriptionText(e.target.value)}
                  rows={12}
                  placeholder="Paste the full job description here, including responsibilities and required qualifications…"
                  className="w-full resize-y rounded-md border border-ink-600 bg-ink-800 px-3.5 py-3 font-body text-sm leading-relaxed text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
                />
                {isTooShort && (
                  <p className="mt-1.5 flex items-center gap-1.5 font-mono text-[11px] text-amber-signal">
                    <FileWarning className="h-3.5 w-3.5" />
                    A bit short — more detail improves match accuracy.
                  </p>
                )}
              </div>

              <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
                <button
                  type="button"
                  onClick={() => navigate("/upload")}
                  className="inline-flex items-center justify-center gap-2 rounded-md border border-ink-600 px-5 py-2.5 font-display text-sm font-semibold text-ink-200 transition-colors hover:border-ink-400"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </button>
                <button
                  type="submit"
                  disabled={!resumeId || isSubmitting}
                  className="btn-primary disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
                >
                  Run Analysis
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  );
}
