import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  CheckCircle2,
  MoreHorizontal
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
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA] font-sans text-gray-900 pb-20">
      {/* Navbar */}
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="h-[72px] bg-white/80 backdrop-blur-xl sticky top-0 z-50 border-b border-gray-200/60"
      >
        <div className="max-w-7xl mx-auto px-4 md:px-8 h-full flex items-center justify-between">
          <div className="flex items-center gap-6">
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onBack} 
              className="p-2 -ml-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5" />
            </motion.button>
            <div className="h-6 w-px bg-gray-200" />
            <div className="flex items-center gap-3">
              <div className="p-2 bg-rose-50 rounded-lg border border-rose-100">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
              </div>
              <h1 className="text-sm font-bold tracking-tight text-gray-900 uppercase">Admin Console</h1>
            </div>
          </div>
          <motion.button 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={exportCSV} 
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-bold hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm text-gray-700"
          >
            <Download className="w-3.5 h-3.5" />
            Export Data
          </motion.button>
        </div>
      </motion.nav>

      <main className="max-w-7xl mx-auto px-4 md:px-8 pt-10 space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard 
            icon={<Users className="text-blue-600" />} 
            label="Total Users" 
            value={stats?.total_users || 0} 
            trend="+12%"
            delay={0.1}
          />
          <StatCard 
            icon={<ExternalLink className="text-purple-600" />} 
            label="Total Executions" 
            value={stats?.total_executions || 0}
            trend="+5%"
            delay={0.2}
          />
          <StatCard 
            icon={<BarChart3 className="text-emerald-600" />} 
            label="Total Revenue" 
            value={`$${stats?.total_revenue.toFixed(2) || '0.00'}`} 
            trend="+8%"
            delay={0.3}
          />
          <StatCard 
            icon={<CheckCircle2 className="text-indigo-600" />} 
            label="System Health" 
            value={stats?.system_status || 'Offline'} 
            highlight
            delay={0.4}
          />
        </div>

        {/* User Table Card */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="ui-card border-gray-200/60 overflow-hidden"
        >
          <div className="p-6 md:p-8 border-b border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900 tracking-tight">User Management</h2>
              <p className="text-sm text-gray-500 mt-1 font-medium">Manage access and monitor user activity.</p>
            </div>
            
            <div className="relative group w-full md:w-auto">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
              <input 
                type="text" 
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-11 pr-4 py-3 bg-gray-50 border border-transparent hover:border-gray-200 hover:bg-white rounded-xl text-sm font-medium outline-none focus:bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 w-full md:w-80 transition-all"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50/50 border-b border-gray-200">
                  <th className="px-8 py-5 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[280px]">User Identity</th>
                  <th className="px-6 py-5 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[120px]">Role</th>
                  <th className="px-6 py-5 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[140px]">Balance</th>
                  <th className="px-6 py-5 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[140px]">Status</th>
                  <th className="px-6 py-5 text-[11px] font-bold text-gray-400 uppercase tracking-wider w-[160px]">Joined Date</th>
                  <th className="px-8 py-5 text-[11px] font-bold text-gray-400 uppercase tracking-wider text-right min-w-[140px]">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                <AnimatePresence mode="popLayout">
                  {users.map((user) => (
                    <motion.tr 
                      layout
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      key={user.user_id} 
                      className="group hover:bg-gray-50/80 transition-colors"
                    >
                      <td className="px-8 py-5">
                        <div className="flex flex-col">
                          <span className="font-bold text-gray-900 text-sm">{user.email}</span>
                          <span className="text-[11px] text-gray-400 font-mono mt-1 tracking-tight">{user.user_id}</span>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide border ${
                          user.role === 'admin' 
                            ? 'bg-purple-50 text-purple-700 border-purple-100' 
                            : 'bg-gray-100 text-gray-600 border-gray-200'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-5">
                        <span className="font-mono text-sm font-bold text-gray-700">${user.balance.toFixed(2)}</span>
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-emerald-500 shadow-[0_0_0_4px_rgba(16,185,129,0.15)]' : 'bg-rose-500 shadow-[0_0_0_4px_rgba(244,63,94,0.15)]'}`} />
                          <span className={`text-xs font-bold ${user.is_active ? 'text-emerald-700' : 'text-rose-700'}`}>
                            {user.is_active ? 'Active' : 'Disabled'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-xs font-bold text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-8 py-5 text-right">
                        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => handleManualRecharge(user.user_id)}
                            disabled={actionLoading === user.user_id}
                            className="p-2 bg-white border border-gray-200 rounded-lg text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50 transition-colors shadow-sm"
                            title="Manual Recharge"
                          >
                            <CreditCard className="w-4 h-4" />
                          </motion.button>
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => toggleUserStatus(user.user_id, user.is_active)}
                            disabled={actionLoading === user.user_id}
                            className={`p-2 rounded-lg transition-colors border shadow-sm ${
                              user.is_active 
                                ? 'bg-white border-gray-200 text-gray-500 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600' 
                                : 'bg-white border-gray-200 text-gray-500 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-600'
                            }`}
                            title={user.is_active ? "Disable User" : "Activate User"}
                          >
                            {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                          </motion.button>
                          <motion.button 
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => deleteUser(user.user_id)}
                            disabled={actionLoading === user.user_id || user.role === 'admin'}
                            className="p-2 bg-white border border-gray-200 rounded-lg text-gray-500 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600 transition-colors disabled:opacity-20 shadow-sm"
                            title="Delete User"
                          >
                            <Trash2 className="w-4 h-4" />
                          </motion.button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
          </div>

          <div className="p-5 border-t border-gray-100 flex items-center justify-between bg-gray-50/30">
            <span className="text-xs text-gray-500 font-bold">
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
        </motion.div>
      </main>
    </div>
  );
};

const StatCard = ({ icon, label, value, trend, highlight, delay = 0 }: { icon: React.ReactNode, label: string, value: string | number, trend?: string, highlight?: boolean, delay?: number }) => (
  <motion.div 
    initial={{ y: 20, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
    transition={{ delay }}
    className="bg-white p-6 rounded-[24px] border border-gray-200 shadow-sm relative overflow-hidden group hover:border-indigo-100 hover:shadow-md transition-all"
  >
    <div className="flex justify-between items-start mb-4">
      <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center group-hover:bg-indigo-50 group-hover:scale-110 transition-all duration-300">
        {icon}
      </div>
      {trend && (
        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
          {trend}
        </span>
      )}
    </div>
    <div className="space-y-1 relative z-10">
      <p className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">{label}</p>
      <h3 className={`text-3xl font-bold tracking-tight ${highlight ? 'text-indigo-600' : 'text-gray-900'}`}>{value}</h3>
    </div>
    {highlight && (
      <div className="absolute -bottom-4 -right-4 w-32 h-32 bg-indigo-50 rounded-full blur-3xl opacity-50 group-hover:opacity-100 transition-opacity" />
    )}
  </motion.div>
);

export default AdminPage;
