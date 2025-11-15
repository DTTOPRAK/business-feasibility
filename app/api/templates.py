# backend/app/api/templates.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.models.user import User
from app.models.project import BusinessProject
from app.models.product import Product
from app.schemas.project import ProjectResponse, ProductResponse
from app.api.auth import get_current_user
from decimal import Decimal

router = APIRouter()

# ============================================
# Business Templates Data
# ============================================

BUSINESS_TEMPLATES = {
    "cafe": {
        "name": "Kafe İşletmesi",
        "industry": "Kafe / Restoran",
        "description": "Küçük/orta boy kafe işletmesi şablonu",
        "products": [
            {
                "name": "Türk Kahvesi",
                "description": "Geleneksel Türk kahvesi",
                "cost_per_unit": Decimal("3.50"),
                "selling_price": Decimal("25.00"),
                "daily_volume": 30,
                "working_days_per_month": 26
            },
            {
                "name": "Filtre Kahve",
                "description": "Filtre kahve çeşitleri",
                "cost_per_unit": Decimal("4.00"),
                "selling_price": Decimal("35.00"),
                "daily_volume": 50,
                "working_days_per_month": 26
            },
            {
                "name": "Pasta / Kek",
                "description": "Günlük tatlılar",
                "cost_per_unit": Decimal("10.00"),
                "selling_price": Decimal("45.00"),
                "daily_volume": 20,
                "working_days_per_month": 26
            }
        ],
        "estimated_initial_investment": Decimal("500000.00"),  # 500K TL
        "estimated_monthly_fixed_costs": Decimal("50000.00")  # 50K TL
    },

    "restaurant": {
        "name": "Restoran İşletmesi",
        "industry": "Restoran",
        "description": "Küçük/orta boy restoran şablonu",
        "products": [
            {
                "name": "Ana Yemek",
                "description": "Günlük ana yemek menüsü",
                "cost_per_unit": Decimal("25.00"),
                "selling_price": Decimal("120.00"),
                "daily_volume": 40,
                "working_days_per_month": 26
            },
            {
                "name": "Çorba",
                "description": "Günlük çorba",
                "cost_per_unit": Decimal("8.00"),
                "selling_price": Decimal("45.00"),
                "daily_volume": 35,
                "working_days_per_month": 26
            },
            {
                "name": "İçecek",
                "description": "Meşrubat ve içecekler",
                "cost_per_unit": Decimal("5.00"),
                "selling_price": Decimal("25.00"),
                "daily_volume": 50,
                "working_days_per_month": 26
            }
        ],
        "estimated_initial_investment": Decimal("800000.00"),
        "estimated_monthly_fixed_costs": Decimal("80000.00")
    },

    "bakery": {
        "name": "Fırın İşletmesi",
        "industry": "Fırın / Pastane",
        "description": "Fırın ve pastane işletmesi şablonu",
        "products": [
            {
                "name": "Ekmek",
                "description": "Günlük ekmek üretimi",
                "cost_per_unit": Decimal("2.00"),
                "selling_price": Decimal("10.00"),
                "daily_volume": 200,
                "working_days_per_month": 30
            },
            {
                "name": "Simit",
                "description": "Simit üretimi",
                "cost_per_unit": Decimal("1.50"),
                "selling_price": Decimal("8.00"),
                "daily_volume": 150,
                "working_days_per_month": 30
            },
            {
                "name": "Börek",
                "description": "Çeşitli börekler",
                "cost_per_unit": Decimal("5.00"),
                "selling_price": Decimal("25.00"),
                "daily_volume": 80,
                "working_days_per_month": 30
            }
        ],
        "estimated_initial_investment": Decimal("600000.00"),
        "estimated_monthly_fixed_costs": Decimal("60000.00")
    },

    "ecommerce": {
        "name": "E-Ticaret İşletmesi",
        "industry": "E-Ticaret",
        "description": "Online mağaza şablonu",
        "products": [
            {
                "name": "Ürün Kategori A",
                "description": "Ana ürün kategorisi",
                "cost_per_unit": Decimal("50.00"),
                "selling_price": Decimal("150.00"),
                "daily_volume": 10,
                "working_days_per_month": 30
            },
            {
                "name": "Ürün Kategori B",
                "description": "İkincil ürün kategorisi",
                "cost_per_unit": Decimal("30.00"),
                "selling_price": Decimal("90.00"),
                "daily_volume": 15,
                "working_days_per_month": 30
            },
            {
                "name": "Aksesuar",
                "description": "Ek satış ürünleri",
                "cost_per_unit": Decimal("10.00"),
                "selling_price": Decimal("40.00"),
                "daily_volume": 20,
                "working_days_per_month": 30
            }
        ],
        "estimated_initial_investment": Decimal("300000.00"),
        "estimated_monthly_fixed_costs": Decimal("35000.00")
    },

    "gym": {
        "name": "Spor Salonu",
        "industry": "Spor / Fitness",
        "description": "Küçük/orta boy spor salonu şablonu",
        "products": [
            {
                "name": "Aylık Üyelik",
                "description": "Standart aylık üyelik",
                "cost_per_unit": Decimal("50.00"),
                "selling_price": Decimal("500.00"),
                "daily_volume": 3,
                "working_days_per_month": 26
            },
            {
                "name": "3 Aylık Üyelik",
                "description": "3 aylık paket üyelik",
                "cost_per_unit": Decimal("120.00"),
                "selling_price": Decimal("1200.00"),
                "daily_volume": 2,
                "working_days_per_month": 26
            },
            {
                "name": "Özel Ders",
                "description": "Bireysel antrenörlük",
                "cost_per_unit": Decimal("50.00"),
                "selling_price": Decimal("300.00"),
                "daily_volume": 2,
                "working_days_per_month": 26
            }
        ],
        "estimated_initial_investment": Decimal("1000000.00"),
        "estimated_monthly_fixed_costs": Decimal("100000.00")
    },

    "beauty_salon": {
        "name": "Güzellik Salonu",
        "industry": "Güzellik / Kuaför",
        "description": "Güzellik salonu ve kuaför şablonu",
        "products": [
            {
                "name": "Saç Kesimi",
                "description": "Kadın/erkek saç kesimi",
                "cost_per_unit": Decimal("20.00"),
                "selling_price": Decimal("150.00"),
                "daily_volume": 8,
                "working_days_per_month": 26
            },
            {
                "name": "Boya / Röfle",
                "description": "Saç boyama hizmetleri",
                "cost_per_unit": Decimal("80.00"),
                "selling_price": Decimal("500.00"),
                "daily_volume": 3,
                "working_days_per_month": 26
            },
            {
                "name": "Cilt Bakımı",
                "description": "Yüz bakımı hizmetleri",
                "cost_per_unit": Decimal("50.00"),
                "selling_price": Decimal("400.00"),
                "daily_volume": 2,
                "working_days_per_month": 26
            }
        ],
        "estimated_initial_investment": Decimal("400000.00"),
        "estimated_monthly_fixed_costs": Decimal("45000.00")
    }
}


