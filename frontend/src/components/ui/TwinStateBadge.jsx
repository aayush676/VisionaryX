const STATE_STYLES = {
  burnout: "bg-rose-500/15 text-rose-300 border-rose-400/40 shadow-[0_0_16px_-4px_rgba(255,59,92,0.7)]",
  distracted: "bg-amber-500/15 text-amber-300 border-amber-400/40 shadow-[0_0_16px_-4px_rgba(255,176,32,0.7)]",
  nominal: "bg-sky-500/15 text-sky-300 border-sky-400/40 shadow-[0_0_16px_-4px_rgba(56,189,248,0.6)]",
  focused: "bg-cyan-500/15 text-cyan-300 border-cyan-400/40 shadow-[0_0_16px_-4px_rgba(0,246,255,0.7)]",
  elite_performer: "bg-violet-500/15 text-violet-300 border-violet-400/40 shadow-[0_0_16px_-4px_rgba(155,92,255,0.8)]",
};

const STATE_LABELS = {
  burnout: "Burnout",
  distracted: "Distracted",
  nominal: "Nominal",
  focused: "Focused",
  elite_performer: "Elite Performer",
};

export default function TwinStateBadge({ state, className = "" }) {
  const style = STATE_STYLES[state] || STATE_STYLES.nominal;
  const label = STATE_LABELS[state] || state;
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 font-display text-sm font-bold uppercase tracking-wider ${style} ${className}`}
    >
      <span className="h-2 w-2 animate-pulse rounded-full bg-current" />
      {label}
    </span>
  );
}
