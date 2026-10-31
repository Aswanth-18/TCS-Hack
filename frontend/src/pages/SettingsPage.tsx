import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon, Shield, Key, Database, Cpu,
  CheckCircle2, XCircle, Info, RefreshCw, ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { SystemHealth } from '../types';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    setLoading(true);
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const providers = [
    { name: 'OpenAI API', key: 'openai', desc: 'GPT-4o, GPT-4o-mini', env: 'OPENAI_API_KEY' },
    { name: 'Anthropic Claude API', key: 'anthropic', desc: 'Claude 3.5 Sonnet, Haiku', env: 'ANTHROPIC_API_KEY' },
    { name: 'Google Gemini API', key: 'gemini', desc: 'Gemini 1.5 Pro, Flash', env: 'GEMINI_API_KEY' },
    { name: 'Groq LPU Acceleration', key: 'groq', desc: 'Llama 3.3 70B (High-Speed)', env: 'GROQ_API_KEY' },
  ];

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          System Configuration & Provider Settings
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage AI provider API credentials, database persistence engine, and enterprise FinOps thresholds.
        </p>
      </div>

      {/* Gateway Operating Mode Card */}
      <div className="p-6 rounded-2xl bg-white border border-surface-border shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
              Current Operating Engine
            </span>
            <span className="text-xs text-slate-500">AstraRoute Gateway</span>
          </div>
          <h2 className="mt-1.5 text-lg font-bold text-slate-900">
            {health?.mode || 'High-Fidelity Simulator Mode'}
          </h2>
          <p className="mt-1 text-xs text-slate-500 max-w-xl leading-relaxed">
            When valid API credentials are provided in <code className="bg-slate-100 px-1.5 py-0.5 rounded font-mono text-slate-700">.env</code>, 
            AstraRoute automatically calls real model providers. When keys are absent, the gateway activates the integrated high-fidelity simulator.
          </p>
        </div>

        <button
          onClick={loadHealth}
          disabled={loading}
          className="px-4 py-2 bg-surface-muted hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl border border-slate-200 transition-colors flex items-center gap-2 shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-Check Health</span>
        </button>
      </div>

      {/* Provider Connectivity Grid */}
      <div className="bg-white rounded-2xl p-6 border border-surface-border shadow-subtle space-y-4">
        <div className="pb-3 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">
            AI Provider Credentials Diagnostic
          </h3>
          <p className="text-xs text-slate-500">
            Securely detected from server-side environment variables. Secret values are never exposed to the client.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {providers.map((p) => {
            const isConfigured = health?.providers ? health.providers[p.key] : false;
            return (
              <div
                key={p.key}
                className="p-4 rounded-xl bg-surface-muted border border-slate-200 flex items-start justify-between"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">{p.name}</span>
                    <span className="text-[10px] font-mono text-slate-400">({p.env})</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">{p.desc}</p>
                </div>

                {isConfigured ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 shrink-0">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Active
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200 shrink-0">
                    <XCircle className="w-3.5 h-3.5 text-slate-400" /> Simulator Fallback
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Persistence Engine */}
      <div className="bg-white rounded-2xl p-6 border border-surface-border shadow-subtle space-y-3 text-xs">
        <div className="pb-3 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-forest-700" />
            <h3 className="text-sm font-bold text-slate-900">Persistence & Database Engine</h3>
          </div>
          <span className="font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
            Connected
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-700">
          <div className="p-3 bg-surface-muted rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Database Engine</span>
            <span className="font-semibold font-mono text-slate-900 mt-0.5 block">
              {health?.database.engine || 'SQLite (Local Zero-Config)'}
            </span>
          </div>
          <div className="p-3 bg-surface-muted rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Registered Models</span>
            <span className="font-semibold font-mono text-slate-900 mt-0.5 block">
              {health?.database.models_registered || 10} Models Active
            </span>
          </div>
        </div>

        <p className="text-slate-500 leading-relaxed pt-1">
          Supports local zero-config SQLite persistence out of the box and seamlessly switches to enterprise 
          Supabase PostgreSQL when <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">DATABASE_URL</code> is defined.
        </p>
      </div>

      {/* Global Fallback & Safety Defaults */}
      <div className="bg-white rounded-2xl p-6 border border-surface-border shadow-subtle space-y-3 text-xs">
        <div className="pb-3 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-900">
            Gateway Policy Defaults
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3 bg-surface-muted rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Default Request Budget Cap</span>
            <span className="font-bold font-mono text-forest-900 mt-0.5 block">$0.050</span>
          </div>
          <div className="p-3 bg-surface-muted rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Default Quality Baseline</span>
            <span className="font-bold font-mono text-slate-800 mt-0.5 block">70.0%</span>
          </div>
          <div className="p-3 bg-surface-muted rounded-xl border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Max Fallback Retries</span>
            <span className="font-bold font-mono text-slate-800 mt-0.5 block">2 Retries</span>
          </div>
        </div>
      </div>

    </div>
  );
};

