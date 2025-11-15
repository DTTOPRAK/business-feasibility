# backend/app/models/project.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """Project status enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class BusinessProject(Base):
    """Business project/idea model"""

    __tablename__ = "business_projects"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Project Information
    name = Column(String(200), nullable=False)
    industry = Column(String(100), nullable=True)  # e.g., "Cafe", "E-commerce", "SaaS"
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="projects")
    products = relationship("Product", back_populates="project", cascade="all, delete-orphan")
    calculations = relationship("Calculation", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BusinessProject(id={self.id}, name={self.name}, user_id={self.user_id})>"