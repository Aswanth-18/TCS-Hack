import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, PlayCircle, SplitSquareVertical, Cpu, Swords,
  BarChart3, Sliders, Brain, Lightbulb, FileText, Settings as SettingsIcon
} from 'lucide-react';

interface SidebarProps {
  recommendationCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ recommendationCount = 0 }) => {
  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Request Playground', path: '/playground', icon: PlayCircle },
    { name: 'Routing Decisions', path: '/decisions', icon: SplitSquareVertical },
    { name: 'Model Registry', path: '/models', icon: Cpu },
    { name: 'Live Routing Arena', path: '/arena', icon: Swords, badge: 'Benchmark' },
    { name: 'FinOps Analytics', path: '/finops', icon: BarChart3 },
    { name: 'Policy Simulator', path: '/simulator', icon: Sliders },
    { name: 'Adaptive Learning', path: '/adaptation', icon: Brain },
    { name: 'Recommendations', path: '/recommendations', icon: Lightbulb, count: recommendationCount },
    { name: 'Audit History', path: '/audit', icon: FileText },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ];

  return (
    <aside className="fixed top-16 left-0 bottom-0 w-64 bg-white border-r border-surface-border flex flex-col z-30 overflow-y-auto">
      {/* Navigation List */}
      <nav className="p-4 space-y-1 flex-1">
        <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Enterprise Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-forest-50 text-forest-900 font-semibold shadow-subtle border border-forest-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-surface-muted'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 text-slate-500 group-hover:text-forest-700" />
                <span>{item.name}</span>
              </div>

              {item.badge && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  {item.badge}
                </span>
              )}

              {item.count !== undefined && item.count > 0 && (
                <span className="text-[10px] font-semibold w-5 h-5 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center">
                  {item.count}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};
