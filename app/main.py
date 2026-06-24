from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes.api import router as api_router
from app.api.routes.pages import router as pages_router
from app.core.config import BASE_DIR, get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.entities import User


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings(); settings.upload_dir.mkdir(parents=True, exist_ok=True); settings.backup_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).limit(1)):
            db.add(User(username=settings.admin_username, password_hash=hash_password(settings.admin_password))); db.commit()
    yield


app = FastAPI(title="头雁学员信息管理系统 API", version="1.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=get_settings().app_secret_key, same_site="lax", https_only=False)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
app.include_router(api_router)
app.include_router(pages_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"code": "VALIDATION_ERROR", "message": "请求数据校验失败", "details": [{"field": ".".join(map(str, error["loc"])), "message": error["msg"]} for error in exc.errors()]})

