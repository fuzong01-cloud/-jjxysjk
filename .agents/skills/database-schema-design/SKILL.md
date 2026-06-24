---
name: database-schema-design
description: Use this skill when designing database tables, relationships, primary keys, foreign keys, indexes, and normalized schema for the 头雁学员信息管理系统.
---

# Database Schema Design Skill

## Goal

Design the final normalized database schema for the 头雁学员信息管理系统.

The source data comes from an Excel student list. The system must support import, query, update, export, audit logging, authentication, and future maintenance.

## Core Rules

1. Use `id` as the internal primary key for each table.
2. Use `id_card_number` as the unique business identifier for students.
3. Do not use student name as a unique key.
4. Keep original Excel row number in imported student-related records when useful.
5. Repeated Excel column groups must become child tables.
6. Honor records must be stored as one row per honor.
7. Annual revenue records must be stored as one row per entity per year.
8. Main industries must be stored as one row per industry.
9. Use clear foreign keys and cascading rules.
10. Add indexes for common query fields.
11. Use `created_at`, `updated_at`, and where applicable `deleted_at`.
12. Prefer soft delete for business records.
13. Store money and financial fields as `Numeric`, not float.
14. Store dates as `Date`.
15. Store long descriptions as `Text`.

## Required Tables

Design at least these tables:

### 1. `students`

Stores core student identity and personal information.

Recommended fields:

- `id`
- `id_card_number`
- `name`
- `gender`
- `birth_date`
- `age_snapshot`
- `ethnicity`
- `native_place`
- `district_county`
- `political_status`
- `phone`
- `health_status`
- `professional_title`
- `wechat`
- `email`
- `household_type`
- `postal_code`
- `home_address`
- `talent_category`
- `status`
- `administrative_position`
- `social_part_time_positions`
- `source_excel_row`
- `created_at`
- `updated_at`
- `deleted_at`

Rules:

- `id_card_number` must be unique.
- `name`, `district_county`, `phone`, `id_card_number` need indexes.
- `age_snapshot` can be stored only as imported reference. Real age should be calculated from `birth_date`.

### 2. `education_records`

Stores education, degree, major, certificate, learning, work, and training history.

Recommended fields:

- `id`
- `student_id`
- `education_level`
- `graduate_school`
- `major`
- `certificate_number`
- `learning_experience`
- `work_experience`
- `training_experience`
- `created_at`
- `updated_at`

### 3. `honor_records`

Stores multiple personal honors.

Recommended fields:

- `id`
- `student_id`
- `honor_time`
- `honor_level`
- `honor_description`
- `source_column_group`
- `created_at`
- `updated_at`
- `deleted_at`

Rules:

- Import honor groups like honor 1-5 into multiple rows.
- Empty honor groups should not create records.
- Adding new personal honor uses this table.

### 4. `business_entities`

Stores new agricultural/business entity information.

Recommended fields:

- `id`
- `student_id`
- `entity_name`
- `entity_intro`
- `entity_type`
- `entity_subtype`
- `established_date`
- `registered_address`
- `unified_social_credit_code`
- `industry_years`
- `student_position_in_entity`
- `technical_partner`
- `quality_inspection_org`
- `quality_system_certification`
- `green_organic_geo_certification`
- `entity_honors`
- `supporting_policies`
- `created_at`
- `updated_at`
- `deleted_at`

Rules:

- A student may have zero, one, or multiple entities.
- Index `entity_name` and `unified_social_credit_code`.
- Do not assume unified social credit code is always present.

### 5. `annual_revenue_records`

Stores financial data by year.

Recommended fields:

- `id`
- `business_entity_id`
- `year`
- `operating_revenue`
- `net_profit`
- `fixed_asset_net_value`
- `total_assets`
- `total_liabilities`
- `employee_count`
- `current_assets`
- `management_expense`
- `government_subsidy_amount`
- `source_column_group`
- `created_at`
- `updated_at`

Rules:

- One row represents one business entity in one year.
- Add unique constraint on `(business_entity_id, year)` if data quality permits.
- Use `Numeric(18, 2)` for money fields.

### 6. `main_industries`

Stores multiple main industries.

Recommended fields:

- `id`
- `business_entity_id`
- `industry_name`
- `three_year_total_income`
- `operation_years`
- `source_column_group`
- `created_at`
- `updated_at`

### 7. `cultivation_records`

Stores cultivation year and training demand.

Recommended fields:

- `id`
- `student_id`
- `cultivation_year`
- `cultivation_needs`
- `training_experience`
- `created_at`
- `updated_at`

### 8. `import_batches`

Stores each Excel import batch.

Recommended fields:

- `id`
- `file_name`
- `file_hash`
- `sheet_name`
- `started_at`
- `finished_at`
- `status`
- `total_rows`
- `success_rows`
- `failed_rows`
- `warning_count`
- `created_by_user_id`

### 9. `import_errors`

Stores import validation and transformation errors.

Recommended fields:

- `id`
- `import_batch_id`
- `excel_row_number`
- `column_name`
- `field_name`
- `raw_value`
- `error_type`
- `error_message`
- `severity`
- `created_at`

### 10. `users`, `roles`, `permissions`

Design authentication and permission tables.

Minimum tables:

- `users`
- `roles`
- `permissions`
- `user_roles`
- `role_permissions`

### 11. `audit_logs`

Stores write operations.

Recommended fields:

- `id`
- `user_id`
- `action`
- `target_table`
- `target_id`
- `before_data`
- `after_data`
- `ip_address`
- `user_agent`
- `created_at`

### 12. `backup_records`

Stores backup metadata.

Recommended fields:

- `id`
- `backup_file_path`
- `database_type`
- `backup_type`
- `status`
- `file_size`
- `file_hash`
- `created_by_user_id`
- `created_at`

## Expected Output

When invoked, produce:

1. Entity relationship explanation.
2. Table list.
3. Field dictionary.
4. SQLAlchemy model design notes.
5. Alembic migration plan.
6. Index plan.
7. Data normalization explanation.
8. Known assumptions and risks.
