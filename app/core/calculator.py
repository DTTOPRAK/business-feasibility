# backend/app/core/calculator.py

from decimal import Decimal
from typing import Dict, List
from app.models.product import Product


class FeasibilityCalculator:
    """İş fizibilitesi hesaplama motoru"""

    def __init__(self,
                 initial_investment: Decimal,
                 monthly_fixed_costs: Decimal,
                 products: List[Product]):
        self.initial_investment = initial_investment
        self.monthly_fixed_costs = monthly_fixed_costs
        self.products = products

    def calculate_monthly_revenue(self) -> Decimal:
        """Aylık toplam gelir hesapla"""
        total_revenue = Decimal(0)

        for product in self.products:
            daily_revenue = product.selling_price * product.daily_volume
            monthly_revenue = daily_revenue * product.working_days_per_month
            total_revenue += monthly_revenue

        return total_revenue

    def calculate_monthly_variable_costs(self) -> Decimal:
        """Aylık değişken maliyet hesapla"""
        total_cost = Decimal(0)

        for product in self.products:
            daily_cost = product.cost_per_unit * product.daily_volume
            monthly_cost = daily_cost * product.working_days_per_month
            total_cost += monthly_cost

        return total_cost

    def calculate_gross_margin(self) -> Decimal:
        """Brüt kar marjı hesapla"""
        revenue = self.calculate_monthly_revenue()
        variable_costs = self.calculate_monthly_variable_costs()

        if revenue == 0:
            return Decimal(0)

        gross_profit = revenue - variable_costs
        margin = (gross_profit / revenue) * 100

        return round(margin, 2)

    def calculate_net_profit(self) -> Decimal:
        """Aylık net kar hesapla"""
        revenue = self.calculate_monthly_revenue()
        variable_costs = self.calculate_monthly_variable_costs()
        fixed_costs = self.monthly_fixed_costs

        net_profit = revenue - variable_costs - fixed_costs

        return round(net_profit, 2)

    def calculate_breakeven(self) -> Dict:
        """Başa-baş analizi"""
        revenue = self.calculate_monthly_revenue()
        variable_costs = self.calculate_monthly_variable_costs()
        fixed_costs = self.monthly_fixed_costs

        # Contribution margin ratio
        if revenue == 0:
            return {
                "breakeven_revenue": 0,
                "breakeven_months": 999,
                "required_increase": 100
            }

        contribution_margin_ratio = (revenue - variable_costs) / revenue

        # Başa-baş geliri
        breakeven_revenue = fixed_costs / contribution_margin_ratio

        # Gerekli artış
        required_increase = ((breakeven_revenue - revenue) / revenue) * 100

        # Başa-baş ayı (yatırımı da geri ödemek için)
        monthly_net_profit = revenue - variable_costs - fixed_costs

        if monthly_net_profit > 0:
            breakeven_months = int(self.initial_investment / monthly_net_profit)
        else:
            breakeven_months = 999  # Sonsuz (zarar ediyor)

        return {
            "breakeven_revenue": round(breakeven_revenue, 2),
            "breakeven_months": breakeven_months,
            "required_increase": round(required_increase, 2),
            "monthly_net_at_breakeven": 0,
            "current_revenue": round(revenue, 2),
            "revenue_gap": round(breakeven_revenue - revenue, 2)
        }

    def calculate_daily_targets(self) -> List[Dict]:
        """Her ürün için günlük başa-baş hedefleri"""
        breakeven_info = self.calculate_breakeven()
        required_increase = breakeven_info["required_increase"] / 100

        targets = []

        for product in self.products:
            current_daily = product.daily_volume
            target_daily = int(current_daily * (1 + required_increase))
            increase_needed = target_daily - current_daily
            increase_pct = required_increase * 100

            targets.append({
                "product_name": product.name,
                "current_daily": current_daily,
                "target_daily": target_daily,
                "increase_needed": increase_needed,
                "increase_percentage": round(increase_pct, 1)
            })

        return targets

    def calculate_all(self) -> Dict:
        """Tüm hesaplamaları yap"""
        revenue = self.calculate_monthly_revenue()
        variable_costs = self.calculate_monthly_variable_costs()
        gross_margin = self.calculate_gross_margin()
        net_profit = self.calculate_net_profit()
        breakeven = self.calculate_breakeven()
        daily_targets = self.calculate_daily_targets()

        return {
            "monthly_revenue": float(revenue),
            "monthly_variable_cost": float(variable_costs),
            "monthly_fixed_cost": float(self.monthly_fixed_costs),
            "monthly_net_profit": float(net_profit),
            "gross_margin": float(gross_margin),
            "net_margin": float((net_profit / revenue * 100) if revenue > 0 else 0),
            "breakeven": breakeven,
            "daily_targets": daily_targets
        }