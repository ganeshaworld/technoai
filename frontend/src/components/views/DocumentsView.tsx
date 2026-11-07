'use client';

import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Plus,
  FileSpreadsheet,
  Presentation,
  CheckCircle2,
  Clock,
  Sparkles,
  Loader2
} from 'lucide-react';
import { DocumentItem } from '@/types';
import { apiRequest } from '@/lib/api';

export default function DocumentsView() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [docType, setDocType] = useState<'docx' | 'pdf' | 'xlsx' | 'pptx' | 'csv'>('docx');
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const data = await apiRequest<DocumentItem[]>('/documents');
      setDocuments(data);
    } catch (e) {
      console.warn('Could not load documents', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setGenerating(true);
    try {
      await apiRequest('/documents/generate', {
        method: 'POST',
        body: JSON.stringify({
          title,
          doc_type: docType,
          prompt
        })
      });
      setIsModalOpen(false);
      setTitle('');
      setPrompt('');
      fetchDocs();
    } catch (e) {
      console.warn('Generation failed', e);
    } finally {
      setGenerating(false);
    }
  };

  const getDocIcon = (type: string) => {
    switch (type) {
      case 'xlsx':
      case 'csv':
        return <FileSpreadsheet className="w-5 h-5 text-emerald-400" />;
      case 'pptx':
        return <Presentation className="w-5 h-5 text-amber-400" />;
      default:
        return <FileText className="w-5 h-5 text-blue-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-[#0F172A] border border-[#1E293B] shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400">
            <FileText className="w-4 h-4" />
            <span>Document Synthesis Studio</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight mt-1">
            Executive Document Generation
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Produce verified, professional deliverables across Word (.docx), PDF, Excel (.xlsx), and PowerPoint (.pptx).
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Generate Deliverable</span>
        </button>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400 gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
          <span>Loading generated documents...</span>
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center p-12 bg-[#0F172A] border border-[#1E293B] rounded-2xl text-slate-400">
          <FileText className="w-8 h-8 text-slate-500 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-white">No documents generated yet</h4>
          <p className="text-xs">Generate your first strategy proposal, financial model, or presentation deck.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-2xl bg-[#0F172A] border border-[#1E293B] hover:border-slate-700 shadow-md space-y-4 flex flex-col justify-between transition-all"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="p-2.5 rounded-xl bg-[#070B14] border border-[#1E293B]">
                    {getDocIcon(doc.doc_type)}
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-slate-800 text-slate-300">
                    .{doc.doc_type}
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-100 line-clamp-1">{doc.title}</h4>
                  <p className="text-[11px] text-slate-400 mt-1">
                    {(doc.file_size_bytes / 1024).toFixed(1)} KB • Verified Binary
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-[#1E293B] flex items-center justify-between">
                <span className="text-[10px] text-slate-500">
                  {new Date(doc.created_at).toLocaleDateString()}
                </span>
                <a
                  href={`http://localhost:8000${doc.download_url}`}
                  download
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/15 hover:bg-blue-600 text-blue-400 hover:text-white text-xs font-semibold border border-blue-500/30 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <form
            onSubmit={handleGenerate}
            className="w-full max-w-md bg-[#0F172A] border border-[#1E293B] rounded-2xl shadow-2xl p-6 space-y-4"
          >
            <h3 className="text-base font-bold text-white">Generate Executive Document</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-400">Document Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Q4 International Expansion Plan"
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Deliverable Format</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value as any)}
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="docx">Microsoft Word (.docx)</option>
                  <option value="pdf">Executive PDF (.pdf)</option>
                  <option value="xlsx">Excel Spreadsheet (.xlsx)</option>
                  <option value="pptx">PowerPoint Presentation (.pptx)</option>
                  <option value="csv">Standard CSV (.csv)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400">Content Prompt / Guidelines</label>
                <textarea
                  rows={3}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Outline key sections, financial parameters, or recommendations..."
                  className="w-full mt-1 px-3 py-2 bg-[#070B14] border border-[#1E293B] rounded-xl text-sm text-white focus:outline-none focus:border-blue-500 resize-none"
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
                disabled={generating}
                className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20"
              >
                {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                <span>{generating ? 'Generating File...' : 'Synthesize File'}</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
