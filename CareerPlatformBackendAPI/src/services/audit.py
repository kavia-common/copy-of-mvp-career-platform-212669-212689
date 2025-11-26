from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.audit_logs import create_audit_log
from src.schemas.audit_log import AuditLogCreate


# PUBLIC_INTERFACE
async def log_action(
    session: AsyncSession,
    user_id: Optional[str],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Create an audit log entry (fire-and-forget semantics).
    """
    try:
        await create_audit_log(
            session,
            AuditLogCreate(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details or {},
            ),
        )
    except Exception:
        # Do not break main flow on audit failure in MVP
        pass
