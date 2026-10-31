import React, { useState, useEffect } from 'react';
import {
  Cpu, Shield, CheckCircle2, XCircle, Search, Filter,
  DollarSign, Clock, Layers, Plus, Edit2, Trash2, X, AlertCircle, RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { ModelItem } from '../types';

export const ModelRegistryPage: React.FC = () => {
  const [models, setModels] = useState<ModelItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [providerFilter, setProviderFilter] = useState<string>('');
  const [tierFilter, setTierFilter] = useState<string>('');
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingModel, setEditingModel] = useState<ModelItem | null>(null);
  const [modalError, setModalError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  // Delete confirmation
  const [deletingModelId, setDeletingModelId] = useState<string | null>(null);
  const [bannerMessage, setBannerMessage] = useState<{ text: string; type: 'success' | 'info' | 'error' } | null>(null);

  // Form Fields
  const [formData, setFormData] = useState({
    name: '',
    model_id: '',
    provider: 'openai',
    tier: 'balanced',
    input_cost_per_m: 0.50,
    output_cost_per_m: 1.50,
    benchmark_quality_score: 0.85,
    latency_p50_ms: 450,
    context_window: 128000,
    privacy_tier: 'standard',
    capabilities: ['reasoning', 'code'],
    enabled: true
  });

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await api.getModels();
      setModels(data);
    } catch (e) {
      console.error(e);
      setBannerMessage({ text: 'Failed to load model registry from database.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAddModal = () => {
    setEditingModel(null);
    setFormData({
      name: '',
      model_id: '',
      provider: 'openai',
      tier: 'balanced',
      input_cost_per_m: 0.50,
      output_cost_per_m: 1.50,
      benchmark_quality_score: 0.85,
      latency_p50_ms: 450,
      context_window: 128000,
      privacy_tier: 'standard',
      capabilities: ['reasoning', 'code'],
      enabled: true
    });
    setModalError(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (model: ModelItem) => {
    setEditingModel(model);
    setFormData({
      name: model.name,
      model_id: model.model_id,
      provider: model.provider,
      tier: model.tier,
      input_cost_per_m: model.input_cost_per_m,
      output_cost_per_m: model.output_cost_per_m,
      benchmark_quality_score: model.benchmark_quality_score,
      latency_p50_ms: model.latency_p50_ms,
      context_window: model.context_window,
      privacy_tier: model.privacy_tier,
      capabilities: model.capabilities || [],
      enabled: model.enabled
    });
    setModalError(null);
    setIsModalOpen(true);
  };

  const handleSaveModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.model_id.trim()) {
      setModalError('Model Display Name and Model Identifier are required.');
      return;
    }

    setSaving(true);
    setModalError(null);

    try {
      if (editingModel) {
        // Edit existing model
        const updated = await api.updateModel(editingModel.model_id, {
          name: formData.name,
          tier: formData.tier,
          input_cost_per_m: Number(formData.input_cost_per_m),
          output_cost_per_m: Number(formData.output_cost_per_m),
          benchmark_quality_score: Number(formData.benchmark_quality_score),
          latency_p50_ms: Number(formData.latency_p50_ms),
          context_window: Number(formData.context_window),
          privacy_tier: formData.privacy_tier,
          capabilities: formData.capabilities,
          enabled: formData.enabled
        });
        setModels(prev => prev.map(m => m.model_id === editingModel.model_id ? updated : m));
        setBannerMessage({ text: `Model '${updated.name}' updated successfully in database.`, type: 'success' });
      } else {
        // Add new model
        const created = await api.createModel({
          name: formData.name.trim(),
          model_id: formData.model_id.trim().toLowerCase(),
          provider: formData.provider,
          tier: formData.tier,
          input_cost_per_m: Number(formData.input_cost_per_m),
          output_cost_per_m: Number(formData.output_cost_per_m),
          benchmark_quality_score: Number(formData.benchmark_quality_score),
          latency_p50_ms: Number(formData.latency_p50_ms),
          context_window: Number(formData.context_window),
          privacy_tier: formData.privacy_tier,
          capabilities: formData.capabilities,
          enabled: formData.enabled
        });
        setModels(prev => [...prev, created]);
        setBannerMessage({ text: `New model '${created.name}' registered and active in router.`, type: 'success' });
      }
      setIsModalOpen(false);
    } catch (err: any) {
      setModalError(err.message || 'Failed to save model.');
    } finally {
      setSaving(false);
    }
  };

  const toggleModelStatus = async (modelId: string, currentStatus: boolean) => {
    try {
      await api.updateModel(modelId, { enabled: !currentStatus });
      setModels((prev) =>
        prev.map((m) => (m.model_id === modelId ? { ...m, enabled: !currentStatus } : m))
      );
      setBannerMessage({ 
        text: `Model '${modelId}' ${!currentStatus ? 'enabled' : 'disabled'} in routing registry.`,
        type: 'info' 
      });
    } catch (e: any) {
      console.error(e);
      setBannerMessage({ text: `Failed to update model status: ${e.message}`, type: 'error' });
    }
  };

  const handleConfirmDelete = async () => {
    if (!deletingModelId) return;
    try {
      const res = await api.deleteModel(deletingModelId);
      if (res.status === 'deactivated') {
        setModels(prev => prev.map(m => m.model_id === deletingModelId ? { ...m, enabled: false } : m));
        setBannerMessage({ text: res.message, type: 'info' });
      } else {
        setModels(prev => prev.filter(m => m.model_id !== deletingModelId));
        setBannerMessage({ text: res.message, type: 'success' });
      }
    } catch (e: any) {
      setBannerMessage({ text: `Error deleting model: ${e.message}`, type: 'error' });
    } finally {
      setDeletingModelId(null);
    }
  };

  const handleCapabilityToggle = (cap: string) => {
    setFormData(prev => ({
      ...prev,
      capabilities: prev.capabilities.includes(cap)
        ? prev.capabilities.filter(c => c !== cap)
        : [...prev.capabilities, cap]
    }));
  };

  const filteredModels = models.filter((m) => {
    const matchesSearch =
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.model_id.toLowerCase().includes(search.toLowerCase());
    const matchesProvider = providerFilter ? m.provider === providerFilter : true;
    const matchesTier = tierFilter ? m.tier === tierFilter : true;
    return matchesSearch && matchesProvider && matchesTier;
  });

  return (
    <div className="space-y-6 animate-fade-in w-full">
      
      {/* Banner message */}
      {bannerMessage && (
        <div className={`p-4 rounded-xl border text-xs flex items-center justify-between transition-all ${
          bannerMessage.type === 'success' 
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
            : bannerMessage.type === 'error'
            ? 'bg-rose-50 border-rose-200 text-rose-900'
            : 'bg-blue-50 border-blue-200 text-blue-900'
        }`}>
          <span>{bannerMessage.text}</span>
          <button onClick={() => setBannerMessage(null)} className="p-1 hover:opacity-75">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Enterprise Model Registry
            </h1>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
              {models.length} Models Cataloged
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Database-backed registry managing inference pricing, privacy tiers, quality baselines, and intelligent routing eligibility.
          </p>
        </div>

        <button
          onClick={handleOpenAddModal}
          className="inline-flex items-center gap-2 px-4 py-2 bg-forest-800 hover:bg-forest-900 text-white text-xs font-semibold rounded-xl shadow-card transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Model</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 bg-white rounded-2xl border border-surface-border shadow-subtle flex flex-wrap items-center gap-3 text-xs w-full">
        <div className="flex items-center gap-2 bg-surface-muted px-3 py-1.5 rounded-xl border border-slate-200 flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search model name or identifier..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent border-none focus:outline-none w-full text-slate-800 placeholder-slate-400 font-medium"
          />
        </div>

        <select
          value={providerFilter}
          onChange={(e) => setProviderFilter(e.target.value)}
          className="rounded-xl border border-slate-200 px-3 py-1.5 bg-white text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-forest-600"
        >
          <option value="">All Providers</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="google">Google</option>
          <option value="groq">Groq</option>
          <option value="deepseek">DeepSeek</option>
          <option value="mistral">Mistral</option>
          <option value="meta">Meta</option>
          <option value="local">Local (On-Prem)</option>
        </select>

        <select
          value={tierFilter}
          onChange={(e) => setTierFilter(e.target.value)}
          className="rounded-xl border border-slate-200 px-3 py-1.5 bg-white text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-forest-600"
        >
          <option value="">All Tiers</option>
          <option value="flagship">Flagship</option>
          <option value="balanced">Balanced</option>
          <option value="economy">Economy</option>
          <option value="specialized">Specialized</option>
        </select>

        <span className="text-slate-400 ml-auto">
          Showing {filteredModels.length} models
        </span>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredModels.map((m) => (
          <div
            key={m.model_id}
            className={`p-5 rounded-2xl border transition-all flex flex-col justify-between ${
              m.enabled
                ? 'bg-white border-surface-border shadow-subtle hover:border-forest-300'
                : 'bg-slate-50/70 border-slate-200 opacity-60'
            }`}
          >
            <div>
              {/* Top row */}
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-surface-muted text-slate-600 border border-slate-200">
                    {m.provider} • {m.tier}
                  </span>
                  <h3 className="mt-2 text-base font-bold text-slate-900">
                    {m.name}
                  </h3>
                  <span className="text-xs font-mono text-slate-400 block mt-0.5">
                    {m.model_id}
                  </span>
                </div>

                {/* Enable/Disable Toggle */}
                <button
                  onClick={() => toggleModelStatus(m.model_id, m.enabled)}
                  className={`p-1.5 rounded-xl text-xs font-semibold flex items-center gap-1 border transition-colors ${
                    m.enabled
                      ? 'bg-forest-50 text-forest-800 border-forest-200 hover:bg-forest-100'
                      : 'bg-slate-100 text-slate-500 border-slate-300 hover:bg-slate-200'
                  }`}
                  title={m.enabled ? 'Click to disable model' : 'Click to enable model'}
                >
                  {m.enabled ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 text-forest-600" />
                      <span>Enabled</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-3.5 h-3.5 text-slate-400" />
                      <span>Disabled</span>
                    </>
                  )}
                </button>
              </div>

              {/* Pricing Matrix */}
              <div className="mt-4 p-3 rounded-xl bg-surface-muted border border-slate-100 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block">Input / 1M Tokens</span>
                  <span className="font-mono font-bold text-slate-800">
                    ${m.input_cost_per_m.toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Output / 1M Tokens</span>
                  <span className="font-mono font-bold text-slate-800">
                    ${m.output_cost_per_m.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Benchmark & Specs */}
              <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs py-2 border-y border-slate-100">
                <div>
                  <span className="text-[10px] text-slate-400 block">Quality</span>
                  <span className="font-semibold text-slate-900">
                    {(m.benchmark_quality_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">P50 Latency</span>
                  <span className="font-mono text-slate-800">
                    {m.latency_p50_ms}ms
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Context</span>
                  <span className="font-mono text-slate-800">
                    {(m.context_window / 1000).toFixed(0)}k
                  </span>
                </div>
              </div>

              {/* Privacy & Capabilities */}
              <div className="mt-3 space-y-1 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Shield className="w-3.5 h-3.5 text-forest-700" />
                    <span className="font-medium text-slate-700 capitalize">{m.privacy_tier?.replace('_', ' ')}</span>
                  </span>
                </div>
                <div className="text-slate-400 text-[11px] truncate">
                  Caps: {m.capabilities?.join(', ') || 'general'}
                </div>
              </div>
            </div>

            {/* Action buttons footer */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end gap-2 text-xs">
              <button
                onClick={() => handleOpenEditModal(m)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium transition-colors"
              >
                <Edit2 className="w-3.5 h-3.5" />
                <span>Edit</span>
              </button>
              <button
                onClick={() => setDeletingModelId(m.model_id)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-rose-200 bg-rose-50 hover:bg-rose-100 text-rose-700 font-medium transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Remove</span>
              </button>
            </div>

          </div>
        ))}
      </div>

      {/* Add / Edit Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-elevated border border-surface-border p-6 max-h-[90vh] overflow-y-auto">
            
            <div className="flex items-center justify-between pb-3 border-b border-surface-border mb-4">
              <h2 className="text-lg font-bold text-slate-900">
                {editingModel ? `Edit Model: ${editingModel.name}` : 'Register New AI Model'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {modalError && (
              <div className="p-3 mb-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleSaveModel} className="space-y-4 text-xs">
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Display Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Llama 3.3 70B Turbo"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-forest-600 font-medium text-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Model Identifier *</label>
                  <input
                    type="text"
                    required
                    disabled={!!editingModel}
                    placeholder="e.g. llama-3.3-70b-groq"
                    value={formData.model_id}
                    onChange={(e) => setFormData({ ...formData, model_id: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-forest-600 font-mono text-slate-800 disabled:bg-slate-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Provider *</label>
                  <select
                    value={formData.provider}
                    disabled={!!editingModel}
                    onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-forest-600 bg-white font-medium text-slate-800 disabled:bg-slate-100"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                    <option value="groq">Groq</option>
                    <option value="deepseek">DeepSeek</option>
                    <option value="mistral">Mistral</option>
                    <option value="meta">Meta</option>
                    <option value="local">Local (On-Prem)</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Tier *</label>
                  <select
                    value={formData.tier}
                    onChange={(e) => setFormData({ ...formData, tier: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-1 focus:ring-forest-600 bg-white font-medium text-slate-800"
                  >
                    <option value="flagship">Flagship (Advanced)</option>
                    <option value="balanced">Balanced (Mid)</option>
                    <option value="economy">Economy (SLM)</option>
                    <option value="specialized">Specialized</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Input Cost ($/1M Toks) *</label>
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    required
                    value={formData.input_cost_per_m}
                    onChange={(e) => setFormData({ ...formData, input_cost_per_m: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 font-mono text-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Output Cost ($/1M Toks) *</label>
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    required
                    value={formData.output_cost_per_m}
                    onChange={(e) => setFormData({ ...formData, output_cost_per_m: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 font-mono text-slate-800"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Quality (0-1) *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.1"
                    max="1.0"
                    required
                    value={formData.benchmark_quality_score}
                    onChange={(e) => setFormData({ ...formData, benchmark_quality_score: parseFloat(e.target.value) || 0.85 })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 font-mono text-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">P50 Latency (ms)</label>
                  <input
                    type="number"
                    step="10"
                    min="50"
                    value={formData.latency_p50_ms}
                    onChange={(e) => setFormData({ ...formData, latency_p50_ms: parseInt(e.target.value) || 450 })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 font-mono text-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Context (Toks)</label>
                  <input
                    type="number"
                    step="1000"
                    min="4000"
                    value={formData.context_window}
                    onChange={(e) => setFormData({ ...formData, context_window: parseInt(e.target.value) || 128000 })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 font-mono text-slate-800"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Privacy Tier *</label>
                <select
                  value={formData.privacy_tier}
                  onChange={(e) => setFormData({ ...formData, privacy_tier: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-white font-medium text-slate-800"
                >
                  <option value="standard">Standard (Cloud API)</option>
                  <option value="enterprise">Enterprise (BAA / Zero Retention)</option>
                  <option value="hipaa_eligible">HIPAA Eligible</option>
                  <option value="zero_data_retention">Zero Data Retention (ZDR)</option>
                  <option value="local_only">Local Only (On-Premises / Air-Gapped)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1.5">Supported Capabilities</label>
                <div className="flex flex-wrap gap-2">
                  {['reasoning', 'code', 'json_mode', 'function_calling', 'vision'].map(cap => (
                    <button
                      type="button"
                      key={cap}
                      onClick={() => handleCapabilityToggle(cap)}
                      className={`px-2.5 py-1 rounded-lg border text-xs font-medium transition-all ${
                        formData.capabilities.includes(cap)
                          ? 'bg-forest-100 text-forest-900 border-forest-300 font-semibold'
                          : 'bg-slate-50 text-slate-600 border-slate-200'
                      }`}
                    >
                      {cap}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between border-t border-slate-100">
                <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                    className="rounded text-forest-700"
                  />
                  <span>Active in Intelligent Router</span>
                </label>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 font-semibold hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-4 py-2 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-semibold flex items-center gap-1.5 shadow-subtle"
                  >
                    {saving && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                    <span>{editingModel ? 'Update Model' : 'Register Model'}</span>
                  </button>
                </div>
              </div>

            </form>
          </div>
        </div>
      )}

      {/* Delete / Deactivate Confirmation Dialog */}
      {deletingModelId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-sm bg-white rounded-2xl shadow-elevated border border-surface-border p-6 text-xs space-y-4">
            <h3 className="text-base font-bold text-slate-900">
              Confirm Model Removal
            </h3>
            <p className="text-slate-600 leading-relaxed">
              Are you sure you want to remove model <strong className="font-mono text-slate-900">{deletingModelId}</strong>?
            </p>
            <p className="text-slate-500 bg-surface-muted p-2.5 rounded-lg border border-slate-200">
              <em>Note:</em> If this model has historical request audit logs, AstraRoute AI will safely <strong>deactivate</strong> the candidate instead of destructive deletion to preserve historical telemetry and compliance records.
            </p>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setDeletingModelId(null)}
                className="px-3.5 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-semibold shadow-subtle"
              >
                Confirm Removal
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
