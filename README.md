# TECHNOPIE AI
### World-Class AI Personal & Executive Assistant SaaS

> **"Your AI. Your Assistant. Your Productivity."**  
> Developed by **Technopie Consultant Pvt. Ltd.**

---

## 🌟 Executive Overview

**Technopie AI** is an enterprise-grade AI Personal and Executive Assistant SaaS platform built to empower founders, CEOs, executives, consultants, and professionals with a 24/7 digital Chief of Staff.

Unlike simple question-and-answer chatbots, Technopie AI follows the rigorous **Six-Stage Autonomous Cognitive Loop**:
```
[ UNDERSTAND ] ──▶ [ REMEMBER ] ──▶ [ PLAN ] ──▶ [ EXECUTE ] ──▶ [ VERIFY ] ──▶ [ REPORT ]
```

---

## 🚀 Key Modules & Capabilities

1. **Central AI Brain & Multi-Provider Abstraction:**
   - Dynamic routing across **Google Gemini** (Gemini 2.5 Flash / Pro), **OpenAI** (GPT-4o / mini), and **Anthropic** (Claude 3.5 Sonnet).
   - High-precision task routing and offline/local fallback engine.
2. **Personal Semantic Memory System:**
   - Isolated vector memory partitions (PostgreSQL + pgvector).
   - Full user governance: View indexed memories, edit facts, delete individual records, or clear all.
3. **Executive Task & Priority Engine:**
   - Natural language task extraction ("Remind me to review the Series A deck tomorrow high priority").
   - Status tracking (`todo`, `in_progress`, `completed`), priorities (`low`, `medium`, `high`, `urgent`), tags, and due dates.
4. **Calendar & Meeting Intelligence:**
   - Two-way Google Calendar synchronization, conflict detection, and automated meeting agenda briefings.
5. **Categorized Email Management (Gmail OAuth):**
   - VIP thread triage, draft reply synthesis in user's executive tone.
   - **Level 3 Autonomy Boundary:** Sending external emails mandates explicit interactive user authorization.
6. **Multi-Format Document Generation:**
   - Generates real binary files: Microsoft Word (`.docx`), Executive PDF (`.pdf`), Excel (`.xlsx`), PowerPoint (`.pptx`), and CSV (`.csv`).
   - Validated binaries served via authenticated download endpoints.
7. **Deep Epistemic Research Assistant:**
   - Multi-source web research distinguishing **Verified Facts**, **Estimates**, **Expert Opinions**, and **Unverified Information** with citations.
8. **Voice Executive Assistant (Phase 1 & Phase 2):**
   - Speech-to-Text (STT) and Text-to-Speech (TTS) with English and Hindi language support.
9. **Subscriptions & Billing:**
   - Tiered plans: *Free*, *Personal*, *Professional*, *Executive*, *Business*.
   - Razorpay and Stripe gateway integration.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 14+ (App Router), React, TypeScript, Tailwind CSS, shadcn/ui styling, Lucide Icons |
| **Backend** | Python 3.14+, FastAPI async architecture, Pydantic v2, Uvicorn, SQLAlchemy |
| **Database** | PostgreSQL, Supabase, `pgvector` (local async SQLite fallback for zero-setup dev) |
| **Document Engines** | `python-docx`, `reportlab`, `openpyxl`, `python-pptx` |
| **AI Providers** | Google Gemini API, OpenAI API, Anthropic Claude API, Local Executive Fallback Engine |
| **Security** | JWT HS256, salted PBKDF2 password derivation, AES-256 token encryption, prompt injection delimiters |

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ (Tested on Node.js v24)
- Git

### 2. Backend Setup
```bash
# 1. Activate Python virtual environment
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # macOS/Linux

# 2. Run backend test suite
python -m pytest backend/tests/test_backend.py -v

# 3. Launch FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Start Next.js development server
npm run dev
```
Open `http://localhost:3000` to interact with Technopie AI.

---

## 📂 Project Structure

```
technoai/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point & lifespan handler
│   │   ├── config.py             # App settings & environment loader
│   │   ├── db/
│   │   │   ├── session.py        # Async SQLAlchemy session manager
│   │   │   └── models.py         # 12 Normalized relational domain models
│   │   ├── core/
│   │   │   ├── security.py       # JWT, password hashing & auth dependencies
│   │   │   └── guardrails.py     # Prompt injection defenses & autonomy levels
│   │   ├── services/
│   │   │   ├── ai_providers.py   # Multi-provider abstraction (Gemini, OpenAI, Claude, Mock)
│   │   │   ├── memory_service.py # Categorized & semantic personal memory
│   │   │   ├── task_service.py   # Executive task board engine
│   │   │   ├── document_service.py # DOCX, PDF, XLSX, PPTX binary builders
│   │   │   ├── calendar_service.py # Schedule & conflict analysis
│   │   │   ├── email_service.py  # Gmail triage & draft replies
│   │   │   ├── research_service.py # Epistemic research syntheses
│   │   │   └── voice_service.py  # Audio STT/TTS pipeline
│   │   ├── agents/
│   │   │   └── orchestrator.py   # Central Executive AI Brain (6-Stage Loop)
│   │   └── api/                  # REST route controllers
│   ├── tests/                    # Pytest unit & integration suite
│   ├── uploads/                  # Temporary file storage
│   └── generated_docs/           # Validated binary output files
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   │   ├── components/           # Sidebar, VoiceButton, OnboardingModal, ApprovalCard
│   │   │   └── views/            # Dashboard, Assistant, Tasks, Calendar, Emails, Docs, etc.
│   │   ├── lib/                  # API client fetch wrapper
│   │   └── types/                # TypeScript interface definitions
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── PRD.md                        # Product Requirements Document
├── ARCHITECTURE.md               # System Architecture Specification
├── DATABASE_SCHEMA.md            # PostgreSQL & pgvector Schema DDL
├── DEVELOPMENT_ROADMAP.md        # Release Roadmap & DoD
├── SECURITY.md                   # Security Policy & Guardrails
├── API_DOCUMENTATION.md          # REST & SSE API Reference
└── .env.example                  # Environment configuration template
```

---

## 🔒 Security & Privacy Commitments
- Strict cryptographic tenant isolation.
- Level 3 actions (sending emails, committing funds, deleting records) always demand explicit user consent.
- Prompt injection defenses wrap untrusted inputs with `<untrusted_content>` delimiters.
- No plaintext storage of third-party tokens.
