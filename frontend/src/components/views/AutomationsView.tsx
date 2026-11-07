'use client';

import React, { useState, useEffect } from 'react';
import {
  Workflow,
  Plus,
  Play,
  Pause,
  Clock,
  CheckCircle2,
  AlertCircle,
  Zap,
  Loader2
} from 'lucide-react';
import { apiRequest } from '@/lib/api';

interface AutomationRule {
  id: string;
  title: string;
  description: string;
  trigger: string;
  action: string;
  is_active: boolean;
  last_run: string;
}

export default function AutomationsView() {
  const [automations, setAutomations] = useState<AutomationRule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest<AutomationRule[]>('/automations')
      .then(setAutomations)
      .catch((e) => console.warn('Could not load automations', e))
      .finally(() => setLoading(false));
  }, []);

  const toggleActive = (id: string) => {
    setAutomations((prev) =>
      prev.map((a) => (a.id === id ? { ...a, is_active: !a.is_active } : a))
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-400">
            <Workflow className="w-4 h-4" />
            <span>Autonomous Workflow Engine</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Automations & Scheduled Jobs
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Event-driven triggers, background cron schedules, and cross-application executive pipelines.
          </p>
        </div>

        <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all self-start sm:self-auto">
          <Plus className="w-4 h-4" />
          <span>New Workflow Rule</span>
        </button>
      </div>

      {/* Rules List */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-amber-400" />
          <span>Loading automation pipelines...</span>
        </div>
      ) : (
        <div className="space-y-4">
          {automations.map((auto) => (
            <div
              key={auto.id}
              className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] hover:border-slate-700 shadow-md space-y-3 transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    <Zap className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-100">{auto.title}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{auto.description}</p>
                  </div>
                </div>

                <button
                  onClick={() => toggleActive(auto.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    auto.is_active
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  {auto.is_active ? <Play className="w-3 h-3 fill-emerald-400" /> : <Pause className="w-3 h-3" />}
                  <span>{auto.is_active ? 'Active' : 'Paused'}</span>
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
                <div className="p-2.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
                  <p className="text-[10px] font-bold text-slate-500 uppercase">Trigger Event</p>
                  <p className="font-semibold text-slate-300 mt-0.5">{auto.trigger}</p>
                </div>
                <div className="p-2.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
                  <p className="text-[10px] font-bold text-slate-500 uppercase">Action Pipeline</p>
                  <p className="font-semibold text-slate-300 mt-0.5">{auto.action}</p>
                </div>
              </div>

              <div className="pt-2 text-[10px] text-slate-500 flex items-center justify-between">
                <span>Last execution: {auto.last_run}</span>
                <span className="text-blue-400">Audit logs available</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
