import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { compareLifePaths, runSimulation, runWhatIf } from "../api/simulations";
import GlassCard from "../components/ui/GlassCard";
import NeonButton from "../components/ui/NeonButton";
import StatTile from "../components/ui/StatTile";
import Loader from "../components/ui/Loader";
import AdjustmentSliders, { EMPTY_ADJUSTMENTS } from "../components/ui/AdjustmentSliders";

const HORIZONS = [
  { value: "1m", label: "1 Month" },
  { value: "3m", label: "3 Months" },
  { value: "6m", label: "6 Months" },
  { value: "12m", label: "12 Months" },
];

const TABS = ["Future Simulation", "What-If Engine", "Life Path Comparison"];

function HorizonPicker({ horizon, setHorizon }) {
  return (
    <div className="flex gap-2">
      {HORIZONS.map((h) => (
        <button
          key={h.value}
          onClick={() => setHorizon(h.value)}
          className={`rounded-full border px-4 py-1.5 text-xs font-semibold uppercase tracking-wider transition-colors ${
            horizon === h.value
              ? "border-cyan-400/60 bg-cyan-400/10 text-cyan-300"
              : "border-white/10 text-white/50 hover:border-white/30"
          }`}
        >
          {h.label}
        </button>
      ))}
    </div>
  );
}

function OutputTiles({ outputs }) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
      <StatTile label="Career Readiness" value={outputs.career_readiness} suffix="%" color="cyan" />
      <StatTile label="Burnout Risk" value={outputs.burnout_risk} suffix="%" color="red" />
      <StatTile label="Goal Achievement" value={outputs.goal_achievement_probability} suffix="%" color="green" />
      <StatTile label="Learning Growth" value={outputs.learning_growth} suffix="%" color="violet" />
      <StatTile label="Productivity" value={outputs.productivity_forecast} suffix="%" color="amber" />
    </div>
  );
}

