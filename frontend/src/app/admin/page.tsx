"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function AdminDashboard() {
  const { loading } = useAuth("SUPER_ADMIN");

  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await api.get("/super-admin/stats");
      setStats(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-8">
        Super Admin Dashboard
      </h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6 mb-10">
        <StatCard title="Total Tenants" value={stats?.total_tenants || 0} />
        <StatCard title="Active Tenants" value={stats?.active_tenants || 0} />
        <StatCard title="Suspended Tenants" value={stats?.suspended_tenants || 0} />
        <StatCard title="Total Invoices" value={stats?.total_invoices || 0} />
      </div>

      {/* Quick Actions */}
      <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>

        <div className="flex gap-4">
          <a
            href="/admin/tenants"
            className="bg-white text-black px-4 py-2 rounded hover:opacity-90"
          >
            Manage Tenants
          </a>

          <button
            onClick={fetchStats}
            className="bg-neutral-800 px-4 py-2 rounded hover:bg-neutral-700"
          >
            Refresh Stats
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
      <p className="text-neutral-400 text-sm mb-2">{title}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  );
}