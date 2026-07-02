import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Lock, Mail } from "lucide-react";
import AuthShell from "../components/AuthShell";
import ErrorBanner from "../components/ErrorBanner";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const nextPath = location.state?.from?.pathname || "/";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await login({ email, password });
      navigate(nextPath, { replace: true });
    } catch (err) {
      setError(err.friendlyMessage || "Login failed. Check your credentials and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthShell
      eyebrow="Auth / Login"
      title="Sign in to your resume workspace"
      description="Access protected resume uploads, ATS scoring, job matching, and history under one JWT-secured session."
      footerText="Need an account?"
      footerLink={{ to: "/signup", label: "Create one" }}
    >
      {error && <div className="mb-4"><ErrorBanner message={error} onDismiss={() => setError(null)} /></div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-ink-400">
            Email
          </label>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-500" />
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              className="w-full rounded-xl border border-ink-600 bg-ink-800/80 py-3 pl-10 pr-3.5 font-body text-sm text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
              placeholder="you@example.com"
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-ink-400">
            Password
          </label>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-500" />
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              className="w-full rounded-xl border border-ink-600 bg-ink-800/80 py-3 pl-10 pr-3.5 font-body text-sm text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
              placeholder="Your password"
              required
            />
          </div>
        </div>

        <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-3.5 disabled:cursor-not-allowed disabled:opacity-60">
          {isSubmitting ? "Signing in…" : "Sign In"}
          <ArrowRight className="h-4 w-4" />
        </button>
      </form>
      <p className="mt-5 text-center font-mono text-[11px] uppercase tracking-wider text-ink-500">
        Protected APIs require a bearer token.
      </p>
    </AuthShell>
  );
}