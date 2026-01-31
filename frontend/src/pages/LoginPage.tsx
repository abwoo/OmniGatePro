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
      setError('Please complete the security verification');
      return;
    }

    if (!isLogin && strengthScore < 100) {
      setError('Please use a stronger password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const cleanEmail = sanitizeInput(email);
      
      if (isLogin) {
        // OAuth2PasswordRequestForm expects x-www-form-urlencoded
        const params = new URLSearchParams();
        params.append('username', cleanEmail);
        params.append('password', password);
        
        const res = await api.post('/v1/auth/token', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
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
      const msg = err.response?.data?.detail || err.message || 'Authentication failed';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
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
    <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd] px-4 py-8">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-apple-blue/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/5 rounded-full blur-[120px]" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[420px] z-10"
      >
        <div className="flex flex-col items-center gap-6 mb-10">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-16 h-16 bg-black rounded-[22%] flex items-center justify-center shadow-2xl shadow-black/20"
          >
            <Sparkles className="text-white w-9 h-9" />
          </motion.div>
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-apple-dark">
              {isLogin ? 'Sign In' : 'Create Account'}
            </h1>
            <p className="text-[15px] font-medium text-black/40">
              The professional runtime for AI artists.
            </p>
          </div>
        </div>

        <div className="card-apple p-8 md:p-10 relative">
          {loading && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-[2px] z-50 flex flex-col items-center justify-center rounded-[24px]">
              <Loader2 className="w-8 h-8 text-apple-blue animate-spin mb-2" />
              <span className="text-xs font-bold text-apple-blue uppercase tracking-widest">Verifying...</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2 group">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1 transition-colors group-focus-within:text-apple-blue">
                Email Address
              </label>
              <div className="relative flex items-center">
                <Mail className="absolute left-4 w-4 h-4 text-black/20 group-focus-within:text-apple-blue transition-colors z-10" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="w-full h-12 bg-[#f5f5f7] border border-transparent rounded-xl pl-11 pr-4 outline-none focus:border-apple-blue/20 focus:bg-white transition-all text-[15px] text-apple-dark font-medium placeholder:text-black/20"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2 group">
              <div className="flex justify-between items-center px-1">
                <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest transition-colors group-focus-within:text-apple-blue">
                  Password
                </label>
                {isLogin && (
                  <button type="button" className="text-[11px] font-bold text-apple-blue hover:opacity-70 transition-opacity">
                    Forgot?
                  </button>
                )}
              </div>
              <div className="relative flex items-center">
                <Lock className="absolute left-4 w-4 h-4 text-black/20 group-focus-within:text-apple-blue transition-colors z-10" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full h-12 bg-[#f5f5f7] border border-transparent rounded-xl pl-11 pr-12 outline-none focus:border-apple-blue/20 focus:bg-white transition-all text-[15px] text-apple-dark font-medium placeholder:text-black/20"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 text-black/20 hover:text-black/40 transition-colors z-10"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Password Strength Indicator */}
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
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
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
                </motion.div>
              )}
            </div>

            {/* Captcha */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">
                Verify you are human
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
                  className="flex items-center gap-3 p-3.5 bg-red-50 rounded-xl text-red-600 border border-red-100"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="text-xs font-bold leading-snug">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <button 
              type="submit"
              disabled={loading || (!isLogin && strengthScore < 100) || !captchaVerified}
              className="w-full h-12 btn-primary flex items-center justify-center gap-2 group relative overflow-hidden shadow-lg shadow-apple-blue/20"
            >
              <span className="relative z-10 flex items-center gap-2 font-bold text-[15px]">
                {isLogin ? 'Sign In' : 'Create Account'}
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
          </form>

          {/* OAuth & Toggle */}
          <div className="mt-8 space-y-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-black/[0.04]"></div>
              </div>
              <div className="relative flex justify-center text-[11px] uppercase tracking-[0.2em] font-black">
                <span className="bg-white px-4 text-black/20">OR</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <OAuthButton icon={<Chrome className="w-4 h-4" />} label="Google" onClick={() => handleOAuthLogin('Google')} />
              <OAuthButton icon={<Github className="w-4 h-4" />} label="GitHub" onClick={() => handleOAuthLogin('GitHub')} />
            </div>

            <button 
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setCaptchaVerified(false);
              }}
              className="w-full py-2 text-[13px] font-bold text-apple-blue hover:opacity-70 transition-all"
            >
              {isLogin ? "New to artfish? Create an account" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-10 text-center space-y-4">
          <div className="flex items-center justify-center gap-2 text-[10px] font-bold text-black/20 uppercase tracking-[0.15em]">
            <ShieldCheck className="w-3.5 h-3.5" />
            End-to-end encrypted
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const OAuthButton = ({ icon, label, onClick }: { icon: React.ReactNode, label: string, onClick: () => void }) => (
  <button 
    onClick={onClick}
    className="h-12 border border-apple-border rounded-xl flex items-center justify-center gap-2.5 hover:bg-apple-gray transition-all active:scale-[0.98] group"
  >
    <span className="text-black/60 group-hover:text-black transition-colors">{icon}</span>
    <span className="text-[13px] font-bold text-black/70 group-hover:text-black">{label}</span>
  </button>
);

export default LoginPage;
