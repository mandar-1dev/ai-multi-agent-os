import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Share2 } from "lucide-react";
import { api, setToken } from "../api/client";

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = mode === "login" ? await api.login(email, password) : await api.register(email, password, fullName);
      setToken(res.access_token);
      navigate("/");
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-bg">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <div className="h-10 w-10 rounded-md bg-signal/10 border border-signal/30 flex items-center justify-center">
            <Share2 size={20} className="text-signal" />
          </div>
          <div className="text-left">
            <div className="font-display font-semibold tracking-tight leading-none">AGENT OS</div>
            <div className="text-[10px] text-text-dim uppercase tracking-widest mt-0.5">Multi-Agent Console</div>
          </div>
        </div>

        <div className="bg-panel border border-border rounded-lg p-6">
          <div className="flex gap-1 mb-6 bg-panel-raised rounded-md p-1">
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 text-sm py-1.5 rounded transition-colors ${
                  mode === m ? "bg-bg text-text" : "text-text-dim"
                }`}
              >
                {m === "login" ? "Sign in" : "Create account"}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-3">
            {mode === "register" && (
              <input
                placeholder="Full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-panel-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-signal/50"
              />
            )}
            <input
              type="email"
              required
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-panel-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-signal/50"
            />
            <input
              type="password"
              required
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-panel-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-signal/50"
            />
            {error && <p className="text-danger text-xs">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-signal text-bg font-medium text-sm rounded-md py-2 mt-2 disabled:opacity-50"
            >
              {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>
        </div>
        <p className="text-center text-text-dim text-xs mt-4">
          First account created becomes the admin.
        </p>
      </div>
    </div>
  );
}
