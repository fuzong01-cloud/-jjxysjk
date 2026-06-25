from app.core.database import SessionLocal
from app.models.entities import Student
from openpyxl import Workbook


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


def test_delete_student_from_list(authenticated_client):
    with SessionLocal() as db:
        student = Student(name="待删除学员", id_card_number="11010519491231002X", district_county="测试区")
        db.add(student); db.commit(); student_id = student.id

    page = authenticated_client.get("/students", params={"name": "待删除"})
    assert page.status_code == 200 and "删除" in page.text and "待删除学员" in page.text

    result = authenticated_client.delete(f"/api/v1/students/{student_id}")
    assert result.status_code == 200
    assert authenticated_client.get(f"/api/v1/students/{student_id}").status_code == 404
    assert authenticated_client.get("/students", params={"name": "待删除"}).text.count("待删除学员") == 0

    logs = authenticated_client.get("/api/v1/audit-logs").json()["data"]
    assert any(row["action"] == "STUDENT_DELETE" for row in logs)


def test_import_template_download(authenticated_client):
    result = authenticated_client.get("/api/v1/import/template.xlsx")
    assert result.status_code == 200
    assert result.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_import_confirmation_preview_rows(authenticated_client, tmp_path):
    path = tmp_path / "preview.xlsx"
    book = Workbook(); sheet = book.active; sheet.title = "Sheet1"
    sheet.append(["学员姓名", "身份证号", "所在区县", "新型经营主体名称", "个人获得荣誉情况1"])
    sheet.append(["预览学员", "11010519491231002X", "北京市延庆区", "预览合作社", "优秀学员"])
    book.save(path)

    with path.open("rb") as handle:
        result = authenticated_client.post(
            "/api/v1/import/preview",
            files={"file": ("preview.xlsx", handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    assert result.status_code == 200
    data = result.json()["data"]
    assert data["rows"][0]["name"] == "预览学员"
    assert data["rows"][0]["business_entity_name"] == "预览合作社"
    assert data["rows"][0]["modules"]["honors"] == 1
    assert data["rows"][0]["modules"]["business_entities"] is True


def test_import_commit_rejects_failed_preview(authenticated_client, tmp_path):
    path = tmp_path / "bad-preview.xlsx"
    book = Workbook(); sheet = book.active; sheet.title = "Sheet1"
    sheet.append(["学员姓名", "身份证号"])
    sheet.append(["错误学员", ""])
    book.save(path)

    with path.open("rb") as handle:
        result = authenticated_client.post(
            "/api/v1/import/preview",
            files={"file": ("bad-preview.xlsx", handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    batch_id = result.json()["data"]["batch_id"]
    error_row = [row for row in result.json()["data"]["rows"] if row["action"] == "错误"][0]
    assert error_row["has_error"] is True
    assert error_row["error_messages"]
    commit = authenticated_client.post(f"/api/v1/import/batches/{batch_id}/commit")
    assert commit.status_code == 400


def test_cancel_import_preview(authenticated_client, tmp_path):
    path = tmp_path / "cancel-preview.xlsx"
    book = Workbook(); sheet = book.active; sheet.title = "Sheet1"
    sheet.append(["学员姓名", "身份证号"])
    sheet.append(["取消预览学员", "11010519491231002X"])
    book.save(path)

    with path.open("rb") as handle:
        result = authenticated_client.post(
            "/api/v1/import/preview",
            files={"file": ("cancel-preview.xlsx", handle, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    batch_id = result.json()["data"]["batch_id"]
    cancel = authenticated_client.delete(f"/api/v1/import/batches/{batch_id}")
    assert cancel.status_code == 200
    assert authenticated_client.get(f"/api/v1/import/batches/{batch_id}/preview").status_code == 404
