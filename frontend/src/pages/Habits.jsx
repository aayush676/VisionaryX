import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { listHabits, logHabit } from "../api/habits";
import GlassCard from "../components/ui/GlassCard";
import FormInput from "../components/ui/FormInput";
import NeonButton from "../components/ui/NeonButton";
import Loader from "../components/ui/Loader";

const DEFAULT_FORM = {
  study_hours: 2,
  sleep_hours: 7,
  screen_time_hours: 4,
  fitness_minutes: 20,
  productivity_score: 60,
  focus_score: 60,
  mood: "neutral",
  notes: "",
};

export default function Habits() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(DEFAULT_FORM);

  const habitsQuery = useQuery({ queryKey: ["habits", 30], queryFn: () => listHabits(30) });

  const logMutation = useMutation({
    mutationFn: () => logHabit(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      queryClient.invalidateQueries({ queryKey: ["digital-twin"] });
      setForm(DEFAULT_FORM);
    },
  });

  const chartData = [...(habitsQuery.data || [])]
    .reverse()
    .map((h) => ({
      date: new Date(h.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      productivity: h.productivity_score,
      focus: h.focus_score,
      sleep: h.sleep_hours,
    }));

  const numberField = (key, label, step = 0.5, max = 24) => (
    <FormInput
      label={label}
      type="number"
      step={step}
      min={0}
      max={max}
      value={form[key]}
      onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })}
    />
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Habit Tracking</h2>
        <p className="text-sm text-white/50">Daily inputs feed your Digital Twin, burnout model, and forecasts.</p>
      </div>

      <GlassCard hover={false}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            logMutation.mutate();
          }}
          className="grid grid-cols-2 gap-4 md:grid-cols-4"
        >
          {numberField("study_hours", "Study Hours")}
          {numberField("sleep_hours", "Sleep Hours")}
          {numberField("screen_time_hours", "Screen Time (h)")}
          {numberField("fitness_minutes", "Fitness (min)", 5, 300)}
          {numberField("productivity_score", "Productivity", 1, 100)}
          {numberField("focus_score", "Focus", 1, 100)}
          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium uppercase tracking-wider text-white/50">Mood</span>
            <select
              value={form.mood}
              onChange={(e) => setForm({ ...form, mood: e.target.value })}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white outline-none focus:border-cyan-400/60"
            >
              {["great", "good", "neutral", "low", "stressed"].map((m) => (
                <option key={m} value={m} className="bg-[#10132a]">
                  {m}
                </option>
              ))}
            </select>
          </label>
          <FormInput label="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <NeonButton type="submit" disabled={logMutation.isPending} className="col-span-2 md:col-span-4">
            {logMutation.isPending ? "Logging..." : "Log Today's Habits"}
          </NeonButton>
        </form>
      </GlassCard>

      <GlassCard>
        <h3 className="font-display mb-4 text-sm font-bold uppercase tracking-widest text-white/60">
          Last 30 Days
        </h3>
        {habitsQuery.isLoading ? (
          <Loader />
        ) : chartData.length === 0 ? (
          <p className="py-8 text-center text-sm text-white/40">No habit logs yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.4)" fontSize={11} />
              <Tooltip contentStyle={{ background: "#10132a", border: "1px solid rgba(0,246,255,0.2)", borderRadius: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="productivity" stroke="#00f6ff" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="focus" stroke="#9b5cff" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="sleep" stroke="#39ff9d" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </GlassCard>
    </div>
  );
}
