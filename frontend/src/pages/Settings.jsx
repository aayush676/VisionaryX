import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { updateProfile } from "../api/auth";
import GlassCard from "../components/ui/GlassCard";
import FormInput from "../components/ui/FormInput";
import NeonButton from "../components/ui/NeonButton";

const MODES = ["mentor", "friend", "strict", "growth"];

export default function Settings() {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [mode, setMode] = useState(user?.preferences?.default_chatbot_mode || "mentor");
  const [notificationsEnabled, setNotificationsEnabled] = useState(user?.preferences?.notifications_enabled ?? true);
  const [saved, setSaved] = useState(false);

  const mutation = useMutation({
    mutationFn: () =>
      updateProfile({
        name,
        preferences: { theme: "dark-neon", notifications_enabled: notificationsEnabled, default_chatbot_mode: mode },
      }),
    onSuccess: async () => {
      await refreshUser();
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  return (
    <div className="flex max-w-xl flex-col gap-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Settings</h2>
        <p className="text-sm text-white/50">Your profile and AI preferences.</p>
      </div>

      <GlassCard hover={false}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
          className="flex flex-col gap-4"
        >
          <FormInput label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <FormInput label="Email" value={user?.email || ""} disabled />

          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium uppercase tracking-wider text-white/50">Default Chatbot Mode</span>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white outline-none focus:border-cyan-400/60"
            >
              {MODES.map((m) => (
                <option key={m} value={m} className="bg-[#10132a] capitalize">
                  {m}
                </option>
              ))}
            </select>
          </label>

          <label className="flex items-center gap-3 text-sm text-white/70">
            <input
              type="checkbox"
              checked={notificationsEnabled}
              onChange={(e) => setNotificationsEnabled(e.target.checked)}
              className="accent-cyan-400"
            />
            Enable notifications
          </label>

          <NeonButton type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Saving..." : saved ? "Saved!" : "Save Changes"}
          </NeonButton>
        </form>
      </GlassCard>
    </div>
  );
}
