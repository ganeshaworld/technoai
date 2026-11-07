'use client';

import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Plus,
  Clock,
  Calendar,
  Tag,
  AlertCircle,
  CheckCircle2,
  Trash2,
  Filter,
  Sparkles,
  Loader2
} from 'lucide-react';
import { TaskItem } from '@/types';
import { apiRequest } from '@/lib/api';

export default function TasksView() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState<'all' | 'today' | 'upcoming' | 'overdue' | 'completed'>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDesc, setNewTaskDesc] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [quickInput, setQuickInput] = useState('');

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const data = await apiRequest<TaskItem[]>(`/tasks?view=${currentView}`);
      setTasks(data);
    } catch (e) {
      console.warn('Could not load tasks', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [currentView]);

  const handleToggleStatus = async (task: TaskItem) => {
    const nextStatus = task.status === 'completed' ? 'todo' : 'completed';
    try {
      await apiRequest(`/tasks/${task.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus })
      });
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: nextStatus } : t))
      );
    } catch (e) {
      console.warn('Could not update task', e);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiRequest(`/tasks/${id}`, { method: 'DELETE' });
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (e) {
      console.warn('Could not delete task', e);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    try {
      const created = await apiRequest<TaskItem>('/tasks', {
        method: 'POST',
        body: JSON.stringify({
          title: newTaskTitle,
          description: newTaskDesc,
          priority: newTaskPriority
        })
      });
      setIsModalOpen(false);
      setNewTaskTitle('');
      setNewTaskDesc('');
      fetchTasks();
    } catch (e) {
      console.warn('Failed to create task', e);
    }
  };

  const handleQuickAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickInput.trim()) return;
    try {
      await apiRequest('/tasks', {
        method: 'POST',
        body: JSON.stringify({
          title: quickInput,
          priority: 'high'
        })
      });
      setQuickInput('');
      fetchTasks();
    } catch (e) {
      console.warn('Failed quick add', e);
    }
  };

  return (
    <div className="space-y-6">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400">
            <CheckSquare className="w-4 h-4" />
            <span>Task & Priority Management</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Executive Deliverables
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Organize, prioritize, and delegate your personal and organizational priorities.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>New Executive Task</span>
        </button>
      </div>

      {/* Quick Add Bar */}
      <form onSubmit={handleQuickAdd} className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={quickInput}
            onChange={(e) => setQuickInput(e.target.value)}
            placeholder="Quick natural language task (e.g. 'Review Series A deck tomorrow high priority')..."
            className="w-full px-4 py-2.5 bg-[#0F172A] border border-[#1E293B] rounded-xl text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={!quickInput.trim()}
          className="px-4 py-2.5 rounded-xl bg-[#1E293B] hover:bg-slate-700 text-xs font-semibold text-slate-200 disabled:opacity-40 transition-colors"
        >
          Add
        </button>
      </form>

      {/* View Tabs */}
      <div className="flex items-center gap-2 border-b border-[#1E293B] pb-3 overflow-x-auto">
        {(['all', 'today', 'upcoming', 'overdue', 'completed'] as const).map((view) => (
          <button
            key={view}
            onClick={() => setCurrentView(view)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
              currentView === view
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-400 hover:text-white hover:bg-[#0F172A]'
            }`}
          >
            {view}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
          <span>Loading tasks...</span>
        </div>
      ) : tasks.length === 0 ? (
        <div className="text-center p-12 bg-[#0F172A] border border-[#1E293B] rounded-2xl text-slate-400 space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
          <h4 className="text-sm font-semibold text-white">No tasks found in this view</h4>
          <p className="text-xs">Your priorities are clear! Add a task or direct your AI Assistant to organize your day.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => {
            const isDone = task.status === 'completed';
            return (
              <div
                key={task.id}
                className={`flex items-start justify-between gap-4 p-4 rounded-xl border transition-all ${
                  isDone
                    ? 'bg-[#0B1120]/40 border-[#1E293B]/60 opacity-60'
                    : 'bg-[#0F172A] border-[#1E293B] hover:border-slate-700 shadow-md'
                }`}
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => handleToggleStatus(task)}
                    className={`mt-0.5 w-5 h-5 rounded-md flex items-center justify-center border transition-colors ${
                      isDone
                        ? 'bg-emerald-600 border-emerald-500 text-white'
                        : 'border-slate-600 hover:border-blue-400'
                    }`}
                  >
                    {isDone && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </button>

                  <div className="space-y-1">
                    <p className={`text-sm font-semibold ${isDone ? 'line-through text-slate-400' : 'text-slate-100'}`}>
                      {task.title}
                    </p>
                    {task.description && (
                      <p className="text-xs text-slate-400">{task.description}</p>
                    )}
                    <div className="flex flex-wrap items-center gap-2 pt-1 text-[10px]">
                      <span
                        className={`px-1.5 py-0.5 rounded font-bold uppercase ${
                          task.priority === 'urgent'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : task.priority === 'high'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        }`}
                      >
                        {task.priority}
                      </span>
                      {task.created_by_agent && (
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                          via {task.created_by_agent}
                        </span>
                      )}
                      {task.due_date && (
                        <span className="flex items-center gap-1 text-slate-400">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(task.due_date).toLocaleDateString()}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(task.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* New Task Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <form
            onSubmit={handleCreateTask}
            className="w-full max-w-md bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-2xl p-6 space-y-4"
          >
            <h3 className="text-base font-bold text-white">Create New Task</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-400">Task Title</label>
                <input
                  type="text"
                  required
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="e.g. Review Q3 Investor Deck"
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Description</label>
                <textarea
                  rows={2}
                  value={newTaskDesc}
                  onChange={(e) => setNewTaskDesc(e.target.value)}
                  placeholder="Additional context or notes..."
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Priority Level</label>
                <select
                  value={newTaskPriority}
                  onChange={(e) => setNewTaskPriority(e.target.value as any)}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="low">Low Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="high">High Priority</option>
                  <option value="urgent">Urgent</option>
                </select>
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
                className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20"
              >
                Create Task
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
