import GlassCard from "./GlassCard";

const COLOR_MAP = {
  cyan: "text-glow-cyan",
  magenta: "text-glow-magenta",
  violet: "text-glow-violet",
  green: "text-emerald-300",
  amber: "text-amber-300",
  red: "text-rose-300",
};

export default function StatTile({ label, value, suffix = "", color = "cyan", subtext }) {
  return (
    <GlassCard className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-widest text-white/50">{label}</span>
      <span className={`font-display text-3xl font-bold ${COLOR_MAP[color] || COLOR_MAP.cyan}`}>
        {value}
        {suffix}
      </span>
      {subtext && <span className="text-xs text-white/40">{subtext}</span>}
    </GlassCard>
  );
}
