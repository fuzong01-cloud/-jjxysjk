from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.utcnow()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class Student(Base, TimestampMixin):
    __tablename__ = "students"
    __table_args__ = (Index("ix_students_name_district", "name", "district_county"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    id_card_number: Mapped[str] = mapped_column(String(18), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    gender: Mapped[str | None] = mapped_column(String(20))
    birth_date: Mapped[date | None] = mapped_column(Date)
    age_snapshot: Mapped[int | None] = mapped_column(Integer)
    ethnicity: Mapped[str | None] = mapped_column(String(50))
    native_place: Mapped[str | None] = mapped_column(String(200))
    district_county: Mapped[str | None] = mapped_column(String(200), index=True)
    political_status: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(50), index=True)
    health_status: Mapped[str | None] = mapped_column(String(100))
    professional_title: Mapped[str | None] = mapped_column(String(100))
    wechat: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(200))
    household_type: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    home_address: Mapped[str | None] = mapped_column(Text)
    talent_category: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(50))
    administrative_position: Mapped[str | None] = mapped_column(String(200))
    social_part_time_positions: Mapped[str | None] = mapped_column(Text)
    source_excel_row: Mapped[int | None] = mapped_column(Integer)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    education: Mapped[EducationRecord | None] = relationship(back_populates="student", cascade="all, delete-orphan", uselist=False)
    honors: Mapped[list[HonorRecord]] = relationship(back_populates="student", cascade="all, delete-orphan")
    entities: Mapped[list[BusinessEntity]] = relationship(back_populates="student", cascade="all, delete-orphan")
    cultivations: Mapped[list[CultivationRecord]] = relationship(back_populates="student", cascade="all, delete-orphan")

    @property
    def age(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


class EducationRecord(Base, TimestampMixin):
    __tablename__ = "education_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True)
    education_level: Mapped[str | None] = mapped_column(String(100))
    graduate_school: Mapped[str | None] = mapped_column(String(200))
    major: Mapped[str | None] = mapped_column(String(200))
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    learning_experience: Mapped[str | None] = mapped_column(Text)
    work_experience: Mapped[str | None] = mapped_column(Text)
    training_experience: Mapped[str | None] = mapped_column(Text)
    student: Mapped[Student] = relationship(back_populates="education")


class HonorRecord(Base, TimestampMixin):
    __tablename__ = "honor_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    honor_number: Mapped[str | None] = mapped_column(String(100))
    honor_time: Mapped[date | None] = mapped_column(Date)
    honor_level: Mapped[str | None] = mapped_column(String(100))
    honor_description: Mapped[str] = mapped_column(Text)
    source_column_group: Mapped[str | None] = mapped_column(String(50))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    student: Mapped[Student] = relationship(back_populates="honors")


class BusinessEntity(Base, TimestampMixin):
    __tablename__ = "business_entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    entity_name: Mapped[str | None] = mapped_column(String(300), index=True)
    entity_intro: Mapped[str | None] = mapped_column(Text)
    entity_type: Mapped[str | None] = mapped_column(String(150))
    entity_subtype: Mapped[str | None] = mapped_column(String(150))
    entity_industry_type: Mapped[str | None] = mapped_column(String(200))
    established_date: Mapped[date | None] = mapped_column(Date)
    registered_address: Mapped[str | None] = mapped_column(Text)
    unified_social_credit_code: Mapped[str | None] = mapped_column(String(50), index=True)
    industry_years: Mapped[int | None] = mapped_column(Integer)
    student_position_in_entity: Mapped[str | None] = mapped_column(String(200))
    patent_applications: Mapped[str | None] = mapped_column(Text)
    farmer_households_driven: Mapped[int | None] = mapped_column(Integer)
    technical_partner_count: Mapped[int | None] = mapped_column(Integer)
    technical_partners: Mapped[str | None] = mapped_column(Text)
    quality_inspection_org: Mapped[str | None] = mapped_column(String(100))
    quality_system_certification: Mapped[str | None] = mapped_column(Text)
    green_organic_geo_certification: Mapped[str | None] = mapped_column(Text)
    entity_honors: Mapped[str | None] = mapped_column(Text)
    supporting_policies: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    student: Mapped[Student] = relationship(back_populates="entities")
    revenues: Mapped[list[AnnualRevenueRecord]] = relationship(back_populates="entity", cascade="all, delete-orphan")
    industries: Mapped[list[MainIndustry]] = relationship(back_populates="entity", cascade="all, delete-orphan")


class AnnualRevenueRecord(Base, TimestampMixin):
    __tablename__ = "annual_revenue_records"
    __table_args__ = (UniqueConstraint("business_entity_id", "year", name="uq_entity_revenue_year"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    business_entity_id: Mapped[int] = mapped_column(ForeignKey("business_entities.id", ondelete="CASCADE"), index=True)
    year: Mapped[int] = mapped_column(Integer)
    operating_revenue: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    net_profit: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    fixed_asset_net_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    total_assets: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    total_liabilities: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    employee_count: Mapped[int | None] = mapped_column(Integer)
    current_assets: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    management_expense: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    government_subsidy_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    source_column_group: Mapped[str | None] = mapped_column(String(50))
    entity: Mapped[BusinessEntity] = relationship(back_populates="revenues")


class MainIndustry(Base, TimestampMixin):
    __tablename__ = "main_industries"
    id: Mapped[int] = mapped_column(primary_key=True)
    business_entity_id: Mapped[int] = mapped_column(ForeignKey("business_entities.id", ondelete="CASCADE"), index=True)
    industry_name: Mapped[str] = mapped_column(String(300))
    three_year_total_income: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    operation_years: Mapped[int | None] = mapped_column(Integer)
    source_column_group: Mapped[str | None] = mapped_column(String(50))
    entity: Mapped[BusinessEntity] = relationship(back_populates="industries")


class CultivationRecord(Base, TimestampMixin):
    __tablename__ = "cultivation_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    cultivation_year: Mapped[int | None] = mapped_column(Integer)
    cultivation_needs: Mapped[str | None] = mapped_column(Text)
    training_experience: Mapped[str | None] = mapped_column(Text)
    student: Mapped[Student] = relationship(back_populates="cultivations")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)


class ImportBatch(Base):
    __tablename__ = "import_batches"
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(300))
    stored_file_path: Mapped[str] = mapped_column(Text)
    file_hash: Mapped[str] = mapped_column(String(64), index=True)
    sheet_name: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="preview")
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    new_rows: Mapped[int] = mapped_column(Integer, default=0)
    updated_rows: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    errors: Mapped[list[ImportError]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class ImportError(Base):
    __tablename__ = "import_errors"
    id: Mapped[int] = mapped_column(primary_key=True)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id", ondelete="CASCADE"), index=True)
    excel_row_number: Mapped[int] = mapped_column(Integer)
    column_name: Mapped[str | None] = mapped_column(String(200))
    field_name: Mapped[str | None] = mapped_column(String(100))
    raw_value: Mapped[str | None] = mapped_column(Text)
    error_type: Mapped[str] = mapped_column(String(100))
    error_message: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="error")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    batch: Mapped[ImportBatch] = relationship(back_populates="errors")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    target_table: Mapped[str | None] = mapped_column(String(100))
    target_id: Mapped[int | None] = mapped_column(Integer)
    before_data: Mapped[str | None] = mapped_column(Text)
    after_data: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(100))
    user_agent: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class BackupRecord(Base):
    __tablename__ = "backup_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    backup_file_path: Mapped[str] = mapped_column(Text)
    database_type: Mapped[str] = mapped_column(String(50), default="sqlite")
    backup_type: Mapped[str] = mapped_column(String(50), default="manual")
    status: Mapped[str] = mapped_column(String(30), default="success")
    file_size: Mapped[int] = mapped_column(Integer)
    file_hash: Mapped[str] = mapped_column(String(64))
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
