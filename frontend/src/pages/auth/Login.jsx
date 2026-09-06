import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { extractErrorMessage } from "../../api/errors";
import GlassCard from "../../components/ui/GlassCard";
import FormInput from "../../components/ui/FormInput";
import NeonButton from "../../components/ui/NeonButton";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/app/dashboard");
    } catch (err) {
      setError(extractErrorMessage(err, "Invalid email or password."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <GlassCard hover={false}>
      <h2 className="font-display mb-6 text-xl font-bold">Access Your Twin</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <NeonButton type="submit" disabled={loading} className="mt-2 w-full">
          {loading ? "Authenticating..." : "Log In"}
        </NeonButton>
      </form>
      <div className="mt-6 flex justify-between text-xs text-white/50">
        <Link to="/forgot-password" className="hover:text-cyan-300">
          Forgot password?
        </Link>
        <Link to="/signup" className="hover:text-cyan-300">
          Create an account
        </Link>
      </div>
    </GlassCard>
  );
}
