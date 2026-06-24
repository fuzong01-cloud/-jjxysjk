# 头雁学员信息管理系统

面向继续教育学院内部使用的学员档案管理系统。支持原始 Excel 预览导入、学员检索和维护、荣誉及经营数据管理、Excel 导出、审计日志以及 SQLite 备份恢复。

普通用户请先阅读：[用户操作说明书](docs/admin_user_manual.md)。

## 快速启动（Windows）

```powershell
cd D:\继续教育学院数据库\touyan-student-system
.\scripts\init.ps1
notepad .env
.\scripts\start.ps1
```

打开 `http://127.0.0.1:8000`。默认账号来自 `.env`；首次运行前务必修改默认密码和 `APP_SECRET_KEY`。API 文档位于 `/docs`。

## 常用命令

```powershell
# 测试
.\scripts\test.ps1

# 命令行预览导入
.\.venv\Scripts\python.exe scripts\import_excel.py --file "..\头雁学员名单2024_学员名单_原版.xlsx" --dry-run

# 确认导入
.\.venv\Scripts\python.exe scripts\import_excel.py --file "..\头雁学员名单2024_学员名单_原版.xlsx" --commit

# 创建迁移
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "说明"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## 目录

- `app/`：FastAPI 应用、模型、服务、页面及静态资源
- `alembic/`：数据库迁移
- `scripts/`：初始化、启动、测试、备份和导入脚本
- `tests/`：自动化测试
- `docs/`：设计、接口、操作和部署文档
- `data/`：本地 SQLite 数据库（不提交 Git）
- `backups/`：数据库备份（不提交 Git）

## 环境变量

参见 `.env.example`。默认仅监听本机 `127.0.0.1`。系统模型避免 SQLite 专有字段，后续可通过 `DATABASE_URL` 迁移到 PostgreSQL。

更完整说明见 [系统文档](docs/system_guide.md)。
