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
  XCircle
} from 'lucide-react';
import { validatePasswordStrength, getPasswordStrengthScore, sanitizeInput } from '../utils/security';
import SliderCaptcha from '../components/SliderCaptcha';
import api from '../utils/api';

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
      setError('Please slide to verify');
      return;
    }

    if (!isLogin && strengthScore < 100) {
      setError('Security requirements not met');
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
      console.error("Login/Register error:", err);
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Authentication failed. Please check your credentials.');
      setCaptchaVerified(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd] p-6">
      {/* Background Glow */}
      <div className="fixed inset-0 overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-apple-blue/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-500/10 rounded-full blur-[120px]" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[400px]"
      >
        <div className="text-center mb-10">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="inline-flex w-16 h-16 bg-black rounded-2xl items-center justify-center shadow-2xl mb-6"
          >
            <Sparkles className="text-white w-9 h-9" />
          </motion.div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            {isLogin ? 'Welcome Back' : 'Get Started'}
          </h1>
          <p className="text-[15px] font-medium text-black/40">
            Secure access to artfish runtime v0.1.0
          </p>
        </div>

        <div className="card-apple p-8 md:p-10">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">
                Email Address
              </label>
              <div className="relative h-12">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                  <Mail className="w-4 h-4 text-black/20" />
                </div>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  required
                  className="w-full h-full bg-apple-gray border-none rounded-xl pl-11 pr-4 text-[15px] font-medium outline-none focus:bg-white focus:ring-1 focus:ring-apple-blue/20 transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <div className="flex justify-between items-center px-1">
                <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest">
                  Password
                </label>
                {isLogin && (
                  <button type="button" className="text-[11px] font-bold text-apple-blue">
                    Reset
                  </button>
                )}
              </div>
              <div className="relative h-12">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                  <Lock className="w-4 h-4 text-black/20" />
                </div>
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full h-full bg-apple-gray border-none rounded-xl pl-11 pr-12 text-[15px] font-medium outline-none focus:bg-white focus:ring-1 focus:ring-apple-blue/20 transition-all"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-4 flex items-center text-black/20 hover:text-black/40 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Strength UI */}
              {!isLogin && password.length > 0 && (
                <div className="pt-2 space-y-3">
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
                        {req.met ? (
                          <CheckCircle2 className="w-3 h-3 text-green-500 shrink-0" />
                        ) : (
                          <XCircle className="w-3 h-3 text-black/10 shrink-0" />
                        )}
                        <span className={`text-[10px] font-bold ${req.met ? 'text-black/60' : 'text-black/30'}`}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Captcha Section */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">
                Bot Protection
              </label>
              <SliderCaptcha onSuccess={() => setCaptchaVerified(true)} />
            </div>

            {/* Error UI */}
            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="flex items-center gap-3 p-4 bg-red-50 rounded-xl text-red-600 border border-red-100"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="text-xs font-bold leading-tight">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <button 
              type="submit"
              disabled={loading || (!isLogin && strengthScore < 100) || !captchaVerified}
              className="w-full h-12 btn-primary relative overflow-hidden flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="font-bold text-[15px]">{isLogin ? 'Sign In' : 'Create Account'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-black/[0.04] space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <button 
                onClick={() => setError('OAuth available in Pro plan')}
                className="h-12 bg-white border border-apple-border rounded-xl flex items-center justify-center gap-3 hover:bg-apple-gray transition-all active:scale-[0.98]"
              >
                <Chrome className="w-4 h-4 text-black/60" />
                <span className="text-[13px] font-bold text-black/70">Google</span>
              </button>
              <button 
                onClick={() => setError('OAuth available in Pro plan')}
                className="h-12 bg-white border border-apple-border rounded-xl flex items-center justify-center gap-3 hover:bg-apple-gray transition-all active:scale-[0.98]"
              >
                <Github className="w-4 h-4 text-black/60" />
                <span className="text-[13px] font-bold text-black/70">GitHub</span>
              </button>
            </div>

            <button 
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setCaptchaVerified(false);
              }}
              className="w-full text-[13px] font-bold text-apple-blue"
            >
              {isLogin ? "Create an account" : "Sign in to existing account"}
            </button>
          </div>
        </div>

        <div className="mt-8 text-center flex items-center justify-center gap-2 text-[11px] font-bold text-black/20 uppercase tracking-[0.1em]">
          <ShieldCheck className="w-4 h-4" />
          SOC2 Type II & GDPR Compliant
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
