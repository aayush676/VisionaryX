import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { resetPassword } from "../../api/auth";
import { extractErrorMessage } from "../../api/errors";
import GlassCard from "../../components/ui/GlassCard";
import FormInput from "../../components/ui/FormInput";
import NeonButton from "../../components/ui/NeonButton";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await resetPassword(token, password);
      navigate("/login");
    } catch (err) {
      setError(extractErrorMessage(err, "Invalid or expired reset link."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <GlassCard hover={false}>
      <h2 className="font-display mb-6 text-xl font-bold">Set New Password</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <FormInput
          label="New Password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <NeonButton type="submit" disabled={loading || !token} className="mt-2 w-full">
          {loading ? "Saving..." : "Reset Password"}
        </NeonButton>
      </form>
      <div className="mt-6 text-center text-xs text-white/50">
        <Link to="/login" className="hover:text-cyan-300">
          Back to login
        </Link>
      </div>
    </GlassCard>
  );
}
