import React, { useState } from 'react';
import {
  Play, Sparkles, AlertTriangle, ShieldCheck, CheckCircle2,
  RefreshCw, DollarSign, Clock, Layers, HelpCircle, ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { ExecutionResponse, TaskType, SensitivityTier, Criticality, RoutingStrategy } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ExecutionTraceModal } from '../components/ExecutionTraceModal';

export const PlaygroundPage: React.FC = () => {
  const [prompt, setPrompt] = useState<string>(
    'Analyze this quarterly sales report and explain why revenue decreased by 14.2% despite marketing spend increase.'
  );
  const [taskType, setTaskType] = useState<string>('');
  const [maxBudget, setMaxBudget] = useState<number>(0.04);
  const [minQuality, setMinQuality] = useState<number>(0.75);
  const [maxLatency, setMaxLatency] = useState<number>(4000);
  const [sensitivity, setSensitivity] = useState<SensitivityTier>('internal');
  const [criticality, setCriticality] = useState<Criticality>('standard');
  const [strategy, setStrategy] = useState<RoutingStrategy>('astraroute_intelligent');
  const [simulateFailure, setSimulateFailure] = useState<boolean>(false);

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ExecutionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTraceModal, setShowTraceModal] = useState<boolean>(false);

  // Sample prompt presets
  const samplePresets = [
    {
      label: 'Sales Variance Analysis',
      prompt: 'Analyze this quarterly sales report and explain why revenue decreased by 14.2% despite marketing spend increase.',
      type: 'data_analysis',
      sens: 'internal' as SensitivityTier
    },
    {
      label: 'Python LRU Cache',
      prompt: 'Implement an LRU Cache class in Python with get and put methods running in O(1) time complexity with unit tests.',
      type: 'coding',
      sens: 'internal' as SensitivityTier
    },
    {
      label: 'SSN Restricted Privacy',
      prompt: 'Process this customer payroll record containing SSN 982-12-4411 and salary data for internal audit.',
      type: 'data_analysis',
      sens: 'restricted' as SensitivityTier
    },
    {
      label: 'Extract JSON Schema',
      prompt: 'Extract employee name, title, department, and salary from text: Alice Wong is Principal SRE in Infrastructure ($185k). Return valid JSON.',
      type: 'structured_output',
      sens: 'internal' as SensitivityTier
    },
    {
      label: 'FinOps Executive TL;DR',
      prompt: 'Summarize the three core lifecycle phases of the FinOps Foundation: Inform, Optimize, and Operate in 3 concise bullet points.',
      type: 'summarization',
      sens: 'public' as SensitivityTier
    }
  ];

  const handleExecute = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const resp = await api.executeRequest({
        prompt,
        task_type: taskType ? taskType : undefined,
        max_budget: maxBudget,
        min_quality: minQuality,
        max_latency: maxLatency,
        sensitivity,
        criticality,
        strategy,
        simulate_failure_attempt: simulateFailure
      });
      setResult(resp);
    } catch (err: any) {
      setError(err.message || 'Execution error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Request & Policy Playground
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Submit prompts, configure hard policy constraints, and inspect real-time autonomous routing decisions.
        </p>
      </div>

      {/* Preset Quick Buttons */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-xs font-semibold text-slate-400">Sample Presets:</span>
        {samplePresets.map((preset, idx) => (
          <button
            key={idx}
            onClick={() => {
              setPrompt(preset.prompt);
              setTaskType(preset.type);
              setSensitivity(preset.sens);
            }}
            className="px-3 py-1 rounded-lg bg-surface-muted hover:bg-forest-50 hover:text-forest-800 border border-surface-border text-xs text-slate-600 transition-colors"
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Input & Constraints (5 Cols) */}
        <div className="lg:col-span-5 space-y-5">
          
          <div className="bg-white rounded-2xl p-5 border border-surface-border shadow-subtle space-y-4">
            
            {/* Prompt Editor */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                User Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                placeholder="Enter prompt to route..."
                className="w-full rounded-xl border border-slate-200 p-3 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-forest-600 focus:border-transparent font-sans"
              />
            </div>

            {/* Task Type Override */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-600 mb-1">
                  Task Category
                </label>
                <select
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 p-2 text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-forest-600"
                >
                  <option value="">Auto-Detect Category</option>
                  <option value="coding">Coding</option>
                  <option value="reasoning">Reasoning</option>
                  <option value="summarization">Summarization</option>
                  <option value="data_analysis">Data Analysis</option>
                  <option value="structured_output">Structured Output</option>
                  <option value="general_qa">General Q&A</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-600 mb-1">
                  Routing Strategy
                </label>
                <select
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value as RoutingStrategy)}
                  className="w-full rounded-lg border border-slate-200 p-2 text-slate-800 bg-white font-medium focus:outline-none focus:ring-1 focus:ring-forest-600"
                >
                  <option value="astraroute_intelligent">AstraRoute AI (Recommended)</option>
                  <option value="always_advanced">Always Advanced (Flagship)</option>
                  <option value="cheapest_eligible">Cheapest Eligible</option>
                  <option value="rule_based">Rule-Based Matrix</option>
                </select>
              </div>
            </div>

            {/* Privacy & Criticality */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-600 mb-1">
                  Data Sensitivity
                </label>
                <select
                  value={sensitivity}
                  onChange={(e) => setSensitivity(e.target.value as SensitivityTier)}
                  className="w-full rounded-lg border border-slate-200 p-2 text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-forest-600"
                >
                  <option value="public">Public (Unrestricted)</option>
                  <option value="internal">Internal (Standard)</option>
                  <option value="confidential">Confidential (HIPAA/Enterprise)</option>
                  <option value="restricted">Restricted (Local/Zero-Retention)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-600 mb-1">
                  Business Criticality
                </label>
                <select
                  value={criticality}
                  onChange={(e) => setCriticality(e.target.value as Criticality)}
                  className="w-full rounded-lg border border-slate-200 p-2 text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-forest-600"
                >
                  <option value="standard">Standard</option>
                  <option value="high">High Criticality</option>
                  <option value="mission_critical">Mission Critical</option>
                </select>
              </div>
            </div>

            {/* Sliders */}
            <div className="space-y-3 pt-2 border-t border-slate-100 text-xs">
              <div>
                <div className="flex items-center justify-between text-slate-600 mb-1">
                  <span className="font-semibold">Max Request Budget Cap</span>
                  <span className="font-mono font-bold text-forest-800">${maxBudget.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.002"
                  max="0.080"
                  step="0.002"
                  value={maxBudget}
                  onChange={(e) => setMaxBudget(parseFloat(e.target.value))}
                  className="w-full accent-forest-700 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex items-center justify-between text-slate-600 mb-1">
                  <span className="font-semibold">Min Quality Target</span>
                  <span className="font-mono font-bold text-forest-800">{(minQuality * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.50"
                  max="0.95"
                  step="0.05"
                  value={minQuality}
                  onChange={(e) => setMinQuality(parseFloat(e.target.value))}
                  className="w-full accent-forest-700 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex items-center justify-between text-slate-600 mb-1">
                  <span className="font-semibold">Max Latency Ceiling</span>
                  <span className="font-mono font-bold text-forest-800">{maxLatency}ms</span>
                </div>
                <input
                  type="range"
                  min="500"
                  max="6000"
                  step="250"
                  value={maxLatency}
                  onChange={(e) => setMaxLatency(parseInt(e.target.value))}
                  className="w-full accent-forest-700 cursor-pointer"
                />
              </div>
            </div>

            {/* Fallback Simulation Toggle */}
            <div className="pt-2 border-t border-slate-100">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-700">
                <input
                  type="checkbox"
                  checked={simulateFailure}
                  onChange={(e) => setSimulateFailure(e.target.checked)}
                  className="rounded text-forest-700 focus:ring-forest-600"
                />
                <span className="font-medium text-slate-800">
                  Simulate Attempt 1 Timeout (Demonstrate Fallback Recovery)
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleExecute}
              disabled={loading}
              className="w-full py-3 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold tracking-wide uppercase shadow-subtle flex items-center justify-center gap-2 transition-all"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Evaluating Gateway Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Execute Intelligent Route</span>
                </>
              )}
            </button>

          </div>

        </div>

        {/* Right Column: Execution Trace & Response (7 Cols) */}
        <div className="lg:col-span-7 space-y-5">
          
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!result && !loading && (
            <div className="bg-white rounded-2xl p-12 border border-surface-border shadow-subtle text-center text-slate-400 space-y-3">
              <Sparkles className="w-8 h-8 text-forest-600/40 mx-auto" />
              <div className="font-semibold text-slate-600 text-sm">
                Ready for Autonomous Routing
              </div>
              <p className="text-xs max-w-sm mx-auto text-slate-400">
                Configure your request parameters on the left or click a sample preset, then execute to inspect the multi-stage gateway trace.
              </p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              
              {/* Step 1: Decision Header Card */}
              <div className="bg-white rounded-2xl p-5 border border-forest-200 shadow-card">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-900 border border-forest-200">
                        Selected Candidate
                      </span>
                      <StatusBadge status={result.verification?.status || 'Verified Pass'} size="sm" />
                      {result.fallback_occurred && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                          Fallback Triggered ({result.attempt_count} attempts)
                        </span>
                      )}
                    </div>
                    <div className="mt-2 text-xl font-bold text-slate-900 flex items-center gap-2">
                      <span>{result.selected_model_id}</span>
                      <span className="text-xs font-normal text-slate-500">({result.selected_provider})</span>
                    </div>
                  </div>

                  <button
                    onClick={() => setShowTraceModal(true)}
                    className="px-3 py-1.5 rounded-xl bg-forest-50 hover:bg-forest-100 text-forest-800 font-semibold text-xs border border-forest-200 flex items-center gap-1.5 transition-colors"
                  >
                    <span>Full Trace Audit</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Score & Explanation */}
                <div className="mt-3 p-3 rounded-xl bg-surface-muted text-xs text-slate-700 leading-relaxed font-sans border border-slate-200">
                  {result.routing_explanation}
                </div>

                {/* Telemetry Strip */}
                <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-3 gap-2 text-center text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Total Request Cost</span>
                    <span className="font-bold font-mono text-forest-900 text-sm">
                      ${result.total_cost_usd.toFixed(6)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Elapsed Latency</span>
                    <span className="font-bold font-mono text-slate-800 text-sm">
                      {result.total_latency_ms}ms
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Total Tokens</span>
                    <span className="font-bold font-mono text-slate-800 text-sm">
                      {result.total_tokens}
                    </span>
                  </div>
                </div>
              </div>

              {/* Step 2: Quality Guardian Verification Report */}
              <div className="bg-white rounded-2xl p-5 border border-surface-border shadow-subtle space-y-2 text-xs">
                <div className="flex items-center justify-between font-semibold text-slate-800">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-forest-700" />
                    <span>Quality Guardian Verification Report</span>
                  </div>
                  <span className="font-mono text-forest-800">
                    Quality: {((result.verification?.score ?? 1.0) * 100).toFixed(0)}%
                  </span>
                </div>
                
                <p className="text-slate-600 italic">
                  "{result.verification?.rationale || 'Verification checks passed.'}"
                </p>

                {result.verification?.passed_checks && result.verification.passed_checks.length > 0 && (
                  <div className="pt-2 space-y-1">
                    {result.verification.passed_checks.map((check, i) => (
                      <div key={i} className="flex items-center gap-1.5 text-emerald-800">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>{check}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Step 3: Verified Final Response Output */}
              <div className="bg-white rounded-2xl p-5 border border-surface-border shadow-subtle space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-700 pb-2 border-b border-slate-100">
                  <span>Model Response Output</span>
                  <span className="text-[11px] font-mono text-slate-400">{result.selected_model_id}</span>
                </div>
                <div className="p-3 bg-surface-muted rounded-xl text-xs font-sans text-slate-800 whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
                  {result.final_response}
                </div>
              </div>

            </div>
          )}

        </div>

      </div>

      {/* Modal */}
      {showTraceModal && result && (
        <ExecutionTraceModal
          trace={result}
          onClose={() => setShowTraceModal(false)}
        />
      )}

    </div>
  );
};

