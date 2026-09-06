import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createGoal, deleteGoal, listGoals, toggleTask, updateGoal } from "../api/goals";
import GlassCard from "../components/ui/GlassCard";
import FormInput from "../components/ui/FormInput";
import NeonButton from "../components/ui/NeonButton";
import Loader from "../components/ui/Loader";

const CATEGORIES = ["dsa", "placement", "fitness", "project", "learning", "general"];

function GoalCard({ goal, onUpdate, onDelete, onToggleTask }) {
  return (
    <GlassCard className="flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="font-display text-base font-bold">{goal.title}</h4>
          <p className="text-xs uppercase tracking-widest text-white/40">{goal.category}</p>
        </div>
        <span className="rounded-full border border-white/10 px-3 py-1 text-xs capitalize text-white/60">
          {goal.status}
        </span>
      </div>

      {goal.description && <p className="text-sm text-white/60">{goal.description}</p>}

      <div>
        <div className="mb-1 flex justify-between text-xs text-white/40">
          <span>Progress</span>
          <span>{goal.progress}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-500 transition-all"
            style={{ width: `${goal.progress}%` }}
          />
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={goal.progress}
          onChange={(e) => onUpdate(goal.id, { progress: Number(e.target.value) })}
          className="mt-2 w-full accent-cyan-400"
        />
      </div>

      {goal.tasks?.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-xs uppercase tracking-widest text-white/40">Generated Tasks</p>
          {goal.tasks.map((task) => (
            <label key={task.id} className="flex items-center gap-2 text-sm text-white/70">
              <input
                type="checkbox"
                checked={task.is_done}
                onChange={(e) => onToggleTask(goal.id, task.id, e.target.checked)}
                className="accent-cyan-400"
              />
              <span className={task.is_done ? "line-through opacity-50" : ""}>{task.title}</span>
              <span className="ml-auto text-[10px] uppercase text-white/30">{task.frequency}</span>
            </label>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {goal.status === "active" && (
          <>
            <NeonButton variant="cyan" onClick={() => onUpdate(goal.id, { status: "completed" })} className="text-xs">
              Mark Complete
            </NeonButton>
            <NeonButton variant="ghost" onClick={() => onUpdate(goal.id, { status: "abandoned" })} className="text-xs">
              Abandon
            </NeonButton>
          </>
        )}
        <NeonButton variant="danger" onClick={() => onDelete(goal.id)} className="text-xs">
          Delete
        </NeonButton>
      </div>
    </GlassCard>
  );
}

export default function Goals() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", category: "general", target_date: "" });

  const goalsQuery = useQuery({ queryKey: ["goals", "all"], queryFn: () => listGoals() });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["goals"] });

  const createMutation = useMutation({
    mutationFn: () =>
      createGoal({ ...form, target_date: form.target_date ? new Date(form.target_date).toISOString() : null }),
    onSuccess: () => {
      invalidate();
      setShowForm(false);
      setForm({ title: "", description: "", category: "general", target_date: "" });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => updateGoal(id, payload),
    onSuccess: invalidate,
  });

  const deleteMutation = useMutation({ mutationFn: deleteGoal, onSuccess: invalidate });

  const toggleTaskMutation = useMutation({
    mutationFn: ({ goalId, taskId, isDone }) => toggleTask(goalId, taskId, isDone),
    onSuccess: invalidate,
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">Goal Intelligence</h2>
          <p className="text-sm text-white/50">Every goal auto-generates a daily / weekly / monthly roadmap.</p>
        </div>
        <NeonButton onClick={() => setShowForm((s) => !s)}>{showForm ? "Cancel" : "New Goal"}</NeonButton>
      </div>

      {showForm && (
        <GlassCard hover={false}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate();
            }}
            className="grid grid-cols-1 gap-4 md:grid-cols-2"
          >
            <FormInput
              label="Title"
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-medium uppercase tracking-wider text-white/50">Category</span>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white outline-none focus:border-cyan-400/60"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c} className="bg-[#10132a]">
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <FormInput
              label="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
            <FormInput
              label="Target Date"
              type="date"
              value={form.target_date}
              onChange={(e) => setForm({ ...form, target_date: e.target.value })}
            />
            <NeonButton type="submit" disabled={createMutation.isPending} className="md:col-span-2">
              {createMutation.isPending ? "Generating Roadmap..." : "Create Goal"}
            </NeonButton>
          </form>
        </GlassCard>
      )}

      {goalsQuery.isLoading ? (
        <Loader label="Loading goals" />
      ) : goalsQuery.data?.length ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {goalsQuery.data.map((goal) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              onUpdate={(id, payload) => updateMutation.mutate({ id, payload })}
              onDelete={(id) => deleteMutation.mutate(id)}
              onToggleTask={(goalId, taskId, isDone) => toggleTaskMutation.mutate({ goalId, taskId, isDone })}
            />
          ))}
        </div>
      ) : (
        <GlassCard>
          <p className="text-sm text-white/40">No goals yet. Create your first one above.</p>
        </GlassCard>
      )}
    </div>
  );
}
