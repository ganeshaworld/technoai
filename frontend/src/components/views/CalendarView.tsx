'use client';

import React, { useState, useEffect } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Users,
  Video,
  Plus,
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { CalendarEventItem } from '@/types';
import { apiRequest } from '@/lib/api';

export default function CalendarView() {
  const [events, setEvents] = useState<CalendarEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [location, setLocation] = useState('');
  const [conflictWarning, setConflictWarning] = useState<string | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await apiRequest<CalendarEventItem[]>('/calendar/events?days=14');
      setEvents(data);
    } catch (e) {
      console.warn('Could not load calendar events', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !startTime || !endTime) return;

    try {
      const res = await apiRequest<{ has_conflicts: boolean; conflict_count: number }>('/calendar/events', {
        method: 'POST',
        body: JSON.stringify({
          title,
          start_time: new Date(startTime).toISOString(),
          end_time: new Date(endTime).toISOString(),
          location
        })
      });

      if (res.has_conflicts) {
        setConflictWarning(`Notice: ${res.conflict_count} calendar conflict(s) detected during this time slot.`);
      } else {
        setConflictWarning(null);
      }

      setIsModalOpen(false);
      setTitle('');
      fetchEvents();
    } catch (e) {
      console.warn('Failed to schedule event', e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
            <CalendarIcon className="w-4 h-4" />
            <span>Executive Schedule Optimizer</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Calendar & Engagements
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Two-way calendar intelligence with proactive conflict analysis and automated agenda briefs.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Schedule Meeting</span>
        </button>
      </div>

      {conflictWarning && (
        <div className="flex items-center gap-2.5 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{conflictWarning}</span>
        </div>
      )}

      {/* Events Feed */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
          <span>Loading commitments...</span>
        </div>
      ) : events.length === 0 ? (
        <div className="text-center p-12 bg-[#0F172A] border border-[#1E293B] rounded-2xl text-slate-400">
          <CalendarIcon className="w-8 h-8 text-slate-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-white">No upcoming meetings scheduled</h4>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {events.map((event) => (
            <div
              key={event.id}
              className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] hover:border-slate-700 shadow-md space-y-3 transition-all"
            >
              <div className="flex items-start justify-between gap-2">
                <h4 className="text-sm font-bold text-slate-100">{event.title}</h4>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-semibold border border-emerald-500/25">
                  {event.status}
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-blue-400" />
                  <span>
                    {new Date(event.start_time).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })} •{' '}
                    {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -{' '}
                    {new Date(event.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                {event.location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    <span>{event.location}</span>
                  </div>
                )}

                {event.meeting_link && (
                  <div className="flex items-center gap-2 text-blue-400">
                    <Video className="w-3.5 h-3.5" />
                    <a href={event.meeting_link} target="_blank" rel="noreferrer" className="underline hover:text-blue-300">
                      Join Virtual Conference
                    </a>
                  </div>
                )}
              </div>

              {event.agenda && (
                <div className="p-3 rounded-xl bg-[#070B14] border border-[#1E293B] text-[11px] text-slate-300 space-y-1">
                  <p className="font-semibold text-blue-400 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    <span>AI Agenda Summary</span>
                  </p>
                  <p className="whitespace-pre-wrap text-slate-400">{event.agenda}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Schedule Meeting Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <form
            onSubmit={handleCreateEvent}
            className="w-full max-w-md bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-2xl p-6 space-y-4"
          >
            <h3 className="text-base font-bold text-white">Schedule Executive Engagement</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-400">Meeting Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Series A Investment Discussion"
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400">Start Time</label>
                  <input
                    type="datetime-local"
                    required
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400">End Time</label>
                  <input
                    type="datetime-local"
                    required
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Location / Platform</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Boardroom A or Zoom Link"
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                />
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
                Save & Optimize
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
