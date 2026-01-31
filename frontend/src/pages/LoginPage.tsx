import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Mail, 
  Lock, 
  ArrowRight, 
  Loader2, 
  ShieldCheck, 
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2,
  XCircle,
  Settings,
  ChevronRight
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
      setError('Please verify you are human');
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
        setError(err.response?.data?.detail || 'Authentication failed');
      }
      setCaptchaVerified(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#FAFAFA] p-4 md:p-8 relative overflow-hidden">
      {/* Background - Subtle Gradient */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-50/50 via-white to-purple-50/50" />
        <div className="absolute -top-[20%] -right-[10%] w-[800px] h-[800px] rounded-full bg-gradient-to-br from-blue-100/40 to-transparent blur-3xl opacity-60" />
        <div className="absolute -bottom-[20%] -left-[10%] w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-purple-100/40 to-transparent blur-3xl opacity-60" />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-[440px] z-10"
      >
        <div className="ui-card p-8 md:p-10 shadow-xl shadow-black/[0.03]">
          {/* Header */}
          <div className="text-center mb-8 space-y-3">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-black text-white shadow-lg shadow-black/20 mb-2">
              <Sparkles className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-gray-900">
              {isLogin ? 'Welcome back' : 'Create an account'}
            </h1>
            <p className="text-sm text-gray-500 font-medium">
              Enter your credentials to access the runtime.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 ml-1 uppercase tracking-wider">Email</label>
              <div className="ui-input-group">
                <Mail className="absolute left-4 w-5 h-5 text-gray-400 pointer-events-none" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="ui-input pl-11"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center px-1">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Password</label>
                {isLogin && (
                  <button type="button" className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors">
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="ui-input-group">
                <Lock className="absolute left-4 w-5 h-5 text-gray-400 pointer-events-none" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="ui-input pl-11 pr-12"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 text-gray-400 hover:text-gray-600 transition-colors p-1"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Password Strength Indicator */}
              <AnimatePresence>
                {!isLogin && password.length > 0 && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="pt-2 space-y-2 overflow-hidden"
                  >
                    <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
                      <motion.div 
                        className={`h-full transition-colors duration-300 ${
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
                            <CheckCircle2 className="w-3.5 h-3.5 text-green-500 shrink-0" />
                          ) : (
                            <div className="w-3.5 h-3.5 rounded-full border border-gray-300 shrink-0" />
                          )}
                          <span className={`text-[11px] font-medium ${req.met ? 'text-gray-700' : 'text-gray-400'}`}>
                            {req.label}
                          </span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Captcha */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-500 ml-1 uppercase tracking-wider">Security Check</label>
              <SliderCaptcha onSuccess={() => setCaptchaVerified(true)} />
            </div>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-start gap-3 p-3 bg-red-50 rounded-xl text-red-600 border border-red-100/50"
                >
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span className="text-xs font-medium leading-relaxed">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <button 
              type="submit"
              disabled={loading || (!isLogin && strengthScore < 100) || !captchaVerified}
              className="w-full h-12 btn-primary flex items-center justify-center gap-2 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin text-white/80" />
              ) : (
                <>
                  <span className="text-[15px]">{isLogin ? 'Sign In' : 'Create Account'}</span>
                  <ArrowRight className="w-4 h-4 opacity-80" />
                </>
              )}
            </button>
          </form>

          {/* Footer / Toggle */}
          <div className="mt-8 pt-6 border-t border-gray-100">
            <div className="flex flex-col gap-4">
              <button 
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setCaptchaVerified(false);
                }}
                className="text-sm font-medium text-gray-600 hover:text-black transition-colors flex items-center justify-center gap-1 group"
              >
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <span className="text-blue-600 group-hover:underline decoration-blue-600/30 underline-offset-2">
                  {isLogin ? "Sign up" : "Log in"}
                </span>
              </button>

              {/* API Config Toggle */}
              <div className="flex justify-center">
                <button 
                  onClick={() => setShowSettings(!showSettings)}
                  className="text-[11px] font-semibold text-gray-400 hover:text-gray-600 flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-gray-100 transition-all"
                >
                  <Settings className="w-3 h-3" />
                  <span>Server Config</span>
                  <ChevronRight className={`w-3 h-3 transition-transform ${showSettings ? 'rotate-90' : ''}`} />
                </button>
              </div>

              {/* Settings Panel */}
              <AnimatePresence>
                {showSettings && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="bg-gray-50 p-4 rounded-xl space-y-3 border border-gray-100">
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Backend URL</p>
                        <div className="flex gap-2">
                          <input 
                            type="text" 
                            value={tempApiUrl}
                            onChange={(e) => setTempApiUrl(e.target.value)}
                            className="flex-grow bg-white border border-gray-200 rounded-lg px-3 py-2 text-xs font-mono text-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                          />
                          <button 
                            onClick={() => setApiUrl(tempApiUrl)}
                            className="bg-black text-white text-[10px] font-bold px-3 py-1.5 rounded-lg hover:bg-gray-800 transition-colors"
                          >
                            Save
                          </button>
                        </div>
                      </div>
                      <p className="text-[10px] text-gray-400 leading-relaxed">
                        If running locally, use <code className="bg-gray-200 px-1 rounded">http://localhost:8000</code>.
                        <br />For production, ensure the server supports CORS.
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/50 backdrop-blur border border-white/20 shadow-sm">
            <ShieldCheck className="w-3.5 h-3.5 text-green-600" />
            <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
              End-to-End Encrypted
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
