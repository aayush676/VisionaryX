export default function FormInput({ label, error, className = "", ...props }) {
  return (
    <label className="flex flex-col gap-1.5">
      {label && <span className="text-xs font-medium uppercase tracking-wider text-white/50">{label}</span>}
      <input
        className={`rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-white/30 outline-none transition-colors focus:border-cyan-400/60 focus:shadow-[0_0_16px_-4px_rgba(0,246,255,0.6)] ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-rose-400">{error}</span>}
    </label>
  );
}
