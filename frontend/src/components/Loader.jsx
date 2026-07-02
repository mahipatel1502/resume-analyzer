export default function Loader({ message = "Processing…", size = "md" }) {
  const dim = size === "lg" ? "h-16 w-16" : "h-10 w-10";
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className={`relative ${dim}`}>
        <div className="absolute inset-0 rounded-full border-2 border-ink-700" />
        <div
          className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-signal-500"
          style={{ filter: "drop-shadow(0 0 6px var(--hero-glow))" }}
        />
      </div>
      <p className="font-mono text-[12px] uppercase tracking-wider text-ink-400">{message}</p>
    </div>
  );
}
