---
name: admin-ui-prototype
description: Use this skill when creating a simple management UI for importing Excel, searching students, viewing details, editing records, adding honors, exporting results, and viewing audit logs.
---

# Admin UI Prototype Skill

## Goal

Create a practical web-based admin interface for the 头雁学员信息管理系统.

The UI can be simple but must be usable.

## Recommended Approach

Choose one of these approaches:

1. FastAPI + Jinja2 + Bootstrap for simple server-rendered pages.
2. FastAPI backend + Vue/React frontend if project requires separate frontend.
3. Streamlit only for quick internal prototypes, not final system.

Default recommendation: FastAPI + Jinja2 + Bootstrap unless user requests otherwise.

## Required Pages

### 1. Login page

- Username/password login.
- Error display.
- Logout button.

### 2. Dashboard

Show:

- Total students.
- Total business entities.
- Total honors.
- Latest import batch.
- Latest audit logs.

### 3. Excel import page

Features:

- Upload Excel.
- Dry-run option.
- Commit import option.
- Import progress/result.
- Link to error report.

### 4. Student search page

Filters:

- Name.
- ID card number.
- District/county.
- Phone.
- Talent category.
- Status.
- Business entity name.

Features:

- Pagination.
- Reset filters.
- Export current result.

### 5. Student detail page

Sections:

- Basic information.
- Education information.
- Honors.
- Business entities.
- Annual revenue.
- Main industries.
- Cultivation information.
- Operation history.

### 6. Edit basic information page

Editable fields include:

- phone
- political status
- professional title
- household type
- talent category
- administrative position
- social part-time positions
- status

Rules:

- Do not edit ID card number casually.
- Record audit log.

### 7. Add honor page

Fields:

- honor time
- honor level
- honor description

Rules:

- Add one record each time.
- Record audit log.

### 8. Edit business entity page

Editable fields include:

- entity name
- intro
- type
- subtype
- established date
- registered address
- unified social credit code
- student position in entity

### 9. Export page

Features:

- Export search result.
- Export full student details.
- Export import error report.

### 10. Audit log page

Features:

- Filter by user.
- Filter by action.
- Filter by time.
- View before/after changes.

### 11. User and role management page

Admin only.

Features:

- Create user.
- Disable user.
- Assign role.
- View permissions.

## UI Rules

1. Keep forms clear and simple.
2. Show validation errors near fields.
3. Show success/failure messages.
4. Mask sensitive ID card numbers in list pages.
5. Require confirmation for destructive actions.
6. All write operations must call backend APIs.
7. All write operations must be audited.

## Expected Files

When invoked, create or update:

- `app/templates/`
- `app/static/`
- `app/api/routes/pages.py`
- `app/services/dashboard_service.py`
- `docs/admin_ui.md`

## Expected Output

When invoked, produce:

1. UI page list.
2. Template files.
3. Form handling.
4. Integration with API/services.
5. Screenshots or usage notes if possible.
