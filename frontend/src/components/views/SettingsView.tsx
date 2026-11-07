'use client';

import React, { useState, useEffect } from 'react';
import {
  Settings,
  CreditCard,
  Shield,
  User,
  Activity,
  Check,
  Zap,
  Globe,
  Loader2
} from 'lucide-react';
import { BillingPlan, AdminStats } from '@/types';
import { apiRequest } from '@/lib/api';

export default function SettingsView() {
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiRequest<BillingPlan[]>('/billing/plans').catch(() => []),
      apiRequest<AdminStats>('/admin/stats').catch(() => null)
    ])
      .then(([p, s]) => {
        setPlans(p);
        setStats(s);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Settings className="w-4 h-4" />
          <span>Platform Settings & Governance</span>
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
          Executive Profile & Subscriptions
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Manage your subscription tier, autonomy thresholds, and review platform telemetry.
        </p>
      </div>

      {/* Subscription Plans */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <CreditCard className="w-4 h-4 text-blue-400" />
          <h3 className="text-base font-bold text-white">Subscription Tiers</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`p-5 rounded-2xl border flex flex-col justify-between transition-all ${
                plan.is_current
                  ? 'bg-gradient-to-b from-blue-950/40 to-[#0F172A] border-blue-500 shadow-lg shadow-blue-500/10'
                  : 'bg-[#0F172A] border-[#1E293B] hover:border-slate-700'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-white">{plan.name}</h4>
                  {plan.is_current && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500 text-white font-bold">
                      CURRENT
                    </span>
                  )}
                </div>

                <div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-2xl font-extrabold text-white">${plan.price_monthly_usd}</span>
                    <span className="text-xs text-slate-400">/mo</span>
                  </div>
                  <p className="text-[10px] text-slate-500 font-medium">₹{plan.price_monthly_inr}/mo (India)</p>
                </div>

                <ul className="space-y-1.5 pt-2 border-t border-[#1E293B] text-[11px] text-slate-300">
                  {plan.features.map((feat, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <Check className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button
                disabled={plan.is_current}
                className={`w-full mt-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  plan.is_current
                    ? 'bg-slate-800 text-slate-400 cursor-default'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20'
                }`}
              >
                {plan.is_current ? 'Active Plan' : 'Select Plan'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Admin Platform Telemetry */}
      {stats && (
        <div className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl space-y-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <h3 className="text-base font-bold text-white">Platform Health & Telemetry</h3>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Active Users</p>
              <p className="text-xl font-bold text-white mt-1">{stats.active_users.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Tokens Processed</p>
              <p className="text-xl font-bold text-white mt-1">{(stats.tokens_processed / 1000000).toFixed(1)}M</p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Vector Query Latency</p>
              <p className="text-xl font-bold text-emerald-400 mt-1">{stats.system_health.vector_search_latency_ms} ms</p>
            </div>
            <div className="p-3.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Monthly Inference Cost</p>
              <p className="text-xl font-bold text-white mt-1">${stats.monthly_api_cost_usd.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
