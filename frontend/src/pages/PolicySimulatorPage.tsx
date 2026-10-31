import React, { useState, useEffect } from 'react';
import {
  Sliders, TrendingDown, AlertTriangle, ShieldCheck, CheckCircle2,
  RefreshCw, DollarSign, Clock, ArrowRight, Zap, Play
} from 'lucide-react';
import { api } from '../services/api';

export const PolicySimulatorPage: React.FC = () => {
  const [budgetCap, setBudgetCap] = useState<number>(0.035);
  const [qualityMin, setQualityMin] = useState<number>(0.75);
  const [latencyMax, setLatencyMax] = useState<number>(3500);
  
  // Weights (sum to 1.0)
  const [wCost, setWCost] = useState<number>(0.45);
  const [wQuality, setWQuality] = useState<number>(0.35);
  const [wLatency, setWLatency] = useState<number>(0.10);
  const [wRel, setWRel] = useState<number>(0.10);

  const [loading, setLoading] = useState<boolean>(false);
  const [simResult, setSimResult] = useState<any | null>(null);
  const [applying, setApplying] = useState<boolean>(false);
  const [applySuccess, setApplySuccess] = useState<string | null>(null);

  useEffect(() => {
    runSimulation();
  }, []);

  const runSimulation = async () => {
    setLoading(true);
    setApplySuccess(null);
    try {
      const res = await api.simulatePolicy({
        max_budget_per_request: budgetCap,
        min_quality_threshold: qualityMin,
        max_latency_ms: latencyMax,
        weight_cost: wCost,
        weight_quality: wQuality,
        weight_latency: wLatency,
        weight_reliability: wRel
      });
      setSimResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!window.confirm('Are you sure you want to activate this proposed policy for live gateway traffic?')) {
      return;
    }
    setApplying(true);
    try {
      const res = await api.applyPolicy({
        max_budget_per_request: budgetCap,
        min_quality_threshold: qualityMin,
        max_latency_ms: latencyMax,
        weight_cost: wCost,
        weight_quality: wQuality,
        weight_latency: wLatency,
        weight_reliability: wRel
      });
      setApplySuccess(res.message);
      runSimulation();
    } catch (e) {
      console.error(e);
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            What-If Policy Simulator
          </h1>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
            Predictive FinOps Modeling
          </span>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Simulate routing weight changes and budget constraints without affecting live traffic.
        </p>
      </div>

      {applySuccess && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{applySuccess}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Controls (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-6 border border-surface-border shadow-subtle space-y-5">
          <div className="pb-3 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Simulation Controls</h2>
            <span className="text-xs text-slate-400">Sandbox Environment</span>
          </div>

          {/* Hard Constraints */}
          <div className="space-y-3 text-xs">
            <div>
              <div className="flex items-center justify-between text-slate-700 mb-1">
                <span className="font-semibold">Max Request Budget</span>
                <span className="font-mono font-bold text-forest-800">${budgetCap.toFixed(3)}</span>
              </div>
              <input
                type="range"
                min="0.005"
                max="0.080"
                step="0.005"
                value={budgetCap}
                onChange={(e) => setBudgetCap(parseFloat(e.target.value))}
                className="w-full accent-forest-700 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-700 mb-1">
                <span className="font-semibold">Min Quality Target</span>
                <span className="font-mono font-bold text-forest-800">{(qualityMin * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.50"
                max="0.95"
                step="0.05"
                value={qualityMin}
                onChange={(e) => setQualityMin(parseFloat(e.target.value))}
                className="w-full accent-forest-700 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-700 mb-1">
                <span className="font-semibold">Max Latency Ceiling</span>
                <span className="font-mono font-bold text-forest-800">{latencyMax}ms</span>
              </div>
              <input
                type="range"
                min="500"
                max="6000"
                step="250"
                value={latencyMax}
                onChange={(e) => setLatencyMax(parseInt(e.target.value))}
                className="w-full accent-forest-700 cursor-pointer"
              />
            </div>
          </div>

          {/* Multi-Objective Routing Weights */}
          <div className="pt-3 border-t border-slate-100 space-y-3 text-xs">
            <span className="font-bold text-slate-800 block">
              Multi-Objective Optimization Weights
            </span>

            <div>
              <div className="flex items-center justify-between text-slate-600 mb-1">
                <span>Cost Weight</span>
                <span className="font-mono font-semibold">{(wCost * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.80"
                step="0.05"
                value={wCost}
                onChange={(e) => setWCost(parseFloat(e.target.value))}
                className="w-full accent-forest-700 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-600 mb-1">
                <span>Quality Weight</span>
                <span className="font-mono font-semibold">{(wQuality * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.80"
                step="0.05"
                value={wQuality}
                onChange={(e) => setWQuality(parseFloat(e.target.value))}
                className="w-full accent-forest-700 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-slate-600 mb-1">
                <span>Latency Weight</span>
                <span className="font-mono font-semibold">{(wLatency * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.40"
                step="0.05"
                value={wLatency}
                onChange={(e) => setWLatency(parseFloat(e.target.value))}
                className="w-full accent-forest-700 cursor-pointer"
              />
            </div>
          </div>

          <button
            onClick={runSimulation}
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-subtle"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
            <span>Re-Calculate Projections</span>
          </button>
        </div>

        {/* Projected Outcomes & Diff (7 cols) */}
        <div className="lg:col-span-7 space-y-5">
          {simResult && (
            <>
              {/* Projected Hero Metric Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-4 rounded-2xl bg-white border border-surface-border shadow-subtle text-xs">
                  <span className="text-slate-400 block text-[11px]">Projected Workload Spend</span>
                  <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">
                    ${simResult.projected_spend_usd.toFixed(5)}
                  </span>
                  <span className={`text-[11px] font-semibold mt-1 block ${
                    simResult.projected_savings_pct >= 0 ? 'text-emerald-700' : 'text-rose-700'
                  }`}>
                    {simResult.projected_savings_pct >= 0 ? `+${simResult.projected_savings_pct}% Savings` : `${simResult.projected_savings_pct}% Spend`}
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-surface-border shadow-subtle text-xs">
                  <span className="text-slate-400 block text-[11px]">Quality Expectation</span>
                  <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">
                    {(simResult.projected_quality_score * 100).toFixed(1)}%
                  </span>
                  <span className="text-[11px] text-slate-500 mt-1 block">
                    Benchmark Satisfied
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-surface-border shadow-subtle text-xs">
                  <span className="text-slate-400 block text-[11px]">Average Latency</span>
                  <span className="text-xl font-bold font-mono text-slate-900 mt-1 block">
                    {simResult.projected_avg_latency_ms.toFixed(0)}ms
                  </span>
                  <span className="text-[11px] text-slate-500 mt-1 block">
                    P50 Expected
                  </span>
                </div>
              </div>

              {/* Trade-off Analysis Narrative */}
              <div className="p-5 rounded-2xl bg-forest-50/60 border border-forest-200 text-xs text-slate-800 leading-relaxed font-sans shadow-subtle">
                <div className="font-bold text-forest-900 mb-1 flex items-center gap-1.5">
                  <Zap className="w-4 h-4 text-forest-700" />
                  <span>Autonomous Trade-Off Analysis</span>
                </div>
                {simResult.trade_off_analysis}
              </div>

              {/* Warnings */}
              {simResult.warnings && simResult.warnings.length > 0 && (
                <div className="p-4 rounded-2xl bg-amber-50/80 border border-amber-200 text-xs space-y-1.5">
                  <div className="font-bold text-amber-900 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-amber-700" />
                    <span>Policy Risk Warnings</span>
                  </div>
                  {simResult.warnings.map((w: string, idx: number) => (
                    <div key={idx} className="text-amber-800 pl-5">
                      • {w}
                    </div>
                  ))}
                </div>
              )}

              {/* Projected Model Distribution */}
              <div className="bg-white rounded-2xl p-5 border border-surface-border shadow-subtle text-xs space-y-3">
                <span className="font-bold text-slate-900 block">
                  Projected Traffic Distribution (% of requests)
                </span>
                <div className="space-y-2">
                  {Object.entries(simResult.projected_model_distribution || {}).map(([model, pct]: any) => (
                    <div key={model}>
                      <div className="flex items-center justify-between text-slate-700 mb-0.5">
                        <span className="font-mono text-slate-800 font-medium">{model}</span>
                        <span className="font-bold">{pct}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div
                          className="bg-forest-700 h-2 rounded-full transition-all"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Apply Action Box */}
              <div className="p-5 bg-white rounded-2xl border border-surface-border shadow-subtle flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-900">
                    Apply Proposed Policy to Live Gateway
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    Requires manual confirmation. Creates a new immutable policy version.
                  </p>
                </div>
                <button
                  onClick={handleApply}
                  disabled={applying}
                  className="px-4 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold transition-all shadow-subtle flex items-center gap-2"
                >
                  {applying ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                  <span>Activate Policy</span>
                </button>
              </div>

            </>
          )}
        </div>

      </div>

    </div>
  );
};

