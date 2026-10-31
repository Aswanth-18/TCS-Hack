import React, { useState, useEffect } from 'react';
import {
  SplitSquareVertical, Search, Filter, RefreshCw,
  ExternalLink, ArrowRight, ShieldCheck, Clock, DollarSign
} from 'lucide-react';
import { api } from '../services/api';
import { ExecutionResponse } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ExecutionTraceModal } from '../components/ExecutionTraceModal';

export const RoutingDecisionsPage: React.FC = () => {
  const [decisions, setDecisions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [taskFilter, setTaskFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedTrace, setSelectedTrace] = useState<ExecutionResponse | null>(null);

  useEffect(() => {
    loadDecisions();
  }, [taskFilter, statusFilter]);

  const loadDecisions = async () => {
    setLoading(true);
    try {
      const filters: Record<string, string> = {};
      if (taskFilter) filters.task_type = taskFilter;
      if (statusFilter) filters.status = statusFilter;
      const data = await api.getAuditHistory(50, filters);
      setDecisions(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in w-full">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Routing Decisions & Telemetry Logs
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Every consequential routing decision recorded with constraint checks, candidate scoring, and verification audits.
          </p>
        </div>

        <button
          onClick={loadDecisions}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-surface-border hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl transition-all shadow-subtle self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-white rounded-2xl border border-surface-border shadow-subtle flex flex-wrap items-center gap-3 text-xs w-full">
        <div className="flex items-center gap-1.5 font-semibold text-slate-600">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span>Filter By:</span>
        </div>

        <select
          value={taskFilter}
          onChange={(e) => setTaskFilter(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-forest-600 font-medium"
        >
          <option value="">All Task Types</option>
          <option value="coding">Coding</option>
          <option value="reasoning">Reasoning</option>
          <option value="data_analysis">Data Analysis</option>
          <option value="summarization">Summarization</option>
          <option value="structured_output">Structured Output</option>
          <option value="general_qa">General Q&A</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-forest-600 font-medium"
        >
          <option value="">All Verification Statuses</option>
          <option value="success">Verified Success</option>
          <option value="failed">Failed Verification</option>
        </select>

        <span className="text-slate-400 ml-auto">
          Showing {decisions.length} traceable requests
        </span>
      </div>

      {/* Decisions Table */}
      <div className="bg-white rounded-2xl border border-surface-border shadow-subtle overflow-hidden w-full">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs min-w-[850px]">
            <thead className="bg-surface-muted border-b border-surface-border">
              <tr className="text-slate-500 font-semibold">
                <th className="py-3 px-4 w-24">Timestamp</th>
                <th className="py-3 px-4">Prompt Query</th>
                <th className="py-3 px-4 w-32">Category</th>
                <th className="py-3 px-4 w-36">Selected Model</th>
                <th className="py-3 px-4 w-36">Strategy</th>
                <th className="py-3 px-4 w-28">Verification</th>
                <th className="py-3 px-4 w-24">Cost (USD)</th>
                <th className="py-3 px-4 w-20">Latency</th>
                <th className="py-3 px-4 text-right w-28">Audit Trace</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {decisions.map((d) => (
                <tr key={d.request_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                    {d.timestamp ? new Date(d.timestamp).toLocaleTimeString() : 'Recent'}
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-900 max-w-sm truncate">
                    {d.prompt_preview || d.prompt_full}
                  </td>
                  <td className="py-3 px-4 capitalize">
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-[11px] font-mono text-slate-700">
                      {d.task_type}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-semibold text-slate-800">{d.selected_model_id}</span>
                    <span className="text-[10px] text-slate-400 block">{d.selected_provider}</span>
                  </td>
                  <td className="py-3 px-4 capitalize text-slate-600 font-medium">
                    {d.routing_strategy?.replace('_', ' ')}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={d.verification_status || d.verification?.status || 'Verified Pass'} size="sm" />
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-forest-800">
                    ${(d.total_cost_usd ?? 0).toFixed(6)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600">
                    {d.total_latency_ms ?? 0}ms
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setSelectedTrace(d)}
                      className="px-2.5 py-1 rounded-lg bg-surface-muted hover:bg-forest-50 hover:text-forest-800 border border-slate-200 text-slate-700 font-medium transition-colors"
                    >
                      Inspect Trace
                    </button>
                  </td>
                </tr>
              ))}
              {decisions.length === 0 && !loading && (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400 text-xs">
                    No routing decisions recorded matching current filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Trace Modal */}
      {selectedTrace && (
        <ExecutionTraceModal
          trace={selectedTrace}
          onClose={() => setSelectedTrace(null)}
        />
      )}

    </div>
  );
};
