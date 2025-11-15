# backend/app/core/risk_analyzer.py

from decimal import Decimal
from typing import Dict, List


class RiskAnalyzer:
    """Risk değerlendirme motoru"""

    def __init__(self,
                 calculation_results: Dict,
                 initial_investment: Decimal,
                 emergency_fund: Decimal):
        self.results = calculation_results
        self.initial_investment = initial_investment
        self.emergency_fund = emergency_fund

    def analyze(self) -> Dict:
        """Tüm risk analizi"""
        risk_score = 0
        warnings = []
        level = "low"

        # 1. Başa-baş süresi kontrolü
        breakeven_months = self.results["breakeven"]["breakeven_months"]

        if breakeven_months > 24:
            risk_score += 40
            warnings.append({
                "type": "critical",
                "message": f"Yatırım geri dönüş süresi çok uzun: {breakeven_months} ay"
            })
        elif breakeven_months > 18:
            risk_score += 30
            warnings.append({
                "type": "high",
                "message": f"Yatırım geri dönüş süresi yüksek: {breakeven_months} ay"
            })
        elif breakeven_months > 12:
            risk_score += 15
            warnings.append({
                "type": "medium",
                "message": f"Yatırım geri dönüş süresi: {breakeven_months} ay"
            })

        # 2. Satış artış gereksinimi
        required_increase = self.results["breakeven"]["required_increase"]

        if required_increase > 100:
            risk_score += 40
            warnings.append({
                "type": "critical",
                "message": f"Satışları %{required_increase:.0f} artırmanız gerekiyor - çok yüksek!"
            })
        elif required_increase > 50:
            risk_score += 25
            warnings.append({
                "type": "high",
                "message": f"Satışları %{required_increase:.0f} artırmanız gerekiyor"
            })
        elif required_increase > 25:
            risk_score += 10
            warnings.append({
                "type": "medium",
                "message": f"Satışları %{required_increase:.0f} artırmanız hedefleniyor"
            })

        # 3. Kar marjı kontrolü
        gross_margin = self.results["gross_margin"]

        if gross_margin < 30:
            risk_score += 25
            warnings.append({
                "type": "high",
                "message": f"Brüt kar marjı düşük: %{gross_margin:.1f}"
            })
        elif gross_margin < 40:
            risk_score += 10
            warnings.append({
                "type": "medium",
                "message": f"Brüt kar marjı iyileştirilebilir: %{gross_margin:.1f}"
            })

        # 4. Acil durum fonu
        monthly_fixed = Decimal(str(self.results["monthly_fixed_cost"]))
        emergency_months = float(self.emergency_fund / monthly_fixed) if monthly_fixed > 0 else 0

        if emergency_months < 3:
            risk_score += 15
            warnings.append({
                "type": "high",
                "message": f"Acil durum fonu yetersiz: {emergency_months:.1f} ay (önerilen: 3 ay)"
            })

        # 5. Günlük hedef gerçekçiliği
        for target in self.results["daily_targets"]:
            if target["increase_percentage"] > 80:
                risk_score += 10
                warnings.append({
                    "type": "medium",
                    "message": f"{target['product_name']}: Günde {target['target_daily']} adet satış hedefi zorlayıcı"
                })

        # Risk seviyesi belirleme
        if risk_score >= 80:
            level = "high"
        elif risk_score >= 50:
            level = "medium"
        else:
            level = "low"

        return {
            "risk_score": min(risk_score, 100),  # Max 100
            "risk_level": level,
            "warnings": warnings,
            "emergency_fund_months": round(emergency_months, 1)
        }