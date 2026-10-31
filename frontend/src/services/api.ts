import {
  RequestAnalysis, ModelItem, ExecutionResponse, FinOpsSummary,
  BenchmarkRunItem, FinOpsRecommendation, AdaptiveObservation, SystemHealth
} from '../types';

const BASE_URL = '/api';

export const api = {
  // Health
  getHealth: async (): Promise<SystemHealth> => {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  // Requests
  analyzeRequest: async (payload: {
    prompt: string;
    task_type?: string;
    max_budget?: number;
    min_quality?: number;
    max_latency?: number;
    sensitivity?: string;
    criticality?: string;
  }): Promise<RequestAnalysis> => {
    const res = await fetch(`${BASE_URL}/requests/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Analysis failed');
    return res.json();
  },

  executeRequest: async (payload: {
    prompt: string;
    task_type?: string;
    max_budget?: number;
    min_quality?: number;
    max_latency?: number;
    sensitivity?: string;
    criticality?: string;
    strategy?: string;
    simulate_failure_attempt?: boolean;
  }): Promise<ExecutionResponse> => {
    const res = await fetch(`${BASE_URL}/requests/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Execution failed');
    }
    return res.json();
  },

  // Models
  getModels: async (): Promise<ModelItem[]> => {
    const res = await fetch(`${BASE_URL}/models`);
    if (!res.ok) throw new Error('Failed to fetch models');
    return res.json();
  },

  updateModel: async (modelId: string, update: Partial<ModelItem>): Promise<ModelItem> => {
    const res = await fetch(`${BASE_URL}/models/${modelId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(update)
    });
    if (!res.ok) throw new Error('Failed to update model');
    return res.json();
  },

  createModel: async (model: Partial<ModelItem>): Promise<ModelItem> => {
    const res = await fetch(`${BASE_URL}/models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(model)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create model');
    }
    return res.json();
  },

  deleteModel: async (modelId: string): Promise<{ status: string; message: string; model_id: string; enabled?: boolean }> => {
    const res = await fetch(`${BASE_URL}/models/${modelId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to remove model');
    }
    return res.json();
  },

  // FinOps
  getFinOpsSummary: async (): Promise<FinOpsSummary> => {
    const res = await fetch(`${BASE_URL}/finops/summary`);
    if (!res.ok) throw new Error('Failed to fetch FinOps summary');
    return res.json();
  },

  getRecommendations: async (status?: string): Promise<FinOpsRecommendation[]> => {
    const url = status ? `${BASE_URL}/finops/recommendations?status=${status}` : `${BASE_URL}/finops/recommendations`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },

  applyRecommendation: async (id: string) => {
    const res = await fetch(`${BASE_URL}/finops/recommendations/${id}/apply`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to apply recommendation');
    return res.json();
  },

  dismissRecommendation: async (id: string) => {
    const res = await fetch(`${BASE_URL}/finops/recommendations/${id}/dismiss`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to dismiss recommendation');
    return res.json();
  },

  // Benchmarks
  runBenchmark: async (limit: number = 15): Promise<BenchmarkRunItem[]> => {
    const res = await fetch(`${BASE_URL}/benchmarks/run?limit=${limit}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to run benchmark');
    return res.json();
  },

  getBenchmarkHistory: async (): Promise<BenchmarkRunItem[]> => {
    const res = await fetch(`${BASE_URL}/benchmarks/history`);
    if (!res.ok) throw new Error('Failed to fetch benchmark history');
    return res.json();
  },

  getBenchmarkExportUrl: () => `${BASE_URL}/benchmarks/export`,

  // Policy
  getCurrentPolicy: async () => {
    const res = await fetch(`${BASE_URL}/policies`);
    if (!res.ok) throw new Error('Failed to fetch policy');
    return res.json();
  },

  simulatePolicy: async (payload: any) => {
    const res = await fetch(`${BASE_URL}/policies/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to simulate policy');
    return res.json();
  },

  applyPolicy: async (payload: any) => {
    const res = await fetch(`${BASE_URL}/policies/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to apply policy');
    return res.json();
  },

  // Adaptation
  getAdaptationHistory: async (): Promise<AdaptiveObservation[]> => {
    const res = await fetch(`${BASE_URL}/adaptation/history`);
    if (!res.ok) throw new Error('Failed to fetch adaptation history');
    return res.json();
  },

  rollbackAdaptation: async (modelId: string, taskCategory: string) => {
    const res = await fetch(`${BASE_URL}/adaptation/rollback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, task_category: taskCategory })
    });
    if (!res.ok) throw new Error('Rollback failed');
    return res.json();
  },

  // Audit
  getAuditHistory: async (limit: number = 50, filters?: Record<string, string>) => {
    const params = new URLSearchParams({ limit: String(limit), ...filters });
    const res = await fetch(`${BASE_URL}/audit?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch audit records');
    return res.json();
  },

  getAuditDetail: async (requestId: string) => {
    const res = await fetch(`${BASE_URL}/audit/${requestId}`);
    if (!res.ok) throw new Error('Failed to fetch audit detail');
    return res.json();
  }
};

