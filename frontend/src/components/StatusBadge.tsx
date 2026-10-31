import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, RefreshCw, ShieldCheck } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const pad = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';

  switch (status) {
    case 'Verified Pass':
    case 'success':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 ${pad}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          <span>Verified Pass</span>
        </span>
      );
    case 'Partially Verified':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 ${pad}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          <span>Partially Verified</span>
        </span>
      );
    case 'Failed Verification':
    case 'failed':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-rose-50 text-rose-800 border border-rose-200 ${pad}`}>
          <XCircle className="w-3.5 h-3.5 text-rose-600" />
          <span>Failed Verification</span>
        </span>
      );
    case 'fallback':
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200 ${pad}`}>
          <RefreshCw className="w-3.5 h-3.5 text-blue-600 animate-spin-slow" />
          <span>Fallback Triggered</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 ${pad}`}>
          <ShieldCheck className="w-3.5 h-3.5 text-slate-500" />
          <span>{status}</span>
        </span>
      );
  }
};

