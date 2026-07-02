import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <p className="font-mono text-5xl font-bold text-ink-700">404</p>
      <h1 className="mt-4 font-display text-xl font-semibold text-ink-100">
        This page isn't in the system.
      </h1>
      <p className="mt-2 font-body text-sm text-ink-300">
        The route you're looking for doesn't exist.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex items-center gap-2 rounded-md bg-signal-500 px-5 py-2.5 font-display text-sm font-semibold text-ink-950 hover:bg-signal-400"
      >
        Back to Home
      </Link>
    </div>
  );
}
