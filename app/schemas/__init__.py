# backend/app/schemas/__init__.py

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    Token,
    TokenData
)

from app.schemas.project import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithProducts,
    CalculationParams
)

from app.schemas.calculation import (
    BreakEvenAnalysis,
    DailyTarget,
    RiskWarning,
    RiskAnalysis,
    CalculationResult,
    CalculationCreate,
    CalculationResponse,
    CalculationListResponse
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",

    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",

    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectWithProducts",
    "CalculationParams",

    # Calculation schemas
    "BreakEvenAnalysis",
    "DailyTarget",
    "RiskWarning",
    "RiskAnalysis",
    "CalculationResult",
    "CalculationCreate",
    "CalculationResponse",
    "CalculationListResponse"
]