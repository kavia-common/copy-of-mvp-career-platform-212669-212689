from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog
from src.schemas.audit_log import AuditLogCreate


# PUBLIC_INTERFACE
async def create_audit_log(session: AsyncSession, payload: AuditLogCreate) -> AuditLog:
    """Create and persist an audit log entry."""
    entity = AuditLog(
        id=payload.id,
        timestamp=payload.timestamp or datetime.utcnow(),
        user_id=payload.user_id,
        action=payload.action,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        details=payload.details,
    )
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity


# PUBLIC_INTERFACE
async def list_audit_logs(session: AsyncSession, limit: int = 100) -> List[AuditLog]:
    """List recent audit log entries, newest first."""
    stmt = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def list_audit_logs_for_entity(
    session: AsyncSession, entity_type: str, entity_id: str, limit: int = 100
) -> List[AuditLog]:
    """List recent audit log entries for a specific entity."""
    stmt = (
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(desc(AuditLog.timestamp))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
