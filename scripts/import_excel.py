import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.models.entities import ImportBatch
from app.services.import_service import commit_batch, create_preview


def main() -> None:
    parser = argparse.ArgumentParser(description="预览或导入头雁学员 Excel")
    parser.add_argument("--file", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        batch: ImportBatch = create_preview(db, args.file, args.file.name, None, get_settings().upload_dir)
        print(f"批次 #{batch.id}: 总计 {batch.total_rows}, 新增 {batch.new_rows}, 更新 {batch.updated_rows}, 错误 {batch.failed_rows}")
        if args.commit:
            commit_batch(db, batch, None); print("已写入数据库")


if __name__ == "__main__": main()
