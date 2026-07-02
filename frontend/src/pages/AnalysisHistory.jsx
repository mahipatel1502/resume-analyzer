import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { History, ExternalLink, Trash2 } from "lucide-react";
import Card, { CardHeader } from "../components/Card";
import RadialGauge from "../components/RadialGauge";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import { getAnalysisHistory, deleteResume } from "../api/endpoints";

export default function AnalysisHistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadHistory = () => {
    setIsLoading(true);
    setError(null);
    getAnalysisHistory()
      .then((data) => setItems(data.items || []))
      .catch((err) => setError(err.friendlyMessage || "Couldn't load analysis history."))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDeleteResume = async (resumeId, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm("Delete this resume and all related analyses?")) return;
    setDeletingId(resumeId);
    try {
      await deleteResume(resumeId);
      loadHistory();
    } catch (err) {
      setError(err.friendlyMessage || "Couldn't delete resume.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="grid-texture min-h-[calc(100vh-4rem)] pb-20">
      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-8">
          <p className="mb-2 font-mono text-[11px] uppercase tracking-wider text-signal-500">
            GET /resume/history
          </p>
          <h1 className="font-display text-3xl font-bold text-ink-100">Analysis History</h1>
          <p className="mt-2 font-body text-sm text-ink-300">
            Past diagnostics saved on the server. Click any row to reopen results.
          </p>
        </div>

        {error && (
          <div className="mb-6">
            <ErrorBanner message={error} onDismiss={() => setError(null)} />
          </div>
        )}

        {isLoading ? (
          <Card>
            <Loader message="Loading history…" />
          </Card>
        ) : items.length === 0 ? (
          <Card className="text-center py-12">
            <History className="mx-auto mb-4 h-10 w-10 text-ink-500" />
            <p className="font-body text-sm text-ink-300">No analyses yet. Run your first diagnostic.</p>
            <Link to="/upload" className="mt-4 inline-block rounded-md bg-signal-500 px-5 py-2.5 font-display text-sm font-semibold text-ink-950 hover:bg-signal-400">
              Start analysis
            </Link>
          </Card>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div
                key={item.analysis_id}
                role="button"
                tabIndex={0}
                onClick={() => navigate(`/results?id=${item.analysis_id}`)}
                onKeyDown={(e) => e.key === "Enter" && navigate(`/results?id=${item.analysis_id}`)}
              >
              <Card className="cursor-pointer transition-colors hover:border-ink-500">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0 flex-1">
                    <CardHeader
                      eyebrow={new Date(item.created_at).toLocaleString()}
                      title={item.job_title || "Untitled role"}
                    />
                    <p className="font-mono text-[12px] text-ink-400">
                      {item.resume_filename}
                      {item.company ? ` · ${item.company}` : ""}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <RadialGauge score={item.ats_score} label="ATS" size={88} />
                    <RadialGauge score={item.match_score} label="Match" size={88} toneOverride="cyan" />
                    <RadialGauge score={item.ml_score || 0} label="ML" size={88} toneOverride="cyan" />
                    <div className="flex flex-col gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/results?id=${item.analysis_id}`);
                        }}
                        className="inline-flex items-center gap-1.5 rounded-md border border-ink-600 px-3 py-1.5 font-mono text-[11px] text-ink-200 hover:border-ink-400"
                      >
                        <ExternalLink className="h-3.5 w-3.5" /> View
                      </button>
                      <button
                        onClick={(e) => handleDeleteResume(item.resume_id, e)}
                        disabled={deletingId === item.resume_id}
                        className="inline-flex items-center gap-1.5 rounded-md border border-rose-signal/30 px-3 py-1.5 font-mono text-[11px] text-rose-signal hover:bg-rose-signal/10 disabled:opacity-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        {deletingId === item.resume_id ? "Deleting…" : "Delete"}
                      </button>
                    </div>
                  </div>
                </div>
              </Card>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
