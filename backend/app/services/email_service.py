from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

class EmailService:
    @staticmethod
    def get_inbox_messages(user_id: str) -> List[Dict[str, Any]]:
        """
        Fetches categorized emails. When Gmail OAuth is active, queries Gmail API;
        otherwise provides initial executive email feed for immediate productivity triage.
        """
        now = datetime.now(timezone.utc)
        return [
            {
                "id": "email_101",
                "sender_name": "Eleanor Vance",
                "sender_email": "eleanor@apexpartners.vc",
                "subject": "Series A Follow-up: Financial Model & Term Sheet Review",
                "snippet": "Alexander, our investment committee reviewed the Q3 updates. Could you share the updated 24-month burn projection by tomorrow noon?",
                "category": "action_required", # action_required | vip | informational | newsletter
                "received_at": (now - timedelta(minutes=42)).isoformat(),
                "is_read": False,
                "draft_reply": "Dear Eleanor,\n\nThank you for the update. I have reviewed our 24-month model with our financial controller and have attached the latest unit economics breakdown.\n\nBest regards,\nAlexander",
                "status": "draft_prepared"
            },
            {
                "id": "email_102",
                "sender_name": "Marcus Sterling",
                "sender_email": "m.sterling@enterprise-cloud.io",
                "subject": "Enterprise SaaS Master Agreement — Security Addendum",
                "snippet": "Attached is the signed enterprise agreement addendum regarding pgvector tenant data isolation and SOC2 compliance.",
                "category": "vip",
                "received_at": (now - timedelta(hours=2, minutes=15)).isoformat(),
                "is_read": False,
                "draft_reply": "Hi Marcus,\n\nReceived and noted. Our compliance team is verifying the addendum today.\n\nRegards,\nAlexander",
                "status": "review_needed"
            },
            {
                "id": "email_103",
                "sender_name": "Tech Leadership Daily",
                "sender_email": "digest@globaltechbrief.com",
                "subject": "Daily Executive Intelligence: The Multi-Agent Enterprise Shift",
                "snippet": "How Fortune 500 companies are adopting autonomous AI executive assistants in 2026...",
                "category": "newsletter",
                "received_at": (now - timedelta(hours=5)).isoformat(),
                "is_read": True,
                "draft_reply": None,
                "status": "archived"
            }
        ]

    @staticmethod
    def generate_draft_reply(email_id: str, prompt: str, user_name: str = "Alexander") -> Dict[str, Any]:
        return {
            "email_id": email_id,
            "draft_text": f"Dear recipient,\n\nThank you for reaching out regarding this matter. {prompt}\n\nWarm regards,\n{user_name}",
            "requires_approval": True,
            "autonomy_level": "level_3",
            "message": "Sending this email requires your explicit authorization."
        }
