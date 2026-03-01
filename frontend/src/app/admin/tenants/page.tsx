"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

type Tenant = {
  id: number;
  name: string;
  status: "ACTIVE" | "SUSPENDED";
};

export default function TenantsPage() {
  const { loading } = useAuth("SUPER_ADMIN");

  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [passwords, setPasswords] = useState<{
    [key: number]: string;
  }>({});
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    try {
      const res = await api.get("/super-admin/tenants");
      setTenants(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  // ✅ FIXED ENDPOINT HERE
  const toggleStatus = async (
    tenantId: number,
    currentStatus: string
  ) => {
    const newStatus =
      currentStatus === "ACTIVE" ? "SUSPENDED" : "ACTIVE";

    try {
      setUpdatingId(tenantId);

      await api.patch(
        `/super-admin/tenants/${tenantId}/status`,
        { status: newStatus }
      );

      await fetchTenants();
    } catch (err: any) {
      console.error(err.response?.data || err.message);
      alert("Status update failed");
    } finally {
      setUpdatingId(null);
    }
  };

  const resetPassword = async (tenantId: number) => {
    const newPassword = passwords[tenantId];

    if (!newPassword) {
      alert("Enter a password first");
      return;
    }

    try {
      await api.post("/super-admin/reset-password", {
        tenant_id: tenantId,
        new_password: newPassword,
      });

      setPasswords({
        ...passwords,
        [tenantId]: "",
      });

      alert("Password reset successful");
    } catch (err) {
      console.error(err);
      alert("Reset failed");
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">
        Tenant Management
      </h1>

      <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-neutral-800">
            <tr>
              <th className="p-4">Tenant</th>
              <th className="p-4">Status</th>
              <th className="p-4">Actions</th>
            </tr>
          </thead>

          <tbody>
            {tenants.map((tenant) => (
              <tr
                key={tenant.id}
                className="border-t border-neutral-800"
              >
                <td className="p-4">{tenant.name}</td>

                <td className="p-4">
                  <span
                    className={`px-3 py-1 rounded text-sm font-medium ${
                      tenant.status === "ACTIVE"
                        ? "bg-green-600"
                        : "bg-red-600"
                    }`}
                  >
                    {tenant.status}
                  </span>
                </td>

                <td className="p-4 space-x-3">
                  <button
                    onClick={() =>
                      toggleStatus(tenant.id, tenant.status)
                    }
                    disabled={updatingId === tenant.id}
                    className="bg-neutral-700 px-3 py-1 rounded hover:bg-neutral-600 transition disabled:opacity-50"
                  >
                    {updatingId === tenant.id
                      ? "Updating..."
                      : tenant.status === "ACTIVE"
                      ? "Suspend"
                      : "Activate"}
                  </button>

                  <input
                    type="password"
                    placeholder="New Password"
                    value={passwords[tenant.id] || ""}
                    onChange={(e) =>
                      setPasswords({
                        ...passwords,
                        [tenant.id]: e.target.value,
                      })
                    }
                    className="bg-neutral-800 border border-neutral-700 px-2 py-1 rounded text-sm text-white placeholder-neutral-400"
                  />

                  <button
                    onClick={() => resetPassword(tenant.id)}
                    className="bg-white text-black px-3 py-1 rounded text-sm hover:opacity-90 transition"
                  >
                    Reset Password
                  </button>
                </td>
              </tr>
            ))}

            {tenants.length === 0 && (
              <tr>
                <td
                  colSpan={3}
                  className="p-6 text-center text-neutral-400"
                >
                  No tenants found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}