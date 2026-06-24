from pathlib import Path

from openpyxl import Workbook

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.entities import Student
from app.services.import_service import commit_batch, create_preview


def test_preview_and_commit(tmp_path: Path):
    path = tmp_path / "students.xlsx"
    book = Workbook(); sheet = book.active; sheet.title = "Sheet1"
    sheet.append(["学员姓名", "身份证号", "所在区县", "个人获得荣誉情况1"])
    sheet.append(["张三", "11010519491231002X", "北京市延庆区", "优秀学员"])
    book.save(path)
    with SessionLocal() as db:
        batch = create_preview(db, path, path.name, None, get_settings().upload_dir)
        assert batch.total_rows == 1 and batch.failed_rows == 0 and batch.new_rows == 1
        commit_batch(db, batch, None)
        student = db.query(Student).one()
        assert student.name == "张三"
        assert len(student.honors) == 1

