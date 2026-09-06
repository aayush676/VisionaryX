import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { extractErrorMessage } from "../../api/errors";
import GlassCard from "../../components/ui/GlassCard";
import FormInput from "../../components/ui/FormInput";
import NeonButton from "../../components/ui/NeonButton";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(form.name, form.email, form.password);
      setDone(true);
      setTimeout(() => navigate("/login"), 2500);
    } catch (err) {
      setError(extractErrorMessage(err, "Could not create account."));
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <GlassCard hover={false}>
        <h2 className="font-display mb-2 text-xl font-bold text-glow-cyan">Account Created</h2>
        <p className="text-sm text-white/60">
          Check your inbox (or the server console in dev) for a verification link. Redirecting to login...
        </p>
      </GlassCard>
    );
  }

  return (
    <GlassCard hover={false}>
      <h2 className="font-display mb-6 text-xl font-bold">Initialize Your Twin</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <FormInput
          label="Full Name"
          required
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <FormInput
          label="Email"
          type="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <FormInput
          label="Password"
          type="password"
          required
          minLength={8}
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <NeonButton type="submit" disabled={loading} variant="magenta" className="mt-2 w-full">
          {loading ? "Creating..." : "Create Account"}
        </NeonButton>
      </form>
      <div className="mt-6 text-center text-xs text-white/50">
        Already have an account?{" "}
        <Link to="/login" className="text-cyan-300 hover:underline">
          Log in
        </Link>
      </div>
    </GlassCard>
  );
}
