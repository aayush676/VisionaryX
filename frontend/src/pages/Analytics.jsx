import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { createSnapshot, getAnalyticsHistory } from "../api/analytics";
import GlassCard from "../components/ui/GlassCard";
import StatTile from "../components/ui/StatTile";
import NeonButton from "../components/ui/NeonButton";
import Loader from "../components/ui/Loader";

const METRIC_LINES = [
  { key: "productivity_score", color: "#00f6ff", name: "Productivity" },
  { key: "focus_score", color: "#9b5cff", name: "Focus" },
  { key: "consistency_score", color: "#39ff9d", name: "Consistency" },
  { key: "burnout_score", color: "#ff3b5c", name: "Burnout" },
  { key: "growth_index", color: "#ffb020", name: "Growth" },
  { key: "career_readiness", color: "#ff2ec4", name: "Career Readiness" },
];

export default function Analytics() {
  const queryClient = useQueryClient();
  const historyQuery = useQuery({ queryKey: ["analytics-history", 90], queryFn: () => getAnalyticsHistory(90) });

  const snapshotMutation = useMutation({
    mutationFn: createSnapshot,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["analytics-history"] }),
  });

  const chartData = (historyQuery.data || []).map((d) => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    ...d,
  }));

  const latest = chartData[chartData.length - 1];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">Analytics Dashboard</h2>
          <p className="text-sm text-white/50">Every score your Digital Twin and simulations are built on.</p>
        </div>
        <NeonButton onClick={() => snapshotMutation.mutate()} disabled={snapshotMutation.isPending}>
          {snapshotMutation.isPending ? "Recomputing..." : "Recompute Today"}
        </NeonButton>
      </div>

      {latest && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
          {METRIC_LINES.map((m) => (
            <StatTile key={m.key} label={m.name} value={latest[m.key]} suffix="%" />
          ))}
        </div>
      )}

      <GlassCard>
        <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">
          Score History
        </h3>
        {historyQuery.isLoading ? (
          <Loader />
        ) : chartData.length === 0 ? (
          <p className="py-8 text-center text-sm text-white/40">
            No analytics yet. Log habits and journal entries, then recompute.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={340}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={11} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#10132a", border: "1px solid rgba(0,246,255,0.2)", borderRadius: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              {METRIC_LINES.map((m) => (
                <Line key={m.key} type="monotone" dataKey={m.key} stroke={m.color} strokeWidth={2} dot={false} name={m.name} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </GlassCard>
    </div>
  );
}
