import hashlib
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import engine
from app.models.entities import BackupRecord


REQUIRED_TABLES = {"students", "users", "audit_logs", "import_batches"}


def database_path() -> Path:
    path = engine.url.database
    if not path:
        raise ValueError("当前数据库不支持文件备份")
    return Path(path).resolve()


def create_backup(db: Session, user_id: int | None, backup_type: str = "manual") -> BackupRecord:
    source = database_path()
    destination = get_settings().backup_dir / f"touyan_{datetime.now():%Y%m%d_%H%M%S_%f}.db"
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_conn = sqlite3.connect(source)
    target_conn = sqlite3.connect(destination)
    try:
        source_conn.backup(target_conn)
    finally:
        source_conn.close(); target_conn.close()
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    record = BackupRecord(backup_file_path=str(destination), backup_type=backup_type, file_size=destination.stat().st_size, file_hash=digest, created_by_user_id=user_id)
    db.add(record); db.commit(); db.refresh(record)
    return record


def validate_database(path: Path) -> None:
    try:
        conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        result = conn.execute("PRAGMA integrity_check").fetchone()
        conn.close()
    except sqlite3.DatabaseError as exc:
        raise ValueError("上传文件不是有效的 SQLite 数据库") from exc
    if not REQUIRED_TABLES.issubset(tables) or not result or result[0] != "ok":
        raise ValueError("数据库结构或完整性校验失败")


def restore_database(db: Session, uploaded: Path, user_id: int | None) -> None:
    validate_database(uploaded)
    create_backup(db, user_id, "before_restore")
    db.close()
    engine.dispose()
    shutil.copy2(uploaded, database_path())

