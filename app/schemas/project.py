# backend/app/schemas/project.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================
# Product Schemas
# ============================================

class ProductBase(BaseModel):
    """Base Product schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    cost_per_unit: Decimal = Field(..., gt=0, decimal_places=2)
    selling_price: Decimal = Field(..., gt=0, decimal_places=2)
    daily_volume: int = Field(..., gt=0)
    working_days_per_month: int = Field(26, ge=1, le=31)


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    cost_per_unit: Optional[Decimal] = Field(None, gt=0)
    selling_price: Optional[Decimal] = Field(None, gt=0)
    daily_volume: Optional[int] = Field(None, gt=0)
    working_days_per_month: Optional[int] = Field(None, ge=1, le=31)


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Project Schemas
# ============================================

class ProjectBase(BaseModel):
    """Base Project schema"""
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    user_id: int


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None  # draft, active, completed, archived


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectWithProducts(ProjectResponse):
    """Schema for project with products"""
    products: List[ProductResponse] = []

    class Config:
        from_attributes = True


# ============================================
# Calculation Parameters
# ============================================

class CalculationParams(BaseModel):
    """Parameters for feasibility calculation"""
    initial_investment: Decimal = Field(..., gt=0, decimal_places=2)
    monthly_fixed_costs: Decimal = Field(..., gt=0, decimal_places=2)
    emergency_fund: Decimal = Field(0, ge=0, decimal_places=2)