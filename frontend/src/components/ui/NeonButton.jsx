import { motion } from "framer-motion";

const VARIANTS = {
  cyan: "border-cyan-400/50 text-cyan-300 hover:shadow-[0_0_20px_-2px_rgba(0,246,255,0.6)] hover:border-cyan-300",
  magenta: "border-fuchsia-400/50 text-fuchsia-300 hover:shadow-[0_0_20px_-2px_rgba(255,46,196,0.6)] hover:border-fuchsia-300",
  violet: "border-violet-400/50 text-violet-300 hover:shadow-[0_0_20px_-2px_rgba(155,92,255,0.6)] hover:border-violet-300",
  ghost: "border-white/10 text-white/70 hover:border-white/30 hover:text-white",
  danger: "border-red-400/50 text-red-300 hover:shadow-[0_0_20px_-2px_rgba(255,59,92,0.6)] hover:border-red-300",
};

export default function NeonButton({
  children,
  variant = "cyan",
  className = "",
  type = "button",
  disabled = false,
  ...props
}) {
  return (
    <motion.button
      type={type}
      disabled={disabled}
      whileTap={{ scale: disabled ? 1 : 0.96 }}
      className={`neon-button rounded-xl border bg-white/5 px-5 py-2.5 text-sm font-semibold uppercase tracking-wider backdrop-blur-md disabled:cursor-not-allowed disabled:opacity-40 ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  );
}
