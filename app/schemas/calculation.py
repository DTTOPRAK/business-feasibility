# backend/app/schemas/calculation.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class BreakEvenAnalysis(BaseModel):
    """Break-even analysis results"""
    breakeven_revenue: Decimal
    breakeven_months: int
    required_increase: Decimal  # Percentage
    monthly_net_at_breakeven: Decimal
    current_revenue: Decimal
    revenue_gap: Decimal


class DailyTarget(BaseModel):
    """Daily sales target for a product"""
    product_name: str
    current_daily: int
    target_daily: int
    increase_needed: int
    increase_percentage: float


class RiskWarning(BaseModel):
    """Risk warning message"""
    type: str  # critical, high, medium, low
    message: str


class RiskAnalysis(BaseModel):
    """Risk analysis results"""
    risk_score: int  # 0-100
    risk_level: str  # low, medium, high
    warnings: List[RiskWarning]
    emergency_fund_months: float


class CalculationResult(BaseModel):
    """Complete calculation result"""
    # Revenue & Costs
    monthly_revenue: float
    monthly_variable_cost: float
    monthly_fixed_cost: float
    monthly_net_profit: float

    # Margins
    gross_margin: float
    net_margin: float

    # Analysis
    breakeven: Dict[str, Any]
    daily_targets: List[Dict[str, Any]]
    risk_analysis: Optional[Dict[str, Any]] = None

    # Metadata
    disclaimer: Optional[str] = None


class CalculationCreate(BaseModel):
    """Schema for creating/saving a calculation"""
    project_id: int
    initial_investment: Decimal = Field(..., gt=0)
    monthly_fixed_costs: Decimal = Field(..., gt=0)
    emergency_fund: Decimal = Field(0, ge=0)
    notes: Optional[str] = None


class CalculationResponse(BaseModel):
    """Schema for calculation response from database"""
    id: int
    project_id: int

    # Input Parameters
    initial_investment: Decimal
    monthly_fixed_costs: Decimal
    emergency_fund: Decimal

    # Results
    monthly_revenue: Optional[Decimal]
    monthly_variable_cost: Optional[Decimal]
    monthly_net_profit: Optional[Decimal]
    gross_margin: Optional[Decimal]
    net_margin: Optional[Decimal]

    # Break-even
    breakeven_months: Optional[int]
    breakeven_revenue: Optional[Decimal]
    required_sales_increase: Optional[Decimal]

    # Risk
    risk_score: Optional[int]
    risk_level: Optional[str]

    # Full results
    full_results: Optional[Dict[str, Any]]
    notes: Optional[str]

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CalculationListResponse(BaseModel):
    """Schema for list of calculations"""
    calculations: List[CalculationResponse]
    total: int
    page: int
    page_size: int