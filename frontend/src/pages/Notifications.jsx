import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listNotifications, markAllNotificationsRead, markNotificationRead } from "../api/notifications";
import GlassCard from "../components/ui/GlassCard";
import NeonButton from "../components/ui/NeonButton";
import Loader from "../components/ui/Loader";

const TYPE_STYLES = {
  info: "border-sky-400/30 text-sky-300",
  warning: "border-amber-400/30 text-amber-300",
  achievement: "border-emerald-400/30 text-emerald-300",
  reminder: "border-violet-400/30 text-violet-300",
};

export default function Notifications() {
  const queryClient = useQueryClient();
  const notificationsQuery = useQuery({ queryKey: ["notifications"], queryFn: () => listNotifications() });

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const markAllMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="font-display text-2xl font-bold">Notifications</h2>
        <NeonButton variant="ghost" onClick={() => markAllMutation.mutate()} disabled={markAllMutation.isPending}>
          Mark all read
        </NeonButton>
      </div>

      {notificationsQuery.isLoading ? (
        <Loader />
      ) : notificationsQuery.data?.length ? (
        <div className="flex flex-col gap-3">
          {notificationsQuery.data.map((n) => (
            <GlassCard
              key={n.id}
              hover={false}
              className={`flex items-start justify-between gap-4 border ${TYPE_STYLES[n.type] || TYPE_STYLES.info} ${n.is_read ? "opacity-50" : ""}`}
            >
              <div>
                <p className="font-semibold">{n.title}</p>
                <p className="text-sm text-white/60">{n.message}</p>
                <p className="mt-1 text-[10px] uppercase tracking-widest text-white/30">
                  {new Date(n.created_at).toLocaleString()}
                </p>
              </div>
              {!n.is_read && (
                <NeonButton variant="ghost" className="text-xs" onClick={() => markReadMutation.mutate(n.id)}>
                  Mark read
                </NeonButton>
              )}
            </GlassCard>
          ))}
        </div>
      ) : (
        <GlassCard>
          <p className="text-sm text-white/40">No notifications yet.</p>
        </GlassCard>
      )}
    </div>
  );
}
