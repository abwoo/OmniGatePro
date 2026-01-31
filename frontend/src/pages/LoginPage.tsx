import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Mail, Lock, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';

interface LoginPageProps {
  onLogin: (token: string) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        const res = await axios.post('http://localhost:8000/v1/auth/token', formData);
        onLogin(res.data.access_token);
      } else {
        const res = await axios.post('http://localhost:8000/v1/auth/register', {
          email,
          password
        });
        onLogin(res.data.access_token);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd] px-6">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[400px] space-y-8"
      >
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 bg-black rounded-xl flex items-center justify-center">
            <Sparkles className="text-white w-7 h-7" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-center">
            {isLogin ? 'Sign in to artfish' : 'Create your account'}
          </h1>
          <p className="text-black/40 text-sm font-medium">
            Experience the future of AI orchestration.
          </p>
        </div>

        <div className="card-apple p-8 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-black/20 group-focus-within:text-apple-blue transition-colors" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  required
                  className="w-full h-12 bg-[#f5f5f7] rounded-xl pl-11 pr-4 outline-none focus:ring-1 focus:ring-apple-blue/20 transition-all text-[15px]"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[11px] font-bold text-black/40 uppercase tracking-widest ml-1">Password</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-black/20 group-focus-within:text-apple-blue transition-colors" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full h-12 bg-[#f5f5f7] rounded-xl pl-11 pr-4 outline-none focus:ring-1 focus:ring-apple-blue/20 transition-all text-[15px]"
                />
              </div>
            </div>

            {error && (
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-red-500 text-xs font-medium text-center"
              >
                {error}
              </motion.p>
            )}

            <button 
              type="submit"
              disabled={loading}
              className="w-full h-12 btn-primary flex items-center justify-center gap-2 group"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  {isLogin ? 'Sign In' : 'Create Account'}
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-black/[0.04]"></div>
            </div>
            <div className="relative flex justify-center text-[11px] uppercase tracking-widest">
              <span className="bg-white px-4 text-black/20 font-bold">Or continue with</span>
            </div>
          </div>

          <button 
            onClick={() => setIsLogin(!isLogin)}
            className="w-full text-sm font-semibold text-apple-blue hover:underline"
          >
            {isLogin ? "Don't have an account? Create one" : "Already have an account? Sign in"}
          </button>
        </div>

        <p className="text-center text-[12px] text-black/30 font-medium">
          By continuing, you agree to artfish's <br />
          <span className="text-black/60 cursor-pointer hover:underline">Terms of Service</span> and <span className="text-black/60 cursor-pointer hover:underline">Privacy Policy</span>.
        </p>
      </motion.div>
    </div>
  );
};

export default LoginPage;
