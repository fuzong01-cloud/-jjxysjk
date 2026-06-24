from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import BASE_DIR
from app.core.database import get_db
from app.core.security import mask_id_card, mask_phone, verify_password
from app.models.entities import AuditLog, BusinessEntity, HonorRecord, ImportBatch, Student, User
from app.services.audit_service import add_audit


router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")
templates.env.globals.update(mask_id_card=mask_id_card, mask_phone=mask_phone)


def _user(request: Request, db: Session) -> User | None:
    return db.get(User, request.session.get("user_id")) if request.session.get("user_id") else None


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
def login(request: Request, username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == username))
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "login.html", {"error": "账号或密码不正确"}, status_code=400)
    request.session.clear(); request.session["user_id"] = user.id; user.last_login_at = datetime.utcnow()
    add_audit(db, user_id=user.id, action="LOGIN", ip_address=request.client.host if request.client else None); db.commit()
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id: add_audit(db, user_id=user_id, action="LOGOUT"); db.commit()
    request.session.clear(); return RedirectResponse("/login", status_code=303)


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if not user: return RedirectResponse("/login")
    context = {"user": user, "student_count": db.scalar(select(func.count(Student.id))) or 0, "entity_count": db.scalar(select(func.count(BusinessEntity.id))) or 0, "honor_count": db.scalar(select(func.count(HonorRecord.id)).where(HonorRecord.deleted_at.is_(None))) or 0, "latest_batch": db.scalar(select(ImportBatch).order_by(ImportBatch.id.desc()).limit(1)), "logs": db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(6)).all()}
    return templates.TemplateResponse(request, "dashboard.html", context)


@router.get("/students", response_class=HTMLResponse)
def student_list(request: Request, name: str = "", district: str = "", entity_name: str = "", page: int = 1, db: Session = Depends(get_db)):
    user = _user(request, db)
    if not user: return RedirectResponse("/login")
    stmt = select(Student).where(Student.deleted_at.is_(None))
    if name: stmt = stmt.where(Student.name.contains(name))
    if district: stmt = stmt.where(Student.district_county.contains(district))
    if entity_name: stmt = stmt.join(Student.entities).where(BusinessEntity.entity_name.contains(entity_name))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Student.id.desc()).offset((max(page, 1)-1)*20).limit(20)).all()
    return templates.TemplateResponse(request, "students.html", {"user": user, "students": rows, "total": total, "page": page, "name": name, "district": district, "entity_name": entity_name})


@router.get("/students/{student_id}", response_class=HTMLResponse)
def student_detail_page(student_id: int, request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if not user: return RedirectResponse("/login")
    student = db.scalar(select(Student).options(selectinload(Student.education), selectinload(Student.honors), selectinload(Student.entities).selectinload(BusinessEntity.revenues), selectinload(Student.entities).selectinload(BusinessEntity.industries), selectinload(Student.cultivations)).where(Student.id == student_id))
    if not student: return templates.TemplateResponse(request, "message.html", {"user": user, "title": "找不到学员", "message": "该档案可能已被删除。"}, status_code=404)
    return templates.TemplateResponse(request, "student_detail.html", {"user": user, "student": student})


@router.get("/import", response_class=HTMLResponse)
def import_page(request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if not user: return RedirectResponse("/login")
    batches = db.scalars(select(ImportBatch).order_by(ImportBatch.id.desc()).limit(20)).all()
    return templates.TemplateResponse(request, "import.html", {"user": user, "batches": batches})


@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if not user: return RedirectResponse("/login")
    logs = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(200)).all()
    return templates.TemplateResponse(request, "audit.html", {"user": user, "logs": logs})


@router.get("/backups", response_class=HTMLResponse)
def backups_page(request: Request, db: Session = Depends(get_db)):
    from app.models.entities import BackupRecord
    user = _user(request, db)
    if not user: return RedirectResponse("/login")
    rows = db.scalars(select(BackupRecord).order_by(BackupRecord.id.desc())).all()
    return templates.TemplateResponse(request, "backups.html", {"user": user, "backups": rows})

