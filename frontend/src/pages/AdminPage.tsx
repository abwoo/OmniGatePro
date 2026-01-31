import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  BarChart3, 
  Search, 
  Download, 
  UserX, 
  UserCheck, 
  Trash2, 
  ShieldAlert,
  ArrowLeft,
  Loader2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  CheckCircle2
} from 'lucide-react';
import api from '../utils/api';

interface AdminUser {
  id: number;
  user_id: string;
  email: string;
  role: string;
  balance: number;
  is_active: number;
  created_at: string;
}

interface AdminStats {
  total_users: number;
  total_executions: number;
  total_revenue: number;
  system_status: string;
}

interface AdminPageProps {
  token: string;
  onBack: () => void;
}

const AdminPage: React.FC<AdminPageProps> = ({ token, onBack }) => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/v1/admin/users', {
        params: { page, search, limit: 10 }
      });
      setUsers(res.data.users);
      setTotal(res.data.total);
    } catch (err) {
      console.error("Failed to fetch users", err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await api.get('/v1/admin/stats');
      setStats(res.data);
    } catch (err) {
      console.error("Failed to fetch stats", err);
    }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchUsers(), fetchStats()]).finally(() => setLoading(false));
  }, [page, search]);

  const toggleUserStatus = async (userId: string, currentStatus: number) => {
    setActionLoading(userId);
    try {
      await api.patch(`/v1/admin/user/${userId}/status`, 
        { active: currentStatus === 0 },
        { params: { active: currentStatus === 0 } }
      );
      fetchUsers();
    } catch (err) {
      alert("Failed to update user status");
    } finally {
      setActionLoading(null);
    }
  };

  const deleteUser = async (userId: string) => {
    if (!window.confirm(`Are you sure you want to PERMANENTLY delete user ${userId}? This action cannot be undone.`)) return;
    
    setActionLoading(userId);
    try {
      await api.delete(`/v1/admin/user/${userId}`);
      fetchUsers();
      fetchStats();
    } catch (err) {
      alert("Failed to delete user");
    } finally {
      setActionLoading(null);
    }
  };

  const exportCSV = () => {
    window.open(`http://localhost:8000/v1/admin/users/export?token=${token}`, '_blank');
  };

  if (loading && page === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd]">
        <Loader2 className="w-8 h-8 text-apple-blue animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fbfbfd] pb-20">
      <nav className="h-16 glass sticky top-0 z-50 border-b border-black/[0.08]">
        <div className="container-custom h-full flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={onBack} className="p-2 hover:bg-black/5 rounded-full transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-red-500" />
              <h1 className="text-xl font-bold tracking-tight">Admin Console</h1>
            </div>
          </div>
          <button onClick={exportCSV} className="btn-secondary px-4 py-2 flex items-center gap-2 text-sm">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </nav>

      <main className="container-custom pt-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard icon={<Users className="text-blue-500" />} label="Total Users" value={stats?.total_users || 0} />
          <StatCard icon={<ExternalLink className="text-purple-500" />} label="Total Executions" value={stats?.total_executions || 0} />
          <StatCard icon={<BarChart3 className="text-green-500" />} label="Total Revenue" value={`$${stats?.total_revenue.toFixed(2) || '0.00'}`} />
          <StatCard icon={<CheckCircle2 className="text-apple-blue" />} label="System Status" value={stats?.system_status || 'Offline'} />
        </div>

        <div className="card-apple overflow-hidden">
          <div className="p-6 border-b border-black/[0.04] flex flex-col md:flex-row md:items-center justify-between gap-4">
            <h2 className="text-lg font-bold">User Management</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black/20" />
              <input 
                type="text" 
                placeholder="Search by ID or Email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2 bg-apple-gray rounded-xl text-sm outline-none focus:ring-1 focus:ring-apple-blue/20 w-full md:w-64"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-apple-gray text-[11px] font-bold text-black/40 uppercase tracking-widest">
                <tr>
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">Balance</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Joined</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/[0.04]">
                {users.map((user) => (
                  <tr key={user.user_id} className="hover:bg-apple-gray/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="font-bold text-black/80">{user.email}</span>
                        <span className="text-[11px] text-black/40 font-mono">{user.user_id}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        user.role === 'admin' ? 'bg-red-500 text-white' : 'bg-apple-gray text-black/40'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium">${user.balance.toFixed(2)}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="font-medium">{user.is_active ? 'Active' : 'Disabled'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-black/40 font-medium">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button 
                          onClick={() => toggleUserStatus(user.user_id, user.is_active)}
                          disabled={actionLoading === user.user_id}
                          className={`p-2 rounded-lg transition-colors ${
                            user.is_active ? 'hover:bg-red-50 text-red-500' : 'hover:bg-green-50 text-green-500'
                          }`}
                        >
                          {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                        </button>
                        <button 
                          onClick={() => deleteUser(user.user_id)}
                          disabled={actionLoading === user.user_id || user.role === 'admin'}
                          className="p-2 hover:bg-red-50 text-red-500 rounded-lg transition-colors disabled:opacity-20"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-6 border-t border-black/[0.04] flex items-center justify-between">
            <span className="text-xs text-black/40 font-medium">
              Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, total)} of {total} users
            </span>
            <div className="flex gap-2">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 hover:bg-apple-gray rounded-lg disabled:opacity-20 transition-all"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button 
                onClick={() => setPage(p => p + 1)}
                disabled={page * 10 >= total}
                className="p-2 hover:bg-apple-gray rounded-lg disabled:opacity-20 transition-all"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const StatCard = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string | number }) => (
  <div className="card-apple p-6 space-y-4">
    <div className="w-10 h-10 bg-apple-gray rounded-xl flex items-center justify-center">
      {icon}
    </div>
    <div className="space-y-1">
      <p className="text-[11px] font-bold text-black/40 uppercase tracking-widest">{label}</p>
      <h3 className="text-2xl font-bold tracking-tight">{value}</h3>
    </div>
  </div>
);

export default AdminPage;
