import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Plus, 
  History, 
  CreditCard, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  Download,
  ChevronRight,
  Wallet,
  Zap,
  ShieldCheck,
  LayoutGrid,
  Menu,
  X,
  Cpu,
  LogOut,
  User
} from 'lucide-react';
import axios from 'axios';
import LoginPage from './pages/LoginPage';

const API_BASE = 'http://localhost:8000';

interface Execution {
  run_id: string;
  status: string;
  total_cost: number;
  start_time: string;
  end_time: string;
  actions_count: number;
}

interface UserInfo {
  user_id: string;
  email: string;
  balance: number;
  total_spent: number;
  api_key: string;
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('artfish_token'));
  const [activeTab, setActiveTab] = useState('execute');
  const [goals, setGoals] = useState('');
  const [loading, setLoading] = useState(false);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/v1/user/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setUserInfo(res.data);
    } catch (err) {
      console.error("Failed to fetch user info", err);
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        handleLogout();
      }
    }
  };

  useEffect(() => {
    if (token) {
      fetchUserInfo();
    }
  }, [token]);

  const handleLogin = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('artfish_token', newToken);
  };

  const handleLogout = () => {
    setToken(null);
    setUserInfo(null);
    localStorage.removeItem('artfish_token');
  };

  const handleSubmit = async () => {
    if (!goals || !token) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/v1/execute`, {
        goals: goals.split(',').map(g => g.trim()),
        user_id: userInfo?.user_id || 'test_user',
        constraints: { style: 'photorealistic' }
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const runId = res.data.run_id;
      pollStatus(runId);
      setGoals('');
      setActiveTab('history');
    } catch (err) {
      alert("Submission failed. Check your balance or connection.");
    } finally {
      setLoading(false);
    }
  };

  const pollStatus = async (runId: string) => {
    const timer = setInterval(async () => {
      if (!token) {
        clearInterval(timer);
        return;
      }
      try {
        const res = await axios.get(`${API_BASE}/v1/execution/${runId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = res.data;
        
        setExecutions(prev => {
          const exists = prev.find(e => e.run_id === runId);
          if (exists) {
            return prev.map(e => e.run_id === runId ? data : e);
          }
          return [data, ...prev];
        });

        if (data.status === 'SUCCESS' || data.status === 'FAIL') {
          clearInterval(timer);
          fetchUserInfo();
        }
      } catch (err) {
        clearInterval(timer);
      }
    }, 2000);
  };

  const downloadReport = (runId: string) => {
    window.open(`${API_BASE}/v1/execution/${runId}/report?type=pdf&token=${token}`, '_blank');
  };

  if (!token) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen w-full flex flex-col">
      {/* 顶部导航 */}
      <nav className="fixed top-0 w-full h-14 glass z-[100] border-b border-black/[0.08]">
        <div className="container-custom h-full flex justify-between items-center">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2 cursor-pointer group" onClick={() => setActiveTab('execute')}>
              <div className="w-7 h-7 bg-black rounded-lg flex items-center justify-center transition-transform group-active:scale-90">
                <Sparkles className="text-white w-4 h-4" />
              </div>
              <span className="text-[17px] font-semibold tracking-tight">artfish</span>
            </div>
            
            {/* 桌面端菜单 */}
            <div className="hidden md:flex gap-6 text-[13px] text-black/60 font-medium">
              <button 
                onClick={() => setActiveTab('execute')} 
                className={`hover:text-black transition-colors ${activeTab === 'execute' ? 'text-black' : ''}`}
              >
                Engine
              </button>
              <button 
                onClick={() => setActiveTab('history')} 
                className={`hover:text-black transition-colors ${activeTab === 'history' ? 'text-black' : ''}`}
              >
                Audit Traces
              </button>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-[#f5f5f7] rounded-full border border-black/[0.04]">
              <Wallet className="w-3.5 h-3.5 text-black/40" />
              <span className="text-[13px] font-semibold">${userInfo?.balance.toFixed(2)}</span>
            </div>

            <div className="relative">
              <button 
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="w-8 h-8 rounded-full bg-apple-gray flex items-center justify-center hover:bg-black/5 transition-colors"
              >
                <User className="w-4 h-4 text-black/60" />
              </button>

              <AnimatePresence>
                {isProfileOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsProfileOpen(false)} />
                    <motion.div 
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute right-0 mt-2 w-64 card-apple p-2 z-50 overflow-hidden"
                    >
                      <div className="px-4 py-3 border-b border-black/[0.04]">
                        <p className="text-[13px] font-bold truncate">{userInfo?.email}</p>
                        <p className="text-[11px] text-black/40 font-medium mt-0.5">ID: {userInfo?.user_id}</p>
                      </div>
                      <div className="p-1">
                        <div className="px-3 py-2 space-y-1">
                           <p className="text-[10px] font-bold text-black/30 uppercase tracking-widest">Your API Key</p>
                           <code className="block bg-apple-gray p-2 rounded-lg text-[10px] font-mono break-all text-black/60">
                             {userInfo?.api_key}
                           </code>
                        </div>
                        <button 
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2 px-3 py-2 text-[13px] font-medium text-red-500 hover:bg-red-50 rounded-xl transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          Sign Out
                        </button>
                      </div>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
            
            {/* 移动端菜单按钮 */}
            <button className="md:hidden p-2" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </nav>

      {/* 移动端抽屉菜单 */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-[90] bg-white pt-20 px-6 md:hidden"
          >
            <div className="flex flex-col gap-8 text-2xl font-semibold">
              <button onClick={() => { setActiveTab('execute'); setIsMenuOpen(false); }}>Engine</button>
              <button onClick={() => { setActiveTab('history'); setIsMenuOpen(false); }}>Audit Traces</button>
              <div className="h-[1px] bg-black/10 w-full" />
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Balance</span>
                <span>${userInfo?.balance.toFixed(2)}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主体内容 */}
      <main className="flex-grow pt-24 pb-20 overflow-y-auto">
        <div className="container-custom">
          <AnimatePresence mode="wait">
            {activeTab === 'execute' ? (
              <motion.div 
                key="execute"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="space-y-12 md:space-y-20"
              >
                {/* 标题区域 */}
                <div className="space-y-6 max-w-2xl">
                  <motion.h1 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-[40px] md:text-[64px] leading-[1.1] font-bold tracking-tight"
                  >
                    Orchestrate <br />
                    <span className="text-black/30">Artistic Intents.</span>
                  </motion.h1>
                  <p className="text-[19px] md:text-[21px] leading-relaxed font-medium text-black/50">
                    A high-performance runtime for generative models. <br className="hidden md:block" />
                    Defined by you, executed by artfish.
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                  {/* 输入区域 */}
                  <div className="lg:col-span-8 space-y-6">
                    <div className="card-apple p-6 md:p-8 space-y-6">
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-[11px] font-bold text-black/40 uppercase tracking-[0.1em]">
                          <Zap className="w-3.5 h-3.5" />
                          Intent Goals
                        </div>
                        <textarea 
                          value={goals}
                          onChange={(e) => setGoals(e.target.value)}
                          placeholder="e.g. Cyberpunk landscape, neon-lit rainy streets, cinematic lighting..."
                          className="w-full h-48 md:h-64 bg-[#f5f5f7] rounded-2xl p-5 focus:ring-1 focus:ring-black/10 outline-none transition-all resize-none text-[17px] leading-relaxed placeholder:text-black/20"
                        />
                      </div>
                      
                      <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                        <div className="flex -space-x-2">
                           {[1,2,3].map(i => (
                             <div key={i} className="w-10 h-10 rounded-full border-2 border-white bg-[#f5f5f7] flex items-center justify-center">
                               <Cpu className="w-5 h-5 text-black/20" />
                             </div>
                           ))}
                           <div className="pl-4 text-[13px] font-medium text-black/40 flex items-center">
                             Model Agnostic
                           </div>
                        </div>
                        
                        <button 
                          onClick={handleSubmit}
                          disabled={loading || !goals}
                          className="w-full sm:w-auto h-12 px-10 btn-primary text-[15px]"
                        >
                          {loading ? 'Initializing Engine...' : 'Execute Runtime'}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 状态面板 */}
                  <div className="lg:col-span-4 space-y-6">
                    <div className="card-apple p-6 space-y-6">
                      <h3 className="text-[17px] font-bold tracking-tight">System Integrity</h3>
                      <div className="space-y-4">
                        <StatusRow icon={<ShieldCheck className="text-green-500" />} label="Backend" value="Secure" />
                        <StatusRow icon={<Clock className="text-blue-500" />} label="Celery" value="Async Ready" />
                        <StatusRow icon={<LayoutGrid className="text-orange-500" />} label="Storage" value="PostgreSQL" />
                      </div>
                    </div>

                    <div className="card-apple p-6 bg-black text-white overflow-hidden relative group">
                      <div className="relative z-10 space-y-4">
                        <p className="text-[11px] font-bold text-white/40 uppercase tracking-widest">Available Balance</p>
                        <h2 className="text-[36px] font-bold tracking-tight">${userInfo?.balance.toFixed(2)}</h2>
                        <div className="pt-2">
                          <button className="w-full py-3 bg-white/10 rounded-xl text-[13px] font-semibold backdrop-blur-md cursor-not-allowed opacity-50">
                            Refill coming soon
                          </button>
                        </div>
                      </div>
                      <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-white/5 rounded-full blur-2xl group-hover:bg-white/10 transition-colors" />
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                key="history"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="space-y-8"
              >
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 px-2">
                  <h2 className="text-[32px] md:text-[40px] font-bold tracking-tight">Audit Traces</h2>
                  <div className="text-[15px] text-black/40 font-medium">Immutable Execution Ledger</div>
                </div>

                <div className="space-y-4">
                  {executions.length === 0 ? (
                    <div className="card-apple py-32 flex flex-col items-center gap-4">
                      <div className="w-16 h-16 bg-[#f5f5f7] rounded-full flex items-center justify-center">
                        <History className="w-8 h-8 text-black/10" />
                      </div>
                      <p className="text-[17px] font-medium text-black/30 text-center">
                        No active traces found. <br />
                        Start an execution to begin.
                      </p>
                    </div>
                  ) : (
                    executions.map((exec) => (
                      <motion.div 
                        layout
                        key={exec.run_id}
                        className="card-apple p-5 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:shadow-[0_8px_32px_rgba(0,0,0,0.06)] transition-all group"
                      >
                        <div className="flex items-center gap-5">
                          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                            exec.status === 'SUCCESS' ? 'bg-green-50 text-green-600' : 
                            exec.status === 'FAIL' ? 'bg-red-50 text-red-600' : 
                            'bg-blue-50 text-blue-600'
                          }`}>
                            {exec.status === 'SUCCESS' ? <CheckCircle2 className="w-6 h-6" /> : 
                             exec.status === 'FAIL' ? <AlertCircle className="w-6 h-6" /> : <Zap className="w-6 h-6 animate-pulse" />}
                          </div>
                          
                          <div>
                            <div className="flex items-center gap-3">
                              <span className="font-bold text-[16px] tracking-tight">{exec.run_id.slice(0, 8).toUpperCase()}</span>
                              <span className={`text-[10px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider ${
                                exec.status === 'SUCCESS' ? 'bg-green-500 text-white' : 
                                exec.status === 'FAIL' ? 'bg-red-500 text-white' : 
                                'bg-blue-500 text-white'
                              }`}>{exec.status}</span>
                            </div>
                            <div className="flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-black/40 font-medium mt-1">
                              <span className="flex items-center gap-1"><Plus className="w-3 h-3" />{exec.actions_count} Actions</span>
                              <span className="flex items-center gap-1"><CreditCard className="w-3 h-3" />${exec.total_cost.toFixed(4)}</span>
                              <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(exec.start_time).toLocaleTimeString()}</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-3 border-t md:border-t-0 pt-4 md:pt-0">
                          {exec.status === 'SUCCESS' && (
                            <button 
                              onClick={() => downloadReport(exec.run_id)}
                              className="flex-grow md:flex-grow-0 h-10 px-6 btn-secondary text-[13px] flex items-center justify-center gap-2"
                            >
                              <Download className="w-4 h-4" />
                              Evidence PDF
                            </button>
                          )}
                          <div className="hidden md:flex w-10 h-10 items-center justify-center rounded-full hover:bg-[#f5f5f7] transition-colors cursor-pointer">
                            <ChevronRight className="w-5 h-5 text-black/20" />
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="py-10 border-t border-black/[0.04]">
        <div className="container-custom flex flex-col md:flex-row justify-between items-center gap-4 text-[12px] font-medium text-black/30">
          <p>© 2026 artfish Runtime. Built for precision.</p>
          <div className="flex gap-6">
            <span>Privacy</span>
            <span>Audit Terms</span>
            <span>Status</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function StatusRow({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <div className="flex items-center gap-3">
        <div className="w-4 h-4 flex items-center justify-center">
          {icon}
        </div>
        <span className="text-[14px] font-medium text-black/60">{label}</span>
      </div>
      <span className="text-[14px] font-bold text-black/80">{value}</span>
    </div>
  );
}

export default App;
