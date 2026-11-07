'use client';

import React from 'react';
import {
  LayoutDashboard,
  Bot,
  CheckSquare,
  Calendar,
  Mail,
  FileText,
  Search,
  Workflow,
  Brain,
  AppWindow,
  Bell,
  Settings,
  Sun,
  Moon,
  ChevronRight,
  ShieldCheck,
  Sparkles,
  Menu,
  X
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  isDark: boolean;
  setIsDark: (dark: boolean) => void;
  isMobileOpen: boolean;
  setIsMobileOpen: (open: boolean) => void;
  unreadCount?: number;
}

export const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'assistant', label: 'AI Assistant', icon: Bot, badge: 'Live' },
  { id: 'tasks', label: 'My Tasks', icon: CheckSquare },
  { id: 'calendar', label: 'Calendar', icon: Calendar },
  { id: 'emails', label: 'Emails', icon: Mail, badge: '2 VIP' },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'research', label: 'Research', icon: Search },
  { id: 'automations', label: 'Automations', icon: Workflow },
  { id: 'memory', label: 'Memory', icon: Brain },
  { id: 'integrations', label: 'Connected Apps', icon: AppWindow },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({
  currentTab,
  setCurrentTab,
  isDark,
  setIsDark,
  isMobileOpen,
  setIsMobileOpen,
  unreadCount = 3
}: SidebarProps) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 bg-[#070B14] border-r border-[#1E293B] transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand / Logo Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#1E293B]">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white font-bold text-lg shadow-lg shadow-blue-500/20">
              T
            </div>
            <div>
              <div className="flex items-center gap-1.5 font-bold tracking-tight text-white text-base">
                <span>TECHNOPIE</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 font-semibold border border-blue-500/20">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium">Technopie Consultant</p>
            </div>
          </div>
          <button
            onClick={() => setIsMobileOpen(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation List */}
        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentTab(item.id);
                  setIsMobileOpen(false);
                }}
                className={`group flex items-center justify-between w-full px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#0F172A]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                    isActive ? 'bg-blue-500 text-white' : 'bg-[#1E293B] text-slate-300'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Executive Tier & Account Footer */}
        <div className="p-4 border-t border-[#1E293B] bg-[#0B1120]/50 space-y-3">
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#0F172A] border border-[#1E293B]">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <div>
                <p className="text-xs font-semibold text-slate-200">Executive Tier</p>
                <p className="text-[10px] text-slate-400">Level 3 Autonomy Active</p>
              </div>
            </div>
            <button
              onClick={() => setIsDark(!isDark)}
              className="p-1.5 rounded-lg bg-[#1E293B] text-slate-300 hover:text-white transition-colors"
              title="Toggle Theme"
            >
              {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
            </button>
          </div>

          <div className="flex items-center gap-3 px-1">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
              AV
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">Alexander Vance</p>
              <p className="text-[10px] text-slate-400 truncate">alexander@technopie.ai</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
