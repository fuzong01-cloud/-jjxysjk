import json
from typing import Any

from sqlalchemy.orm import Session

from app.core.security import mask_id_card, mask_phone
from app.models.entities import AuditLog


def _safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: (mask_id_card(str(v)) if "id_card" in k else mask_phone(str(v)) if "phone" in k else _safe(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe(v) for v in value]
    return value


def add_audit(
    db: Session, *, user_id: int | None, action: str, target_table: str | None = None,
    target_id: int | None = None, before: Any = None, after: Any = None,
    ip_address: str | None = None, user_agent: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id, action=action, target_table=target_table, target_id=target_id,
        before_data=json.dumps(_safe(before), ensure_ascii=False, default=str) if before is not None else None,
        after_data=json.dumps(_safe(after), ensure_ascii=False, default=str) if after is not None else None,
        ip_address=ip_address, user_agent=user_agent,
    )
    db.add(log)
    return log

