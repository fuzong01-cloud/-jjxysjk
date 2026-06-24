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

