import { Link } from "react-router-dom";
import NeonButton from "../components/ui/NeonButton";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <div className="app-background" />
      <h1 className="font-display text-glow-magenta text-6xl font-black">404</h1>
      <p className="text-white/60">This timeline doesn't exist.</p>
      <Link to="/">
        <NeonButton>Return Home</NeonButton>
      </Link>
    </div>
  );
}
