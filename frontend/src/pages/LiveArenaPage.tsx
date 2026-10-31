import React, { useState, useEffect } from 'react';
import {
  Swords, Download, Play, CheckCircle2, XCircle, TrendingDown,
  Layers, Clock, ShieldCheck, RefreshCw, ArrowUpRight
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { api } from '../services/api';
import { BenchmarkRunItem } from '../types';

export const LiveArenaPage: React.FC = () => {
  const [runs, setRuns] = useState<BenchmarkRunItem[]>([]);
  const [selectedTaskCount, setSelectedTaskCount] = useState<number>(15);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedRun, setSelectedRun] = useState<BenchmarkRunItem | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const history = await api.getBenchmarkHistory();
      if (history && history.length >= 4) {
        setRuns(history.slice(0, 4));
        setSelectedRun(history[0]);
      } else {
        // Auto-run if no benchmark yet
        executeBenchmark(10);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const executeBenchmark = async (count: number) => {
    setLoading(true);
    try {
      const newRuns = await api.runBenchmark(count);
      setRuns(newRuns);
      if (newRuns.length > 0) {
        setSelectedRun(newRuns[3] || newRuns[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const strategyDisplayName = (s: string) => {
    switch (s) {
      case 'astraroute_intelligent': return 'AstraRoute Intelligent';
      case 'always_advanced': return 'Always Advanced';
      case 'cheapest_eligible': return 'Cheapest Eligible';
      case 'rule_based': return 'Rule-Based Routing';
      default: return s;
    }
  };

  const chartData = runs.map((r) => ({
    name: strategyDisplayName(r.strategy),
    costPerSuccess: Number(((r.cost_per_successful_outcome || 0) * 1000).toFixed(2)),
    totalSpend: Number((r.total_cost_usd * 1000).toFixed(2)),
    successRate: Number((r.verification_success_rate * 100).toFixed(1)),
    avgLatency: Number(r.avg_latency_ms.toFixed(0)),
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Live Routing Arena
            </h1>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
              Comparative Evaluation
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Side-by-side benchmark executing identical workloads across four distinct routing strategies.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={api.getBenchmarkExportUrl()}
            download
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-white border border-surface-border hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl transition-all shadow-subtle"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </a>

          <button
            onClick={() => executeBenchmark(selectedTaskCount)}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl transition-all shadow-subtle"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
            <span>Run Benchmark</span>
          </button>
        </div>
      </div>

      {/* Dataset Selector Banner */}
      <div className="p-4 bg-white rounded-2xl border border-surface-border shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-700">
          <Swords className="w-4 h-4 text-forest-700 shrink-0" />
          <span>
            Select Workload Suite:
          </span>
          <div className="flex items-center gap-1.5 ml-2">
            {[10, 20, 35].map((cnt) => (
              <button
                key={cnt}
                onClick={() => setSelectedTaskCount(cnt)}
                className={`px-2.5 py-1 rounded-lg border font-medium ${
                  selectedTaskCount === cnt
                    ? 'bg-forest-100 text-forest-900 border-forest-300 font-bold'
                    : 'bg-surface-muted text-slate-600 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {cnt} Tasks Suite
              </button>
            ))}
          </div>
        </div>

        <div className="text-slate-500">
          Evaluates coding, data analysis, JSON schema, reasoning, and summarization.
        </div>
      </div>

      {/* 4 Strategies Side-by-Side Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {runs.map((r, idx) => {
          const isAstra = r.strategy === 'astraroute_intelligent';
          const isCheap = r.strategy === 'cheapest_eligible';
          return (
            <div
              key={idx}
              onClick={() => setSelectedRun(r)}
              className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                isAstra
                  ? 'bg-gradient-to-br from-forest-50/80 via-white to-sage-50/50 border-forest-300 shadow-card ring-1 ring-forest-400'
                  : 'bg-white border-surface-border shadow-subtle hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`text-xs font-bold uppercase tracking-wider ${
                  isAstra ? 'text-forest-900' : 'text-slate-600'
                }`}>
                  Strategy {String.fromCharCode(65 + idx)}
                </span>
                {isAstra && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-600 text-white">
                    Optimal FinOps
                  </span>
                )}
                {isCheap && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800">
                    High Failures
                  </span>
                )}
              </div>

              <h3 className="mt-2 text-base font-bold text-slate-900">
                {strategyDisplayName(r.strategy)}
              </h3>

              {/* Cost Per Successful Outcome Hero */}
              <div className="mt-4 p-3 rounded-xl bg-surface-muted border border-slate-100">
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
                  Cost / Success (CPSO)
                </span>
                <span className={`text-lg font-bold font-mono ${isAstra ? 'text-forest-900' : 'text-slate-800'}`}>
                  ${(r.cost_per_successful_outcome || 0).toFixed(6)}
                </span>
              </div>

              {/* Secondary Metrics */}
              <div className="mt-4 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Success Rate:</span>
                  <span className="font-semibold text-slate-900">
                    {(r.verification_success_rate * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Total Workload Cost:</span>
                  <span className="font-mono text-slate-800 font-semibold">
                    ${r.total_cost_usd.toFixed(5)}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Average Latency:</span>
                  <span className="font-mono text-slate-800">
                    {r.avg_latency_ms.toFixed(0)}ms
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Arena Charts: CPSO & Quality vs Latency */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Cost Per Successful Outcome Bar Chart */}
        <div className="bg-white rounded-2xl p-6 border border-surface-border shadow-subtle">
          <div className="pb-4 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">
              Cost Per Successful Outcome (CPSO) Comparison
            </h3>
            <p className="text-xs text-slate-500">
              Lower is better. Accounts for total attempts, failed runs, and fallback spend.
            </p>
          </div>

          <div className="mt-6 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  formatter={(val: any) => [`$${(val / 1000).toFixed(6)}`, 'CPSO']}
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="costPerSuccess" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.name.includes('AstraRoute') ? '#15803d' : entry.name.includes('Cheapest') ? '#e11d48' : '#94a3b8'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Success Rate Comparison */}
        <div className="bg-white rounded-2xl p-6 border border-surface-border shadow-subtle">
          <div className="pb-4 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">
              Quality Guardian Verification Success Rate (%)
            </h3>
            <p className="text-xs text-slate-500">
              Notice how the unguided Cheapest model collapses on complex reasoning and coding tasks.
            </p>
          </div>

          <div className="mt-6 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={[0, 100]} />
                <Tooltip
                  formatter={(val: any) => [`${val}%`, 'Verification Pass Rate']}
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="successRate" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-rate-${index}`}
                      fill={entry.name.includes('AstraRoute') ? '#166534' : entry.name.includes('Cheapest') ? '#f43f5e' : '#475569'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Task Breakdown for Selected Run */}
      {selectedRun && (
        <div className="bg-white rounded-2xl p-6 border border-surface-border shadow-subtle">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Detailed Workload Trace — {strategyDisplayName(selectedRun.strategy)}
              </h3>
              <p className="text-xs text-slate-500">
                Item-by-item verification outcomes, models assigned, and individual request costs
              </p>
            </div>
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-surface-muted text-slate-700">
              {selectedRun.total_items} Items Evaluated
            </span>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 font-medium">
                  <th className="pb-3 font-semibold">Category</th>
                  <th className="pb-3 font-semibold">Difficulty</th>
                  <th className="pb-3 font-semibold">Model Selected</th>
                  <th className="pb-3 font-semibold">Verification</th>
                  <th className="pb-3 font-semibold">Latency</th>
                  <th className="pb-3 font-semibold text-right">Cost (USD)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {selectedRun.details?.map((d, i) => (
                  <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 capitalize font-medium text-slate-800">
                      {d.task_category.replace('_', ' ')}
                    </td>
                    <td className="py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        d.difficulty === 'complex' ? 'bg-rose-50 text-rose-800' :
                        d.difficulty === 'moderate' ? 'bg-amber-50 text-amber-800' : 'bg-emerald-50 text-emerald-800'
                      }`}>
                        {d.difficulty}
                      </span>
                    </td>
                    <td className="py-2.5 font-mono text-slate-700">
                      {d.model_selected}
                    </td>
                    <td className="py-2.5">
                      {d.verified ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700 font-medium">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Pass
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-700 font-medium">
                          <XCircle className="w-3.5 h-3.5 text-rose-600" /> Failed
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 font-mono text-slate-600">
                      {d.latency_ms}ms
                    </td>
                    <td className="py-2.5 text-right font-mono font-semibold text-slate-900">
                      ${d.cost_usd.toFixed(6)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};

