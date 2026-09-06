import { Outlet } from "react-router-dom";
import ParticleField from "../ui/ParticleField";

export default function AuthLayout() {
  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <div className="app-background" />
      <div className="grid-overlay" />
      <ParticleField count={70} />

      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="font-display text-3xl font-black text-glow-cyan">
            VISIONARY<span className="text-glow-magenta">X</span>
          </h1>
          <p className="mt-2 text-xs uppercase tracking-[0.3em] text-white/40">
            Predict Possibilities. Shape Reality.
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
