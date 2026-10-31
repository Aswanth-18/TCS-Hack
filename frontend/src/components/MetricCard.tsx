import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    positive?: boolean;
    neutral?: boolean;
  };
  highlight?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subValue,
  icon: Icon,
  trend,
  highlight = false,
}) => {
  return (
    <div
      className={`rounded-2xl p-5 border transition-all duration-200 ${
        highlight
          ? 'bg-gradient-to-br from-forest-50/70 via-white to-sage-50/50 border-forest-200 shadow-card'
          : 'bg-white border-surface-border shadow-subtle hover:border-sage-300'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
          {title}
        </span>
        <div
          className={`p-2.5 rounded-xl ${
            highlight ? 'bg-forest-100 text-forest-800' : 'bg-surface-muted text-slate-600'
          }`}
        >
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-slate-900">{value}</div>
        {subValue && (
          <div className="mt-1 text-xs text-slate-500 font-medium">{subValue}</div>
        )}
      </div>

      {trend && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-xs">
          <span
            className={`font-semibold ${
              trend.neutral
                ? 'text-slate-600'
                : trend.positive
                ? 'text-emerald-700'
                : 'text-rose-700'
            }`}
          >
            {trend.value}
          </span>
          <span className="text-slate-400">vs Always-Advanced Baseline</span>
        </div>
      )}
    </div>
  );
};

