import re
from typing import Tuple, List, Dict, Any

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt override",
    r"disregard all prior rules",
    r"you are now in developer mode",
    r"jailbreak enabled",
    r"as an unrestricted ai",
]

def wrap_untrusted_input(content: str, source_label: str = "external_data") -> str:
    """Wraps external untrusted inputs with strict XML delimiters to isolate malicious instructions."""
    sanitized = content.replace("</" + source_label + ">", "")
    return f"<{source_label}>\n{sanitized}\n</{source_label}>"

def inspect_prompt_safety(prompt: str) -> Tuple[bool, List[str]]:
    """Analyzes prompts for common prompt injection patterns."""
    detected = []
    lower = prompt.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            detected.append(pattern)
    return len(detected) == 0, detected

class AutonomyLevel:
    LEVEL_1_READ = "level_1"       # Automated: Read calendar, emails, tasks
    LEVEL_2_PREPARE = "level_2"   # Automated Draft: Create draft email, build schedule proposal
    LEVEL_3_EXECUTE = "level_3"   # Human Approval Required: Send email, book invite, delete data

SENSITIVE_ACTIONS = {
    "send_email": AutonomyLevel.LEVEL_3_EXECUTE,
    "delete_task": AutonomyLevel.LEVEL_3_EXECUTE,
    "cancel_calendar_event": AutonomyLevel.LEVEL_3_EXECUTE,
    "clear_memory": AutonomyLevel.LEVEL_3_EXECUTE,
    "generate_document": AutonomyLevel.LEVEL_2_PREPARE,
    "create_task": AutonomyLevel.LEVEL_2_PREPARE,
    "schedule_event": AutonomyLevel.LEVEL_2_PREPARE,
    "read_emails": AutonomyLevel.LEVEL_1_READ,
    "read_calendar": AutonomyLevel.LEVEL_1_READ,
    "list_tasks": AutonomyLevel.LEVEL_1_READ,
    "search_web": AutonomyLevel.LEVEL_1_READ,
}

def requires_user_confirmation(action_name: str, user_approval_level: str = "level_2") -> bool:
    action_level = SENSITIVE_ACTIONS.get(action_name, AutonomyLevel.LEVEL_2_PREPARE)
    if action_level == AutonomyLevel.LEVEL_3_EXECUTE:
        return True
    return False