# ============================================
# Template Endpoints
# ============================================

@router.get("/list")
def list_templates():
    """
    Get list of available business templates

    Returns a list of pre-configured business templates
    with estimated costs and product suggestions
    """
    templates = []

    for template_id, template_data in BUSINESS_TEMPLATES.items():
        templates.append({
            "id": template_id,
            "name": template_data["name"],
            "industry": template_data["industry"],
            "description": template_data["description"],
            "product_count": len(template_data["products"]),
            "estimated_initial_investment": float(template_data["estimated_initial_investment"]),
            "estimated_monthly_fixed_costs": float(template_data["estimated_monthly_fixed_costs"])
        })

    return {"templates": templates}


@router.get("/{template_id}")
def get_template_detail(template_id: str):
    """
    Get detailed information about a specific template

    Returns complete template data including products and estimates
    """
    if template_id not in BUSINESS_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found"
        )

    template = BUSINESS_TEMPLATES[template_id].copy()

    # Convert Decimal to float for JSON serialization
    template["estimated_initial_investment"] = float(template["estimated_initial_investment"])
    template["estimated_monthly_fixed_costs"] = float(template["estimated_monthly_fixed_costs"])

    for product in template["products"]:
        product["cost_per_unit"] = float(product["cost_per_unit"])
        product["selling_price"] = float(product["selling_price"])

    return {
        "template_id": template_id,
        **template
    }


@router.post("/{template_id}/create-project", response_model=ProjectResponse)
def create_project_from_template(
        template_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Create a new project from a template

    Creates a project with pre-filled products and estimates
    based on the selected template
    """
    if template_id not in BUSINESS_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found"
        )

    template = BUSINESS_TEMPLATES[template_id]

    # Create project
    project = BusinessProject(
        user_id=current_user.id,
        name=template["name"],
        industry=template["industry"],
        description=template["description"],
        status="draft"
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # Create products for this project
    for product_data in template["products"]:
        product = Product(
            project_id=project.id,
            name=product_data["name"],
            description=product_data["description"],
            cost_per_unit=product_data["cost_per_unit"],
            selling_price=product_data["selling_price"],
            daily_volume=product_data["daily_volume"],
            working_days_per_month=product_data["working_days_per_month"]
        )
        db.add(product)

    db.commit()
    db.refresh(project)

    return project


@router.get("/industries/list")
def list_industries():
    """
    Get list of available industries

    Returns unique industries from all templates
    """
    industries = set()

    for template in BUSINESS_TEMPLATES.values():
        industries.add(template["industry"])

    return {"industries": sorted(list(industries))}