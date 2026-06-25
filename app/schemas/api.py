from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StudentUpdate(BaseModel):
    id_card_number: str | None = None
    name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    ethnicity: str | None = None
    native_place: str | None = None
    district_county: str | None = None
    phone: str | None = None
    political_status: str | None = None
    health_status: str | None = None
    professional_title: str | None = None
    wechat: str | None = None
    email: str | None = None
    household_type: str | None = None
    postal_code: str | None = None
    home_address: str | None = None
    talent_category: str | None = None
    status: str | None = None
    administrative_position: str | None = None
    social_part_time_positions: str | None = None


class HonorCreate(BaseModel):
    honor_number: str | None = None
    honor_time: date | None = None
    honor_level: str | None = None
    honor_description: str = Field(min_length=1)


class EducationUpdate(BaseModel):
    education_level: str | None = None
    graduate_school: str | None = None
    major: str | None = None
    certificate_number: str | None = None
    learning_experience: str | None = None
    work_experience: str | None = None
    training_experience: str | None = None


class EntityUpdate(BaseModel):
    entity_name: str | None = None
    entity_intro: str | None = None
    entity_type: str | None = None
    entity_subtype: str | None = None
    entity_industry_type: str | None = None
    established_date: date | None = None
    registered_address: str | None = None
    unified_social_credit_code: str | None = None
    industry_years: int | None = None
    student_position_in_entity: str | None = None
    patent_applications: str | None = None
    farmer_households_driven: int | None = None
    technical_partner_count: int | None = None
    technical_partners: str | None = None
    quality_inspection_org: str | None = None
    quality_system_certification: str | None = None
    green_organic_geo_certification: str | None = None
    entity_honors: str | None = None
    supporting_policies: str | None = None


class RevenueCreate(BaseModel):
    year: int = Field(ge=1900, le=2100)
    operating_revenue: float | None = None
    net_profit: float | None = None
    fixed_asset_net_value: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None
    employee_count: int | None = None
    current_assets: float | None = None
    management_expense: float | None = None
    government_subsidy_amount: float | None = None


class IndustryCreate(BaseModel):
    industry_name: str = Field(min_length=1)
    three_year_total_income: float | None = None
    operation_years: int | None = Field(default=None, ge=0)


class CultivationCreate(BaseModel):
    cultivation_year: int | None = Field(default=None, ge=1900, le=2100)
    cultivation_needs: str | None = None
    training_experience: str | None = None


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
