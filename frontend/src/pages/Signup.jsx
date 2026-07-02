import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, User, Mail, Lock } from "lucide-react";
import AuthShell from "../components/AuthShell";
import ErrorBanner from "../components/ErrorBanner";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await signup({ full_name: fullName, email, password });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.friendlyMessage || "Signup failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthShell
      eyebrow="Auth / Signup"
      title="Create your secure resume analyzer account"
      description="Unlock the full workflow: upload PDFs, compare against roles, and store analysis history behind JWT authentication."
      footerText="Already have an account?"
      footerLink={{ to: "/login", label: "Sign in" }}
    >
      {error && <div className="mb-4"><ErrorBanner message={error} onDismiss={() => setError(null)} /></div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="fullName" className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-ink-400">
            Full name
          </label>
          <div className="relative">
            <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-500" />
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoComplete="name"
              className="w-full rounded-xl border border-ink-600 bg-ink-800/80 py-3 pl-10 pr-3.5 font-body text-sm text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
              placeholder="Your name"
            />
          </div>
        </div>

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
              autoComplete="new-password"
              className="w-full rounded-xl border border-ink-600 bg-ink-800/80 py-3 pl-10 pr-3.5 font-body text-sm text-ink-100 placeholder:text-ink-500 focus:border-signal-500 focus:outline-none"
              placeholder="At least 8 characters"
              required
            />
          </div>
        </div>

        <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-3.5 disabled:cursor-not-allowed disabled:opacity-60">
          {isSubmitting ? "Creating account…" : "Create Account"}
          <ArrowRight className="h-4 w-4" />
        </button>
      </form>
      <p className="mt-5 text-center font-mono text-[11px] uppercase tracking-wider text-ink-500">
        Sign-up immediately issues a JWT for protected routes.
      </p>
    </AuthShell>
  );
}