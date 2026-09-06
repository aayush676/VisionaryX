import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { getDigitalTwin } from "../api/digitalTwin";
import GlassCard from "../components/ui/GlassCard";
import StatTile from "../components/ui/StatTile";
import Loader from "../components/ui/Loader";
import TwinStateBadge from "../components/ui/TwinStateBadge";

const STATE_ORB_COLORS = {
  burnout: ["#ff3b5c", "#7a0d24"],
  distracted: ["#ffb020", "#7a4c00"],
  nominal: ["#38bdf8", "#0d3a5c"],
  focused: ["#00f6ff", "#053b47"],
  elite_performer: ["#9b5cff", "#2f0d59"],
};

function clamp(value, max) {
  return Math.min(100, Math.max(0, (value / max) * 100));
}

export default function DigitalTwin() {
  const { data: twin, isLoading } = useQuery({ queryKey: ["digital-twin"], queryFn: getDigitalTwin });

  if (isLoading) return <Loader label="Rendering Digital Twin" />;
  const m = twin.metrics;
  const [glowFrom, glowTo] = STATE_ORB_COLORS[twin.state] || STATE_ORB_COLORS.nominal;

  const radarData = [
    { metric: "Productivity", value: m.productivity },
    { metric: "Focus", value: m.focus },
    { metric: "Fitness", value: m.fitness },
    { metric: "Consistency", value: m.consistency },
    { metric: "Emotional Balance", value: m.emotional_state },
    { metric: "Sleep Quality", value: clamp(m.sleep_hours, 9) },
    { metric: "Screen Discipline", value: 100 - clamp(m.screen_time, 12) },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Digital Twin</h2>
        <p className="text-sm text-white/50">A living model of you, rebuilt from your last 14 days of behavior.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[320px_1fr]">
        <GlassCard className="flex flex-col items-center justify-center gap-6 py-10">
          <motion.div
            animate={{ boxShadow: [`0 0 40px 10px ${glowFrom}55`, `0 0 70px 20px ${glowFrom}88`, `0 0 40px 10px ${glowFrom}55`] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="flex h-44 w-44 items-center justify-center rounded-full"
            style={{ background: `radial-gradient(circle at 35% 30%, ${glowFrom}, ${glowTo})` }}
          >
            <motion.div
              animate={{ scale: [1, 1.06, 1] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
              className="h-24 w-24 rounded-full bg-white/10 backdrop-blur-sm"
            />
          </motion.div>
          <TwinStateBadge state={twin.state} />
          <p className="max-w-xs text-center text-xs text-white/50">
            Last synced {new Date(twin.updated_at).toLocaleString()}
          </p>
        </GlassCard>

        <GlassCard>
          <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">
            Behavioral Profile
          </h3>
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={radarData} outerRadius="75%">
              <PolarGrid stroke="rgba(255,255,255,0.12)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }} />
              <Radar name="You" dataKey="value" stroke="#00f6ff" fill="#00f6ff" fillOpacity={0.28} />
            </RadarChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatTile label="Study Hours / day" value={m.study_hours} color="cyan" />
        <StatTile label="Sleep Hours / day" value={m.sleep_hours} color="violet" />
        <StatTile label="Screen Time / day" value={m.screen_time} suffix="h" color="amber" />
        <StatTile label="Fitness" value={m.fitness} suffix="%" color="green" />
      </div>
    </div>
  );
}
