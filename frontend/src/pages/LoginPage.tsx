import React from 'react';
import { Sparkles, Shield, ArrowRight, CheckCircle2, Lock } from 'lucide-react';

interface LoginPageProps {
  onLogin: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  return (
    <div className="min-h-screen bg-surface-ground flex flex-col justify-center items-center p-4 font-sans">
      <div className="w-full max-w-md bg-white rounded-3xl border border-surface-border shadow-elevated p-8 md:p-10 space-y-6 animate-fade-in">
        
        {/* Logo and Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-forest-800 text-white flex items-center justify-center mx-auto shadow-card">
            <Sparkles className="w-6 h-6 text-emerald-200" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            AstraRoute AI
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Autonomous AI FinOps & Intelligent Model Routing
          </p>
        </div>

        {/* Feature Badges */}
        <div className="bg-surface-muted rounded-2xl p-4 border border-slate-200/80 space-y-2 text-xs text-slate-700">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-forest-700 shrink-0" />
            <span>Autonomous multi-objective routing engine</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-forest-700 shrink-0" />
            <span>Real-time Cost Per Successful Outcome (CPSO)</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-forest-700 shrink-0" />
            <span>Quality Guardian task verification & fallback</span>
          </div>
        </div>

        {/* Access Button */}
        <div className="space-y-3 pt-2">
          <button
            onClick={onLogin}
            className="w-full py-3.5 px-4 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-semibold text-xs tracking-wider uppercase shadow-card flex items-center justify-center gap-2 transition-all"
          >
            <span>Enter Enterprise Demo</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          
          <div className="flex items-center justify-center gap-1.5 text-[11px] text-slate-400">
            <Lock className="w-3.5 h-3.5" />
            <span>Autonomous AI FinOps & Intelligent Model Routing</span>
          </div>
        </div>

      </div>
    </div>
  );
};