function TimelineChart({ timeline, lines }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={timeline}>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="label" stroke="rgba(255,255,255,0.4)" fontSize={11} />
        <YAxis stroke="rgba(255,255,255,0.4)" fontSize={11} domain={[0, 100]} />
        <Tooltip contentStyle={{ background: "#10132a", border: "1px solid rgba(0,246,255,0.2)", borderRadius: 12 }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {lines.map((l) => (
          <Line key={l.dataKey} type="monotone" dataKey={l.dataKey} stroke={l.color} strokeWidth={2} dot={false} name={l.name} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

function FutureSimulationTab() {
  const [horizon, setHorizon] = useState("3m");
  const mutation = useMutation({ mutationFn: () => runSimulation(horizon) });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <HorizonPicker horizon={horizon} setHorizon={setHorizon} />
        <NeonButton onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          {mutation.isPending ? "Simulating..." : "Run Simulation"}
        </NeonButton>
      </div>

      {mutation.isPending && <Loader label="Projecting your future self" />}

      {mutation.data && (
        <>
          <OutputTiles outputs={mutation.data.outputs} />
          <GlassCard>
            <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">Timeline</h3>
            <TimelineChart
              timeline={mutation.data.timeline}
              lines={[
                { dataKey: "productivity", color: "#00f6ff", name: "Productivity" },
                { dataKey: "burnout_risk", color: "#ff3b5c", name: "Burnout Risk" },
                { dataKey: "growth", color: "#39ff9d", name: "Growth" },
              ]}
            />
          </GlassCard>
        </>
      )}
    </div>
  );
}

function WhatIfTab() {
  const [horizon, setHorizon] = useState("3m");
  const [adjustments, setAdjustments] = useState(EMPTY_ADJUSTMENTS);
  const mutation = useMutation({ mutationFn: () => runWhatIf(horizon, adjustments) });

  const merged =
    mutation.data &&
    mutation.data.baseline.timeline.map((point, i) => ({
      label: point.label,
      baseline_productivity: point.productivity,
      whatif_productivity: mutation.data.what_if.timeline[i].productivity,
      baseline_burnout: point.burnout_risk,
      whatif_burnout: mutation.data.what_if.timeline[i].burnout_risk,
    }));

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[320px_1fr]">
        <GlassCard hover={false} className="flex flex-col gap-4">
          <HorizonPicker horizon={horizon} setHorizon={setHorizon} />
          <AdjustmentSliders value={adjustments} onChange={setAdjustments} />
          <NeonButton onClick={() => mutation.mutate()} disabled={mutation.isPending} variant="magenta">
            {mutation.isPending ? "Comparing..." : "Run What-If"}
          </NeonButton>
        </GlassCard>

        <div className="flex flex-col gap-6">
          {mutation.isPending && <Loader label="Recomputing future outcomes" />}

          {mutation.data && (
            <>
              <div>
                <p className="mb-2 text-xs uppercase tracking-widest text-white/40">Baseline</p>
                <OutputTiles outputs={mutation.data.baseline.outputs} />
              </div>
              <div>
                <p className="mb-2 text-xs uppercase tracking-widest text-cyan-300">Adjusted (What-If)</p>
                <OutputTiles outputs={mutation.data.what_if.outputs} />
              </div>
              <GlassCard>
                <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">
                  Productivity &amp; Burnout: Baseline vs What-If
                </h3>
                <TimelineChart
                  timeline={merged}
                  lines={[
                    { dataKey: "baseline_productivity", color: "rgba(0,246,255,0.4)", name: "Baseline Productivity" },
                    { dataKey: "whatif_productivity", color: "#00f6ff", name: "What-If Productivity" },
                    { dataKey: "baseline_burnout", color: "rgba(255,59,92,0.4)", name: "Baseline Burnout" },
                    { dataKey: "whatif_burnout", color: "#ff3b5c", name: "What-If Burnout" },
                  ]}
                />
              </GlassCard>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function LifePathTab() {
  const [horizon, setHorizon] = useState("6m");
  const [paths, setPaths] = useState([
    { label: "Consistent Routine", adjustments: { ...EMPTY_ADJUSTMENTS, study_hours_delta: 2, consistency_delta: 20, sleep_hours_delta: 1 } },
    { label: "Inconsistent Routine", adjustments: { ...EMPTY_ADJUSTMENTS, screen_time_delta: 2, consistency_delta: -20 } },
  ]);

  const mutation = useMutation({
    mutationFn: () =>
      compareLifePaths(horizon, paths.map((p) => p.adjustments), paths.map((p) => p.label)),
  });

  const updatePath = (index, updates) => {
    setPaths((prev) => prev.map((p, i) => (i === index ? { ...p, ...updates } : p)));
  };

  const addPath = () => {
    if (paths.length >= 4) return;
    setPaths((prev) => [...prev, { label: `Path ${String.fromCharCode(65 + prev.length)}`, adjustments: { ...EMPTY_ADJUSTMENTS } }]);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <HorizonPicker horizon={horizon} setHorizon={setHorizon} />
        <div className="flex gap-3">
          <NeonButton variant="ghost" onClick={addPath} disabled={paths.length >= 4}>
            + Add Path
          </NeonButton>
          <NeonButton variant="violet" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending ? "Comparing..." : "Compare Paths"}
          </NeonButton>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {paths.map((path, i) => (
          <GlassCard key={i} hover={false} className="flex flex-col gap-3">
            <input
              value={path.label}
              onChange={(e) => updatePath(i, { label: e.target.value })}
              className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm font-bold outline-none focus:border-cyan-400/60"
            />
            <AdjustmentSliders value={path.adjustments} onChange={(adj) => updatePath(i, { adjustments: adj })} />
          </GlassCard>
        ))}
      </div>

      {mutation.isPending && <Loader label="Simulating alternate timelines" />}

      {mutation.data && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {mutation.data.paths.map((result) => (
            <GlassCard key={result.label} className="flex flex-col gap-3">
              <h4 className="font-display text-sm font-bold text-cyan-300">{result.label}</h4>
              <div className="flex flex-col gap-2 text-sm">
                <Row label="Career Readiness" value={result.outputs.career_readiness} />
                <Row label="Burnout Risk" value={result.outputs.burnout_risk} />
                <Row label="Goal Achievement" value={result.outputs.goal_achievement_probability} />
                <Row label="Growth" value={result.outputs.learning_growth} />
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-white/5 pb-1">
      <span className="text-white/50">{label}</span>
      <span className="font-bold text-white">{value}%</span>
    </div>
  );
}

export default function Simulations() {
  const [tab, setTab] = useState(TABS[0]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Future Simulation</h2>
        <p className="text-sm text-white/50">
          Probable outcomes, not prophecies — powered by your Digital Twin and behavioral trends.
        </p>
      </div>

      <div className="flex gap-2 border-b border-white/10 pb-2">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-t-lg px-4 py-2 text-sm font-semibold transition-colors ${
              tab === t ? "bg-white/10 text-cyan-300" : "text-white/50 hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Future Simulation" && <FutureSimulationTab />}
      {tab === "What-If Engine" && <WhatIfTab />}
      {tab === "Life Path Comparison" && <LifePathTab />}
    </div>
  );
}
