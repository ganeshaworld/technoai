'use client';

import React, { useState, useEffect } from 'react';
import {
  AppWindow,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  RefreshCw,
  Plus,
  Loader2
} from 'lucide-react';
import { IntegrationItem } from '@/types';
import { apiRequest } from '@/lib/api';

export default function IntegrationsView() {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest<IntegrationItem[]>('/integrations')
      .then(setIntegrations)
      .catch((e) => console.warn('Could not load integrations', e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400">
            <AppWindow className="w-4 h-4" />
            <span>Connected Apps & Ecosystem</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Integrations Marketplace
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Connect external productivity apps with strict OAuth token encryption and explicit authorization scopes.
          </p>
        </div>
      </div>

      {/* Integrations Grid */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
          <span>Auditing active connections...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {integrations.map((item) => {
            const isConnected = item.status === 'connected';
            return (
              <div
                key={item.id}
                className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] hover:border-slate-700 shadow-md space-y-4 flex flex-col justify-between transition-all"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      {item.category}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase border ${
                        isConnected
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-100">{item.name}</h4>
                    {item.account_email && (
                      <p className="text-xs text-slate-400 mt-0.5">
                        Account: <span className="text-slate-300 font-mono">{item.account_email}</span>
                      </p>
                    )}
                  </div>

                  {item.scopes && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {item.scopes.map((s, idx) => (
                        <span key={idx} className="text-[9px] px-1.5 py-0.5 rounded bg-[#070B14] text-slate-400 border border-[#1E293B]">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-[#1E293B] flex items-center justify-between">
                  <span className="text-[10px] text-slate-500">
                    {isConnected ? 'AES-256 Encrypted' : 'Requires OAuth 2.0'}
                  </span>

                  {isConnected ? (
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white bg-[#1E293B] hover:bg-slate-700 transition-colors">
                      <RefreshCw className="w-3 h-3" />
                      <span>Reauthorize</span>
                    </button>
                  ) : (
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-600/20 transition-all">
                      <ExternalLink className="w-3 h-3" />
                      <span>Connect App</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
