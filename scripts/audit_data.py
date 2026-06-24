"""逐人核对原始 Excel 与数据库，输出 JSON 审计结果。"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal
from app.core.validators import clean_text, parse_date, parse_decimal, parse_int, parse_year
from app.models.entities import BusinessEntity, Student
from app.services.excel_parser import (
    BASIC_FIELDS,
    EDUCATION_FIELDS,
    ENTITY_FIELDS,
    parse_workbook,
)


def comparable(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    text = clean_text(value)
    return text.replace(".0", "") if text and text.endswith(".0") else text


def mapped_headers() -> set[str]:
    direct = set(BASIC_FIELDS) | set(EDUCATION_FIELDS) | set(ENTITY_FIELDS) | {"培育年份", "培育诉求"}
    repeated = {
        "荣誉编号", "个人获得荣誉时间", "个人获得荣誉级别", "个人获得荣誉情况",
        "营收年份", "营业收入（万元）", "净利润（万元）", "固定资产净值（万元）",
        "总资产（万元）", "负债总额（万元）", "从业人数（人）", "流动资产（万元）",
        "管理费用（万元）", "政府补贴金额（万元）", "主营产业",
        "近三年经营总收入（万元）", "经营年限",
    }
    return direct | repeated


def header_is_mapped(header: str) -> bool:
    if header in mapped_headers():
        return True
    base = header.rstrip("0123456789")
    return base in mapped_headers()


def compare_fields(source: dict[str, Any], target: Any, mapping: dict[str, str], category: str) -> list[dict[str, Any]]:
    differences: list[dict[str, Any]] = []
    for header, field in mapping.items():
        raw = source.get(field)
        if raw in (None, ""):
            continue
        stored = getattr(target, field, None) if target is not None else None
        if field in {"birth_date", "established_date"}:
            raw_text = comparable(raw)
            if raw_text:
                raw_text = raw_text.replace("/", "-")
        else:
            raw_text = comparable(raw)
        if raw_text != comparable(stored):
            differences.append({"category": category, "field": field, "source": raw_text, "database": comparable(stored)})
    return differences


def normalized_record(record: dict[str, Any], field_types: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field, value in record.items():
        if field == "source_column_group":
            continue
        try:
            if field_types.get(field) == "date": value = parse_date(value)
            elif field_types.get(field) == "year": value = parse_year(value)
            elif field_types.get(field) == "money": value = parse_decimal(value)
            elif field_types.get(field) == "int": value = parse_int(value)
        except ValueError:
            pass
        normalized = comparable(value)
        if normalized is not None:
            result[field] = normalized
    return result


def compare_record_lists(category: str, source: list[dict[str, Any]], database: list[dict[str, Any]], field_types: dict[str, str]) -> list[dict[str, Any]]:
    source_values = [normalized_record(item, field_types) for item in source]
    database_values = [normalized_record(item, field_types) for item in database]
    if source_values == database_values:
        return []
    return [{"category": category, "field": "records", "source": source_values, "database": database_values}]


def audit(excel_path: Path) -> dict[str, Any]:
    sheet_name, rows, parser_unknown = parse_workbook(excel_path)
    all_headers = list(rows[0].raw) if rows else []
    source_nonempty = {header: sum(row.raw.get(header) not in (None, "") for row in rows) for header in all_headers}
    unmapped = [header for header in all_headers if not header_is_mapped(header)]

    with SessionLocal() as db:
        students = db.scalars(
            select(Student).options(
                selectinload(Student.education), selectinload(Student.honors),
                selectinload(Student.entities).selectinload(BusinessEntity.revenues),
                selectinload(Student.entities).selectinload(BusinessEntity.industries),
                selectinload(Student.cultivations),
            )
        ).all()
        by_card = {student.id_card_number: student for student in students}
        source_cards: set[str] = set()
        missing_students: list[dict[str, Any]] = []
        person_issues: list[dict[str, Any]] = []

        for row in rows:
            card = str(row.basic.get("id_card_number") or "").strip().upper()
            source_cards.add(card)
            student = by_card.get(card)
            if student is None:
                missing_students.append({"excel_row": row.row_number, "name": row.basic.get("name"), "id_card_number": card})
                continue
            differences = compare_fields(row.basic, student, {field: field for field in row.basic}, "基本信息")
            differences += compare_fields(row.education, student.education, {field: field for field in row.education}, "受教育情况")
            entity = next((item for item in student.entities if item.deleted_at is None), None)
            differences += compare_fields(row.entity, entity, {field: field for field in row.entity}, "新型经营主体")
            source_honors = [item for item in row.honors if clean_text(item.get("honor_description"))]
            database_honors = [{"honor_number": getattr(item, "honor_number", None), "honor_time": item.honor_time, "honor_level": item.honor_level, "honor_description": item.honor_description} for item in student.honors if item.deleted_at is None]
            differences += compare_record_lists("荣誉情况", source_honors, database_honors, {"honor_time": "date"})
            source_revenues = [item for item in row.revenues if item.get("year") not in (None, "")]
            database_revenues = [] if entity is None else [{"year": item.year, "operating_revenue": item.operating_revenue, "net_profit": item.net_profit, "fixed_asset_net_value": item.fixed_asset_net_value, "total_assets": item.total_assets, "total_liabilities": item.total_liabilities, "employee_count": item.employee_count, "current_assets": item.current_assets, "management_expense": item.management_expense, "government_subsidy_amount": item.government_subsidy_amount} for item in entity.revenues]
            revenue_types = {"year": "year", "employee_count": "int", "operating_revenue": "money", "net_profit": "money", "fixed_asset_net_value": "money", "total_assets": "money", "total_liabilities": "money", "current_assets": "money", "management_expense": "money", "government_subsidy_amount": "money"}
            differences += compare_record_lists("近三年营收", source_revenues, database_revenues, revenue_types)
            source_industries = [item for item in row.industries if clean_text(item.get("industry_name"))]
            database_industries = [] if entity is None else [{"industry_name": item.industry_name, "three_year_total_income": item.three_year_total_income, "operation_years": item.operation_years} for item in entity.industries]
            differences += compare_record_lists("主营产业", source_industries, database_industries, {"three_year_total_income": "money", "operation_years": "int"})
            source_cultivations = [row.cultivation] if row.cultivation.get("cultivation_year") or clean_text(row.cultivation.get("cultivation_needs")) else []
            database_cultivations = [{"cultivation_year": item.cultivation_year, "cultivation_needs": item.cultivation_needs, "training_experience": item.training_experience} for item in student.cultivations]
            differences += compare_record_lists("个人培育", source_cultivations, database_cultivations, {"cultivation_year": "year"})
            if differences:
                person_issues.append({"excel_row": row.row_number, "name": student.name, "id_card_number": card, "differences": differences})

        extra_students = [
            {"database_id": student.id, "name": student.name, "id_card_number": student.id_card_number}
            for student in students if student.id_card_number not in source_cards
        ]

    return {
        "source": {"sheet": sheet_name, "student_rows": len(rows), "columns": len(all_headers)},
        "database": {"students": len(students)},
        "matched_students": len(rows) - len(missing_students),
        "missing_students": missing_students,
        "extra_students": extra_students,
        "unmapped_columns": [{"name": name, "nonempty_rows": source_nonempty[name]} for name in unmapped],
        "parser_reported_unknown_columns": parser_unknown,
        "students_with_differences": len(person_issues),
        "person_issues": person_issues,
        "column_nonempty_counts": source_nonempty,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.file)
    text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
