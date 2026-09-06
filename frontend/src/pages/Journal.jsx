import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createJournal, listJournals } from "../api/journals";
import GlassCard from "../components/ui/GlassCard";
import NeonButton from "../components/ui/NeonButton";
import Loader from "../components/ui/Loader";

const EMOTION_COLORS = {
  stress: "#ffb020",
  burnout: "#ff3b5c",
  focus: "#00f6ff",
  happiness: "#39ff9d",
  anxiety: "#ff2ec4",
  motivation: "#9b5cff",
};

function EmotionBars({ emotions }) {
  return (
    <div className="flex flex-col gap-2">
      {Object.entries(emotions).map(([key, value]) => (
        <div key={key} className="flex items-center gap-3 text-xs">
          <span className="w-24 shrink-0 capitalize text-white/50">{key}</span>
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full"
              style={{ width: `${value}%`, background: EMOTION_COLORS[key] }}
            />
          </div>
          <span className="w-8 text-right text-white/40">{Math.round(value)}</span>
        </div>
      ))}
    </div>
  );
}

export default function Journal() {
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");

  const journalsQuery = useQuery({ queryKey: ["journals", 30], queryFn: () => listJournals(30) });

  const createMutation = useMutation({
    mutationFn: () => createJournal(content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["journals"] });
      queryClient.invalidateQueries({ queryKey: ["digital-twin"] });
      setContent("");
    },
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Emotional Intelligence</h2>
        <p className="text-sm text-white/50">Write freely — sentiment and emotion analysis runs automatically.</p>
      </div>

      <GlassCard hover={false}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (content.trim()) createMutation.mutate();
          }}
          className="flex flex-col gap-4"
        >
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={5}
            placeholder="How was today? What's on your mind?"
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-white/30 outline-none focus:border-cyan-400/60"
          />
          <NeonButton type="submit" disabled={createMutation.isPending || !content.trim()} className="self-end">
            {createMutation.isPending ? "Analyzing..." : "Save Entry"}
          </NeonButton>
        </form>
      </GlassCard>

      {journalsQuery.isLoading ? (
        <Loader label="Loading journal" />
      ) : journalsQuery.data?.length ? (
        <div className="flex flex-col gap-4">
          {journalsQuery.data.map((entry) => (
            <GlassCard key={entry.id} className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div className="flex-1">
                <p className="mb-2 text-xs text-white/40">{new Date(entry.created_at).toLocaleString()}</p>
                <p className="text-sm text-white/80">{entry.content}</p>
                <p className="mt-2 text-xs uppercase tracking-widest text-cyan-300">
                  Dominant: {entry.dominant_emotion}
                </p>
              </div>
              <div className="w-full md:w-64">
                <EmotionBars emotions={entry.emotions} />
              </div>
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard>
          <p className="text-sm text-white/40">No journal entries yet.</p>
        </GlassCard>
      )}
    </div>
  );
}
