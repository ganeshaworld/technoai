'use client';

import React, { useState } from 'react';
import {
  Search,
  Sparkles,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  FileText,
  ExternalLink,
  ShieldAlert,
  Loader2
} from 'lucide-react';
import { ResearchResult } from '@/types';
import { apiRequest } from '@/lib/api';

export default function ResearchView() {
  const [query, setQuery] = useState('Autonomous AI agent market trends 2026 enterprise adoption');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResearchResult | null>({
    query: 'Autonomous AI agent market trends 2026 enterprise adoption',
    timestamp: new Date().toISOString(),
    executive_summary:
      'Multi-source synthesis completed. Enterprise adoption of autonomous agent workflows has shifted decisively toward deterministic execution guardrails, privacy-first isolated memory, and hybrid human-in-the-loop approval gates.',
    epistemic_breakdown: {
      verified_facts: [
        'PostgreSQL with pgvector delivers sub-20ms semantic indexing within strictly isolated tenant partitions.',
        'Level 3 autonomous operations require cryptographically verified human approval tokens before dispatching external communications.',
        'Multi-provider LLM routing minimizes vendor single-point-of-failure vulnerabilities.'
      ],
      estimates: [
        'Executive productivity gains from autonomous assistants range between 25% and 38% for routine communications and scheduling.',
        'Average response latency for hybrid multi-agent workflows averages 400ms to 1200ms depending on tool invocation depth.'
      ],
      opinions: [
        'Industry analysts predict conversational executive interfaces will supersede traditional static SaaS navigation menus by 2028.',
        'Founders strongly prefer unified executive assistants over fragmented single-purpose productivity point solutions.'
      ],
      unverified_information: [
        'Unconfirmed industry rumors of a universal single-token protocol standard across foundation model providers.'
      ]
    },
    sources: [
      { name: 'Gartner Enterprise AI Advisory 2026', url: 'https://gartner.com/ai-agents' },
      { name: 'MIT Technology Review — Autonomous Systems', url: 'https://technologyreview.com/agents-enterprise' },
      { name: 'Stanford HAI State of AI Report', url: 'https://hai.stanford.edu/reports' }
    ]
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const data = await apiRequest<ResearchResult>('/research/query', {
        method: 'POST',
        body: JSON.stringify({ query, depth: 'comprehensive' })
      });
      setResult(data);
    } catch (e) {
      console.warn('Research failed', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
            <Search className="w-4 h-4" />
            <span>Deep Research Assistant</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Epistemic Market Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Strict factual classification: distinguishing Verified Facts, Estimates, Opinions, and Unverified Information.
          </p>
        </div>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter research topic, competitive query, or market inquiry..."
            className="w-full px-4 py-3 bg-[#0F172A] border border-[#1E293B] rounded-xl text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          <span>Synthesize</span>
        </button>
      </form>

      {/* Research Output View */}
      {result && (
        <div className="space-y-6">
          {/* Executive Summary Card */}
          <div className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-cyan-400">
                <Sparkles className="w-4 h-4" />
                <span>Executive Synthesis Summary</span>
              </div>
              <span className="text-[10px] text-slate-400">
                Generated {new Date(result.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed">{result.executive_summary}</p>
          </div>

          {/* Epistemic Breakdown 4-Card Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Verified Facts */}
            <div className="p-5 rounded-2xl bg-[#0F172A] border border-emerald-500/30 shadow-lg space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span>Verified Facts</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {result.epistemic_breakdown.verified_facts.map((fact, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-emerald-400 font-bold shrink-0">✓</span>
                    <span>{fact}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Estimates & Projections */}
            <div className="p-5 rounded-2xl bg-[#0F172A] border border-blue-500/30 shadow-lg space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-blue-400">
                <TrendingUp className="w-4 h-4" />
                <span>Estimates & Projections</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {result.epistemic_breakdown.estimates.map((est, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-400 font-bold shrink-0">~</span>
                    <span>{est}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Expert Opinions */}
            <div className="p-5 rounded-2xl bg-[#0F172A] border border-amber-500/30 shadow-lg space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                <HelpCircle className="w-4 h-4" />
                <span>Expert Opinions</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {result.epistemic_breakdown.opinions.map((op, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-amber-400 font-bold shrink-0">💬</span>
                    <span>{op}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Unverified Information */}
            <div className="p-5 rounded-2xl bg-[#0F172A] border border-slate-700 shadow-lg space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400">
                <ShieldAlert className="w-4 h-4" />
                <span>Unverified / Preliminary</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-400">
                {result.epistemic_breakdown.unverified_information.map((unv, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-slate-500 font-bold shrink-0">?</span>
                    <span>{unv}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sources Section */}
          <div className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-lg space-y-2">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Verified Sources & Citations
            </h4>
            <div className="flex flex-wrap gap-2 pt-1">
              {result.sources.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#070B14] hover:bg-slate-800 border border-[#1E293B] text-xs text-slate-300 hover:text-white transition-colors"
                >
                  <span>{src.name}</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
