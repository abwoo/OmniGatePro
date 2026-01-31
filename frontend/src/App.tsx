import { useState, useEffect } from 'react';
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
  Copy,
  Check
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import AdminPage from './pages/AdminPage';
import api from './utils/api';

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
  const { t } = useTranslation();
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

  // 初始化 Guest ID
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
    } catch (err: unknown) {
      console.error("Failed to fetch user info", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        await api.get('/health');
        await fetchUserInfo();
      } catch (err: unknown) {
        console.error("Initialization failed", err);
      }
    };
    init();
  }, []);

  const handleLogout = () => {
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
    } catch {
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
      } catch {
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
    } catch {
      alert("Top-up failed. Please try again.");
    }
  };

  if (isAdminView && userInfo?.role === 'admin') {
    return <AdminPage onBack={() => setIsAdminView(false)} />;
  }

  return (
    <div className="min-h-screen w-full flex flex-col bg-[#FAFAFA] font-sans text-gray-900 selection:bg-indigo-100 selection:text-indigo-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full h-[72px] bg-white/80 backdrop-blur-xl z-[100] border-b border-gray-200/60 transition-all duration-300">
        <div className="max-w-7xl mx-auto h-full px-4 md:px-8 flex justify-between items-center">
          <div className="flex items-center gap-12">
            {/* Logo */}
            <motion.div 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-3 cursor-pointer group shrink-0" 
              onClick={() => setActiveTab('execute')}
            >
              <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center shadow-lg shadow-black/10 transition-shadow group-hover:shadow-black/20">
                <Sparkles className="text-white w-5 h-5" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight text-gray-900 leading-none">artfish</span>
                <span className="text-[10px] font-bold text-indigo-600 tracking-wide mt-0.5">V3.0 PRO</span>
              </div>
            </motion.div>
            
            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-1 bg-gray-100/50 p-1 rounded-full border border-gray-200/50">
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
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white rounded-full border border-gray-200 shadow-sm cursor-default"
            >
              <Wallet className="w-3.5 h-3.5 text-gray-400" />
              <span className="text-xs font-semibold text-gray-700 font-mono">${userInfo?.balance.toFixed(2)}</span>
            </motion.div>

            {/* Profile Menu */}
            <div className="relative">
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="w-10 h-10 rounded-full bg-gradient-to-tr from-gray-100 to-white flex items-center justify-center border border-gray-200 hover:border-indigo-200 hover:shadow-md transition-all"
              >
                <User className="w-5 h-5 text-gray-600" />
              </motion.button>

              <AnimatePresence>
                {isProfileOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsProfileOpen(false)} />
                    <motion.div 
                      initial={{ opacity: 0, y: 10, scale: 0.96 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.96 }}
                      transition={{ duration: 0.2, ease: "easeOut" }}
                      className="absolute right-0 mt-3 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden ring-1 ring-black/5"
                    >
                      <div className="px-6 py-5 border-b border-gray-100 bg-gray-50/50">
                        <p className="text-sm font-bold text-gray-900 truncate">{userInfo?.email}</p>
                        <p className="text-xs text-gray-500 font-medium mt-0.5 font-mono">ID: {userInfo?.user_id}</p>
                      </div>
                      <div className="p-2 space-y-1">
                        <div className="px-4 py-3">
                           <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">My Pass ID (Backup this)</p>
                           <motion.div 
                             whileHover={{ scale: 1.01, borderColor: '#6366f1' }}
                             whileTap={{ scale: 0.99 }}
                             onClick={() => {
                               navigator.clipboard.writeText(userInfo?.user_id || '');
                               setCopied(true);
                               setTimeout(() => setCopied(false), 2000);
                             }}
                             className="bg-gray-50 p-3 rounded-xl border border-gray-200 flex items-center justify-between group cursor-pointer transition-colors"
                           >
                             <code className="text-[11px] font-mono text-gray-600 truncate max-w-[180px]">
                               {userInfo?.user_id}
                             </code>
                             {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 text-gray-400 group-hover:text-indigo-500" />}
                           </motion.div>
                        </div>
                        
                        <div className="h-px bg-gray-100 my-1 mx-4" />

                        {userInfo?.role === 'admin' && (
                          <button 
                            onClick={() => { setIsAdminView(true); setIsProfileOpen(false); }}
                            className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-xl transition-colors"
                          >
                            <ShieldCheck className="w-4 h-4" />
                            Admin Console
                          </button>
                        )}
                        <button 
                          onClick={handleLogout}
                          className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-red-600 hover:bg-red-50 rounded-xl transition-colors"
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
            className="fixed inset-0 z-[90] bg-white/95 backdrop-blur-xl pt-24 px-6 md:hidden"
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

      <main className="flex-grow pt-32 pb-24 px-4 md:px-8 max-w-7xl mx-auto w-full">
        {/* Top-up Modal */}
        <AnimatePresence>
          {isTopupOpen && (
            <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsTopupOpen(false)}
                className="absolute inset-0 bg-black/20 backdrop-blur-sm"
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                transition={{ type: "spring", bounce: 0.3 }}
                className="relative w-full max-w-md bg-white rounded-[32px] p-8 shadow-2xl border border-gray-100 overflow-hidden"
              >
                <div className="flex justify-between items-center mb-8">
                  <h3 className="text-xl font-bold text-gray-900">Add Funds</h3>
                  <button onClick={() => setIsTopupOpen(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                    <X className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
                
                <div className="space-y-8">
                  <div className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl border border-indigo-100/50">
                    <p className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-2">Current Balance</p>
                    <p className="text-3xl font-bold text-indigo-900 font-mono tracking-tight">${userInfo?.balance.toFixed(2)}</p>
                  </div>

                  <div className="space-y-4">
                    <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Select Amount</label>
                    <div className="grid grid-cols-3 gap-3">
                      {['10', '50', '100'].map(amount => (
                        <motion.button 
                          key={amount}
                          whileHover={{ scale: 1.03 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => setTopupAmount(amount)}
                          className={`py-4 rounded-xl text-sm font-bold border-2 transition-all ${
                            topupAmount === amount 
                              ? 'border-indigo-600 bg-indigo-600 text-white shadow-lg shadow-indigo-200' 
                              : 'border-gray-100 text-gray-500 hover:border-gray-200 hover:bg-gray-50'
                          }`}
                        >
                          ${amount}
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  <div className="pt-4 space-y-4">
                    <p className="text-[11px] text-gray-400 text-center leading-relaxed max-w-xs mx-auto">
                      Secure payment simulation. No actual charges will be made.
                    </p>
                    <motion.button 
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={handleTopup}
                      className="w-full h-14 bg-black text-white rounded-2xl font-bold text-sm shadow-xl shadow-black/10 flex items-center justify-center gap-2"
                    >
                      <span>Confirm Payment</span>
                      <ChevronRight className="w-4 h-4" />
                    </motion.button>
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
                  transition={{ delay: 0.1 }}
                  className="text-display text-gray-900 mb-4"
                >
                  Design Intelligence.
                </motion.h1>
                <motion.p 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-lg text-gray-500 max-w-2xl leading-relaxed font-medium"
                >
                  Orchestrate complex generative workflows with precision. 
                  <span className="hidden md:inline"> Define your constraints, set your goals, and let the runtime handle the execution.</span>
                </motion.p>
              </div>

              {/* Main Input Area */}
              <div className="lg:col-span-8 space-y-6">
                <div className="ui-card p-1.5 border-gray-200/60">
                  <div className="bg-gray-50/50 rounded-[22px] p-6 md:p-8">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-2 bg-indigo-100 rounded-lg">
                        <Zap className="w-4 h-4 text-indigo-600" />
                      </div>
                      <span className="text-label">Command Center</span>
                    </div>
                    
                    <div className="relative group">
                      <div className="absolute -inset-2 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
                      <textarea 
                        value={goals}
                        onChange={(e) => setGoals(e.target.value)}
                        placeholder="Describe your intent..."
                        className="relative w-full h-48 md:h-64 bg-white rounded-xl border border-gray-200 p-6 text-lg md:text-xl text-gray-900 placeholder:text-gray-300 font-medium leading-relaxed resize-none outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all shadow-sm"
                      />
                    </div>
                    
                    <div className="h-px w-full bg-gray-200 my-8" />
                    
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-6">
                      <div className="flex items-center gap-3">
                         <div className="flex -space-x-2">
                           {[1,2,3].map(i => (
                             <div key={i} className="w-8 h-8 rounded-full border-2 border-gray-50 bg-white flex items-center justify-center shadow-sm">
                               <Cpu className="w-3.5 h-3.5 text-gray-400" />
                             </div>
                           ))}
                         </div>
                         <span className="text-xs font-bold text-gray-400">AUTO-SCALING ENABLED</span>
                      </div>
                      
                      <motion.button 
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleSubmit}
                        disabled={loading || !goals}
                        className="w-full sm:w-auto h-14 px-8 bg-black text-white rounded-2xl font-bold flex items-center justify-center gap-3 shadow-xl shadow-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transition-all"
                      >
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                        <span className="text-sm">Run Execution</span>
                      </motion.button>
                    </div>
                  </div>
                </div>
              </div>

                <div className="lg:col-span-4 space-y-6">
                  <div className="ui-card p-6">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-sm font-bold text-gray-900">System Status</h3>
                      <span className="flex h-2.5 w-2.5 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                      </span>
                    </div>
                    <div className="space-y-3">
                      <StatusRow icon={<ShieldCheck className="text-emerald-500" />} label="Security" value="Active" />
                      <StatusRow icon={<Box className="text-blue-500" />} label="Nodes" value="3/3 Online" />
                      <StatusRow icon={<LayoutGrid className="text-purple-500" />} label="Database" value="Healthy" />
                    </div>
                  </div>

                  <motion.div 
                    whileHover={{ scale: 1.02, rotate: 1 }}
                    className="bg-gradient-to-br from-gray-900 to-black rounded-[32px] p-8 text-white relative overflow-hidden group shadow-2xl shadow-gray-900/20 cursor-pointer"
                    onClick={() => setIsTopupOpen(true)}
                  >
                    <div className="relative z-10">
                      <p className="text-xs font-bold text-white/40 uppercase tracking-widest mb-3">Available Credits</p>
                      <h2 className="text-4xl font-bold tracking-tight font-mono mb-8">${userInfo?.balance.toFixed(2)}</h2>
                      <div className="flex items-center gap-2 text-sm font-bold text-white/90 group-hover:text-white transition-colors">
                        <Wallet className="w-4 h-4" />
                        <span>Top-up Credits</span>
                        <ChevronRight className="w-4 h-4 ml-auto opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                      </div>
                    </div>
                    <div className="absolute top-0 right-0 -mr-12 -mt-12 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:bg-white/15 transition-colors duration-500" />
                  </motion.div>
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
                  <p className="text-gray-500 mt-2 font-medium">Immutable ledger of all runtime executions.</p>
                </div>
              </div>

              <div className="grid gap-4">
                {executions.length === 0 ? (
                  <div className="ui-card py-32 border-dashed flex flex-col items-center gap-4 bg-gray-50/50">
                    <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center shadow-sm border border-gray-100">
                      <History className="w-8 h-8 text-gray-300" />
                    </div>
                    <p className="text-gray-400 font-medium">No execution history found</p>
                  </div>
                ) : (
                  executions.map((exec) => (
                    <motion.div 
                      layout
                      key={exec.run_id}
                      className="ui-card p-6 hover:border-indigo-200 group flex flex-col sm:flex-row sm:items-center justify-between gap-6"
                    >
                      <div className="flex items-start sm:items-center gap-6">
                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 shadow-sm border ${
                          exec.status === 'SUCCESS' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : 
                          exec.status === 'FAIL' ? 'bg-red-50 border-red-100 text-red-600' : 
                          'bg-blue-50 border-blue-100 text-blue-600'
                        }`}>
                          {exec.status === 'SUCCESS' ? <CheckCircle2 className="w-7 h-7" /> : 
                           exec.status === 'FAIL' ? <AlertCircle className="w-7 h-7" /> : <Zap className="w-7 h-7 animate-pulse" />}
                        </div>
                        
                        <div>
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-bold text-gray-900 font-mono text-lg tracking-tight">{exec.run_id.slice(0, 8)}</span>
                            <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                              exec.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-700' : 
                              exec.status === 'FAIL' ? 'bg-red-100 text-red-700' : 
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {exec.status}
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-5 text-xs font-bold text-gray-500">
                            <span className="flex items-center gap-1.5"><Plus className="w-3.5 h-3.5" />{exec.actions_count} Actions</span>
                            <span className="flex items-center gap-1.5 text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md"><CreditCard className="w-3.5 h-3.5" />${exec.total_cost.toFixed(4)}</span>
                            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />{new Date(exec.start_time).toLocaleTimeString()}</span>
                          </div>
                        </div>
                      </div>

                      {exec.status === 'SUCCESS' && (
                        <motion.button 
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => downloadReport(exec.run_id)}
                          className="w-full sm:w-auto h-12 px-6 rounded-xl bg-gray-50 text-gray-700 font-bold text-sm hover:bg-gray-100 transition-colors flex items-center justify-center gap-2 border border-gray-200"
                        >
                          <Download className="w-4 h-4" />
                          Report
                        </motion.button>
                      )}
                    </motion.div>
                  ))
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

// UI Components
const NavButton = ({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) => (
  <motion.button 
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    onClick={onClick}
    className={`
      flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold transition-all relative
      ${active ? 'text-gray-900 bg-white shadow-sm' : 'text-gray-500 hover:text-gray-900'}
    `}
  >
    {icon}
    <span>{label}</span>
  </motion.button>
);

const MobileNavButton = ({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) => (
  <button 
    onClick={onClick}
    className={`
      flex items-center gap-4 p-4 rounded-2xl text-lg font-bold transition-all w-full
      ${active ? 'bg-gray-900 text-white shadow-lg' : 'bg-gray-50 text-gray-600'}
    `}
  >
    {icon}
    <span>{label}</span>
  </button>
);

const StatusRow = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
  <div className="flex items-center justify-between p-3.5 rounded-2xl bg-gray-50/50 border border-transparent hover:border-gray-100 transition-colors">
    <div className="flex items-center gap-3">
      <div className="w-6 h-6 flex items-center justify-center bg-white rounded-lg shadow-sm border border-gray-100">{icon}</div>
      <span className="text-sm font-bold text-gray-500">{label}</span>
    </div>
    <span className="text-sm font-bold text-gray-900">{value}</span>
  </div>
);

const Loader2 = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);

const ChevronRight = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m9 18 6-6-6-6"/>
  </svg>
);

export default App;
