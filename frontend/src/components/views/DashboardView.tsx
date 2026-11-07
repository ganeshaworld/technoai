'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Send,
  Calendar,
  CheckCircle2,
  Clock,
  Mail,
  FileText,
  AlertCircle,
  ArrowUpRight,
  ChevronRight,
  Bot,
  User,
  ShieldCheck,
  CheckSquare,
  Search,
  Loader2
} from 'lucide-react';
import { Message, TaskItem, CalendarEventItem, ActionRequired } from '@/types';
import VoiceButton from '@/components/VoiceButton';
import ApprovalCard from '@/components/ApprovalCard';
import { apiRequest } from '@/lib/api';

interface DashboardViewProps {
  onNavigateTab: (tab: string) => void;
  selectedProvider: string;
}

export default function DashboardView({ onNavigateTab, selectedProvider }: DashboardViewProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'm-init',
      sender_role: 'assistant',
      content:
        "Good morning, Alexander. I am your **Technopie AI Executive Assistant**.\n\nI have cross-referenced your upcoming schedule, scanned your VIP inbox, and audited today's priority tasks. How would you like to direct your day?",
      created_at: new Date().toISOString()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [events, setEvents] = useState<CalendarEventItem[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load initial tasks & calendar events
    apiRequest<TaskItem[]>('/tasks?view=today').then(setTasks).catch(() => {});
    apiRequest<CalendarEventItem[]>('/calendar/events?days=2').then(setEvents).catch(() => {});
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: `u-${Date.now()}`,
      sender_role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const response = await apiRequest<{
        id: string;
        content: string;
        model_provider: string;
        model_name: string;
        plan_steps?: string[];
        action_required?: ActionRequired | null;
        created_at: string;
      }>('/chat/message', {
        method: 'POST',
        body: JSON.stringify({
          message: text,
          provider: selectedProvider
        })
      });

      const asstMsg: Message = {
        id: response.id || `a-${Date.now()}`,
        sender_role: 'assistant',
        content: response.content,
        model_provider: response.model_provider,
        model_name: response.model_name,
        plan_steps: response.plan_steps,
        action_required: response.action_required,
        created_at: response.created_at || new Date().toISOString()
      };

      setMessages((prev) => [...prev, asstMsg]);

      // Refresh tasks if task intent was processed
      if (text.toLowerCase().includes('task') || text.toLowerCase().includes('schedule')) {
        apiRequest<TaskItem[]>('/tasks?view=today').then(setTasks).catch(() => {});
      }
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender_role: 'assistant',
          content: `I encountered an issue connecting to the AI Brain: ${e.message || 'Please check service status'}.`,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const suggestedCommands = [
    'Prepare my schedule for tomorrow, check important emails and identify unfinished tasks.',
    'Create an urgent task to review Q3 Financial Model by 5 PM.',
    'Summarize my important emails and prepare draft replies.',
    'Research the latest enterprise AI adoption trends in 2026.',
    'Draft a 3-page executive strategy proposal in DOCX format.'
  ];

  return (
    <div className="space-y-6">
      {/* Executive Greeting & KPI Row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400">
            <Sparkles className="w-4 h-4" />
            <span>Executive Command Center</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Good day, Alexander
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Technopie AI is actively managing your executive workload across calendar, inbox, and priority tasks.
          </p>
        </div>

        {/* Quick KPI Badges */}
        <div className="grid grid-cols-3 gap-3">
          <div
            onClick={() => onNavigateTab('calendar')}
            className="cursor-pointer p-3 rounded-xl bg-[#070B14] border border-[#1E293B] hover:border-blue-500/40 transition-all"
          >
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-semibold">
              <Calendar className="w-3.5 h-3.5 text-blue-400" />
              <span>Meetings</span>
            </div>
            <p className="text-lg font-bold text-white mt-1">{events.length}</p>
          </div>

          <div
            onClick={() => onNavigateTab('tasks')}
            className="cursor-pointer p-3 rounded-xl bg-[#070B14] border border-[#1E293B] hover:border-amber-500/40 transition-all"
          >
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-semibold">
              <CheckSquare className="w-3.5 h-3.5 text-amber-400" />
              <span>Priorities</span>
            </div>
            <p className="text-lg font-bold text-white mt-1">{tasks.length}</p>
          </div>

          <div
            onClick={() => onNavigateTab('emails')}
            className="cursor-pointer p-3 rounded-xl bg-[#070B14] border border-[#1E293B] hover:border-rose-500/40 transition-all"
          >
            <div className="flex items-center gap-1.5 text-slate-400 text-[10px] font-semibold">
              <Mail className="w-3.5 h-3.5 text-rose-400" />
              <span>VIP Emails</span>
            </div>
            <p className="text-lg font-bold text-white mt-1">2</p>
          </div>
        </div>
      </div>

      {/* Main Grid: AI Assistant Workspace (Left/Center) + Executive Context (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Central AI Executive Conversation Interface (2 cols) */}
        <div className="lg:col-span-2 flex flex-col h-[650px] bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-xl overflow-hidden">
          {/* Chat Header */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1E293B] bg-[#0B1120]/60">
            <div className="flex items-center gap-2.5">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
                <Bot className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">Technopie AI Executive Assistant</h4>
                <p className="text-[10px] text-slate-400">Provider: {selectedProvider.toUpperCase()} • 6-Stage Autonomous Engine</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Active & Ready
              </span>
            </div>
          </div>

          {/* Chat Messages Feed */}
          <div className="flex-1 p-5 space-y-4 overflow-y-auto">
            {messages.map((m) => {
              const isUser = m.sender_role === 'user';
              return (
                <div
                  key={m.id}
                  className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 shrink-0 mt-0.5">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-[85%] space-y-2`}>
                    <div
                      className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-wrap ${
                        isUser
                          ? 'bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-600/15'
                          : 'bg-[#070B14] text-slate-200 border border-[#1E293B] rounded-tl-none'
                      }`}
                    >
                      {m.content}
                    </div>

                    {/* Plan Steps Accordion */}
                    {m.plan_steps && m.plan_steps.length > 0 && (
                      <div className="p-2.5 rounded-xl bg-[#070B14] border border-[#1E293B] text-[11px] text-slate-400 space-y-1">
                        <p className="font-semibold text-slate-300 flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                          <span>Autonomous Execution Plan:</span>
                        </p>
                        {m.plan_steps.map((step, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 pl-4 text-slate-400">
                            <span className="text-[10px] text-slate-500">•</span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Level 3 Approval Card if required */}
                    {m.action_required && (
                      <ApprovalCard
                        action={m.action_required}
                        onResolved={() => {
                          setMessages((prev) =>
                            prev.map((item) =>
                              item.id === m.id ? { ...item, action_required: null } : item
                            )
                          );
                        }}
                      />
                    )}
                  </div>

                  {isUser && (
                    <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 shrink-0 mt-0.5 text-xs font-bold">
                      AV
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 shrink-0">
                  <Bot className="w-4 h-4 animate-spin" />
                </div>
                <div className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-[#070B14] border border-[#1E293B] text-xs text-slate-400">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
                  <span>Understanding intent & evaluating executive context...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Suggested Quick Prompts */}
          <div className="px-4 py-2 border-t border-[#1E293B] bg-[#070B14]/40 flex gap-2 overflow-x-auto">
            {suggestedCommands.slice(0, 3).map((cmd, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(cmd)}
                className="shrink-0 px-2.5 py-1 rounded-lg bg-[#0F172A] hover:bg-slate-800 border border-[#1E293B] text-[11px] text-slate-400 hover:text-slate-200 transition-colors"
              >
                {cmd.length > 40 ? cmd.slice(0, 40) + '...' : cmd}
              </button>
            ))}
          </div>

          {/* Chat Input Bar */}
          <div className="p-3.5 border-t border-[#1E293B] bg-[#0B1120]/90">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <VoiceButton
                onTranscription={(text) => {
                  setInputText(text);
                  handleSendMessage(text);
                }}
              />

              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Direct your assistant (e.g. 'Organize my day tomorrow', 'Check emails')..."
                className="flex-1 px-4 py-2.5 bg-[#070B14] border border-[#1E293B] rounded-xl text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />

              <button
                type="submit"
                disabled={!inputText.trim() || loading}
                className="flex items-center justify-center p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white shadow-lg shadow-blue-600/20 transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Executive Sidebar Context: Today's Priorities & Upcoming Meetings */}
        <div className="space-y-6">
          {/* Today's Priorities */}
          <div className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-white">
                <CheckSquare className="w-4 h-4 text-blue-400" />
                <span>Today's Priorities</span>
              </div>
              <button
                onClick={() => onNavigateTab('tasks')}
                className="text-[11px] text-blue-400 hover:text-blue-300 font-medium flex items-center gap-0.5"
              >
                <span>View all</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-2">
              {tasks.slice(0, 3).map((task) => (
                <div
                  key={task.id}
                  className="p-3 rounded-xl bg-[#070B14] border border-[#1E293B] space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs font-semibold text-slate-200 line-clamp-2">
                      {task.title}
                    </p>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                        task.priority === 'urgent'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : task.priority === 'high'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                  {task.due_date && (
                    <div className="flex items-center gap-1 text-[10px] text-slate-400">
                      <Clock className="w-3 h-3" />
                      <span>Due {new Date(task.due_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Meetings */}
          <div className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-white">
                <Calendar className="w-4 h-4 text-emerald-400" />
                <span>Upcoming Commitments</span>
              </div>
              <button
                onClick={() => onNavigateTab('calendar')}
                className="text-[11px] text-blue-400 hover:text-blue-300 font-medium flex items-center gap-0.5"
              >
                <span>Full agenda</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            <div className="space-y-2">
              {events.slice(0, 2).map((event) => (
                <div
                  key={event.id}
                  className="p-3 rounded-xl bg-[#070B14] border border-[#1E293B] space-y-1.5"
                >
                  <p className="text-xs font-semibold text-slate-200">{event.title}</p>
                  <div className="flex items-center gap-1 text-[10px] text-slate-400">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>
                      {new Date(event.start_time).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })} •{' '}
                      {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  {event.location && (
                    <p className="text-[10px] text-slate-500 truncate">{event.location}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
