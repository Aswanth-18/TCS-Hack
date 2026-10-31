import React, { useState, useEffect } from 'react';
import {
  Lightbulb, Sparkles, CheckCircle2, XCircle, ArrowRight,
  TrendingDown, ShieldAlert, Check, X, RefreshCw, Layers, Database
} from 'lucide-react';
import { api } from '../services/api';
import { FinOpsRecommendation } from '../types';

export const RecommendationsPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<FinOpsRecommendation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<'pending' | 'all' | 'applied' | 'dismissed'>('pending');

  useEffect(() => {
    loadRecs();
  }, []);

  const loadRecs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRecommendations();
      setRecommendations(data || []);
      // Notify application of live count
      window.dispatchEvent(new CustomEvent('recommendations-updated'));
    } catch (e: any) {
      console.error(e);
      setError(e.message || 'Failed to load recommendations');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (id: string) => {
    try {
      const res = await api.applyRecommendation(id);
      setMessage(res.message);
      await loadRecs();
      window.dispatchEvent(new CustomEvent('recommendations-updated'));
    } catch (e: any) {
      alert(e.message || 'Failed to apply recommendation');
    }
  };

  const handleDismiss = async (id: string) => {
    try {
      await api.dismissRecommendation(id);
      await loadRecs();
      window.dispatchEvent(new CustomEvent('recommendations-updated'));
    } catch (e: any) {
      alert(e.message || 'Failed to dismiss');
    }
  };

  const pendingCount = recommendations.filter((r) => r.status === 'pending').length;
  const appliedCount = recommendations.filter((r) => r.status === 'applied').length;
  const dismissedCount = recommendations.filter((r) => r.status === 'dismissed').length;

  const totalProjectedSavings = recommendations
    .filter((r) => r.status === 'pending')
    .reduce((sum, r) => sum + r.expected_monthly_savings_usd, 0);

  const displayedRecs = recommendations.filter((r) => {
    if (statusFilter === 'all') return true;
    return r.status === statusFilter;
  });

  return (
    <div className="space-y-6 animate-fade-in w-full">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Autonomous FinOps Recommendations
            </h1>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
              {pendingCount} Actionable
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Automated intelligence detecting overspending, underutilized economy tiers, and caching opportunities.
          </p>
        </div>

        {/* Savings Badge */}
        <div className="px-4 py-2.5 rounded-2xl bg-gradient-to-r from-forest-800 to-forest-600 text-white shadow-card flex items-center gap-2 self-start sm:self-auto">
          <TrendingDown className="w-5 h-5 text-emerald-300" />
          <div>
            <div className="text-[10px] uppercase font-bold text-emerald-200">Actionable Monthly Savings</div>
            <div className="text-lg font-bold">${totalProjectedSavings.toLocaleString()}/month</div>
          </div>
        </div>
      </div>

      {message && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{message}</span>
          </div>
          <button onClick={() => setMessage(null)} className="p-1 hover:opacity-75">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-2 bg-white rounded-2xl border border-surface-border shadow-subtle text-xs">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setStatusFilter('pending')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition-all ${
              statusFilter === 'pending'
                ? 'bg-forest-50 text-forest-900 border border-forest-200 shadow-subtle'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            Actionable Pending ({pendingCount})
          </button>

          <button
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition-all ${
              statusFilter === 'all'
                ? 'bg-forest-50 text-forest-900 border border-forest-200 shadow-subtle'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            All Recommendations ({recommendations.length})
          </button>

          <button
            onClick={() => setStatusFilter('applied')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition-all ${
              statusFilter === 'applied'
                ? 'bg-forest-50 text-forest-900 border border-forest-200 shadow-subtle'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            Applied ({appliedCount})
          </button>

          <button
            onClick={() => setStatusFilter('dismissed')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition-all ${
              statusFilter === 'dismissed'
                ? 'bg-forest-50 text-forest-900 border border-forest-200 shadow-subtle'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
            }`}
          >
            Dismissed ({dismissedCount})
          </button>
        </div>

        <button
          onClick={loadRecs}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-surface-muted hover:bg-slate-100 text-slate-700 font-semibold rounded-xl border border-slate-200 transition-colors ml-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Sync Telemetry</span>
        </button>
      </div>

      {loading && (
        <div className="p-12 text-center text-slate-400 text-xs">
          <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-forest-700" />
          <span>Analyzing inference telemetry and calculating savings...</span>
        </div>
      )}

      {/* Cards List */}
      {!loading && (
        <div className="space-y-4">
        {displayedRecs.map((rec) => {
          const isPending = rec.status === 'pending';
          const isApplied = rec.status === 'applied';
          const isDismissed = rec.status === 'dismissed';
          const isTelemetryDerived = rec.supporting_data?.source === 'telemetry_derived';

          return (
            <div
              key={rec.id}
              className={`p-6 rounded-2xl border transition-all ${
                isApplied
                  ? 'bg-emerald-50/30 border-emerald-200'
                  : isDismissed
                  ? 'bg-slate-50/70 border-slate-200 opacity-60'
                  : 'bg-white border-surface-border shadow-subtle hover:border-forest-300'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                
                {/* Details */}
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      rec.severity === 'high' ? 'bg-rose-100 text-rose-800' :
                      rec.severity === 'medium' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {rec.severity} Priority
                    </span>

                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-surface-muted text-slate-600 font-mono">
                      {rec.category.replace('_', ' ')}
                    </span>

                    {/* Honest Origin Source Label */}
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                      isTelemetryDerived
                        ? 'bg-forest-50 text-forest-900 border-forest-200'
                        : 'bg-blue-50 text-blue-900 border-blue-200'
                    }`}>
                      {isTelemetryDerived ? 'Telemetry-Derived (Empirical)' : 'Baseline FinOps Intelligence (Pre-Seeded Demo)'}
                    </span>

                    {isApplied && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                        Applied to Live Policy
                      </span>
                    )}

                    {isDismissed && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-300">
                        Dismissed
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-slate-900">
                    {rec.title}
                  </h3>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    <strong>Observed Issue:</strong> {rec.issue}
                  </p>

                  <div className="p-3 bg-surface-muted rounded-xl text-xs text-slate-800 border border-slate-200">
                    <strong>Proposed FinOps Action:</strong> {rec.proposed_action}
                  </div>

                  {/* Supporting Data */}
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-500 font-medium">
                    <span className="font-semibold text-slate-600">Supporting Data:</span>
                    {Object.entries(rec.supporting_data || {}).map(([key, val]) => {
                      if (key === 'source') return null;
                      return (
                        <span key={key} className="px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-700">
                          {key.replace(/_/g, ' ')}: <strong>{String(val)}</strong>
                        </span>
                      );
                    })}
                    <span>Confidence: <strong>{(rec.confidence_score * 100).toFixed(0)}%</strong></span>
                  </div>
                </div>

                {/* Right Action Column */}
                <div className="flex md:flex-col items-center md:items-end justify-between gap-3 shrink-0">
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Projected Savings</span>
                    <span className="text-xl font-bold font-mono text-emerald-700">
                      +${rec.expected_monthly_savings_usd.toFixed(0)}
                      <span className="text-xs font-normal text-slate-500">/mo</span>
                    </span>
                  </div>

                  {isPending && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDismiss(rec.id)}
                        className="px-3 py-2 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 text-xs font-semibold transition-colors"
                      >
                        Dismiss
                      </button>

                      <button
                        onClick={() => handleApply(rec.id)}
                        className="px-4 py-2 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold transition-all shadow-subtle flex items-center gap-1.5"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Apply Policy</span>
                      </button>
                    </div>
                  )}

                  {isApplied && (
                    <span className="inline-flex items-center gap-1 text-xs text-emerald-800 font-semibold bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Active in Policy
                    </span>
                  )}

                  {isDismissed && (
                    <span className="inline-flex items-center gap-1 text-xs text-slate-500 font-medium bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200">
                      Dismissed by Operator
                    </span>
                  )}
                </div>

              </div>
            </div>
          );
        })}

        {displayedRecs.length === 0 && (
          <div className="p-12 text-center text-slate-400 text-xs bg-white rounded-2xl border border-surface-border">
            No recommendations in "{statusFilter}" view.
          </div>
        )}

        </div>
      )}

    </div>
  );
};
