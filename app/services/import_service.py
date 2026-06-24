import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.validators import birth_date_from_id_card, clean_text, gender_from_id_card, normalize_id_card, normalize_phone, parse_date, parse_decimal, parse_int, parse_year
from app.models.entities import AnnualRevenueRecord, BusinessEntity, CultivationRecord, EducationRecord, HonorRecord, ImportBatch, ImportError, MainIndustry, Student
from app.services.audit_service import add_audit
from app.services.excel_parser import ParsedRow, parse_workbook


def _error(batch: ImportBatch, row: int, field: str, raw: Any, message: str, severity: str = "error") -> None:
    batch.errors.append(ImportError(excel_row_number=row, field_name=field, raw_value=clean_text(raw), error_type="validation", error_message=message, severity=severity))


def create_preview(db: Session, source: Path, original_name: str, user_id: int | None, upload_dir: Path) -> ImportBatch:
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    stored = upload_dir / f"{datetime.now():%Y%m%d_%H%M%S}_{digest[:10]}.xlsx"
    upload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, stored)
    sheet_name, rows, unknown = parse_workbook(stored)
    batch = ImportBatch(
        file_name=original_name, stored_file_path=str(stored), file_hash=digest,
        sheet_name=sheet_name, total_rows=len(rows), created_by_user_id=user_id,
        success_rows=0, failed_rows=0, warning_count=0, new_rows=0, updated_rows=0,
    )
    db.add(batch)
    existing = set(db.scalars(select(Student.id_card_number)).all())
    for item in rows:
        try:
            card = normalize_id_card(item.basic.get("id_card_number"))
            if not clean_text(item.basic.get("name")):
                raise ValueError("学员姓名不能为空")
            batch.updated_rows += card in existing
            batch.new_rows += card not in existing
        except ValueError as exc:
            batch.failed_rows += 1
            _error(batch, item.row_number, "id_card_number", item.basic.get("id_card_number"), str(exc))
    for header in unknown:
        batch.warning_count += 1
        _error(batch, 1, "unknown_column", header, f"未映射列：{header}", "warning")
    batch.success_rows = batch.total_rows - batch.failed_rows
    db.commit()
    db.refresh(batch)
    return batch


def _convert_row(item: ParsedRow) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    data = {key: clean_text(value) for key, value in item.basic.items()}
    errors: list[tuple[str, str]] = []
    try:
        data["id_card_number"] = normalize_id_card(data.get("id_card_number"))
        data["birth_date"] = parse_date(data.get("birth_date")) or birth_date_from_id_card(data["id_card_number"])
        data["gender"] = data.get("gender") or gender_from_id_card(data["id_card_number"])
    except ValueError as exc:
        errors.append(("id_card_number", str(exc)))
    try:
        data["phone"] = normalize_phone(data.get("phone"))
    except ValueError as exc:
        errors.append(("phone", str(exc)))
        data["phone"] = clean_text(item.basic.get("phone"))
    try:
        data["age_snapshot"] = parse_int(data.get("age_snapshot"))
    except ValueError:
        data["age_snapshot"] = None
    data["source_excel_row"] = item.row_number
    return data, errors


def commit_batch(db: Session, batch: ImportBatch, user_id: int | None) -> ImportBatch:
    if batch.status != "preview":
        raise ValueError("该批次已经处理")
    _, rows, _ = parse_workbook(Path(batch.stored_file_path))
    for item in rows:
        data, errors = _convert_row(item)
        if any(field == "id_card_number" for field, _ in errors):
            continue
        student = db.scalar(select(Student).where(Student.id_card_number == data["id_card_number"]))
        if student is None:
            student = Student(**data)
            db.add(student)
            db.flush()
        else:
            for key, value in data.items():
                if value is not None:
                    setattr(student, key, value)
            for collection in (student.honors, student.entities, student.cultivations):
                collection.clear()
        education_data = {k: clean_text(v) for k, v in item.education.items()}
        if student.education:
            for key, value in education_data.items(): setattr(student.education, key, value)
        elif any(education_data.values()):
            student.education = EducationRecord(**education_data)
        for honor in item.honors:
            description = clean_text(honor.get("honor_description"))
            if description:
                try: honor_time = parse_date(honor.get("honor_time"))
                except ValueError: honor_time = None
                student.honors.append(HonorRecord(honor_time=honor_time, honor_level=clean_text(honor.get("honor_level")), honor_description=description, source_column_group=honor["source_column_group"]))
        entity_data = {k: clean_text(v) for k, v in item.entity.items()}
        for key in ("established_date",):
            try: entity_data[key] = parse_date(entity_data.get(key))
            except ValueError: entity_data[key] = None
        for key in ("industry_years", "farmer_households_driven", "technical_partner_count"):
            try: entity_data[key] = parse_int(entity_data.get(key))
            except ValueError: entity_data[key] = None
        if any(entity_data.values()) or item.revenues or item.industries:
            entity = BusinessEntity(**entity_data)
            student.entities.append(entity)
            for rev in item.revenues:
                try:
                    year = parse_year(rev.get("year"))
                    if year:
                        values = {k: parse_int(v) if k == "employee_count" else parse_decimal(v) for k, v in rev.items() if k not in {"year", "source_column_group"}}
                        entity.revenues.append(AnnualRevenueRecord(year=year, source_column_group=rev["source_column_group"], **values))
                except ValueError: pass
            for industry in item.industries:
                name = clean_text(industry.get("industry_name"))
                if name:
                    try: income = parse_decimal(industry.get("three_year_total_income"))
                    except ValueError: income = None
                    try: years = parse_int(industry.get("operation_years"))
                    except ValueError: years = None
                    entity.industries.append(MainIndustry(industry_name=name, three_year_total_income=income, operation_years=years, source_column_group=industry["source_column_group"]))
        try: cultivation_year = parse_year(item.cultivation.get("cultivation_year"))
        except ValueError: cultivation_year = None
        if cultivation_year or clean_text(item.cultivation.get("cultivation_needs")):
            student.cultivations.append(CultivationRecord(cultivation_year=cultivation_year, cultivation_needs=clean_text(item.cultivation.get("cultivation_needs")), training_experience=clean_text(item.cultivation.get("training_experience"))))
    batch.status = "completed"
    batch.finished_at = datetime.utcnow()
    add_audit(db, user_id=user_id, action="IMPORT_COMMIT", target_table="import_batches", target_id=batch.id, after={"file": batch.file_name, "rows": batch.success_rows})
    db.commit()
    db.refresh(batch)
    return batch
