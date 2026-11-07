export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  preferred_name: string;
  profession: string;
  work_description?: string;
  preferred_language: string;
  timezone: string;
  productivity_goals: string[];
  ai_tone_preference: string;
  onboarding_completed: boolean;
}

export interface Message {
  id: string;
  sender_role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  model_provider?: string;
  model_name?: string;
  plan_steps?: string[];
  action_required?: ActionRequired | null;
  created_at: string;
}

export interface ActionRequired {
  action: string;
  target?: string;
  description: string;
  requires_approval: boolean;
  autonomy_level: 'level_1' | 'level_2' | 'level_3';
}

export interface Conversation {
  id: string;
  title: string;
  agent_type: string;
  is_pinned?: boolean;
  updated_at: string;
}

export interface TaskItem {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string | null;
  tags?: string[];
  created_by_agent?: string;
  created_at: string;
}

export interface CalendarEventItem {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  meeting_link?: string;
  status: string;
  agenda?: string;
}

export interface EmailItem {
  id: string;
  sender_name: string;
  sender_email: string;
  subject: string;
  snippet: string;
  category: 'action_required' | 'vip' | 'informational' | 'newsletter';
  received_at: string;
  is_read: boolean;
  draft_reply?: string | null;
  status: string;
}

export interface DocumentItem {
  id: string;
  title: string;
  doc_type: 'docx' | 'pdf' | 'xlsx' | 'pptx' | 'csv' | 'txt';
  file_size_bytes: number;
  status: string;
  download_url: string;
  created_at: string;
}

export interface MemoryItem {
  id: string;
  category: 'personal' | 'professional' | 'preference' | 'habit' | 'goal';
  content: string;
  importance_score: number;
  is_pinned: boolean;
  created_at: string;
}

export interface ResearchResult {
  query: string;
  timestamp: string;
  executive_summary: string;
  epistemic_breakdown: {
    verified_facts: string[];
    estimates: string[];
    opinions: string[];
    unverified_information: string[];
  };
  sources: { name: string; url: string }[];
}

export interface IntegrationItem {
  id: string;
  name: string;
  category: string;
  status: 'connected' | 'available' | 'disconnected';
  account_email?: string | null;
  connected_at?: string | null;
  scopes?: string[];
}

export interface BillingPlan {
  id: string;
  name: string;
  price_monthly_usd: number;
  price_monthly_inr: number;
  features: string[];
  is_current: boolean;
}

export interface AdminStats {
  platform: string;
  parent_company: string;
  active_users: number;
  total_conversations: number;
  tokens_processed: number;
  monthly_api_cost_usd: number;
  model_distribution: Record<string, string>;
  system_health: Record<string, any>;
}
