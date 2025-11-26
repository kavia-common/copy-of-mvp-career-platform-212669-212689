from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user
from src.db.session import get_session
from src.repositories.audit_logs import list_audit_logs
from src.schemas.audit_log import AuditLogRead

router = APIRouter(prefix="/api/v1", tags=["Audit"])


# PUBLIC_INTERFACE
@router.get(
    "/audit-logs",
    response_model=List[AuditLogRead],
    summary="Retrieve audit logs (admin only)",
    description="List recent audit logs. Requires 'admin' role.",
)
async def get_audit_logs(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> List[AuditLogRead]:
    """
    Return recent audit logs if the user has an 'admin' role.
    """
    if "admin" not in (user.roles or []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    logs = await list_audit_logs(session, limit=200)
    return [AuditLogRead.model_validate(l, from_attributes=True) for l in logs]
