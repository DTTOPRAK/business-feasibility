# backend/app/api/calculations.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
import io

from app.db.database import get_db
from app.models.user import User
from app.models.project import BusinessProject
from app.models.product import Product
from app.models.calculation import Calculation
from app.schemas.calculation import (
    CalculationCreate,
    CalculationResponse,
    CalculationListResponse
)
from app.core.calculator import FeasibilityCalculator
from app.core.risk_analyzer import RiskAnalyzer
from app.utils.pdf_generator import FeasibilityReportGenerator
from app.api.auth import get_current_user

router = APIRouter()


# ============================================
# Calculation Endpoints
# ============================================

@router.post("/{project_id}/calculate")
def calculate_project_feasibility(
        project_id: int,
        params: CalculationCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Calculate feasibility for a project

    - **project_id**: ID of the project to calculate
    - **initial_investment**: Total initial investment
    - **monthly_fixed_costs**: Monthly fixed costs
    - **emergency_fund**: Emergency fund (optional)

    Returns complete feasibility analysis with risk assessment
    """
    # Get project and verify ownership
    project = db.query(BusinessProject).filter(
        BusinessProject.id == project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have access"
        )

    # Get products for this project
    products = db.query(Product).filter(Product.project_id == project_id).all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project must have at least one product to calculate feasibility"
        )

    # Run calculation
    calculator = FeasibilityCalculator(
        initial_investment=params.initial_investment,
        monthly_fixed_costs=params.monthly_fixed_costs,
        products=products
    )

    results = calculator.calculate_all()

    # Run risk analysis
    risk_analyzer = RiskAnalyzer(
        calculation_results=results,
        initial_investment=params.initial_investment,
        emergency_fund=params.emergency_fund
    )

    risk_analysis = risk_analyzer.analyze()

    # Combine results
    final_results = {
        **results,
        "risk_analysis": risk_analysis,
        "disclaimer": "Bu hesaplama bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir."
    }

    # Convert all Decimal values to float for JSON serialization
    def convert_decimals(obj):
        """Recursively convert Decimal to float in dictionaries and lists"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_decimals(item) for item in obj]
        return obj

    # Convert the full results for JSON storage
    full_results_json = convert_decimals(final_results)

    # Save to database
    calculation = Calculation(
        project_id=project_id,
        initial_investment=params.initial_investment,
        monthly_fixed_costs=params.monthly_fixed_costs,
        emergency_fund=params.emergency_fund,
        monthly_revenue=Decimal(str(results['monthly_revenue'])),
        monthly_variable_cost=Decimal(str(results['monthly_variable_cost'])),
        monthly_net_profit=Decimal(str(results['monthly_net_profit'])),
        gross_margin=Decimal(str(results['gross_margin'])),
        net_margin=Decimal(str(results['net_margin'])),
        breakeven_months=results['breakeven']['breakeven_months'],
        breakeven_revenue=Decimal(str(results['breakeven']['breakeven_revenue'])),
        required_sales_increase=Decimal(str(results['breakeven']['required_increase'])),
        risk_score=risk_analysis['risk_score'],
        risk_level=risk_analysis['risk_level'],
        full_results=full_results_json,  # Use the converted version
        notes=params.notes
    )

    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    return final_results


@router.get("/{project_id}/history", response_model=CalculationListResponse)
def get_calculation_history(
        project_id: int,
        skip: int = 0,
        limit: int = 10,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get calculation history for a project

    Returns a paginated list of all calculations for this project
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

    # Get calculations
    calculations = db.query(Calculation).filter(
        Calculation.project_id == project_id
    ).order_by(
        Calculation.created_at.desc()
    ).offset(skip).limit(limit).all()

    # Get total count
    total = db.query(Calculation).filter(
        Calculation.project_id == project_id
    ).count()

    return {
        "calculations": calculations,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/detail/{calculation_id}", response_model=CalculationResponse)
def get_calculation_detail(
        calculation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Get detailed calculation by ID

    Returns complete calculation results including full JSON data
    """
    # Get calculation
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id
    ).first()

    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )

    # Verify ownership through project
    project = db.query(BusinessProject).filter(
        BusinessProject.id == calculation.project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this calculation"
        )

    return calculation


@router.delete("/{calculation_id}")
def delete_calculation(
        calculation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Delete a calculation

    Permanently removes a calculation record
    """
    # Get calculation
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id
    ).first()

    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )

    # Verify ownership
    project = db.query(BusinessProject).filter(
        BusinessProject.id == calculation.project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this calculation"
        )

    # Delete
    db.delete(calculation)
    db.commit()

    return {"message": "Calculation deleted successfully"}


@router.get("/{calculation_id}/export/pdf")
def export_calculation_pdf(
        calculation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Export calculation as PDF report

    Returns a downloadable PDF file with complete feasibility analysis
    """
    # Get calculation
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id
    ).first()

    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )

    # Get project
    project = db.query(BusinessProject).filter(
        BusinessProject.id == calculation.project_id,
        BusinessProject.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this calculation"
        )

    # Prepare project data
    project_data = {
        "name": project.name,
        "industry": project.industry,
        "location": project.location,
        "description": project.description
    }

    # Get full calculation results
    calculation_results = calculation.full_results

    # Generate PDF
    pdf_generator = FeasibilityReportGenerator()
    pdf_bytes = pdf_generator.generate_report(
        project_data=project_data,
        calculation_results=calculation_results
    )

    # Return as downloadable file
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=fizibilite_rapor_{project.name}_{calculation.id}.pdf"
        }
    )