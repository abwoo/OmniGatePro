import React, { useState, useEffect } from 'react';
import { 
  Users, 
  BarChart3, 
  Search, 
  Download, 
  CreditCard,
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
  onBack: () => void;
}

const AdminPage: React.FC<AdminPageProps> = ({ onBack }) => {
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
    } catch (err: unknown) {
      console.error("Failed to update user status", err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleManualRecharge = async (userId: string) => {
    const amount = prompt("Enter amount to recharge (USD):", "10");
    if (!amount || isNaN(parseFloat(amount))) return;
    
    setActionLoading(userId);
    try {
      await api.post('/v1/admin/recharge', null, { 
        params: { target_user_id: userId, amount: parseFloat(amount) } 
      });
      fetchUsers();
      fetchStats();
      alert("Recharge successful!");
    } catch {
      alert("Recharge failed.");
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
    } catch {
      alert("Failed to delete user");
    } finally {
      setActionLoading(null);
    }
  };

  const exportCSV = () => {
    window.open(`http://localhost:8000/v1/admin/users/export`, '_blank');
  };

  if (loading && page === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 text-black animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Navbar */}
      <nav className="h-16 bg-white/80 backdrop-blur-xl sticky top-0 z-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={onBack} 
              className="p-2 -ml-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="h-6 w-px bg-gray-200" />
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 bg-red-100 rounded-lg">
                <ShieldAlert className="w-4 h-4 text-red-600" />
              </div>
              <h1 className="text-sm font-bold tracking-tight text-gray-900 uppercase">Admin Console</h1>
            </div>
          </div>
          <button 
            onClick={exportCSV} 
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-semibold hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            Export Data
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard 
            icon={<Users className="text-blue-600" />} 
            label="Total Users" 
            value={stats?.total_users || 0} 
            trend="+12%"
          />
          <StatCard 
            icon={<ExternalLink className="text-purple-600" />} 
            label="Total Executions" 
            value={stats?.total_executions || 0}
            trend="+5%"
          />
          <StatCard 
            icon={<BarChart3 className="text-emerald-600" />} 
            label="Total Revenue" 
            value={`$${stats?.total_revenue.toFixed(2) || '0.00'}`} 
            trend="+8%"
          />
          <StatCard 
            icon={<CheckCircle2 className="text-indigo-600" />} 
            label="System Health" 
            value={stats?.system_status || 'Offline'} 
            highlight
          />
        </div>

        {/* User Table Card */}
        <div className="bg-white rounded-[24px] border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900">User Management</h2>
              <p className="text-sm text-gray-500 mt-1">Manage access and monitor user activity.</p>
            </div>
            
            <div className="relative group">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
              <input 
                type="text" 
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-full md:w-72 transition-all"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50/50 border-b border-gray-200">
                  <th className="px-6 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[240px]">User Identity</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[100px]">Role</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[120px]">Balance</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[120px]">Status</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[140px]">Joined Date</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider text-right min-w-[120px]">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((user) => (
                  <tr key={user.user_id} className="group hover:bg-gray-50/80 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="font-semibold text-gray-900 text-sm">{user.email}</span>
                        <span className="text-[11px] text-gray-400 font-mono mt-0.5">{user.user_id}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide border ${
                        user.role === 'admin' 
                          ? 'bg-purple-50 text-purple-700 border-purple-100' 
                          : 'bg-gray-100 text-gray-600 border-gray-200'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-sm font-medium text-gray-700">${user.balance.toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-emerald-500 shadow-[0_0_0_4px_rgba(16,185,129,0.1)]' : 'bg-red-500'}`} />
                        <span className={`text-xs font-medium ${user.is_active ? 'text-emerald-700' : 'text-red-700'}`}>
                          {user.is_active ? 'Active' : 'Disabled'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleManualRecharge(user.user_id)}
                          disabled={actionLoading === user.user_id}
                          className="p-2 bg-white border border-gray-200 rounded-lg text-blue-500 hover:border-blue-200 hover:bg-blue-50 transition-colors"
                          title="Manual Recharge"
                        >
                          <CreditCard className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => toggleUserStatus(user.user_id, user.is_active)}
                          disabled={actionLoading === user.user_id}
                          className={`p-2 rounded-lg transition-colors border ${
                            user.is_active 
                              ? 'bg-white border-gray-200 text-gray-500 hover:border-red-200 hover:bg-red-50 hover:text-red-600' 
                              : 'bg-white border-gray-200 text-gray-500 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-600'
                          }`}
                          title={user.is_active ? "Disable User" : "Activate User"}
                        >
                          {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                        </button>
                        <button 
                          onClick={() => deleteUser(user.user_id)}
                          disabled={actionLoading === user.user_id || user.role === 'admin'}
                          className="p-2 bg-white border border-gray-200 rounded-lg text-gray-500 hover:border-red-200 hover:bg-red-50 hover:text-red-600 transition-colors disabled:opacity-20"
                          title="Delete User"
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

          <div className="p-4 border-t border-gray-100 flex items-center justify-between bg-gray-50/30">
            <span className="text-xs text-gray-500 font-medium">
              Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, total)} of {total} results
            </span>
            <div className="flex gap-2">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 bg-white border border-gray-200 hover:bg-gray-50 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                <ChevronLeft className="w-4 h-4 text-gray-600" />
              </button>
              <button 
                onClick={() => setPage(p => p + 1)}
                disabled={page * 10 >= total}
                className="p-2 bg-white border border-gray-200 hover:bg-gray-50 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                <ChevronRight className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const StatCard = ({ icon, label, value, trend, highlight }: { icon: React.ReactNode, label: string, value: string | number, trend?: string, highlight?: boolean }) => (
  <div className="bg-white p-6 rounded-[20px] border border-gray-200 shadow-sm relative overflow-hidden group hover:border-blue-100 transition-colors">
    <div className="flex justify-between items-start mb-4">
      <div className="w-10 h-10 bg-gray-50 rounded-xl flex items-center justify-center group-hover:bg-blue-50 transition-colors">
        {icon}
      </div>
      {trend && (
        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
          {trend}
        </span>
      )}
    </div>
    <div className="space-y-1 relative z-10">
      <p className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">{label}</p>
      <h3 className={`text-2xl font-bold tracking-tight ${highlight ? 'text-indigo-600' : 'text-gray-900'}`}>{value}</h3>
    </div>
    {highlight && (
      <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-indigo-50 rounded-full blur-2xl opacity-50 group-hover:opacity-100 transition-opacity" />
    )}
  </div>
);

export default AdminPage;
