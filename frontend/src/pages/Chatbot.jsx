import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { sendChatMessage } from "../api/chatbot";
import GlassCard from "../components/ui/GlassCard";
import NeonButton from "../components/ui/NeonButton";
import { IconSend, IconSparkle } from "../components/Icons";

const MODES = [
  { value: "mentor", label: "Mentor" },
  { value: "friend", label: "Friend" },
  { value: "strict", label: "Strict" },
  { value: "growth", label: "Growth" },
];

export default function Chatbot() {
  const [mode, setMode] = useState("mentor");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "twin", text: "I'm your Future Self. Tell me what's going on — I have access to your goals and history." },
  ]);
  const scrollRef = useRef(null);

  const mutation = useMutation({
    mutationFn: (message) => sendChatMessage(message, mode),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: "twin", text: data.reply }]);
    },
    onError: () => {
      setMessages((prev) => [...prev, { role: "twin", text: "I couldn't reach your data right now. Try again in a moment." }]);
    },
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: "user", text }]);
    mutation.mutate(text);
    setInput("");
  };

  return (
    <div className="flex h-[calc(100vh-9rem)] flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">Future Self</h2>
          <p className="text-sm text-white/50">Grounded in your Digital Twin, goals, and memory.</p>
        </div>
        <div className="flex gap-2">
          {MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => setMode(m.value)}
              className={`rounded-full border px-4 py-1.5 text-xs font-semibold uppercase tracking-wider transition-colors ${
                mode === m.value
                  ? "border-violet-400/60 bg-violet-400/10 text-violet-300"
                  : "border-white/10 text-white/50 hover:border-white/30"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      <GlassCard hover={false} className="flex flex-1 flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto pr-2">
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                  msg.role === "user"
                    ? "bg-cyan-500/15 text-cyan-100"
                    : "border border-violet-400/20 bg-violet-500/10 text-violet-50"
                }`}
              >
                {msg.role === "twin" && (
                  <div className="mb-1 flex items-center gap-1 text-[10px] uppercase tracking-widest text-violet-300">
                    <IconSparkle width={12} height={12} /> Future Self · {mode}
                  </div>
                )}
                {msg.text}
              </div>
            </motion.div>
          ))}
          {mutation.isPending && (
            <div className="flex items-center gap-2 text-xs text-white/40">
              <span className="h-1.5 w-1.5 animate-ping rounded-full bg-violet-400" />
              Future Self is thinking...
            </div>
          )}
        </div>

        <form onSubmit={handleSend} className="mt-4 flex gap-3 border-t border-white/10 pt-4">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your future self anything..."
            className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm outline-none focus:border-violet-400/60"
          />
          <NeonButton type="submit" variant="violet" disabled={mutation.isPending || !input.trim()}>
            <IconSend width={16} height={16} />
          </NeonButton>
        </form>
      </GlassCard>
    </div>
  );
}
