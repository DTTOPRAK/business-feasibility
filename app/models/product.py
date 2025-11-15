# backend/app/models/product.py

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Product(Base):
    """Product or Service model for business projects"""

    __tablename__ = "products"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    project_id = Column(Integer, ForeignKey("business_projects.id", ondelete="CASCADE"), nullable=False)

    # Product Information
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)

    # Pricing
    cost_per_unit = Column(Numeric(10, 2), nullable=False)  # Birim maliyet
    selling_price = Column(Numeric(10, 2), nullable=False)  # Satış fiyatı

    # Volume/Capacity
    daily_volume = Column(Integer, nullable=False)  # Günlük satış miktarı
    working_days_per_month = Column(Integer, default=26)  # Aylık çalışma günü

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("BusinessProject", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, project_id={self.project_id})>"

    @property
    def unit_profit(self):
        """Calculate profit per unit"""
        return float(self.selling_price - self.cost_per_unit)

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.selling_price == 0:
            return 0
        return (self.unit_profit / float(self.selling_price)) * 100