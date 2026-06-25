from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StudentUpdate(BaseModel):
    birth_date: date | None = None
    phone: str | None = None
    political_status: str | None = None
    professional_title: str | None = None
    household_type: str | None = None
    talent_category: str | None = None
    administrative_position: str | None = None
    social_part_time_positions: str | None = None


class HonorCreate(BaseModel):
    honor_number: str | None = None
    honor_time: date | None = None
    honor_level: str | None = None
    honor_description: str = Field(min_length=1)


class EntityUpdate(BaseModel):
    entity_name: str | None = None
    entity_intro: str | None = None
    entity_type: str | None = None
    entity_subtype: str | None = None
    established_date: date | None = None
    registered_address: str | None = None
    unified_social_credit_code: str | None = None
    student_position_in_entity: str | None = None


class RevenueCreate(BaseModel):
    year: int = Field(ge=1900, le=2100)
    operating_revenue: float | None = None
    net_profit: float | None = None


class IndustryCreate(BaseModel):
    industry_name: str = Field(min_length=1)
    three_year_total_income: float | None = None
    operation_years: int | None = Field(default=None, ge=0)


class ApiResponse(BaseModel):
    data: Any = None
    message: str = "success"


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=10)


class StudentBulkDelete(BaseModel):
    student_ids: list[int] = Field(min_length=1, max_length=100)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
