import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, ForeignKey, DateTime, JSON
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    connected_accounts = relationship("ConnectedAccount", back_populates="user", cascade="all, delete-orphan")
    automations = relationship("Automation", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    preferred_name = Column(String(100), nullable=True)
    profession = Column(String(255), nullable=True)
    work_description = Column(Text, nullable=True)
    preferred_language = Column(String(50), default="en", nullable=False)
    timezone = Column(String(100), default="UTC", nullable=False)
    avatar_url = Column(Text, nullable=True)
    productivity_goals = Column(JSON, default=list)
    ai_tone_preference = Column(String(50), default="executive") # executive, concise, detailed
    auto_approval_level = Column(String(20), default="level_2")
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="profile")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Executive Session", nullable=False)
    agent_type = Column(String(100), default="general_assistant", nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    context_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_role = Column(String(20), nullable=False) # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    model_provider = Column(String(50), default="gemini")
    model_name = Column(String(100), default="gemini-2.5-flash")
    tokens_used = Column(Integer, default=0)
    tool_calls = Column(JSON, default=list)
    tool_results = Column(JSON, default=list)
    action_items = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False) # personal, professional, preference, habit, goal
    content = Column(Text, nullable=False)
    importance_score = Column(Float, default=1.0)
    confidence_score = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True, nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="memories")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="todo", nullable=False) # 'todo', 'in_progress', 'completed', 'cancelled'
    priority = Column(String(50), default="medium", nullable=False) # 'low', 'medium', 'high', 'urgent'
    due_date = Column(DateTime(timezone=True), nullable=True)
    reminder_at = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSON, default=list)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(100), nullable=True)
    created_by_agent = Column(String(100), default="User")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="tasks")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    external_event_id = Column(String(255), nullable=True)
    provider = Column(String(50), default="technopie") # google, outlook, technopie
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(100), default="UTC", nullable=False)
    location = Column(Text, nullable=True)
    attendees = Column(JSON, default=list)
    meeting_link = Column(Text, nullable=True)
    status = Column(String(50), default="confirmed")
    ai_agenda_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="calendar_events")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    doc_type = Column(String(50), nullable=False) # docx, pdf, xlsx, pptx, csv, txt
    file_path = Column(Text, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    source_prompt = Column(Text, nullable=True)
    status = Column(String(50), default="ready")
    metadata_info = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="documents")

class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(100), nullable=False) # google, microsoft, slack
    account_email = Column(String(255), nullable=False)
    scopes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    encrypted_token_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="connected_accounts")

class Automation(Base):
    __tablename__ = "automations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(String(100), nullable=False) # cron, email_received, task_created
    trigger_config = Column(JSON, default=dict)
    action_type = Column(String(100), nullable=False) # daily_briefing, auto_summarize
    action_config = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="automations")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    type = Column(String(50), default="info") # info, warning, action_required, success
    is_read = Column(Boolean, default=False, nullable=False)
    action_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="notifications")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan_tier = Column(String(50), default="free", nullable=False) # free, personal, professional, executive, business
    gateway = Column(String(50), nullable=True) # razorpay, stripe
    gateway_subscription_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="subscription")
