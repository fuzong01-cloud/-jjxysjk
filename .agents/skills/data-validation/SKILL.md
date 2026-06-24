---
name: data-validation
description: Use this skill when validating identity numbers, phone numbers, email, date, year, money, required fields, and API input data for the 头雁学员信息管理系统.
---

# Data Validation Skill

## Goal

Create consistent validation rules for Excel import, API requests, database writes, and admin forms.

## Core Rules

1. Validation must be reusable.
2. Validation errors must be clear and user-readable.
3. Validation should distinguish error and warning.
4. Do not crash on bad Excel data; record the error and continue when safe.
5. API validation should return structured error responses.
6. Imported empty strings should become `None`.
7. Money fields should use `Decimal`.
8. Dates should be normalized to `YYYY-MM-DD`.
9. Years should be normalized to integer year.
10. Validation rules should be tested.

## Required Validators

### ID card number

Validate Chinese resident ID card number.

Rules:

- Accept 18-digit ID card numbers.
- Last character may be digit or `X`.
- Normalize lowercase `x` to uppercase `X`.
- Validate date portion when possible.
- Validate checksum when implementation is available.
- Extract birth date when possible.
- Extract gender when possible.
- Do not log or display full ID card number unnecessarily.

### Phone number

Rules:

- Strip spaces, hyphens, and invisible characters.
- Validate common mainland China mobile phone format when possible.
- Keep original value in import error if invalid.
- Allow warning rather than hard failure if phone is missing.

### Email

Rules:

- Validate basic email format.
- Convert empty string to `None`.

### Date

Rules:

- Accept Excel date cells.
- Accept strings like `2024-01-01`, `2024/1/1`, `2024年1月1日`.
- Normalize to `date`.
- Report invalid dates.

### Year

Rules:

- Accept integer year.
- Accept strings like `2023年`.
- Reject impossible years.
- Normalize to int.

### Money

Rules:

- Accept int, float, Decimal, and numeric strings.
- Strip commas and currency symbols.
- Convert to `Decimal`.
- Preserve two decimal places when needed.
- Empty money field becomes `None`.
- Invalid money field produces import error.

### Integer count

Rules:

- Used for employee count and operation years where applicable.
- Accept numeric strings.
- Reject non-numeric text unless business rule says warning.

### Required fields

At minimum:

- Student name.
- ID card number.

Business entity name may be required only when importing entity-related records.

## Validation Levels

Use these severity levels:

- `error`: row cannot be imported safely.
- `warning`: row can be imported but needs review.
- `info`: non-blocking note.

## API Error Format

Return errors like:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "请求数据校验失败",
  "details": [
    {
      "field": "id_card_number",
      "message": "身份证号格式不正确"
    }
  ]
}
```

## Import Error Format

Save errors with:

- Excel row number.
- Original column name.
- Internal field name.
- Raw value.
- Error type.
- Error message.
- Severity.

## Expected Files

When invoked, create or update:

- `app/core/validators.py`
- `app/core/exceptions.py`
- `app/schemas/common.py`
- `tests/test_validators.py`
- `docs/validation_rules.md`

## Expected Output

When invoked, provide:

1. Validation rule list.
2. Reusable validator functions.
3. Pydantic validators.
4. Import error integration.
5. Tests for valid and invalid values.
