from app.core.database import SessionLocal
from app.models.entities import Student


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_api_requires_login(client):
    assert client.get("/api/v1/students").status_code == 401


def test_search_update_and_audit(authenticated_client):
    with SessionLocal() as db:
        student = Student(name="测试学员", id_card_number="11010519491231002X", district_county="北京市延庆区")
        db.add(student); db.commit(); student_id = student.id
    result = authenticated_client.get("/api/v1/students", params={"name": "测试"})
    assert result.status_code == 200
    assert result.json()["total"] == 1
    update = authenticated_client.patch(f"/api/v1/students/{student_id}/basic-info", json={"phone": "13800138000"})
    assert update.status_code == 200
    logs = authenticated_client.get("/api/v1/audit-logs").json()["data"]
    assert any(row["action"] == "STUDENT_UPDATE" for row in logs)


def test_add_honor(authenticated_client):
    with SessionLocal() as db:
        student = Student(name="荣誉学员", id_card_number="11010519491231002X")
        db.add(student); db.commit(); student_id = student.id
    result = authenticated_client.post(f"/api/v1/students/{student_id}/honors", json={"honor_level": "市级", "honor_description": "优秀学员"})
    assert result.status_code == 200


def test_change_password(authenticated_client):
    result = authenticated_client.post("/api/v1/auth/password", json={"current_password": "TestPass123!", "new_password": "NewTestPass456!"})
    assert result.status_code == 200
    authenticated_client.post("/logout")
    assert authenticated_client.post("/login", data={"username": "admin", "password": "NewTestPass456!"}).status_code == 200


def test_id_card_page_search_and_category_tables(authenticated_client):
    with SessionLocal() as db:
        student = Student(name="分类测试", id_card_number="11010519491231002X")
        db.add(student); db.commit(); student_id = student.id
    result = authenticated_client.get("/students", params={"id_card": "11010519491231002x"})
    assert result.status_code == 200 and "分类测试" in result.text and "身份证号（精准查询）" in result.text
    detail = authenticated_client.get(f"/students/{student_id}")
    for title in ("基本信息表", "受教育情况表", "荣誉情况表", "新型经营主体情况表", "近三年营收情况表", "主营产业情况表", "个人培育信息表"):
        assert title in detail.text


def test_import_template_download(authenticated_client):
    result = authenticated_client.get("/api/v1/import/template.xlsx")
    assert result.status_code == 200
    assert result.headers["content-type"].startswith("application/vnd.openxmlformats")
