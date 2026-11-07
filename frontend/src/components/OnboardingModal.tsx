'use client';

import React, { useState } from 'react';
import { Sparkles, ArrowRight, Check, X, ShieldAlert } from 'lucide-react';
import { apiRequest } from '@/lib/api';

interface OnboardingModalProps {
  isOpen: boolean;
  onComplete: () => void;
}

export default function OnboardingModal({ isOpen, onComplete }: OnboardingModalProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: 'Alexander Vance',
    profession: 'Founder & CEO',
    workDescription: 'Directing strategic enterprise initiatives and product roadmap.',
    language: 'en',
    timezone: 'UTC',
    productivityGoals: ['Inbox Zero', 'Automated Daily Briefing', 'Priority Time-Blocking'],
    connectedApps: ['Google Workspace', 'Slack'],
    tasksToManage: ['Schedule Optimization', 'VIP Email Drafting', 'Market Research']
  });

  if (!isOpen) return null;

  const handleFinish = async () => {
    try {
      await apiRequest('/auth/profile/onboarding', {
        method: 'PUT',
        body: JSON.stringify({
          profession: formData.profession,
          work_description: formData.workDescription,
          preferred_language: formData.language,
          timezone: formData.timezone,
          productivity_goals: formData.productivityGoals,
          ai_tone_preference: 'executive'
        })
      });
    } catch (e) {
      console.warn('Could not save onboarding remote', e);
    }
    onComplete();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div className="w-full max-w-xl bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-2xl p-6 sm:p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#1E293B] pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Technopie AI Executive Onboarding</h3>
              <p className="text-xs text-slate-400">Step {step} of 4 • Tailoring your executive assistant</p>
            </div>
          </div>
          <button
            onClick={onComplete}
            className="text-xs text-slate-400 hover:text-white underline"
          >
            Skip for now
          </button>
        </div>

        {/* Step Content */}
        {step === 1 && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-slate-200">1. Executive Profile & Role</h4>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-400">Your Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Current Role / Title</label>
                <input
                  type="text"
                  value={formData.profession}
                  onChange={(e) => setFormData({ ...formData, profession: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-slate-200">2. Working Scope & Focus Areas</h4>
            <div>
              <label className="text-xs font-medium text-slate-400">What does your primary work entail?</label>
              <textarea
                rows={3}
                value={formData.workDescription}
                onChange={(e) => setFormData({ ...formData, workDescription: e.target.value })}
                className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 resize-none"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-400">Preferred Language</label>
                <select
                  value={formData.language}
                  onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="en">English (US/UK/Global)</option>
                  <option value="hi">Hindi (हिन्दी)</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Time Zone</label>
                <select
                  value={formData.timezone}
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="UTC">UTC (Coordinated Universal Time)</option>
                  <option value="Asia/Kolkata">Asia/Kolkata (IST +5:30)</option>
                  <option value="America/New_York">America/New_York (EST)</option>
                  <option value="Europe/London">Europe/London (GMT)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-slate-200">3. Productivity Goals</h4>
            <p className="text-xs text-slate-400">Select what your assistant should help you achieve:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {[
                'Zero Inbox by end of day',
                'Morning executive briefing',
                'Calendar deconflicting',
                'Meeting agenda preparation',
                'Deep market research',
                'Executive proposal drafting'
              ].map((goal) => {
                const isSelected = formData.productivityGoals.includes(goal);
                return (
                  <button
                    key={goal}
                    type="button"
                    onClick={() => {
                      const updated = isSelected
                        ? formData.productivityGoals.filter((g) => g !== goal)
                        : [...formData.productivityGoals, goal];
                      setFormData({ ...formData, productivityGoals: updated });
                    }}
                    className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-medium text-left border transition-all ${
                      isSelected
                        ? 'bg-blue-600/20 text-blue-400 border-blue-500/40'
                        : 'bg-[#070B14] text-slate-400 border-[#1E293B] hover:text-white'
                    }`}
                  >
                    <div className={`w-4 h-4 rounded flex items-center justify-center border ${
                      isSelected ? 'bg-blue-600 border-blue-500 text-white' : 'border-slate-600'
                    }`}>
                      {isSelected && <Check className="w-3 h-3" />}
                    </div>
                    <span>{goal}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-slate-200">4. Ecosystem Integrations & Safeguards</h4>
            <p className="text-xs text-slate-400">Technopie AI enforces Level 3 consent before external actions:</p>
            <div className="p-3.5 rounded-xl bg-blue-950/20 border border-blue-500/20 text-xs text-blue-300 space-y-1">
              <p className="font-semibold text-blue-200">🔒 Autonomous Security Policy:</p>
              <p>Your assistant reads authorized schedules and drafts replies automatically, but will NEVER send emails or book meetings without your explicit permission.</p>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-[#1E293B]">
          {step > 1 ? (
            <button
              onClick={() => setStep(step - 1)}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
            >
              Back
            </button>
          ) : <div />}

          {step < 4 ? (
            <button
              onClick={() => setStep(step + 1)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
            >
              <span>Continue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              onClick={handleFinish}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/25 transition-all"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Complete Setup & Launch</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
