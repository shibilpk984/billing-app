"use client";

import { useAuth } from "@/hooks/useAuth";

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="min-h-screen bg-neutral-950 p-8">
      <h1 className="text-2xl font-semibold mb-6">
        Tenant Dashboard
      </h1>

      <div className="bg-neutral-900 border border-neutral-800 p-6 rounded-xl">
        <p><strong>User ID:</strong> {user.user_id}</p>
        <p><strong>Tenant ID:</strong> {user.tenant_id}</p>
        <p><strong>Role:</strong> {user.role}</p>
      </div>
    </div>
  );
}