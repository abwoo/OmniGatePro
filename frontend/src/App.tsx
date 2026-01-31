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
  User,
  Activity,
  Box,
  Terminal,
  Key,
  Copy,
  Check
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import AdminPage from './pages/AdminPage';
import api from './utils/api';
import { v4 as uuidv4 } from 'uuid';

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
  role: string;
}

function App() {
  const { t, i18n } = useTranslation();
  const [activeTab, setActiveTab] = useState('execute');
  const [isAdminView, setIsAdminView] = useState(false);
  const [goals, setGoals] = useState('');
  const [loading, setLoading] = useState(false);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isTopupOpen, setIsTopupOpen] = useState(false);
  const [topupAmount, setTopupAmount] = useState('10');
  const [copied, setCopied] = useState(false);

  // 初始化 Guest ID (商业化：无感登录核心)
  useEffect(() => {
    let guestId = localStorage.getItem('artfish_guest_id');
    if (!guestId) {
      guestId = 'guest_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('artfish_guest_id', guestId);
    }
  }, []);

  const fetchUserInfo = async () => {
    try {
      const res = await api.get('/v1/user/me');
      setUserInfo(res.data);
    } catch (err: any) {
      console.error("Failed to fetch user info", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        await api.get('/health');
        await fetchUserInfo();
      } catch (err) {
        console.error("Initialization failed", err);
      }
    };
    init();
  }, []);

  const handleLogout = () => {
    // 在匿名模式下，登出意味着重置 ID (清除钱包)
    if (window.confirm("Warning: Logging out will discard your current Guest ID and Balance. Continue?")) {
      localStorage.removeItem('artfish_guest_id');
      localStorage.removeItem('artfish_token');
      window.location.reload();
    }
  };

  const handleSubmit = async () => {
    if (!goals) return;
    setLoading(true);
    try {
      const res = await api.post('/v1/execute', {
        goals: goals.split(',').map(g => g.trim()),
        user_id: userInfo?.user_id || 'test_user',
        constraints: { style: 'photorealistic' }
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
      try {
        const res = await api.get(`/v1/execution/${runId}`);
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

  const downloadReport = (run_id: string) => {
    window.open(`http://localhost:8000/v1/execution/${run_id}/report?type=pdf`, '_blank');
  };

  const handleTopup = async () => {
    try {
      await api.post('/v1/user/topup', null, { params: { amount: parseFloat(topupAmount) } });
      await fetchUserInfo();
      setIsTopupOpen(false);
      alert("Success! Credits added.");
    } catch (err) {
      alert("Top-up failed. Please try again.");
    }
  };

  if (isAdminView && userInfo?.role === 'admin') {
    return <AdminPage onBack={() => setIsAdminView(false)} />;
  }

  return (
    <div className="min-h-screen w-full flex flex-col bg-gray-50/50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full h-16 bg-white/80 backdrop-blur-xl z-[100] border-b border-gray-200/60">
        <div className="max-w-6xl mx-auto h-full px-4 md:px-6 flex justify-between items-center">
          <div className="flex items-center gap-10">
            {/* Logo */}
            <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setActiveTab('execute')}>
              <div className="w-9 h-9 bg-black rounded-xl flex items-center justify-center transition-transform group-active:scale-95 shadow-lg shadow-black/10">
                <Sparkles className="text-white w-5 h-5" />
              </div>
              <span className="text-lg font-bold tracking-tight text-gray-900">artfish</span>
              <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full ml-1">V2.0 LIVE</span>
            </div>
            
            {/* Desktop Menu */}
            <div className="hidden md:flex gap-1">
              <NavButton 
                active={activeTab === 'execute'} 
                onClick={() => setActiveTab('execute')}
                icon={<Terminal className="w-4 h-4" />}
                label={t('engine')}
              />
              <NavButton 
                active={activeTab === 'history'} 
                onClick={() => setActiveTab('history')}
                icon={<Activity className="w-4 h-4" />}
                label={t('audit')}
              />
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Balance Badge */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white rounded-full border border-gray-200 shadow-sm">
              <Wallet className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-xs font-semibold text-gray-700 font-mono">${userInfo?.balance.toFixed(2)}</span>
            </div>

            {/* Profile Menu */}
            <div className="relative">
              <button 
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="w-9 h-9 rounded-full bg-gradient-to-tr from-gray-100 to-gray-200 flex items-center justify-center border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <User className="w-4 h-4 text-gray-600" />
              </button>

              <AnimatePresence>
                {isProfileOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsProfileOpen(false)} />
                    <motion.div 
                      initial={{ opacity: 0, y: 8, scale: 0.96 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.96 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 mt-3 w-72 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden ring-1 ring-black/5"
                    >
                      <div className="px-5 py-4 border-b border-gray-100 bg-gray-50/50">
                        <p className="text-sm font-bold text-gray-900 truncate">{userInfo?.email}</p>
                        <p className="text-xs text-gray-500 font-medium mt-0.5 font-mono">ID: {userInfo?.user_id}</p>
                      </div>
                      <div className="p-2 space-y-1">
                        <div className="px-3 py-2">
                           <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">My Pass ID (Backup this)</p>
                           <div 
                             onClick={() => {
                               navigator.clipboard.writeText(userInfo?.user_id || '');
                               setCopied(true);
                               setTimeout(() => setCopied(false), 2000);
                             }}
                             className="bg-gray-50 p-2.5 rounded-lg border border-gray-100 flex items-center justify-between group cursor-pointer hover:border-blue-200 transition-colors"
                           >
                             <code className="text-[10px] font-mono text-gray-600 truncate max-w-[180px]">
                               {userInfo?.user_id}
                             </code>
                             {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3 text-gray-300 group-hover:text-blue-500" />}
                           </div>
                        </div>
                        
                        <div className="h-px bg-gray-100 my-1 mx-3" />

                        {userInfo?.role === 'admin' && (
                          <button 
                            onClick={() => { setIsAdminView(true); setIsProfileOpen(false); }}
                            className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-xl transition-colors"
                          >
                            <ShieldCheck className="w-4 h-4" />
                            Admin Console
                          </button>
                        )}
                        <button 
                          onClick={handleLogout}
                          className="w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 rounded-xl transition-colors"
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
            
            <button className="md:hidden p-2 text-gray-600" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-[90] bg-white pt-24 px-6 md:hidden"
          >
            <div className="flex flex-col gap-6">
              <MobileNavButton 
                active={activeTab === 'execute'} 
                onClick={() => { setActiveTab('execute'); setIsMenuOpen(false); }}
                icon={<Terminal className="w-5 h-5" />}
                label="Runtime Engine"
              />
              <MobileNavButton 
                active={activeTab === 'history'} 
                onClick={() => { setActiveTab('history'); setIsMenuOpen(false); }}
                icon={<Activity className="w-5 h-5" />}
                label="Audit Traces"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="flex-grow pt-28 pb-20 px-4 md:px-6">
        <div className="max-w-6xl mx-auto">
          {/* Top-up Modal */}
          <AnimatePresence>
            {isTopupOpen && (
              <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsTopupOpen(false)}
                  className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                />
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 20 }}
                  className="relative w-full max-w-md bg-white rounded-[32px] p-8 shadow-2xl border border-gray-100"
                >
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-gray-900">Top-up Credits</h3>
                    <button onClick={() => setIsTopupOpen(false)} className="p-2 hover:bg-gray-100 rounded-full">
                      <X className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="p-4 bg-blue-50 rounded-2xl border border-blue-100">
                      <p className="text-xs font-semibold text-blue-600 uppercase tracking-wider mb-1">Current Balance</p>
                      <p className="text-2xl font-bold text-blue-900">${userInfo?.balance.toFixed(2)}</p>
                    </div>

                    <div className="space-y-3">
                      <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Select Amount</label>
                      <div className="grid grid-cols-3 gap-3">
                        {['10', '50', '100'].map(amount => (
                          <button 
                            key={amount}
                            onClick={() => setTopupAmount(amount)}
                            className={`py-3 rounded-xl text-sm font-bold border-2 transition-all ${
                              topupAmount === amount ? 'border-blue-500 bg-blue-50 text-blue-600' : 'border-gray-100 text-gray-400 hover:border-gray-200'
                            }`}
                          >
                            ${amount}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="pt-4 space-y-3">
                      <p className="text-[10px] text-gray-400 text-center leading-relaxed">
                        Simulation: Clicking "Confirm Payment" will instantly add credits to your account. 
                        In production, this would redirect to Stripe or Alipay.
                      </p>
                      <button 
                        onClick={handleTopup}
                        className="w-full h-12 btn-primary shadow-lg shadow-blue-500/20"
                      >
                        Confirm Payment
                      </button>
                    </div>
                  </div>
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          <AnimatePresence mode="wait">
            {activeTab === 'execute' ? (
              <motion.div 
                key="execute"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"
              >
                {/* Hero Section */}
                <div className="lg:col-span-12 mb-8">
                  <motion.h1 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-4xl md:text-5xl font-bold tracking-tight text-gray-900 mb-4"
                  >
                    Design Intelligence.
                  </motion.h1>
                  <p className="text-lg text-gray-500 max-w-2xl leading-relaxed">
                    Orchestrate complex generative workflows with precision. 
                    <span className="hidden md:inline"> Define your constraints, set your goals, and let the runtime handle the execution.</span>
                  </p>
                </div>

                {/* Main Input Area */}
                <div className="lg:col-span-8 space-y-6">
                  <div className="bg-white rounded-[24px] p-1 shadow-xl shadow-black/[0.02] border border-gray-100">
                    <div className="bg-gray-50/50 rounded-[20px] p-6 md:p-8">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="p-1.5 bg-blue-100 rounded-lg">
                          <Zap className="w-4 h-4 text-blue-600" />
                        </div>
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Execution Parameters</span>
                      </div>
                      
                      <textarea 
                        value={goals}
                        onChange={(e) => setGoals(e.target.value)}
                        placeholder="Describe your intent..."
                        className="w-full h-48 md:h-64 bg-transparent border-none outline-none resize-none text-lg md:text-xl text-gray-900 placeholder:text-gray-300 font-medium leading-relaxed"
                      />
                      
                      <div className="h-px w-full bg-gray-200 my-6" />
                      
                      <div className="flex flex-col sm:flex-row justify-between items-center gap-6">
                        <div className="flex items-center gap-3">
                           <div className="flex -space-x-2">
                             {[1,2,3].map(i => (
                               <div key={i} className="w-8 h-8 rounded-full border-2 border-gray-50 bg-white flex items-center justify-center shadow-sm">
                                 <Cpu className="w-3.5 h-3.5 text-gray-400" />
                               </div>
                             ))}
                           </div>
                           <span className="text-xs font-semibold text-gray-400">Auto-scaling enabled</span>
                        </div>
                        
                        <button 
                          onClick={handleSubmit}
                          disabled={loading || !goals}
                          className="w-full sm:w-auto h-12 px-8 btn-primary flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
                        >
                          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                          <span className="font-semibold">{loading ? 'Processing...' : 'Run Execution'}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                  <div className="lg:col-span-4 space-y-6">
                    <div className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-sm font-bold text-gray-900">System Status</h3>
                        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">LIVE</span>
                      </div>
                      <div className="space-y-4">
                        <StatusRow icon={<ShieldCheck className="text-emerald-500" />} label="Security" value="Active" />
                        <StatusRow icon={<Box className="text-blue-500" />} label="Nodes" value="3/3 Online" />
                        <StatusRow icon={<LayoutGrid className="text-purple-500" />} label="Database" value="Healthy" />
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-gray-900 to-black rounded-3xl p-8 text-white relative overflow-hidden group shadow-xl">
                      <div className="relative z-10">
                        <p className="text-xs font-bold text-white/40 uppercase tracking-widest mb-2">Available Credits</p>
                        <h2 className="text-4xl font-bold tracking-tight font-mono mb-6">${userInfo?.balance.toFixed(2)}</h2>
                        <button 
                          onClick={() => setIsTopupOpen(true)}
                          className="w-full py-3 bg-white text-black rounded-xl text-sm font-bold hover:bg-gray-100 transition-all flex items-center justify-center gap-2"
                        >
                          <Wallet className="w-4 h-4" />
                          Top-up Credits
                        </button>
                      </div>
                      <div className="absolute top-0 right-0 -mr-12 -mt-12 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:bg-white/15 transition-colors duration-500" />
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
                <div className="flex items-end justify-between px-1">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Audit Traces</h2>
                    <p className="text-gray-500 mt-1">Immutable ledger of all runtime executions.</p>
                  </div>
                </div>

                <div className="grid gap-4">
                  {executions.length === 0 ? (
                    <div className="bg-white rounded-3xl py-32 border border-gray-100 border-dashed flex flex-col items-center gap-4">
                      <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center">
                        <History className="w-8 h-8 text-gray-300" />
                      </div>
                      <p className="text-gray-400 font-medium">No execution history found</p>
                    </div>
                  ) : (
                    executions.map((exec) => (
                      <div 
                        key={exec.run_id}
                        className="bg-white rounded-2xl p-5 border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all group flex flex-col sm:flex-row sm:items-center justify-between gap-6"
                      >
                        <div className="flex items-start sm:items-center gap-5">
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                            exec.status === 'SUCCESS' ? 'bg-emerald-50 text-emerald-600' : 
                            exec.status === 'FAIL' ? 'bg-red-50 text-red-600' : 
                            'bg-blue-50 text-blue-600'
                          }`}>
                            {exec.status === 'SUCCESS' ? <CheckCircle2 className="w-6 h-6" /> : 
                             exec.status === 'FAIL' ? <AlertCircle className="w-6 h-6" /> : <Zap className="w-6 h-6 animate-pulse" />}
                          </div>
                          
                          <div>
                            <div className="flex items-center gap-3 mb-1">
                              <span className="font-bold text-gray-900 font-mono text-lg">{exec.run_id.slice(0, 8)}</span>
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                exec.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-700' : 
                                exec.status === 'FAIL' ? 'bg-red-100 text-red-700' : 
                                'bg-blue-100 text-blue-700'
                              }`}>
                                {exec.status}
                              </span>
                            </div>
                            <div className="flex flex-wrap gap-4 text-xs font-medium text-gray-500">
                              <span className="flex items-center gap-1.5"><Plus className="w-3.5 h-3.5" />{exec.actions_count} Actions</span>
                              <span className="flex items-center gap-1.5 text-blue-600"><CreditCard className="w-3.5 h-3.5" />Cost: ${exec.total_cost.toFixed(4)}</span>
                              <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />{new Date(exec.start_time).toLocaleTimeString()}</span>
                            </div>
                          </div>
                        </div>

                        {exec.status === 'SUCCESS' && (
                          <button 
                            onClick={() => downloadReport(exec.run_id)}
                            className="w-full sm:w-auto h-10 px-5 rounded-xl bg-gray-50 text-gray-700 font-medium text-sm hover:bg-gray-100 transition-colors flex items-center justify-center gap-2 border border-gray-100"
                          >
                            <Download className="w-4 h-4" />
                            Report
                          </button>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

// UI Components
const NavButton = ({ active, onClick, icon, label }: any) => (
  <button 
    onClick={onClick}
    className={`
      flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all
      ${active ? 'bg-gray-900 text-white shadow-md' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900'}
    `}
  >
    {icon}
    <span>{label}</span>
  </button>
);

const MobileNavButton = ({ active, onClick, icon, label }: any) => (
  <button 
    onClick={onClick}
    className={`
      flex items-center gap-4 p-4 rounded-2xl text-lg font-medium transition-all w-full
      ${active ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-600'}
    `}
  >
    {icon}
    <span>{label}</span>
  </button>
);

const StatusRow = ({ icon, label, value }: any) => (
  <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50/50">
    <div className="flex items-center gap-3">
      <div className="w-5 h-5 flex items-center justify-center">{icon}</div>
      <span className="text-sm font-medium text-gray-600">{label}</span>
    </div>
    <span className="text-sm font-bold text-gray-900">{value}</span>
  </div>
);

const Loader2 = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

export default App;
