import React, { useState, useEffect } from 'react';
import {
  FileText, Search, Shield, Filter, RefreshCw,
  ExternalLink, ArrowRight, ShieldCheck, Clock, DollarSign
} from 'lucide-react';
import { api } from '../services/api';
import { ExecutionResponse } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ExecutionTraceModal } from '../components/ExecutionTraceModal';

export const AuditHistoryPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [selectedTrace, setSelectedTrace] = useState<ExecutionResponse | null>(null);

  useEffect(() => {
    loadAudit();
  }, []);

  const loadAudit = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditHistory(100);
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs.filter((l) => {
    const q = search.toLowerCase();
    return (
      (l.prompt_full || l.prompt_preview || '').toLowerCase().includes(q) ||
      (l.request_id || '').toLowerCase().includes(q) ||
      (l.selected_model_id || '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Compliance & Security Audit History
            </h1>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
              Enterprise Governance
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Immutable audit record of request data-handling, policy evaluations, and verification checks.
          </p>
        </div>

        <button
          onClick={loadAudit}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-surface-border hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl transition-all shadow-subtle"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit Trail</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="p-4 bg-white rounded-2xl border border-surface-border shadow-subtle flex items-center gap-3 text-xs">
        <div className="flex items-center gap-2 bg-surface-muted px-3 py-1.5 rounded-xl border border-slate-200 flex-1">
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by Request ID, prompt text, or model name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent border-none focus:outline-none w-full text-slate-800 placeholder-slate-400 font-medium"
          />
        </div>
        <span className="text-slate-400">
          Showing {filteredLogs.length} audit records
        </span>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-surface-border shadow-subtle overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-muted border-b border-surface-border">
              <tr className="text-slate-500 font-semibold">
                <th className="py-3 px-4">Request ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Sensitivity Tier</th>
                <th className="py-3 px-4">Model Assigned</th>
                <th className="py-3 px-4">Policy Version</th>
                <th className="py-3 px-4">Verification Check</th>
                <th className="py-3 px-4">Cost (USD)</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredLogs.map((l) => (
                <tr key={l.request_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4 font-mono font-medium text-slate-700">
                    {l.request_id.slice(0, 8)}...
                  </td>
                  <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                    {new Date(l.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                      l.data_sensitivity === 'restricted' ? 'bg-rose-100 text-rose-800' :
                      l.data_sensitivity === 'confidential' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {l.data_sensitivity}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-800">
                    {l.selected_model_id}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600">
                    v{l.policy_version || 1}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={l.verification_status} size="sm" />
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-forest-800">
                    ${l.total_cost_usd?.toFixed(6)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setSelectedTrace(l)}
                      className="px-2.5 py-1 rounded-lg bg-surface-muted hover:bg-forest-50 hover:text-forest-800 border border-slate-200 text-slate-700 font-medium transition-colors"
                    >
                      Audit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedTrace && (
        <ExecutionTraceModal
          trace={selectedTrace}
          onClose={() => setSelectedTrace(null)}
        />
      )}

    </div>
  );
};

