'use client';

import React, { useState, useEffect } from 'react';
import {
  Mail,
  Send,
  Star,
  Clock,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Loader2,
  FileText
} from 'lucide-react';
import { EmailItem } from '@/types';
import { apiRequest } from '@/lib/api';
import ApprovalCard from '@/components/ApprovalCard';

export default function EmailsView() {
  const [emails, setEmails] = useState<EmailItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<EmailItem | null>(null);
  const [draftPrompt, setDraftPrompt] = useState('');
  const [drafting, setDrafting] = useState(false);
  const [showApproval, setShowApproval] = useState(false);

  useEffect(() => {
    apiRequest<EmailItem[]>('/emails/inbox')
      .then((data) => {
        setEmails(data);
        if (data.length > 0) setSelectedEmail(data[0]);
      })
      .catch((e) => console.warn('Could not load inbox', e))
      .finally(() => setLoading(false));
  }, []);

  const handleGenerateDraft = async () => {
    if (!selectedEmail) return;
    setDrafting(true);
    try {
      const res = await apiRequest<{ draft_text: string }>('/emails/draft-reply', {
        method: 'POST',
        body: JSON.stringify({
          email_id: selectedEmail.id,
          prompt: draftPrompt || 'Acknowledge request and confirm deliverables by tomorrow noon.'
        })
      });
      setSelectedEmail({
        ...selectedEmail,
        draft_reply: res.draft_text,
        status: 'draft_prepared'
      });
    } catch (e) {
      console.warn('Draft generation error', e);
    } finally {
      setDrafting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-rose-400">
            <Mail className="w-4 h-4" />
            <span>Executive Email Intelligence</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Prioritized Inbox & Drafts
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated email triage, VIP thread analysis, and Level 3 human authorization for external replies.
          </p>
        </div>

        <div className="flex items-center gap-2 p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300">
          <ShieldCheck className="w-4 h-4 text-blue-400 shrink-0" />
          <span>OAuth Connected: Google Workspace</span>
        </div>
      </div>

      {/* Main Inbox & Detail Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[680px]">
        {/* Email List (5 cols) */}
        <div className="lg:col-span-5 flex flex-col bg-[#0F172A] border border-[#1E293B] rounded-2xl overflow-hidden shadow-xl">
          <div className="px-5 py-3.5 border-b border-[#1E293B] bg-[#0B1120]/60 flex items-center justify-between">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Categorized Inbox ({emails.length})
            </h4>
            <span className="text-[10px] text-slate-400">Synced Real-Time</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-[#1E293B]">
            {loading ? (
              <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                <span>Loading emails...</span>
              </div>
            ) : (
              emails.map((email) => {
                const isSelected = selectedEmail?.id === email.id;
                return (
                  <button
                    key={email.id}
                    onClick={() => {
                      setSelectedEmail(email);
                      setShowApproval(false);
                    }}
                    className={`w-full p-4 text-left transition-all ${
                      isSelected
                        ? 'bg-blue-600/15 border-l-4 border-l-blue-500'
                        : 'hover:bg-[#070B14]'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-xs font-bold text-slate-200 truncate">
                        {email.sender_name}
                      </p>
                      <span
                        className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase shrink-0 ${
                          email.category === 'action_required'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : email.category === 'vip'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {email.category.replace('_', ' ')}
                      </span>
                    </div>

                    <p className="text-xs font-semibold text-slate-100 truncate mt-1">
                      {email.subject}
                    </p>
                    <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">
                      {email.snippet}
                    </p>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Email Detail & AI Reply Studio (7 cols) */}
        <div className="lg:col-span-7 flex flex-col bg-[#0F172A] border border-[#1E293B] rounded-2xl overflow-hidden shadow-xl">
          {selectedEmail ? (
            <div className="flex flex-col h-full">
              {/* Email Content Header */}
              <div className="p-5 border-b border-[#1E293B] space-y-2 bg-[#0B1120]/40">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-white">{selectedEmail.subject}</h3>
                  <span className="text-[10px] text-slate-400">
                    {new Date(selectedEmail.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="font-semibold text-slate-200">{selectedEmail.sender_name}</span>
                  <span>&lt;{selectedEmail.sender_email}&gt;</span>
                </div>
              </div>

              {/* Email Body */}
              <div className="p-5 border-b border-[#1E293B] text-xs sm:text-sm text-slate-300 leading-relaxed bg-[#070B14]/40">
                {selectedEmail.snippet}
              </div>

              {/* AI Draft & Level 3 Authorization Section */}
              <div className="flex-1 p-5 overflow-y-auto space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-white">
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <span>Executive AI Draft Response</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
                    Matching Executive Tone
                  </span>
                </div>

                {selectedEmail.draft_reply ? (
                  <div className="p-4 rounded-xl bg-[#070B14] border border-[#1E293B] space-y-3">
                    <p className="text-xs sm:text-sm whitespace-pre-wrap text-slate-200 leading-relaxed">
                      {selectedEmail.draft_reply}
                    </p>

                    {showApproval ? (
                      <ApprovalCard
                        action={{
                          action: 'send_email',
                          target: selectedEmail.sender_email,
                          description: `Send reply to ${selectedEmail.sender_name} with attached financial updates`,
                          requires_approval: true,
                          autonomy_level: 'level_3'
                        }}
                        onResolved={() => setShowApproval(false)}
                      />
                    ) : (
                      <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#1E293B]">
                        <button
                          onClick={() => setShowApproval(true)}
                          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all"
                        >
                          <Send className="w-3.5 h-3.5" />
                          <span>Review & Authorize Send</span>
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-[#070B14] border border-[#1E293B] space-y-3 text-center text-slate-400 text-xs">
                    <p>No draft generated yet for this thread.</p>
                    <button
                      onClick={handleGenerateDraft}
                      disabled={drafting}
                      className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20"
                    >
                      {drafting ? 'Generating Draft...' : 'Generate Smart Draft'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-400 text-xs">
              Select an email thread from the inbox to inspect.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
