# backend/app/models/calculation.py

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Calculation(Base):
    """Saved calculation results for business feasibility"""

    __tablename__ = "calculations"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    project_id = Column(Integer, ForeignKey("business_projects.id", ondelete="CASCADE"), nullable=False)

    # Input Parameters
    initial_investment = Column(Numeric(12, 2), nullable=False)
    monthly_fixed_costs = Column(Numeric(10, 2), nullable=False)
    emergency_fund = Column(Numeric(10, 2), default=0)

    # Calculated Results
    monthly_revenue = Column(Numeric(12, 2))
    monthly_variable_cost = Column(Numeric(12, 2))
    monthly_net_profit = Column(Numeric(12, 2))
    gross_margin = Column(Numeric(5, 2))  # Percentage
    net_margin = Column(Numeric(5, 2))  # Percentage

    # Break-even Analysis
    breakeven_months = Column(Integer)
    breakeven_revenue = Column(Numeric(12, 2))
    required_sales_increase = Column(Numeric(5, 2))  # Percentage

    # Risk Analysis
    risk_score = Column(Integer)
    risk_level = Column(String(20))  # low, medium, high

    # Full Results (JSON)
    full_results = Column(JSON, nullable=True)  # Complete calculation results
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("BusinessProject", back_populates="calculations")

    def __repr__(self):
        return f"<Calculation(id={self.id}, project_id={self.project_id}, created_at={self.created_at})>"