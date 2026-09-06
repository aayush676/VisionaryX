import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import ParticleField from "../components/ui/ParticleField";
import GlassCard from "../components/ui/GlassCard";
import NeonButton from "../components/ui/NeonButton";
import { IconTwin, IconSimulate, IconChat, IconAnalytics } from "../components/Icons";

const FEATURES = [
  { icon: IconTwin, title: "Digital Twin Engine", desc: "A living model of you that evolves with every habit you log." },
  { icon: IconSimulate, title: "Future Simulation", desc: "Probable outcomes across 1, 3, 6 and 12 months — not prophecies." },
  { icon: IconChat, title: "Future Self Chatbot", desc: "A mentor grounded in your real goals, memory, and behavior." },
  { icon: IconAnalytics, title: "Decision Intelligence", desc: "What-If simulations and life-path comparisons, side by side." },
];

export default function Landing() {
  return (
    <div className="relative min-h-screen">
      <div className="app-background" />
      <div className="grid-overlay" />
      <ParticleField count={90} />

      <header className="flex items-center justify-between px-8 py-6">
        <h1 className="font-display text-xl font-black text-glow-cyan">
          VISIONARY<span className="text-glow-magenta">X</span>
        </h1>
        <div className="flex gap-3">
          <Link to="/login">
            <NeonButton variant="ghost">Log In</NeonButton>
          </Link>
          <Link to="/signup">
            <NeonButton variant="cyan">Get Started</NeonButton>
          </Link>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col items-center px-6 pb-24 pt-16 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="font-display text-4xl font-black leading-tight md:text-6xl"
        >
          Predict Possibilities.
          <br />
          <span className="text-glow-cyan">Shape Reality.</span>
        </motion.h2>
        <p className="mt-6 max-w-2xl text-white/60">
          VisionaryX is an AI-powered Future Self Decision Simulator and Digital Twin platform. It analyzes your
          habits, emotions, and goals to simulate probable futures — so you can make better decisions today.
        </p>
        <div className="mt-8 flex gap-4">
          <Link to="/signup">
            <NeonButton variant="magenta" className="px-8 py-3">
              Build Your Digital Twin
            </NeonButton>
          </Link>
        </div>

        <div className="mt-20 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <GlassCard key={title} className="flex flex-col items-center gap-3 text-center">
              <div className="rounded-full border border-cyan-400/30 p-3 text-cyan-300">
                <Icon width={26} height={26} />
              </div>
              <h3 className="font-display text-sm font-bold">{title}</h3>
              <p className="text-xs text-white/50">{desc}</p>
            </GlassCard>
          ))}
        </div>
      </main>
    </div>
  );
}
