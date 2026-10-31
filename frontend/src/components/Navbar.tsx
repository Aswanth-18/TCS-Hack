import React from 'react';
import { Sparkles, Shield, Cpu, Activity, LogOut, User } from 'lucide-react';
import { SystemHealth } from '../types';

interface NavbarProps {
  health: SystemHealth | null;
  onLogout?: () => void;
  isAuthenticated?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ health, onLogout, isAuthenticated }) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-40 h-16 bg-white/95 backdrop-blur-md border-b border-surface-border px-6 flex items-center justify-between transition-all">
      {/* Left Branding */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-forest-800 flex items-center justify-center text-white shadow-card">
          <Sparkles className="w-5 h-5 text-emerald-200" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base tracking-tight text-slate-900">
              AstraRoute AI
            </span>
            <span className="hidden sm:inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full bg-forest-50 text-forest-800 border border-forest-200">
              Autonomous AI FinOps Gateway
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium">
            Autonomous AI FinOps & Intelligent Model Routing
          </p>
        </div>
      </div>

      {/* Right Environment Context & Demo User */}
      <div className="flex items-center gap-3 text-xs">
        {/* Truthful Engine Mode */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-surface-muted border border-surface-border text-slate-600">
          <Cpu className="w-3.5 h-3.5 text-forest-700" />
          <span>Engine: <strong className="text-slate-800">{health?.mode || 'High-Fidelity Simulator'}</strong></span>
        </div>

        {/* Active Policy Version */}
        <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-forest-50/60 border border-forest-100 text-forest-900">
          <Shield className="w-3.5 h-3.5 text-forest-700" />
          <span>Active Policy: <strong>v{health?.active_policy?.version || 3} (Intelligent)</strong></span>
        </div>

        {/* Demo User Pill */}
        {isAuthenticated && (
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-muted text-slate-700 text-xs font-medium">
              <User className="w-3.5 h-3.5 text-slate-500" />
              <span>Operator Demo</span>
            </div>
            {onLogout && (
              <button
                onClick={onLogout}
                title="Switch to Demo Login"
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
};
