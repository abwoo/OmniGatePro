import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Mail, 
  Lock, 
  ArrowRight, 
  Loader2, 
  Github, 
  Chrome, 
  ShieldCheck, 
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2,
  XCircle,
  Settings
} from 'lucide-react';
import { validatePasswordStrength, getPasswordStrengthScore, sanitizeInput } from '../utils/security';
import SliderCaptcha from '../components/SliderCaptcha';
import api, { setApiUrl } from '../utils/api';

interface LoginPageProps {
  onLogin: (token: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<{ label: string; met: boolean }[]>([]);
  const [strengthScore, setStrengthScore] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [tempApiUrl, setTempApiUrl] = useState(localStorage.getItem('artfish_api_url') || 'http://localhost:8000');

  useEffect(() => {
    if (!isLogin) {
      const strength = validatePasswordStrength(password);
      setPasswordStrength(strength);
      setStrengthScore(getPasswordStrengthScore(password));
    }
  }, [password, isLogin]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!captchaVerified) {
      setError('Please slide to verify your identity');
      return;
    }

    if (!isLogin && strengthScore < 100) {
      setError('Password security requirements not met');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const cleanEmail = sanitizeInput(email);
      
      if (isLogin) {
        const params = new URLSearchParams();
        params.append('username', cleanEmail);
        params.append('password', password);
        
        const res = await api.post('/v1/auth/token', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        onLogin(res.data.access_token);
      } else {
        const res = await api.post('/v1/auth/register', {
          email: cleanEmail,
          password: password
        });
        onLogin(res.data.access_token);
      }
    } catch (err: any) {
      console.error("Auth error:", err);
      if (!err.response) {
        setError('Cannot reach server. Is the backend running?');
      } else {
        setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
      }
      setCaptchaVerified(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd] p-6 relative overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-apple-blue/5 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-purple-500/5 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[420px] z-10"
      >
        <div className="text-center mb-10">
          <motion.div 
            whileHover={{ scale: 1.05, rotate: 5 }}
            className="inline-flex w-16 h-16 bg-black rounded-2xl items-center justify-center shadow-2xl mb-6 cursor-pointer"
          >
            <Sparkles className="text-white w-9 h-9" />
          </motion.div>
          <h1 className="text-3xl font-bold tracking-tight text-apple-dark mb-2">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-[15px] font-medium text-black/40">
            Artfish Runtime v0.1.0 • Enterprise Ready
          </p>
        </div>

        <div className="card-apple p-8 md:p-10 relative bg-white/80 backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field - New Flex Layout */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">
                Identity
              </label>
              <div className="flex items-center bg-apple-gray rounded-xl h-12 px-4 focus-within:bg-white focus-within:ring-2 focus-within:ring-apple-blue/10 transition-all border border-transparent focus-within:border-apple-blue/20">
                <Mail className="w-4 h-4 text-black/20 shrink-0" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="flex-grow bg-transparent border-none outline-none ml-3 text-[15px] font-medium text-apple-dark placeholder:text-black/20"
                />
              </div>
            </div>

            {/* Password Field - New Flex Layout */}
            <div className="space-y-2">
              <div className="flex justify-between items-center px-1">
                <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest">
                  Security Key
                </label>
                {isLogin && (
                  <button type="button" className="text-[11px] font-bold text-apple-blue hover:opacity-70 transition-opacity">
                    Lost access?
                  </button>
                )}
              </div>
              <div className="flex items-center bg-apple-gray rounded-xl h-12 px-4 focus-within:bg-white focus-within:ring-2 focus-within:ring-apple-blue/10 transition-all border border-transparent focus-within:border-apple-blue/20">
                <Lock className="w-4 h-4 text-black/20 shrink-0" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="flex-grow bg-transparent border-none outline-none ml-3 text-[15px] font-medium text-apple-dark placeholder:text-black/20"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-black/20 hover:text-black/40 transition-colors ml-2"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Password Strength */}
              {!isLogin && password.length > 0 && (
                <div className="pt-2 space-y-3 px-1">
                  <div className="h-1 w-full bg-apple-gray rounded-full overflow-hidden">
                    <motion.div 
                      className={`h-full transition-colors ${
                        strengthScore < 40 ? 'bg-red-500' : 
                        strengthScore < 80 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      initial={{ width: 0 }}
                      animate={{ width: `${strengthScore}%` }}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {passwordStrength.map((req, i) => (
                      <div key={i} className="flex items-center gap-2">
                        {req.met ? <CheckCircle2 className="w-3 h-3 text-green-500" /> : <XCircle className="w-3 h-3 text-black/10" />}
                        <span className={`text-[10px] font-bold ${req.met ? 'text-black/60' : 'text-black/30'}`}>{req.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Captcha */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">
                Human Verification
              </label>
              <SliderCaptcha onSuccess={() => setCaptchaVerified(true)} />
            </div>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="flex items-center gap-3 p-4 bg-red-50 rounded-xl text-red-600 border border-red-100"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="text-[12px] font-bold leading-tight">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <button 
              type="submit"
              disabled={loading || (!isLogin && strengthScore < 100) || !captchaVerified}
              className="w-full h-12 btn-primary flex items-center justify-center gap-2 group relative overflow-hidden shadow-lg shadow-apple-blue/20 active:scale-[0.98] transition-all"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="font-bold text-[15px]">{isLogin ? 'Sign In' : 'Create Account'}</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Settings / API URL toggle */}
          <div className="mt-8 pt-6 border-t border-black/[0.04] space-y-4">
            <div className="flex justify-center gap-4">
              <button 
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setCaptchaVerified(false);
                }}
                className="text-[13px] font-bold text-apple-blue hover:opacity-70"
              >
                {isLogin ? "Join artfish" : "Have an account?"}
              </button>
              <span className="text-black/10">|</span>
              <button 
                onClick={() => setShowSettings(!showSettings)}
                className="text-[13px] font-bold text-black/30 hover:text-black/60 flex items-center gap-1"
              >
                <Settings className="w-3.5 h-3.5" />
                API Config
              </button>
            </div>

            {showSettings && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-3 pt-2"
              >
                <div className="bg-apple-gray p-3 rounded-xl space-y-2">
                  <p className="text-[10px] font-black text-black/30 uppercase tracking-widest">Target Backend URL</p>
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      value={tempApiUrl}
                      onChange={(e) => setTempApiUrl(e.target.value)}
                      className="flex-grow bg-white border border-black/5 rounded-lg px-3 py-1.5 text-xs font-mono"
                    />
                    <button 
                      onClick={() => setApiUrl(tempApiUrl)}
                      className="bg-black text-white text-[10px] font-bold px-3 py-1.5 rounded-lg"
                    >
                      Apply
                    </button>
                  </div>
                  <p className="text-[9px] text-black/20 font-medium">Changing this will reload the page.</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        <div className="mt-10 text-center flex flex-col items-center gap-4">
          <div className="flex items-center gap-2 text-[10px] font-bold text-black/20 uppercase tracking-[0.2em]">
            <ShieldCheck className="w-3.5 h-3.5" />
            SOC2 Type II • ISO 27001
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
