import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verifyEmail } from "../../api/auth";
import GlassCard from "../../components/ui/GlassCard";
import Loader from "../../components/ui/Loader";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setStatus("error");
      return;
    }
    verifyEmail(token)
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [searchParams]);

  return (
    <GlassCard hover={false}>
      <h2 className="font-display mb-4 text-xl font-bold">Email Verification</h2>
      {status === "loading" && <Loader label="Verifying" />}
      {status === "success" && (
        <p className="text-sm text-emerald-300">Your email has been verified. You can now log in.</p>
      )}
      {status === "error" && (
        <p className="text-sm text-rose-400">This verification link is invalid or has expired.</p>
      )}
      <div className="mt-6 text-center text-xs text-white/50">
        <Link to="/login" className="hover:text-cyan-300">
          Back to login
        </Link>
      </div>
    </GlassCard>
  );
}
