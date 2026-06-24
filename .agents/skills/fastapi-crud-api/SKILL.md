---
name: fastapi-crud-api
description: Use this skill when building FastAPI routes, services, schemas, CRUD logic, pagination, filtering, and structured API responses for the 头雁学员信息管理系统.
---

# FastAPI CRUD API Skill

## Goal

Build the backend API for the 头雁学员信息管理系统.

## Technical Rules

1. Use FastAPI.
2. Use Pydantic v2 schemas.
3. Use SQLAlchemy sessions through dependency injection.
4. Keep route, schema, service, and repository logic separated.
5. Use structured responses.
6. Use pagination for list endpoints.
7. Add filtering and sorting where useful.
8. Enforce authentication and permissions where required.
9. Log write operations through audit log service.
10. Validate request bodies.
11. Do not expose full sensitive ID card numbers in list responses unless required.

## Required API Groups

### Health

- `GET /health`

### Students

- `GET /api/students`
- `GET /api/students/{student_id}`
- `GET /api/students/by-id-card/{id_card_number}`
- `GET /api/students/search`
- `PATCH /api/students/{student_id}/basic-info`

Required filters:

- name
- id card number
- district/county
- phone
- status
- talent category

### Honors

- `GET /api/students/{student_id}/honors`
- `POST /api/students/{student_id}/honors`
- `PATCH /api/honors/{honor_id}`
- `DELETE /api/honors/{honor_id}`

### Business entities

- `GET /api/business-entities`
- `GET /api/business-entities/{entity_id}`
- `PATCH /api/business-entities/{entity_id}`

Required filters:

- entity name
- student name
- district/county
- unified social credit code
- entity type

### Revenue

- `GET /api/business-entities/{entity_id}/revenue`
- `POST /api/business-entities/{entity_id}/revenue`
- `PATCH /api/revenue/{revenue_id}`

### Industries

- `GET /api/business-entities/{entity_id}/industries`
- `POST /api/business-entities/{entity_id}/industries`
- `PATCH /api/industries/{industry_id}`

### Import

- `POST /api/import/excel`
- `GET /api/import/batches`
- `GET /api/import/batches/{batch_id}`
- `GET /api/import/batches/{batch_id}/errors`

### Export

- `GET /api/export/students.xlsx`
- `GET /api/export/business-entities.xlsx`

### Audit

- `GET /api/audit-logs`

### Auth

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

## Response Format

Use consistent response models.

Example success:

```json
{
  "data": {},
  "message": "success"
}
```

Example list:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

Example error:

```json
{
  "code": "NOT_FOUND",
  "message": "学员不存在",
  "details": []
}
```

## Expected Files

When invoked, create or update:

- `app/main.py`
- `app/api/router.py`
- `app/api/routes/*.py`
- `app/schemas/*.py`
- `app/services/*.py`
- `app/repositories/*.py`
- `app/core/exceptions.py`
- `tests/test_api_*.py`

## Expected Output

When invoked, produce:

1. API route plan.
2. Pydantic schemas.
3. Service and repository code.
4. Error handling.
5. Authentication integration.
6. Audit log integration.
7. Tests.
