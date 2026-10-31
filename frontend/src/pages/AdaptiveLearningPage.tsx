import React, { useState, useEffect } from 'react';
import {
  Brain, RotateCcw, CheckCircle2, TrendingUp, History,
  ShieldCheck, AlertTriangle, Layers, Clock
} from 'lucide-react';
import { api } from '../services/api';
import { AdaptiveObservation } from '../types';

export const AdaptiveLearningPage: React.FC = () => {
  const [observations, setObservations] = useState<AdaptiveObservation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadAdaptations();
  }, []);

  const loadAdaptations = async () => {
    setLoading(true);
    try {
      const data = await api.getAdaptationHistory();
      setObservations(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (modelId: string, taskCategory: string) => {
    if (!window.confirm(`Revert empirical quality score for ${modelId} on ${taskCategory}?`)) {
      return;
    }
    try {
      const res = await api.rollbackAdaptation(modelId, taskCategory);
      setMessage(res.message);
      loadAdaptations();
    } catch (e: any) {
      alert(e.message || 'Rollback failed');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Adaptive Learning & Empirical Feedback Loop
          </h1>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
            Bayesian Smoothing Active
          </span>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Historical request telemetry updates model suitability statistics. Includes confidence thresholds and rollback controls.
        </p>
      </div>

      {message && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Explanatory Banner */}
      <div className="p-4 rounded-2xl bg-white border border-surface-border shadow-subtle flex items-start gap-3 text-xs">
        <Brain className="w-5 h-5 text-forest-700 shrink-0 mt-0.5" />
        <div className="text-slate-600 leading-relaxed">
          <strong className="text-slate-900">Safeguarded Adaptation Logic:</strong> AstraRoute AI applies an exponential moving average (alpha = 0.20) 
          and minimum sample thresholds to verify empirical model outcomes without drastic shifts from transient network glitches. Operators can inspect the full update rationale or roll back any adjustment.
        </div>
      </div>

      {/* Observations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {observations.map((obs, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-white border border-surface-border shadow-subtle flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-surface-muted text-slate-600 font-mono">
                    {obs.task_category}
                  </span>
                  <h3 className="mt-1.5 text-base font-bold text-slate-900">
                    {obs.model_id}
                  </h3>
                </div>

                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                  {obs.sample_count} Samples
                </span>
              </div>

              {/* Empirical Metrics */}
              <div className="mt-4 p-3 rounded-xl bg-surface-muted border border-slate-100 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block">Empirical Quality</span>
                  <span className="font-mono font-bold text-forest-900 text-sm">
                    {(obs.empirical_quality_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Observed Latency</span>
                  <span className="font-mono font-bold text-slate-800 text-sm">
                    {obs.empirical_latency_ms.toFixed(0)}ms
                  </span>
                </div>
              </div>

              {/* History Snippet */}
              <div className="mt-3 text-xs space-y-1">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                  <History className="w-3 h-3" />
                  <span>Recent Score Updates</span>
                </span>
                <div className="space-y-1">
                  {obs.update_history?.slice(-2).map((h, i) => (
                    <div key={i} className="text-[11px] text-slate-600 p-1.5 rounded bg-slate-50 border border-slate-100">
                      <span className="font-mono font-medium text-slate-800">
                        {(h.old_score * 100).toFixed(0)}% → {(h.new_score * 100).toFixed(0)}%:
                      </span>{' '}
                      <span className="text-slate-500">{h.reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Action */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[10px] text-slate-400">
                Success: {(obs.success_rate * 100).toFixed(0)}%
              </span>
              <button
                onClick={() => handleRollback(obs.model_id, obs.task_category)}
                className="px-2.5 py-1 rounded-lg bg-surface-muted hover:bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200 flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3 text-slate-500" />
                <span>Rollback Score</span>
              </button>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

