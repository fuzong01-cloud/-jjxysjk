---
name: project-docs
description: Use this skill when creating README, setup guide, database design document, API document, import/export guide, deployment guide, and user manual.
---

# Project Docs Skill

## Goal

Generate complete documentation for the 头雁学员信息管理系统.

## Required Documents

### 1. README.md

Must include:

- Project introduction.
- Feature list.
- Tech stack.
- Directory structure.
- Quick start.
- Environment variables.
- Database migration commands.
- Excel import commands.
- Test commands.
- Deployment overview.

### 2. Database design document

Must include:

- Table list.
- Field dictionary.
- Relationships.
- Indexes.
- Business rules.
- ER diagram text description if diagram is not available.

### 3. Excel import guide

Must include:

- Supported file format.
- Required columns.
- Field mapping.
- Import command.
- Dry-run mode.
- Error report explanation.
- Common problems.

### 4. API document

Must include:

- Endpoint list.
- Request parameters.
- Response format.
- Error format.
- Auth requirements.
- Example requests.

### 5. Admin user manual

Must include:

- Login.
- Search students.
- View student details.
- Add honor.
- Edit basic information.
- Edit business entity.
- Import Excel.
- Export Excel.
- View audit logs.

### 6. Deployment guide

Must include:

- Local development.
- Docker deployment.
- PostgreSQL configuration.
- Environment variables.
- Backup strategy.
- Upgrade and migration steps.

### 7. Developer guide

Must include:

- Coding conventions.
- How to add new fields.
- How to write migrations.
- How to add tests.
- How to use Codex skills.

## Documentation Rules

1. Use Chinese for user-facing documentation.
2. Keep commands copy-pasteable.
3. Avoid vague instructions.
4. Mention default development database clearly.
5. Include troubleshooting section.
6. Keep sensitive credentials out of docs.

## Expected Files

When invoked, create or update:

- `README.md`
- `docs/database_design.md`
- `docs/excel_import.md`
- `docs/api.md`
- `docs/admin_user_manual.md`
- `docs/deployment.md`
- `docs/developer_guide.md`

## Expected Output

When invoked, produce complete Markdown documentation.
