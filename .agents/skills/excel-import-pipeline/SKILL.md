---
name: excel-import-pipeline
description: Use this skill when importing, cleaning, validating, transforming, and loading the 头雁学员名单 Excel file into normalized database tables.
---

# Excel Import Pipeline Skill

## Goal

Build a robust Excel import pipeline for the 头雁学员信息管理系统.

The import process must read the Excel file, clean column names, validate data, split repeated groups into child tables, insert/update the database, and generate an import report.

## Input

Expected input file:

- `.xlsx`
- Usually stored under `data/`
- Example name: `头雁学员名单2024.xlsx`

## Core Rules

1. Do not silently drop data.
2. Preserve original Excel file name, sheet name, and row number.
3. Detect and report missing required columns.
4. Normalize column names before mapping.
5. Handle merged cells, empty rows, and repeated header rows when possible.
6. Import should be idempotent when possible.
7. Use `id_card_number` to match existing students.
8. Name is not enough to identify a student.
9. Convert repeated Excel columns into child table records.
10. Create an import report every time.
11. Save import warnings and errors into `import_errors`.
12. Support dry-run mode.

## Required Pipeline Steps

### 1. Load workbook

Use `pandas` and/or `openpyxl`.

Tasks:

- Read all sheet names.
- Identify data sheet.
- Read header row.
- Read data rows.
- Keep original row number.

### 2. Normalize columns

Column normalization should:

- Strip spaces and line breaks.
- Convert full-width punctuation where needed.
- Handle Chinese aliases.
- Map original column name to internal field name.
- Preserve unknown columns in report.

### 3. Validate required fields

Required fields should include at least:

- `name`
- `id_card_number`

Recommended additional checks:

- `phone`
- `district_county`
- `birth_date`
- `business_entity.entity_name`

### 4. Validate field types

Validate:

- ID card number.
- Phone number.
- Email.
- Date.
- Year.
- Money.
- Integer count.
- Percentage-like text if present.
- Unified social credit code if present.

### 5. Transform student data

Map basic student fields into `students`.

Rules:

- Birth date can be parsed from ID card number if missing.
- Gender can be parsed from ID card number if missing.
- Age should be recalculated from birth date or stored as snapshot only.
- Empty strings become `None`.

### 6. Transform education data

Map education-related fields into `education_records`.

### 7. Transform honors

Repeated Excel columns may look like:

- 荣誉时间1, 荣誉级别1, 荣誉情况1
- 荣誉时间2, 荣誉级别2, 荣誉情况2
- ...
- 荣誉时间5, 荣誉级别5, 荣誉情况5

Rules:

- Each non-empty group becomes one `honor_records` row.
- Do not create an honor record if all fields in a group are empty.
- Keep `source_column_group`, such as `honor_1`.

### 8. Transform business entity

Map fields into `business_entities`.

Rules:

- A student can have multiple business entities if source data contains them.
- If the Excel only contains one entity per row, create one entity per student row.
- Avoid duplicate entity creation by checking name and unified social credit code.

### 9. Transform annual revenue

Repeated Excel columns may look like:

- 营收年份1, 营业收入1, 净利润1, 总资产1...
- 营收年份2, 营业收入2, 净利润2, 总资产2...
- 营收年份3, 营业收入3, 净利润3, 总资产3...

Rules:

- Each year group becomes one `annual_revenue_records` row.
- Money fields use Decimal.
- Employee count uses integer.
- Keep `source_column_group`, such as `revenue_1`.

### 10. Transform industries

Repeated Excel columns may look like:

- 主营产业1, 近三年经营总收入1, 经营年限1
- 主营产业2, 近三年经营总收入2, 经营年限2
- 主营产业3, 近三年经营总收入3, 经营年限3

Rules:

- Each non-empty industry group becomes one `main_industries` row.
- Keep `source_column_group`.

### 11. Save import result

For each row:

- Insert or update student.
- Insert related child records.
- Save validation errors.
- Count success, warning, failed rows.

### 12. Generate report

Report should include:

- Import batch ID.
- File name.
- Sheet name.
- Total rows.
- Success rows.
- Failed rows.
- Warning count.
- Error details.
- Unknown columns.
- Duplicate ID card numbers.
- Rows skipped and reasons.

## Expected Files

When invoked, create or update:

- `scripts/import_excel.py`
- `app/services/import_service.py`
- `app/services/excel_parser.py`
- `app/services/field_mapping.py`
- `app/schemas/import_schema.py`
- `tests/test_excel_import.py`
- `docs/excel_import.md`

## CLI Interface

Provide command like:

```bash
python scripts/import_excel.py --file data/头雁学员名单2024.xlsx --dry-run
python scripts/import_excel.py --file data/头雁学员名单2024.xlsx --commit
```

## Expected Output

When invoked, produce:

1. Import architecture.
2. Field mapping.
3. Validation rules.
4. Transformation code.
5. Import report format.
6. Tests.
7. Usage documentation.
