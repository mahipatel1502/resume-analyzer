import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud, FileText, X, ArrowRight, CheckCircle2, RefreshCw } from "lucide-react";
import Card, { CardHeader } from "../components/Card";
import StepIndicator from "../components/StepIndicator";
import ProgressBar from "../components/ProgressBar";
import ErrorBanner from "../components/ErrorBanner";
import { SkillTagGrid } from "../components/SkillTag";
import { uploadResume, getResumeAnalysis, reanalyzeResume, parseResume } from "../api/endpoints";
import { useAnalysis } from "../context/AnalysisContext";

const ACCEPTED_TYPES = [".pdf"];
const MAX_SIZE_MB = 5;

function isAcceptedFile(file) {
  const name = file.name.toLowerCase();
  return ACCEPTED_TYPES.some((ext) => name.endsWith(ext));
}

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error
  const [error, setError] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [resumeId, setResumeId] = useState(null);
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { setResume } = useAnalysis();

  const validateAndSetFile = useCallback((candidate) => {
    if (!candidate) return;
    if (!isAcceptedFile(candidate)) {
      setError("Unsupported file type. Upload a PDF document (.pdf).");
      return;
    }
    if (candidate.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File is too large. Keep it under ${MAX_SIZE_MB}MB.`);
      return;
    }
    setError(null);
    setFile(candidate);
    setStatus("idle");
    setProgress(0);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files?.[0];
      validateAndSetFile(dropped);
    },
    [validateAndSetFile]
  );

  const handleInputChange = (e) => {
    const selected = e.target.files?.[0];
    validateAndSetFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    setError(null);
    setProgress(0);
    try {
      const data = await uploadResume(file, setProgress);
      setResume(data.resume_id, file, data, data.filename);
      setResumeId(data.resume_id);
      const analysis = await getResumeAnalysis(data.resume_id);
      setParsedData(analysis);
      setStatus("success");
    } catch (err) {
      setStatus("error");
      setError(err.friendlyMessage || "Upload failed. Please try again.");
    }
  };

  const handleRemove = () => {
    setFile(null);
    setStatus("idle");
    setProgress(0);
    setError(null);
    setParsedData(null);
    setResumeId(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleReanalyze = async () => {
    if (!resumeId) return;
    setIsReanalyzing(true);
    setError(null);
    try {
      await reanalyzeResume(resumeId);
      const [analysis, parsed] = await Promise.all([
        getResumeAnalysis(resumeId),
        parseResume(resumeId),
      ]);
      setParsedData(analysis);
      setResume(resumeId, file, { ...parsed, parsed_skills: parsed.skills }, parsed.filename);
    } catch (err) {
      setError(err.friendlyMessage || "Reanalysis failed.");
    } finally {
      setIsReanalyzing(false);
    }
  };

  return (
    <div className="grid-texture min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 lg:px-8">
        <StepIndicator current="upload" />

        <div className="mb-8 text-center">
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
            Step 1
          </p>
          <h1 className="font-display text-3xl font-bold text-ink-100">
            Upload your resume
          </h1>
          <p className="mt-2 font-body text-sm text-ink-300">
            PDF only, up to {MAX_SIZE_MB}MB.
          </p>
        </div>

        <Card>
          {error && (
            <div className="mb-5">
              <ErrorBanner message={error} onDismiss={() => setError(null)} />
            </div>
          )}

          {!file ? (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
              className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-16 text-center transition-colors ${
                isDragging
                  ? "border-signal-500 bg-signal-500/5"
                  : "border-ink-600 hover:border-ink-400"
              }`}
            >
              <UploadCloud
                className={`mb-4 h-10 w-10 ${isDragging ? "text-signal-500" : "text-ink-400"}`}
              />
              <p className="font-display text-base font-semibold text-ink-100">
                Drag and drop your resume here
              </p>
              <p className="mt-1 font-body text-[13px] text-ink-400">
                or click to browse files
              </p>
              <input
                ref={inputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleInputChange}
              />
            </div>
          ) : (
            <div className="rounded-lg border border-ink-600 bg-ink-800/60 p-5">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 overflow-hidden">
                  <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md bg-ink-700">
                    <FileText className="h-5 w-5 text-signal-500" />
                  </span>
                  <div className="overflow-hidden">
                    <p className="truncate font-body text-sm font-medium text-ink-100">
                      {file.name}
                    </p>
                    <p className="font-mono text-[11px] text-ink-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                {status !== "uploading" && (
                  <button
                    onClick={handleRemove}
                    aria-label="Remove file"
                    className="flex-shrink-0 text-ink-400 hover:text-rose-signal"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
                {status === "success" && (
                  <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-signal-500" />
                )}
              </div>

              {status === "uploading" && (
                <div className="mt-4">
                  <ProgressBar value={progress} label="Uploading & parsing" tone="signal" />
                </div>
              )}
            </div>
          )}

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
            {file && status !== "success" && (
              <button
                onClick={handleUpload}
                disabled={status === "uploading"}
                className="btn-primary disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                {status === "uploading" ? "Uploading…" : "Upload & Parse"}
              </button>
            )}
            {status === "success" && (
              <button
                onClick={() => navigate("/job-description")}
                className="btn-primary"
              >
                Continue to Job Description
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </Card>

        {status === "success" && parsedData && (
          <Card className="mt-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <CardHeader eyebrow="GET /resume-analysis" title="Parsed Resume Structure" />
              <button
                onClick={handleReanalyze}
                disabled={isReanalyzing}
                className="inline-flex items-center gap-1.5 rounded-md border border-ink-600 px-3 py-1.5 font-mono text-[11px] text-ink-200 hover:border-ink-400 disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isReanalyzing ? "animate-spin" : ""}`} />
                POST /reanalyze-resume
              </button>
            </div>
            <div className="mb-5">
              <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">Skills</p>
              <SkillTagGrid skills={parsedData.skills || []} variant="found" />
            </div>
            {parsedData.education?.length > 0 && (
              <div className="mb-5">
                <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">Education</p>
                <ul className="space-y-2">
                  {parsedData.education.map((e, i) => (
                    <li key={i} className="font-body text-[13px] text-ink-300">
                      {e.degree || e.raw_text}{e.university ? ` — ${e.university}` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {parsedData.experience?.length > 0 && (
              <div>
                <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">Experience</p>
                <ul className="space-y-2">
                  {parsedData.experience.map((e, i) => (
                    <li key={i} className="font-body text-[13px] text-ink-300">
                      {e.experience_type || e.raw_text}
                      {e.years_of_experience != null ? ` (${e.years_of_experience} yrs)` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        )}

        <p className="mt-6 text-center font-mono text-[11px] text-ink-500">
          Your file is parsed for text and structure — it is not stored
          beyond this analysis session.
        </p>
      </div>
    </div>
  );
}
