"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loading } = useAuth("SUPER_ADMIN");
  const router = useRouter();

  const handleLogout = async () => {
    await api.post("/auth/logout");
    router.push("/login");
  };

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="flex min-h-screen bg-neutral-950">
      {/* Sidebar */}
      <aside className="w-64 bg-black text-white p-6 space-y-6 border-r border-neutral-800">
        <h2 className="text-xl font-semibold tracking-wide">
          Admin Panel
        </h2>

        <nav className="space-y-3 text-neutral-300">
          <Link href="/admin" className="block hover:text-white">
            Dashboard
          </Link>
          <Link href="/admin/tenants" className="block hover:text-white">
            Tenants
          </Link>
        </nav>

        <button
          onClick={handleLogout}
          className="mt-10 bg-neutral-800 hover:bg-neutral-700 px-3 py-2 rounded-lg w-full transition"
        >
          Logout
        </button>
      </aside>

      {/* Content */}
      <main className="flex-1 p-8 bg-neutral-950">
        {children}
      </main>
    </div>
  );
}