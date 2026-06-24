from datetime import date
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.entities import (
    AnnualRevenueRecord,
    BusinessEntity,
    CultivationRecord,
    EducationRecord,
    MainIndustry,
    Student,
)
from app.services.import_service import commit_batch, create_preview


MODULE_TITLES = (
    "基本信息表", "受教育情况表", "个人荣誉情况表", "新型经营主体情况表",
    "近三年营收情况表", "主营产业情况表", "个人培育信息表",
)


def create_complete_student() -> tuple[int, int, str]:
    with SessionLocal() as db:
        student = Student(
            name="严格需求测试", id_card_number="11010519491231002X", birth_date=date(1990, 6, 15),
            district_county="北京市测试区", political_status="群众", phone="13800138000",
        )
        student.education = EducationRecord(education_level="本科", graduate_school="测试大学")
        entity = BusinessEntity(
            entity_name="测试主体", entity_intro="原简介", entity_type="合作社", entity_subtype="示范合作社",
            established_date=date(2020, 1, 2), registered_address="原地址",
            unified_social_credit_code="91110000TEST000001", student_position_in_entity="负责人",
        )
        entity.revenues.append(AnnualRevenueRecord(year=2024, operating_revenue=100))
        entity.industries.append(MainIndustry(industry_name="种植业", three_year_total_income=300, operation_years=5))
        student.entities.append(entity)
        student.cultivations.append(CultivationRecord(cultivation_year=2024, cultivation_needs="品牌建设"))
        db.add(student); db.commit()
        return student.id, entity.id, student.id_card_number


def test_requirements_file_installs_one_requirement_per_line():
    lines = [line.strip() for line in Path("requirements.txt").read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    assert len(lines) == 11
    assert all(" " not in line for line in lines)
    assert lines == [
        "fastapi>=0.115,<1", "uvicorn[standard]>=0.30,<1", "sqlalchemy>=2.0,<3",
        "alembic>=1.13,<2", "pydantic-settings>=2.4,<3", "jinja2>=3.1,<4",
        "itsdangerous>=2.2,<3", "python-multipart>=0.0.9,<1", "openpyxl>=3.1,<4",
        "httpx>=0.27,<1", "pytest>=8,<9",
    ]


def test_full_archive_api_and_page_have_seven_modules(authenticated_client):
    student_id, _, card = create_complete_student()
    response = authenticated_client.get(f"/api/v1/students/{student_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert set(data) == {"basic_info", "education", "honors", "business_entities", "annual_revenues", "main_industries", "cultivations"}
    by_card = authenticated_client.get(f"/api/v1/students/by-id-card/{card.lower()}")
    assert by_card.status_code == 200 and by_card.json()["data"] == data
    page = authenticated_client.get(f"/students/{student_id}")
    assert all(title in page.text for title in MODULE_TITLES)


def test_name_search_add_honor_and_reopen(authenticated_client):
    student_id, _, _ = create_complete_student()
    search = authenticated_client.get("/students", params={"name": "严格需求"})
    assert search.status_code == 200 and f'/students/{student_id}' in search.text
    added = authenticated_client.post(
        f"/api/v1/students/{student_id}/honors",
        json={"honor_time": "2025-05-01", "honor_level": "市级", "honor_description": "严格需求荣誉"},
    )
    assert added.status_code == 200
    reopened = authenticated_client.get(f"/students/{student_id}")
    assert "2025-05-01" in reopened.text and "市级" in reopened.text and "严格需求荣誉" in reopened.text


def test_update_required_basic_fields_and_dynamic_age(authenticated_client):
    student_id, _, _ = create_complete_student()
    payload = {
        "birth_date": "2000-01-01", "political_status": "中共党员", "phone": "13900139000",
        "professional_title": "农艺师", "household_type": "农业户口", "talent_category": "能人回乡",
        "administrative_position": "主任", "social_part_time_positions": "协会理事",
    }
    assert authenticated_client.patch(f"/api/v1/students/{student_id}/basic-info", json=payload).status_code == 200
    data = authenticated_client.get(f"/api/v1/students/{student_id}").json()["data"]["basic_info"]
    for field, value in payload.items(): assert data[field] == value
    today = date.today(); expected_age = today.year - 2000 - ((today.month, today.day) < (1, 1))
    assert data["age"] == expected_age
    assert "age_snapshot" not in data
    page = authenticated_client.get(f"/students/{student_id}")
    assert all(value in page.text for value in payload.values())


def test_update_required_entity_fields_and_reopen(authenticated_client):
    student_id, entity_id, _ = create_complete_student()
    payload = {
        "entity_name": "修改后主体", "entity_intro": "修改后简介", "entity_type": "涉农企业",
        "entity_subtype": "一般企业", "established_date": "2021-02-03", "registered_address": "修改后地址",
        "unified_social_credit_code": "91110000TEST999999", "student_position_in_entity": "总经理",
    }
    assert authenticated_client.patch(f"/api/v1/business-entities/{entity_id}", json=payload).status_code == 200
    detail = authenticated_client.get(f"/api/v1/business-entities/{entity_id}").json()["data"]
    for field, value in payload.items(): assert detail[field] == value
    page = authenticated_client.get(f"/students/{student_id}")
    assert all(value in page.text for value in payload.values())


def test_id_card_and_district_search_open_full_archive(authenticated_client):
    student_id, _, card = create_complete_student()
    by_id = authenticated_client.get("/students", params={"id_card": card.lower()})
    by_district = authenticated_client.get("/students", params={"district": "北京市测试区"})
    assert f'/students/{student_id}' in by_id.text
    assert f'/students/{student_id}' in by_district.text
    archive = authenticated_client.get(f"/students/{student_id}")
    assert all(title in archive.text for title in MODULE_TITLES)


def test_empty_archive_keeps_all_modules_with_no_data(authenticated_client):
    with SessionLocal() as db:
        student = Student(name="空模块测试", id_card_number="11010519491231002X")
        db.add(student); db.commit(); student_id = student.id
    page = authenticated_client.get(f"/students/{student_id}")
    assert all(title in page.text for title in MODULE_TITLES)
    assert page.text.count("暂无数据") >= 6


def test_original_excel_imports_into_seven_modules():
    source = Path("../头雁学员名单2024_学员名单_原版.xlsx")
    if not source.exists(): pytest.skip("原始 Excel 不在项目父目录")
    with SessionLocal() as db:
        batch = create_preview(db, source, source.name, None, get_settings().upload_dir)
        assert batch.total_rows == 95 and batch.failed_rows == 0
        commit_batch(db, batch, None)
        students = db.query(Student).all()
        assert len(students) == 95
        sample = next(student for student in students if student.name == "靳桢")
        assert sample.education is not None
        assert sample.entities and sample.entities[0].revenues and sample.entities[0].industries
        assert sample.cultivations
