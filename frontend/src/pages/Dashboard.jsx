import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { getDigitalTwin } from "../api/digitalTwin";
import { listGoals } from "../api/goals";
import { listMemory } from "../api/memory";
import { getAnalyticsHistory, createSnapshot } from "../api/analytics";
import GlassCard from "../components/ui/GlassCard";
import StatTile from "../components/ui/StatTile";
import Loader from "../components/ui/Loader";
import TwinStateBadge from "../components/ui/TwinStateBadge";
import NeonButton from "../components/ui/NeonButton";

export default function Dashboard() {
  const queryClient = useQueryClient();

  const twinQuery = useQuery({ queryKey: ["digital-twin"], queryFn: getDigitalTwin });
  const goalsQuery = useQuery({ queryKey: ["goals", "active"], queryFn: () => listGoals("active") });
  const memoryQuery = useQuery({ queryKey: ["memory"], queryFn: () => listMemory(5) });
  const analyticsQuery = useQuery({ queryKey: ["analytics-history", 30], queryFn: () => getAnalyticsHistory(30) });

  const snapshotMutation = useMutation({
    mutationFn: createSnapshot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analytics-history"] });
      queryClient.invalidateQueries({ queryKey: ["digital-twin"] });
    },
  });

  if (twinQuery.isLoading) return <Loader label="Syncing Digital Twin" />;

  const twin = twinQuery.data;
  const metrics = twin?.metrics;
  const chartData = (analyticsQuery.data || []).map((d) => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    productivity: d.productivity_score,
    growth: d.growth_index,
    burnout: d.burnout_score,
  }));

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">Command Center</h2>
          <p className="text-sm text-white/50">A live snapshot of your Digital Twin and trajectory.</p>
        </div>
        <div className="flex items-center gap-3">
          {twin && <TwinStateBadge state={twin.state} />}
          <NeonButton onClick={() => snapshotMutation.mutate()} disabled={snapshotMutation.isPending} variant="violet">
            {snapshotMutation.isPending ? "Syncing..." : "Refresh Analytics"}
          </NeonButton>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatTile label="Productivity" value={metrics?.productivity ?? 0} suffix="%" color="cyan" />
        <StatTile label="Focus" value={metrics?.focus ?? 0} suffix="%" color="violet" />
        <StatTile label="Consistency" value={metrics?.consistency ?? 0} suffix="%" color="green" />
        <StatTile label="Emotional State" value={metrics?.emotional_state ?? 50} suffix="/100" color="magenta" />
      </div>

      <GlassCard>
        <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">
          Productivity &amp; Growth Trend
        </h3>
        {chartData.length === 0 ? (
          <p className="py-8 text-center text-sm text-white/40">
            No analytics yet — log some habits, then hit "Refresh Analytics".
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={11} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#10132a", border: "1px solid rgba(0,246,255,0.2)", borderRadius: 12 }} />
              <Line type="monotone" dataKey="productivity" stroke="#00f6ff" strokeWidth={2} dot={false} name="Productivity" />
              <Line type="monotone" dataKey="growth" stroke="#39ff9d" strokeWidth={2} dot={false} name="Growth" />
              <Line type="monotone" dataKey="burnout" stroke="#ff3b5c" strokeWidth={2} dot={false} name="Burnout Risk" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </GlassCard>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <GlassCard>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-display text-sm font-bold uppercase tracking-widest text-white/60">Active Goals</h3>
            <Link to="/app/goals" className="text-xs text-cyan-300 hover:underline">
              View all
            </Link>
          </div>
          {goalsQuery.isLoading ? (
            <Loader label="Loading" />
          ) : goalsQuery.data?.length ? (
            <ul className="flex flex-col gap-3">
              {goalsQuery.data.slice(0, 4).map((goal) => (
                <li key={goal.id} className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3">
                  <span className="text-sm">{goal.title}</span>
                  <span className="text-xs font-bold text-cyan-300">{goal.progress}%</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-white/40">No active goals yet. Create one to get a generated roadmap.</p>
          )}
        </GlassCard>

        <GlassCard>
          <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">
            AI Memory Feed
          </h3>
          {memoryQuery.isLoading ? (
            <Loader label="Loading" />
          ) : memoryQuery.data?.length ? (
            <ul className="flex flex-col gap-3">
              {memoryQuery.data.map((m) => (
                <li key={m.id} className="rounded-xl bg-white/5 px-4 py-3 text-sm text-white/70">
                  {m.summary}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-white/40">No memory events yet.</p>
          )}
        </GlassCard>
      </div>
    </div>
  );
}
