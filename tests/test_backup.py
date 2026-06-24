from pathlib import Path

import pytest

from app.core.database import SessionLocal
from app.services.backup_service import create_backup, validate_database


def test_backup_and_validation():
    with SessionLocal() as db:
        record = create_backup(db, None)
        path = Path(record.backup_file_path)
        assert path.exists() and path.stat().st_size > 0
        validate_database(path)


def test_invalid_backup_rejected(tmp_path: Path):
    path = tmp_path / "bad.db"; path.write_text("not sqlite", encoding="utf-8")
    with pytest.raises(ValueError): validate_database(path)

