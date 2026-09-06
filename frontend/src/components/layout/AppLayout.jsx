import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../../context/AuthContext";
import { getDigitalTwin } from "../../api/digitalTwin";
import TwinStateBadge from "../ui/TwinStateBadge";
import ParticleField from "../ui/ParticleField";
import {
  IconDashboard,
  IconTwin,
  IconGoal,
  IconHabit,
  IconJournal,
  IconSimulate,
  IconChat,
  IconAnalytics,
  IconBell,
  IconSettings,
  IconLogout,
} from "../Icons";

const NAV_ITEMS = [
  { to: "/app/dashboard", label: "Dashboard", icon: IconDashboard },
  { to: "/app/twin", label: "Digital Twin", icon: IconTwin },
  { to: "/app/goals", label: "Goals", icon: IconGoal },
  { to: "/app/habits", label: "Habits", icon: IconHabit },
  { to: "/app/journal", label: "Journal", icon: IconJournal },
  { to: "/app/simulations", label: "Simulations", icon: IconSimulate },
  { to: "/app/chatbot", label: "Future Self", icon: IconChat },
  { to: "/app/analytics", label: "Analytics", icon: IconAnalytics },
  { to: "/app/notifications", label: "Notifications", icon: IconBell },
  { to: "/app/settings", label: "Settings", icon: IconSettings },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { data: twin } = useQuery({
    queryKey: ["digital-twin"],
    queryFn: getDigitalTwin,
    refetchInterval: 60_000,
  });

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="relative min-h-screen">
      <div className="app-background" />
      <div className="grid-overlay" />
      <ParticleField count={40} />

      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col gap-6 border-r border-white/10 bg-black/20 p-6 backdrop-blur-xl lg:flex">
          <div>
            <h1 className="font-display text-xl font-black text-glow-cyan">VISIONARY<span className="text-glow-magenta">X</span></h1>
            <p className="mt-1 text-[10px] uppercase tracking-widest text-white/40">Predict Possibilities. Shape Reality.</p>
          </div>

          <nav className="flex flex-1 flex-col gap-1 overflow-y-auto">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-cyan-400/10 text-cyan-300 shadow-[inset_0_0_0_1px_rgba(0,246,255,0.35)]"
                      : "text-white/60 hover:bg-white/5 hover:text-white"
                  }`
                }
              >
                <Icon />
                {label}
              </NavLink>
            ))}
          </nav>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/50 transition-colors hover:bg-rose-500/10 hover:text-rose-300"
          >
            <IconLogout />
            Sign Out
          </button>
        </aside>

        <div className="flex flex-1 flex-col">
          <header className="sticky top-0 z-10 flex items-center justify-between border-b border-white/10 bg-black/20 px-6 py-4 backdrop-blur-xl">
            <div>
              <p className="text-xs uppercase tracking-widest text-white/40">Welcome back</p>
              <p className="font-display text-lg font-bold">{user?.name || "Visionary"}</p>
            </div>
            {twin && <TwinStateBadge state={twin.state} />}
          </header>

          <main className="flex-1 p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
