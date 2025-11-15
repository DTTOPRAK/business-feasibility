# backend/app/api/projects.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.models.project import BusinessProject
from app.models.product import Product
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithProducts,
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from app.api.auth import get_current_user

router = APIRouter()


# ============================================
# Project Endpoints
# ============================================

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
        project: ProjectCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Create a new business project

    - **name**: Project name (required)
    - **industry**: Industry type (e.g., "Cafe", "Restaurant")
    - **location**: Business location
    - **description**: Project description
    """
    db_project = BusinessProject(
        user_id=current_user.id,
        name=project.name,
        industry=project.industry,
        location=project.location,
        description=project.description,
        status="draft"
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.get("/", response_model=List[ProjectResponse])
def get_user_projects(
        skip: int = 0,
        limit: int = 20,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get all projects for the current user

    Returns a paginated list of user's projects
    """
    projects = db.query(BusinessProject).filter(
        BusinessProject.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return projects


@router.get("/{project_id}", response_model=ProjectWithProducts)
def get_project_detail(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get detailed project information including products

    Returns project with all associated products
    """
    project = db.query(BusinessProject).filter(
        BusinessProject.id == project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
        project_id: int,
        project_update: ProjectUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Update project information

    Updates only the fields that are provided
    """
    project = db.query(BusinessProject).filter(
        BusinessProject.id == project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )

    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Delete a project

    Permanently deletes the project and all associated products and calculations
    """
    project = db.query(BusinessProject).filter(
        BusinessProject.id == project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )

    db.delete(project)
    db.commit()

    return None


# ============================================
# Product Endpoints
# ============================================

@router.post("/{project_id}/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
        project_id: int,
        product: ProductCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Add a product/service to a project

    - **name**: Product name
    - **cost_per_unit**: Cost per unit
    - **selling_price**: Selling price per unit
    - **daily_volume**: Expected daily sales volume
    - **working_days_per_month**: Working days per month (default: 26)
    """
    # Verify project ownership
    project = db.query(BusinessProject).filter(
        BusinessProject.id == project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )

    # Create product
    db_product = Product(
        project_id=project_id,
        name=product.name,
        description=product.description,
        cost_per_unit=product.cost_per_unit,
        selling_price=product.selling_price,
        daily_volume=product.daily_volume,
        working_days_per_month=product.working_days_per_month
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get("/{project_id}/products", response_model=List[ProductResponse])
def get_project_products(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get all products for a project

    Returns list of all products/services in the project
    """
    # Verify project ownership
    project = db.query(BusinessProject).filter(
        BusinessProject.id == project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )

    products = db.query(Product).filter(Product.project_id == project_id).all()

    return products


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
        product_id: int,
        product_update: ProductUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Update product information

    Updates only the fields that are provided
    """
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Verify ownership through project
    project = db.query(BusinessProject).filter(
        BusinessProject.id == product.project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this product"
        )

    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
        product_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Delete a product

    Permanently removes the product from the project
    """
    # Get product
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Verify ownership through project
    project = db.query(BusinessProject).filter(
        BusinessProject.id == product.project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this product"
        )

    db.delete(product)
    db.commit()

    return None