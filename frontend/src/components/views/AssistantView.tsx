'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  Plus,
  Sparkles,
  Paperclip,
  CheckCircle2,
  Clock,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { Message, Conversation, ActionRequired } from '@/types';
import VoiceButton from '@/components/VoiceButton';
import ApprovalCard from '@/components/ApprovalCard';
import { apiRequest } from '@/lib/api';

interface AssistantViewProps {
  selectedProvider: string;
  setSelectedProvider: (provider: string) => void;
}

export default function AssistantView({ selectedProvider, setSelectedProvider }: AssistantViewProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiRequest<Conversation[]>('/chat/conversations')
      .then((convs) => {
        setConversations(convs);
        if (convs.length > 0) {
          setActiveConvId(convs[0].id);
        }
      })
      .catch((e) => console.warn('Could not load conversations', e));
  }, []);

  useEffect(() => {
    if (activeConvId) {
      apiRequest<Message[]>(`/chat/conversations/${activeConvId}/messages`)
        .then(setMessages)
        .catch((e) => console.warn('Could not load messages', e));
    }
  }, [activeConvId]);

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
          conversation_id: activeConvId,
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
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender_role: 'assistant',
          content: `Communication error: ${e.message || 'Please check service connectivity.'}`,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = async () => {
    try {
      const newConv = await apiRequest<Conversation>('/chat/conversations', {
        method: 'POST',
        body: JSON.stringify({ title: 'New Executive Briefing' })
      });
      setConversations((prev) => [newConv, ...prev]);
      setActiveConvId(newConv.id);
      setMessages([]);
    } catch (e) {
      console.warn('Failed to create new conversation', e);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[760px]">
      {/* Sessions Sidebar (3 cols) */}
      <div className="lg:col-span-3 flex flex-col bg-[#0F172A] border border-[#1E293B] rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-[#1E293B] bg-[#0B1120]/60 flex items-center justify-between">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">Sessions</h4>
          <button
            onClick={handleNewSession}
            className="p-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-sm"
            title="New Conversation"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((c) => {
            const isActive = c.id === activeConvId;
            return (
              <button
                key={c.id}
                onClick={() => setActiveConvId(c.id)}
                className={`w-full p-3 rounded-xl text-left text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#070B14]'
                }`}
              >
                <p className="font-semibold truncate">{c.title}</p>
                <p className="text-[10px] text-slate-500 mt-0.5">
                  {new Date(c.updated_at).toLocaleDateString()}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Chat Stream Area (9 cols) */}
      <div className="lg:col-span-9 flex flex-col bg-[#0F172A] border border-[#1E293B] rounded-2xl overflow-hidden shadow-xl">
        {/* Chat Header & Provider Switcher */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#1E293B] bg-[#0B1120]/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">Technopie AI Dedicated Assistant</h4>
              <p className="text-[10px] text-slate-400">Context: Personalized Executive Memory Active</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-400">Model Engine:</span>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="px-2.5 py-1 rounded-lg bg-[#070B14] border border-[#1E293B] text-xs font-semibold text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="gemini">Google Gemini 2.5</option>
              <option value="openai">OpenAI GPT-4o</option>
              <option value="anthropic">Anthropic Claude 3.5</option>
              <option value="mock">Local Executive Fallback</option>
            </select>
          </div>
        </div>

        {/* Message Feed */}
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

                <div className="max-w-[85%] space-y-2">
                  <div
                    className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-wrap ${
                      isUser
                        ? 'bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-600/15'
                        : 'bg-[#070B14] text-slate-200 border border-[#1E293B] rounded-tl-none'
                    }`}
                  >
                    {m.content}
                  </div>

                  {m.plan_steps && m.plan_steps.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-[#070B14] border border-[#1E293B] text-[11px] text-slate-400 space-y-1">
                      <p className="font-semibold text-slate-300 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                        <span>Execution Steps:</span>
                      </p>
                      {m.plan_steps.map((step, idx) => (
                        <div key={idx} className="flex items-center gap-1.5 pl-4">
                          <span className="text-[10px] text-slate-500">•</span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  )}

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
            <div className="flex items-center gap-2 p-3 rounded-2xl bg-[#070B14] border border-[#1E293B] text-xs text-slate-400 w-fit">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
              <span>Synthesizing response & verifying tools...</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
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
              placeholder="Ask, instruct, or delegate a complex executive task..."
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
    </div>
  );
}
