import { AlertTriangle, X } from "lucide-react";

export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="flex items-start gap-3 rounded-lg border border-rose-signal/30 bg-rose-signal/10 px-4 py-3">
      <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-rose-signal" />
      <p className="flex-1 font-body text-[13px] text-rose-signal/90">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="text-rose-signal/70 hover:text-rose-signal"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
