"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/auth/login", { username, password });
      const res = await api.get("/auth/me");

      if (res.data.role === "SUPER_ADMIN") {
        router.push("/admin");
      } else {
        router.push("/dashboard");
      }
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-950">
      <div className="bg-neutral-900 border border-neutral-800 p-8 rounded-xl w-full max-w-md">
        <h1 className="text-2xl font-semibold mb-6 text-center">
          Billing POS Login
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            className="bg-neutral-800 border border-neutral-700 px-3 py-2 rounded w-full text-white placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-white"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            className="bg-neutral-800 border border-neutral-700 px-3 py-2 rounded w-full text-white placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-white text-black py-2 rounded hover:opacity-90 transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </div>
  );
}