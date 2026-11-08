'use client';

import React, { useState, useEffect } from 'react';
import {
  Menu,
  Bell,
  Sparkles,
  Bot,
  ShieldCheck,
  Search,
  CheckCircle2,
  Calendar,
  CheckSquare,
  Mail,
  FileText
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import DashboardView from '@/components/views/DashboardView';
import AssistantView from '@/components/views/AssistantView';
import TasksView from '@/components/views/TasksView';
import CalendarView from '@/components/views/CalendarView';
import EmailsView from '@/components/views/EmailsView';
import DocumentsView from '@/components/views/DocumentsView';
import ResearchView from '@/components/views/ResearchView';
import MemoryView from '@/components/views/MemoryView';
import IntegrationsView from '@/components/views/IntegrationsView';
import AutomationsView from '@/components/views/AutomationsView';
import SettingsView from '@/components/views/SettingsView';
import OnboardingModal from '@/components/OnboardingModal';
import { apiRequest } from '@/lib/api';

export default function Home() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [isDark, setIsDark] = useState(true);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('gemini');

  useEffect(() => {
    // Ensure an authenticated executive session token exists in localStorage
    const token = localStorage.getItem('technopie_token');
    if (!token) {
      apiRequest<{ access_token?: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'demo@technopie.ai', password: 'DemoPassword123!' })
      })
        .then((data) => {
          if (data && data.access_token) {
            localStorage.setItem('technopie_token', data.access_token);
          }
        })
        .catch((e) => console.warn('Could not auto-login demo executive', e));
    }

    // Check onboarding status in local storage
    const completed = localStorage.getItem('technopie_onboarding_done');
    if (!completed) {
      setIsOnboardingOpen(true);
    }
  }, []);

  const handleCompleteOnboarding = () => {
    localStorage.setItem('technopie_onboarding_done', 'true');
    setIsOnboardingOpen(false);
  };

  return (
    <div className={`min-h-screen ${isDark ? 'dark bg-[#070B14]' : 'light bg-slate-50'}`}>
      {/* Guided Executive Onboarding Modal */}
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onComplete={handleCompleteOnboarding}
      />

      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        isDark={isDark}
        setIsDark={setIsDark}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main Content Area */}
      <div className="lg:pl-64 flex flex-col min-h-screen">
        {/* Top Executive Header */}
        <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-3.5 bg-[#070B14]/80 backdrop-blur-md border-b border-[#1E293B]">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsMobileOpen(true)}
              className="p-2 rounded-xl text-slate-400 hover:text-white bg-[#0F172A] border border-[#1E293B] lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="hidden sm:flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Workspace:</span>
              <span className="text-xs font-bold text-slate-200 capitalize">{currentTab.replace('_', ' ')}</span>
            </div>
          </div>

          {/* Quick Header Controls */}
          <div className="flex items-center gap-3">
            {/* AI Provider Indicator */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0F172A] border border-[#1E293B] text-xs">
              <Bot className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-slate-400">AI Engine:</span>
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="bg-transparent font-semibold text-white focus:outline-none cursor-pointer"
              >
                <option value="gemini" className="bg-[#0F172A]">Gemini 2.5</option>
                <option value="openai" className="bg-[#0F172A]">OpenAI GPT-4o</option>
                <option value="anthropic" className="bg-[#0F172A]">Claude 3.5</option>
                <option value="mock" className="bg-[#0F172A]">Smart Fallback</option>
              </select>
            </div>

            <button
              onClick={() => setCurrentTab('notifications')}
              className="relative p-2 rounded-xl bg-[#0F172A] border border-[#1E293B] text-slate-400 hover:text-white transition-colors"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-500" />
            </button>

            <div className="flex items-center gap-2 pl-2 border-l border-[#1E293B]">
              <div className="w-7 h-7 rounded-full bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center text-xs font-bold">
                AV
              </div>
              <span className="hidden sm:inline text-xs font-semibold text-slate-200">
                Alexander Vance
              </span>
            </div>
          </div>
        </header>

        {/* View Workspace Renderer */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {currentTab === 'dashboard' && (
            <DashboardView
              onNavigateTab={(tab) => setCurrentTab(tab)}
              selectedProvider={selectedProvider}
            />
          )}

          {currentTab === 'assistant' && (
            <AssistantView
              selectedProvider={selectedProvider}
              setSelectedProvider={setSelectedProvider}
            />
          )}

          {currentTab === 'tasks' && <TasksView />}

          {currentTab === 'calendar' && <CalendarView />}

          {currentTab === 'emails' && <EmailsView />}

          {currentTab === 'documents' && <DocumentsView />}

          {currentTab === 'research' && <ResearchView />}

          {currentTab === 'memory' && <MemoryView />}

          {currentTab === 'integrations' && <IntegrationsView />}

          {currentTab === 'automations' && <AutomationsView />}

          {currentTab === 'notifications' && (
            <div className="p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl space-y-4">
              <h3 className="text-base font-bold text-white">Executive Notifications</h3>
              <div className="space-y-3">
                <div className="p-4 rounded-xl bg-[#070B14] border border-[#1E293B] flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 mt-0.5">
                    <Calendar className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-white">Schedule Conflict Detected</h5>
                    <p className="text-xs text-slate-400 mt-0.5">
                      12:45 PM lunch meeting overlaps with your scheduled focus work block.
                    </p>
                    <span className="text-[10px] text-slate-500 mt-1 inline-block">10 minutes ago</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#070B14] border border-[#1E293B] flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 mt-0.5">
                    <Mail className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-white">VIP Draft Awaiting Authorization</h5>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Draft reply for Eleanor Vance (Apex Partners) is ready for your Level 3 review.
                    </p>
                    <span className="text-[10px] text-slate-500 mt-1 inline-block">45 minutes ago</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
}
