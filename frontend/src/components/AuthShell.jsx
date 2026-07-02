import { ShieldCheck, Sparkles, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function AuthShell({ eyebrow, title, description, children, footerLink, footerText }) {
  return (
    <div className="grid-texture relative min-h-screen overflow-hidden bg-ink-950">
      <div className="hero-orb hero-orb--primary -left-24 top-0 h-[28rem] w-[28rem] opacity-40" />
      <div className="hero-orb hero-orb--secondary right-0 bottom-0 h-80 w-80 opacity-30" />
      <div className="relative mx-auto grid min-h-screen max-w-7xl items-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8">
        <section className="animate-tick max-w-xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-signal-500/25 bg-signal-500/10 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-wider text-signal-500">
            <ShieldCheck className="h-3.5 w-3.5" />
            Secure workspace
          </div>
          <h1 className="font-display text-4xl font-bold leading-[1.05] tracking-tight text-ink-100 sm:text-5xl">
            {title}
          </h1>
          <p className="mt-5 max-w-lg font-body text-base leading-relaxed text-ink-300 sm:text-lg">
            {description}
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            {[
              "JWT-protected upload, analysis, and history flows",
              "Secure token persistence in the browser",
              "Fast resume-to-job diagnostics after sign-in",
              "Switch between login and signup without losing context",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-ink-700/70 bg-ink-900/55 p-4 shadow-[var(--card-shadow)] backdrop-blur-sm">
                <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg border border-signal-500/20 bg-signal-500/10 text-signal-500">
                  <Sparkles className="h-4 w-4" />
                </div>
                <p className="font-body text-[13px] leading-relaxed text-ink-200">{item}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="animate-float">
          <div className="mx-auto w-full max-w-md rounded-3xl border border-ink-700/70 bg-ink-900/80 p-6 shadow-[var(--card-shadow)] backdrop-blur-xl sm:p-8">
            <div className="mb-6">
              <p className="font-mono text-[11px] uppercase tracking-wider text-signal-500">{eyebrow}</p>
              <h2 className="mt-2 font-display text-2xl font-semibold text-ink-100">{title}</h2>
              <p className="mt-2 font-body text-sm leading-relaxed text-ink-300">{description}</p>
            </div>
            {children}
            {footerLink && footerText && (
              <div className="mt-6 border-t border-ink-700/60 pt-5 text-center font-body text-sm text-ink-300">
                {footerText}{" "}
                <Link to={footerLink.to} className="inline-flex items-center gap-1 font-semibold text-signal-500 hover:text-signal-400">
                  {footerLink.label}
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}