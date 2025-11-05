from django.utils import timezone
from apps.accounts.models import AuditLog

def log_audit(user, action, details):
    """
    Log an audit event for security and compliance tracking.
    
    Args:
        user: The user performing the action (can be None for anonymous actions)
        action: The type of action being performed
        details: Additional details about the action (as a dict)
    """
    AuditLog.objects.create(user=user, action=action, details=details, timestamp=timezone.now())
