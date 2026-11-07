'use client';

import React, { useState, useEffect } from 'react';
import {
  Brain,
  Plus,
  Trash2,
  Pin,
  Sparkles,
  ShieldAlert,
  Edit2,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { MemoryItem } from '@/types';
import { apiRequest } from '@/lib/api';

export default function MemoryView() {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [content, setContent] = useState('');
  const [category, setCategory] = useState<'preference' | 'personal' | 'professional' | 'habit' | 'goal'>('preference');
  const [isPinned, setIsPinned] = useState(false);

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const data = await apiRequest<MemoryItem[]>('/memories');
      setMemories(data);
    } catch (e) {
      console.warn('Could not load memories', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    try {
      await apiRequest('/memories', {
        method: 'POST',
        body: JSON.stringify({
          category,
          content,
          is_pinned: isPinned
        })
      });
      setIsModalOpen(false);
      setContent('');
      setIsPinned(false);
      fetchMemories();
    } catch (e) {
      console.warn('Failed to add memory', e);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiRequest(`/memories/${id}`, { method: 'DELETE' });
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      console.warn('Failed to delete memory', e);
    }
  };

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to permanently clear all stored executive memories?')) {
      try {
        await apiRequest('/memories/clear/all', { method: 'DELETE' });
        setMemories([]);
      } catch (e) {
        console.warn('Failed to clear memories', e);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-purple-400">
            <Brain className="w-4 h-4" />
            <span>Personal & Executive Memory Engine</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Isolated Semantic Memory
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Full user governance: view, refine, add, or permanently delete personal habits, constraints, and project memories.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClearAll}
            className="px-3 py-2 rounded-xl text-xs font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 border border-rose-500/20 transition-all"
          >
            Clear All
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Memory Fact</span>
          </button>
        </div>
      </div>

      {/* Memory Cards Grid */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-purple-400" />
          <span>Retrieving semantic memory bank...</span>
        </div>
      ) : memories.length === 0 ? (
        <div className="text-center p-12 bg-[#0F172A] border border-[#1E293B] rounded-2xl text-slate-400">
          <Brain className="w-8 h-8 text-slate-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-white">No memory items indexed</h4>
          <p className="text-xs">Add explicit preferences or allow the assistant to remember your habits.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {memories.map((mem) => (
            <div
              key={mem.id}
              className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] hover:border-slate-700 shadow-md space-y-3 flex flex-col justify-between transition-all"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-purple-500/15 text-purple-400 border border-purple-500/25">
                    {mem.category}
                  </span>
                  {mem.is_pinned && (
                    <span className="flex items-center gap-1 text-[10px] text-amber-400 font-semibold">
                      <Pin className="w-3 h-3 fill-amber-400" />
                      Pinned
                    </span>
                  )}
                </div>

                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                  {mem.content}
                </p>
              </div>

              <div className="pt-3 border-t border-[#1E293B] flex items-center justify-between">
                <span className="text-[10px] text-slate-500">
                  {new Date(mem.created_at).toLocaleDateString()}
                </span>
                <button
                  onClick={() => handleDelete(mem.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Memory Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <form
            onSubmit={handleAddMemory}
            className="w-full max-w-md bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-2xl p-6 space-y-4"
          >
            <h3 className="text-base font-bold text-white">Record Executive Memory Item</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-400">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value as any)}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="preference">Executive Preference</option>
                  <option value="professional">Professional Context</option>
                  <option value="habit">Working Habit</option>
                  <option value="goal">Strategic Goal</option>
                  <option value="personal">Personal Detail</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Memory Fact or Constraint</label>
                <textarea
                  rows={3}
                  required
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="e.g. Never schedule investor calls before 10 AM; prefer concise bullet summaries."
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-purple-500 resize-none"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="pinCheck"
                  checked={isPinned}
                  onChange={(e) => setIsPinned(e.target.checked)}
                  className="rounded border-slate-700 text-purple-600 focus:ring-0"
                />
                <label htmlFor="pinCheck" className="text-xs text-slate-300">
                  Pin to always include in high-priority context
                </label>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1E293B]">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-md shadow-purple-600/20"
              >
                Index Memory
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
