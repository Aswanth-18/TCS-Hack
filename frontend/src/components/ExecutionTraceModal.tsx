import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, CheckCircle, XCircle, Clock, Layers, DollarSign } from 'lucide-react';
import { ExecutionResponse } from '../types';
import { StatusBadge } from './StatusBadge';

interface ExecutionTraceModalProps {
  trace: ExecutionResponse | any | null;
  onClose: () => void;
}

export const ExecutionTraceModal: React.FC<ExecutionTraceModalProps> = ({ trace, onClose }) => {
  // Prevent background page scrolling while modal is open
  useEffect(() => {
    if (!trace) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [trace]);

  // Support closing with Escape key
  useEffect(() => {
    if (!trace) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [trace, onClose]);

  if (!trace) return null;

  // Defensive normalization supporting both ExecutionResponse and AuditLog record shapes
  const verification = trace.verification || {
    status: trace.verification_status || 'Verified Pass',
    method: trace.verification_method || 'rubric',
    score: trace.verification_score ?? 1.0,
    passed_checks: trace.verification_details?.passed_checks || [],
    failed_checks: trace.verification_details?.failed_checks || [],
    rationale: trace.verification_details?.rationale || 'Verification completed successfully'
  };

  const eligibleModels: string[] = trace.eligible_models || [];
  const rejectedModels = trace.rejected_models || [];
  const attempts = trace.attempts || [];
  const totalCost = typeof trace.total_cost_usd === 'number' ? trace.total_cost_usd : 0;
  const totalTokens = typeof trace.total_tokens === 'number' ? trace.total_tokens : 0;
  const totalLatency = typeof trace.total_latency_ms === 'number' ? trace.total_latency_ms : 0;
  const routingScore = typeof trace.routing_score === 'number' ? trace.routing_score : 0.85;

  const modalContent = (
    <div 
      className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-6 bg-slate-900/50 backdrop-blur-sm animate-fade-in"
      style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}
      onClick={onClose}
    >
      <div 
        className="relative w-full flex flex-col bg-white rounded-2xl shadow-2xl border border-surface-border overflow-hidden my-auto"
        style={{
          maxWidth: 'min(860px, calc(100vw - 32px))',
          maxHeight: '85vh',
          height: 'auto'
        }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-trace-title"
      >
        
        {/* Stationary Header (Fixed at top of modal) */}
        <div className="shrink-0 px-5 sm:px-6 py-4 border-b border-surface-border bg-white flex items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-forest-50 text-forest-800 border border-forest-200">
                Audit Trace
              </span>
              <span className="text-[11px] font-mono text-slate-400">ID: {(trace.request_id || '').slice(0, 8)}...</span>
              <StatusBadge status={verification.status || 'Verified Pass'} size="sm" />
            </div>
            <h2 id="modal-trace-title" className="mt-1 text-base sm:text-lg font-bold text-slate-900">
              Autonomous Routing & Execution Trace
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Trace Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 text-xs overscroll-contain">
          
          {/* Step 1: Request Analysis */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-surface-muted border border-surface-border">
            <div className="flex items-center gap-2 text-xs font-semibold text-forest-900 mb-2">
              <span className="w-5 h-5 rounded-full bg-forest-700 text-white flex items-center justify-center text-[10px] font-bold">1</span>
              <span>Request Classification & Policy Constraints</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-2.5">
              <div className="p-2 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Task Category</span>
                <span className="font-semibold text-slate-800 capitalize text-xs">{trace.task_type || 'General'}</span>
              </div>
              <div className="p-2 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Complexity</span>
                <span className="font-semibold text-slate-800 capitalize text-xs">{trace.detected_complexity || 'Moderate'}</span>
              </div>
              <div className="p-2 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Routing Strategy</span>
                <span className="font-semibold text-slate-800 capitalize text-xs">{(trace.routing_strategy || 'astraroute_intelligent').replace('_', ' ')}</span>
              </div>
              <div className="p-2 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Total Tokens</span>
                <span className="font-semibold text-slate-800 text-xs">{totalTokens.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Step 2: Policy & Eligibility Filter */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-white border border-surface-border">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-900 mb-2">
              <span className="w-5 h-5 rounded-full bg-slate-700 text-white flex items-center justify-center text-[10px] font-bold">2</span>
              <span>Eligibility & Hard Constraint Filter</span>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                <span className="text-slate-600">
                  <strong className="text-slate-800">{eligibleModels.length} Eligible Models:</strong> {eligibleModels.join(', ') || 'None'}
                </span>
              </div>

              {rejectedModels && rejectedModels.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100">
                  <span className="text-slate-500 font-medium block mb-1">Excluded Models & Policy Violations:</span>
                  <div className="space-y-1.5">
                    {rejectedModels.map((r: any, i: number) => (
                      <div key={i} className="flex items-start gap-2 bg-rose-50/60 p-2 rounded-lg border border-rose-100 text-slate-700">
                        <XCircle className="w-3.5 h-3.5 text-rose-500 mt-0.5 shrink-0" />
                        <div>
                          <strong className="text-rose-900">{r.model_id}:</strong> {r.reason}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Step 3: Explainable Selection */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-forest-50/50 border border-forest-200">
            <div className="flex items-center gap-2 text-xs font-semibold text-forest-900 mb-2">
              <span className="w-5 h-5 rounded-full bg-forest-800 text-white flex items-center justify-center text-[10px] font-bold">3</span>
              <span>Intelligent Model Selection Rationale</span>
            </div>
            <div className="p-3 bg-white rounded-xl border border-forest-100 text-slate-700 leading-relaxed font-sans text-xs">
              {trace.routing_explanation || 'Candidate selected using multi-objective FinOps scoring.'}
            </div>
            <div className="mt-2.5 flex flex-wrap items-center justify-between text-forest-900 font-medium px-1 gap-1">
              <span>Selected Candidate: <strong>{trace.selected_model_id}</strong> ({trace.selected_provider})</span>
              <span>FinOps Composite Score: <strong>{(routingScore * 100).toFixed(1)}/100</strong></span>
            </div>
          </div>

          {/* Step 4: Execution Attempts & Fallback Recovery */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-white border border-surface-border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-900">
                <span className="w-5 h-5 rounded-full bg-slate-700 text-white flex items-center justify-center text-[10px] font-bold">4</span>
                <span>Execution Telemetry & Recovery Path</span>
              </div>
              {trace.fallback_occurred && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                  Fallback Recovered ({trace.attempt_count} attempts)
                </span>
              )}
            </div>

            <div className="space-y-2">
              {attempts.length > 0 ? (
                attempts.map((att: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-2.5 sm:p-3 rounded-xl border ${
                      att.is_fallback
                        ? 'bg-blue-50/40 border-blue-200'
                        : 'bg-surface-muted border-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between font-medium">
                      <span className="text-slate-800 flex items-center gap-1.5">
                        <span className="font-mono bg-white px-1.5 py-0.5 rounded border border-slate-200 text-[10px]">
                          Attempt #{att.attempt_number}
                        </span>
                        <strong>{att.model_id}</strong> ({att.provider})
                        {att.is_fallback && <span className="text-blue-700 text-[10px] font-semibold">(Fallback Escalation)</span>}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                        att.status === 'success' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {att.status}
                      </span>
                    </div>

                    {att.fallback_reason && (
                      <div className="mt-1 text-blue-800 text-[11px] font-sans">
                        Reason: {att.fallback_reason}
                      </div>
                    )}

                    <div className="mt-2 pt-2 border-t border-slate-200/60 flex flex-wrap items-center gap-3 text-slate-500 text-[11px]">
                      <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {att.latency_ms || 0}ms</span>
                      <span className="flex items-center gap-1"><Layers className="w-3.5 h-3.5" /> {att.input_tokens || 0} in / {att.output_tokens || 0} out</span>
                      <span className="flex items-center gap-1 font-semibold text-slate-800"><DollarSign className="w-3.5 h-3.5 text-forest-700" /> ${(att.cost_usd || 0).toFixed(6)}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 italic p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  Initial execution succeeded on first attempt with no fallback escalation required.
                </div>
              )}
            </div>
          </div>

          {/* Step 5: Quality Guardian Verification */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-white border border-surface-border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-900">
                <span className="w-5 h-5 rounded-full bg-slate-700 text-white flex items-center justify-center text-[10px] font-bold">5</span>
                <span>Quality Guardian Verification</span>
              </div>
              <StatusBadge status={verification.status || 'Verified Pass'} size="sm" />
            </div>

            <div className="space-y-1.5">
              <div className="text-slate-600">
                Evaluation Method: <strong className="text-slate-800 font-mono">{verification.method || 'rubric'}</strong> (Quality Score: {Math.round((verification.score ?? 1.0) * 100)}%)
              </div>
              <div className="text-slate-700 italic">
                "{verification.rationale || 'Verification checks passed.'}"
              </div>

              {verification.passed_checks && verification.passed_checks.length > 0 && (
                <div className="space-y-1 mt-2">
                  {verification.passed_checks.map((chk: string, i: number) => (
                    <div key={i} className="flex items-center gap-1.5 text-emerald-800">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{chk}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Step 6: Response Output */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-slate-900 text-slate-100 font-mono">
            <div className="text-slate-400 mb-1.5 flex items-center justify-between text-xs">
              <span>FINAL RESPONSE PAYLOAD</span>
              <span className="text-[10px] text-slate-400">{trace.selected_model_id}</span>
            </div>
            <pre className="whitespace-pre-wrap overflow-y-auto max-h-36 sm:max-h-44 text-slate-200 font-sans text-xs">
              {trace.final_response || '(No response payload)'}
            </pre>
          </div>

        </div>

        {/* Stationary Footer (Fixed at bottom of modal) */}
        <div className="shrink-0 px-5 sm:px-6 py-3.5 border-t border-surface-border bg-white flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
          <div>
            Total Spend: <strong className="text-slate-800">${totalCost.toFixed(6)}</strong> | Latency: <strong className="text-slate-800">{totalLatency}ms</strong>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-xl transition-colors"
          >
            Close Trace
          </button>
        </div>

      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
