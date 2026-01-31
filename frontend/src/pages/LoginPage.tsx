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
      setError('Please complete the verification');
      return;
    }

    if (!isLogin && strengthScore < 100) {
      setError('Password is not strong enough');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const cleanEmail = sanitizeInput(email);
      const cleanPassword = password;

      if (isLogin) {
        const formData = new FormData();
        formData.append('username', cleanEmail);
        formData.append('password', cleanPassword);
        
        const res = await api.post('/v1/auth/token', formData);
        onLogin(res.data.access_token);
      } else {
        const res = await api.post('/v1/auth/register', {
          email: cleanEmail,
          password: cleanPassword
        });
        onLogin(res.data.access_token);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
      setCaptchaVerified(false);
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthLogin = (provider: string) => {
    console.log(`Logging in with ${provider}...`);
    setError(`OAuth with ${provider} is currently in sandbox mode.`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd] px-6 py-12">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-apple-blue via-purple-500 to-pink-500" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[440px] space-y-8"
      >
        <div className="flex flex-col items-center gap-4">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-14 h-14 bg-black rounded-2xl flex items-center justify-center shadow-xl shadow-black/10"
          >
            <Sparkles className="text-white w-8 h-8" />
          </motion.div>
          <div className="text-center space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">
              {isLogin ? 'Welcome Back' : 'Join artfish'}
            </h1>
            <p className="text-black/40 text-[15px] font-medium">
              Enterprise-grade artistic agent runtime.
            </p>
          </div>
        </div>

        <div className="card-apple p-8 md:p-10 space-y-8 relative overflow-hidden">
          {loading && (
            <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-50 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-apple-blue animate-spin" />
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2 group">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1 transition-colors group-focus-within:text-apple-blue">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-black/20 group-focus-within:text-apple-blue transition-colors" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  required
                  autoComplete="email"
                  aria-label="Email Address"
                  className="w-full h-12 bg-[#f5f5f7] border border-transparent rounded-xl pl-11 pr-4 outline-none focus:border-apple-blue/20 focus:bg-white transition-all text-[15px]"
                />
              </div>
            </div>

            <div className="space-y-2 group">
              <div className="flex justify-between items-center px-1">
                <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest transition-colors group-focus-within:text-apple-blue">
                  Password
                </label>
                {isLogin && (
                  <button type="button" className="text-[11px] font-bold text-apple-blue hover:underline">
                    Forgot?
                  </button>
                )}
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-black/20 group-focus-within:text-apple-blue transition-colors" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  aria-label="Password"
                  className="w-full h-12 bg-[#f5f5f7] border border-transparent rounded-xl pl-11 pr-12 outline-none focus:border-apple-blue/20 focus:bg-white transition-all text-[15px]"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-black/20 hover:text-black/40 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {!isLogin && password.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="pt-2 space-y-3"
                >
                  <div className="h-1.5 w-full bg-apple-gray rounded-full overflow-hidden">
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
                      <div key={i} className="flex items-center gap-1.5">
                        {req.met ? (
                          <CheckCircle2 className="w-3 h-3 text-green-500" />
                        ) : (
                          <XCircle className="w-3 h-3 text-black/10" />
                        )}
                        <span className={`text-[10px] font-medium ${req.met ? 'text-black/60' : 'text-black/30'}`}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">
                Security Verification
              </label>
              <SliderCaptcha onSuccess={() => setCaptchaVerified(true)} />
            </div>

            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="flex items-center gap-2 p-3 bg-red-50 rounded-xl text-red-600 border border-red-100"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="text-xs font-semibold leading-tight">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <button 
              type="submit"
              disabled={loading || (!isLogin && strengthScore < 100) || !captchaVerified}
              className="w-full h-12 btn-primary flex items-center justify-center gap-2 group relative overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-2">
                {isLogin ? 'Sign In' : 'Create Account'}
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
              <motion.div 
                className="absolute inset-0 bg-white/10"
                initial={{ x: '-100%' }}
                whileHover={{ x: '100%' }}
                transition={{ duration: 0.6 }}
              />
            </button>
          </form>

          <div className="space-y-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-black/[0.04]"></div>
              </div>
              <div className="relative flex justify-center text-[11px] uppercase tracking-widest">
                <span className="bg-white px-4 text-black/20 font-black">Secure OAuth2</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button 
                onClick={() => handleOAuthLogin('Google')}
                className="h-12 border border-apple-border rounded-xl flex items-center justify-center gap-2 hover:bg-apple-gray transition-all active:scale-[0.98]"
              >
                <Chrome className="w-4 h-4" />
                <span className="text-[13px] font-bold">Google</span>
              </button>
              <button 
                onClick={() => handleOAuthLogin('GitHub')}
                className="h-12 border border-apple-border rounded-xl flex items-center justify-center gap-2 hover:bg-apple-gray transition-all active:scale-[0.98]"
              >
                <Github className="w-4 h-4" />
                <span className="text-[13px] font-bold">GitHub</span>
              </button>
            </div>

            <button 
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setCaptchaVerified(false);
              }}
              className="w-full text-[13px] font-bold text-apple-blue hover:text-apple-blue/80 transition-colors"
            >
              {isLogin ? "Don't have an account? Create one" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>

        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2 text-[11px] font-bold text-black/20 uppercase tracking-widest">
            <ShieldCheck className="w-3.5 h-3.5" />
            SOC2 Type II Compliant
          </div>
          <p className="text-[12px] text-black/30 font-medium leading-relaxed">
            By continuing, you agree to artfish's <br />
            <span className="text-black/60 cursor-pointer hover:underline font-bold">Terms of Service</span> and <span className="text-black/60 cursor-pointer hover:underline font-bold">Privacy Policy</span>.
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
