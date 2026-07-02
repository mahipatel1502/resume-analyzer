import { useEffect, useState } from "react";
import { FileText, RefreshCw, Trash2 } from "lucide-react";
import Card, { CardHeader } from "../components/Card";
import { SkillTagGrid } from "../components/SkillTag";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import {
  getResumeSkills,
  getEducation,
  getExperience,
  getResumeAnalysis,
  reanalyzeResume,
  deleteResume,
  getAtsScore,
} from "../api/endpoints";
import ATSDetailsPanel from "../components/AnalysisDetailsPanels";

export default function ResumeLibrary() {
  const [resumes, setResumes] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [education, setEducation] = useState(null);
  const [experience, setExperience] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [atsDetails, setAtsDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [error, setError] = useState(null);

  const loadResumes = () => {
    setIsLoading(true);
    getResumeSkills()
      .then((data) => {
        const list = data.resumes || [];
        setResumes(list);
        if (list.length > 0 && !selectedId) {
          setSelectedId(list[0].resume_id);
        }
      })
      .catch((err) => setError(err.friendlyMessage || "Couldn't load resumes."))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadResumes();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setIsDetailLoading(true);
    setError(null);
    Promise.all([
      getEducation(selectedId),
      getExperience(selectedId),
      getResumeAnalysis(selectedId),
      getAtsScore(selectedId),
    ])
      .then(([edu, exp, anal, ats]) => {
        setEducation(edu);
        setExperience(exp);
        setAnalysis(anal);
        setAtsDetails(ats);
      })
      .catch((err) => setError(err.friendlyMessage || "Couldn't load resume details."))
      .finally(() => setIsDetailLoading(false));
  }, [selectedId]);

  const handleReanalyze = async () => {
    if (!selectedId) return;
    setIsReanalyzing(true);
    setError(null);
    try {
      const updated = await reanalyzeResume(selectedId);
      setAnalysis(updated);
      const ats = await getAtsScore(selectedId);
      setAtsDetails(ats);
      loadResumes();
    } catch (err) {
      setError(err.friendlyMessage || "Reanalysis failed.");
    } finally {
      setIsReanalyzing(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedId || !window.confirm("Delete this resume permanently?")) return;
    try {
      await deleteResume(selectedId);
      setSelectedId(null);
      setEducation(null);
      setExperience(null);
      setAnalysis(null);
      setAtsDetails(null);
      loadResumes();
    } catch (err) {
      setError(err.friendlyMessage || "Delete failed.");
    }
  };

  const selectedResume = resumes.find((r) => r.resume_id === selectedId);

  return (
    <div className="grid-texture min-h-[calc(100vh-4rem)] pb-20">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-8">
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
            GET /resume-skills · /education · /experience · /resume-analysis
          </p>
          <h1 className="font-display text-3xl font-bold text-ink-100">Resume Library</h1>
          <p className="mt-2 font-body text-sm text-ink-300">
            Browse uploaded resumes, view parsed structure, re-run NLP analysis, or delete.
          </p>
        </div>

        {error && (
          <div className="mb-6">
            <ErrorBanner message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {isLoading ? (
          <Card><Loader message="Loading resumes…" /></Card>
        ) : resumes.length === 0 ? (
          <Card className="py-12 text-center">
            <FileText className="mx-auto mb-4 h-10 w-10 text-ink-500" />
            <p className="font-body text-sm text-ink-300">No resumes uploaded yet.</p>
          </Card>
        ) : (
          <div className="grid gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardHeader eyebrow={`${resumes.length} files`} title="Uploaded Resumes" />
              <ul className="space-y-2">
                {resumes.map((resume) => (
                  <li key={resume.resume_id}>
                    <button
                      onClick={() => setSelectedId(resume.resume_id)}
                      className={`w-full rounded-md border px-3 py-2.5 text-left transition-colors ${
                        selectedId === resume.resume_id
                          ? "border-signal-500/50 bg-signal-500/10"
                          : "border-ink-600 hover:border-ink-400"
                      }`}
                    >
                      <p className="truncate font-body text-sm font-medium text-ink-100">{resume.filename}</p>
                      <p className="font-mono text-[10px] text-ink-500">
                        ID {resume.resume_id} · {resume.extracted_skills?.length || 0} skills
                      </p>
                    </button>
                  </li>
                ))}
              </ul>
            </Card>

            <div className="space-y-5 lg:col-span-2">
              {isDetailLoading ? (
                <Card><Loader message="Loading resume details…" /></Card>
              ) : selectedResume ? (
                <>
                  <Card>
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <CardHeader eyebrow="Selected" title={selectedResume.filename} />
                      <div className="flex gap-2">
                        <button
                          onClick={handleReanalyze}
                          disabled={isReanalyzing}
                          className="inline-flex items-center gap-1.5 rounded-md border border-ink-600 px-3 py-1.5 font-mono text-[11px] text-ink-200 hover:border-ink-400 disabled:opacity-50"
                        >
                          <RefreshCw className={`h-3.5 w-3.5 ${isReanalyzing ? "animate-spin" : ""}`} />
                          POST /reanalyze-resume
                        </button>
                        <button
                          onClick={handleDelete}
                          className="inline-flex items-center gap-1.5 rounded-md border border-rose-signal/30 px-3 py-1.5 font-mono text-[11px] text-rose-signal hover:bg-rose-signal/10"
                        >
                          <Trash2 className="h-3.5 w-3.5" /> DELETE
                        </button>
                      </div>
                    </div>
                    {analysis && (
                      <div className="mt-4">
                        <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-ink-400">Parsed Skills</p>
                        <SkillTagGrid skills={analysis.skills || selectedResume.extracted_skills} variant="found" />
                      </div>
                    )}
                  </Card>

                  <div className="grid gap-5 sm:grid-cols-2">
                    <Card>
                      <CardHeader eyebrow="GET /education" title="Education" />
                      {education?.education?.length > 0 ? (
                        <ul className="space-y-3">
                          {education.education.map((entry, i) => (
                            <li key={i} className="rounded-md border border-ink-600 bg-ink-800/40 p-3">
                              {entry.degree && <p className="font-body text-sm font-medium text-ink-100">{entry.degree}</p>}
                              {entry.university && <p className="font-body text-[13px] text-ink-300">{entry.university}</p>}
                              {entry.graduation_year && <p className="font-mono text-[11px] text-ink-500">{entry.graduation_year}</p>}
                              {entry.raw_text && !entry.degree && <p className="font-body text-[13px] text-ink-300">{entry.raw_text}</p>}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="font-mono text-[12px] text-ink-500">No education entries found.</p>
                      )}
                    </Card>

                    <Card>
                      <CardHeader eyebrow="GET /experience" title="Experience" />
                      {experience?.experience?.length > 0 ? (
                        <ul className="space-y-3">
                          {experience.experience.map((entry, i) => (
                            <li key={i} className="rounded-md border border-ink-600 bg-ink-800/40 p-3">
                              {entry.experience_type && <p className="font-body text-sm font-medium text-ink-100">{entry.experience_type}</p>}
                              {entry.years_of_experience != null && (
                                <p className="font-mono text-[11px] text-ink-500">{entry.years_of_experience} years</p>
                              )}
                              {entry.raw_text && <p className="font-body text-[13px] text-ink-300">{entry.raw_text}</p>}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="font-mono text-[12px] text-ink-500">No experience entries found.</p>
                      )}
                    </Card>
                  </div>

                  {atsDetails && (
                    <Card>
                      <CardHeader eyebrow="POST /ats-score" title="ATS Section Breakdown" />
                      <ATSDetailsPanel atsDetails={atsDetails} />
                    </Card>
                  )}
                </>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
