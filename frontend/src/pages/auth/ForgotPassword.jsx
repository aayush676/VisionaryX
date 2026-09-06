import { useState } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../../api/auth";
import GlassCard from "../../components/ui/GlassCard";
import FormInput from "../../components/ui/FormInput";
import NeonButton from "../../components/ui/NeonButton";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await forgotPassword(email);
    } finally {
      setSent(true);
      setLoading(false);
    }
  };

  return (
    <GlassCard hover={false}>
      <h2 className="font-display mb-6 text-xl font-bold">Reset Access</h2>
      {sent ? (
        <p className="text-sm text-white/60">
          If that email is registered, a reset link has been sent. Check the server console in dev mode.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <FormInput label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          <NeonButton type="submit" disabled={loading} className="mt-2 w-full">
            {loading ? "Sending..." : "Send Reset Link"}
          </NeonButton>
        </form>
      )}
      <div className="mt-6 text-center text-xs text-white/50">
        <Link to="/login" className="hover:text-cyan-300">
          Back to login
        </Link>
      </div>
    </GlassCard>
  );
}
