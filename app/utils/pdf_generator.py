# backend/app/utils/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any
import io


class FeasibilityReportGenerator:
    """Generate PDF reports for business feasibility calculations"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5282'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_LEFT
        ))

        # Warning style
        self.styles.add(ParagraphStyle(
            name='WarningText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#c53030'),
            alignment=TA_LEFT,
            leftIndent=10
        ))

    def generate_report(self,
                        project_data: Dict[str, Any],
                        calculation_results: Dict[str, Any],
                        output_path: str = None) -> bytes:
        """
        Generate a complete feasibility report PDF

        Args:
            project_data: Project information (name, industry, etc.)
            calculation_results: Calculation results from FeasibilityCalculator
            output_path: Optional file path to save PDF

        Returns:
            PDF content as bytes
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm
        )

        # Build PDF content
        elements = []

        # Header
        elements.extend(self._create_header(project_data))
        elements.append(Spacer(1, 12))

        # Executive Summary
        elements.extend(self._create_summary(calculation_results))
        elements.append(Spacer(1, 20))

        # Financial Details
        elements.extend(self._create_financial_details(calculation_results))
        elements.append(Spacer(1, 20))

        # Break-even Analysis
        elements.extend(self._create_breakeven_section(calculation_results))
        elements.append(Spacer(1, 20))

        # Risk Analysis
        elements.extend(self._create_risk_section(calculation_results))
        elements.append(Spacer(1, 20))

        # Daily Targets
        elements.extend(self._create_targets_section(calculation_results))
        elements.append(Spacer(1, 20))

        # Footer/Disclaimer
        elements.extend(self._create_footer())

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Optionally save to file
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def _create_header(self, project_data: Dict[str, Any]) -> list:
        """Create report header"""
        elements = []

        # Title
        title = Paragraph(
            "İŞ FİZİBİLİTE RAPORU",
            self.styles['CustomTitle']
        )
        elements.append(title)

        # Project name
        project_name = project_data.get('name', 'Proje Adı Belirtilmemiş')
        elements.append(Paragraph(
            f"<b>Proje:</b> {project_name}",
            self.styles['InfoText']
        ))

        # Industry & Location
        if project_data.get('industry'):
            elements.append(Paragraph(
                f"<b>Sektör:</b> {project_data['industry']}",
                self.styles['InfoText']
            ))

        if project_data.get('location'):
            elements.append(Paragraph(
                f"<b>Lokasyon:</b> {project_data['location']}",
                self.styles['InfoText']
            ))

        # Report date
        report_date = datetime.now().strftime("%d.%m.%Y")
        elements.append(Paragraph(
            f"<b>Rapor Tarihi:</b> {report_date}",
            self.styles['InfoText']
        ))

        return elements

    def _create_summary(self, results: Dict[str, Any]) -> list:
        """Create executive summary"""
        elements = []

        elements.append(Paragraph("ÖZE", self.styles['CustomSubtitle']))

        # Summary table
        data = [
            ['Metrik', 'Değer'],
            ['Aylık Gelir', f"₺{results['monthly_revenue']:,.2f}"],
            ['Aylık Net Kar', f"₺{results['monthly_net_profit']:,.2f}"],
            ['Brüt Kar Marjı', f"%{results['gross_margin']:.1f}"],
            ['Net Kar Marjı', f"%{results['net_margin']:.1f}"],
            ['Başa-Baş Süresi', f"{results['breakeven']['breakeven_months']} ay"],
        ]

        table = Table(data, colWidths=[80 * mm, 80 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))

        elements.append(table)

        return elements

    def _create_financial_details(self, results: Dict[str, Any]) -> list:
        """Create financial details section"""
        elements = []

        elements.append(Paragraph("FİNANSAL DETAYLAR", self.styles['CustomSubtitle']))

        data = [
            ['Kalem', 'Aylık Tutar'],
            ['Gelir', f"₺{results['monthly_revenue']:,.2f}"],
            ['Değişken Maliyet', f"₺{results['monthly_variable_cost']:,.2f}"],
            ['Sabit Maliyet', f"₺{results['monthly_fixed_cost']:,.2f}"],
            ['NET KAR', f"₺{results['monthly_net_profit']:,.2f}"],
        ]

        table = Table(data, colWidths=[80 * mm, 80 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#bee3f8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        return elements

    def _create_breakeven_section(self, results: Dict[str, Any]) -> list:
        """Create break-even analysis section"""
        elements = []

        elements.append(Paragraph("BAŞA-BAŞ ANALİZİ", self.styles['CustomSubtitle']))

        breakeven = results['breakeven']

        data = [
            ['Metrik', 'Değer'],
            ['Başa-Baş Süresi', f"{breakeven['breakeven_months']} ay"],
            ['Başa-Baş Geliri', f"₺{breakeven['breakeven_revenue']:,.2f}"],
            ['Mevcut Gelir', f"₺{breakeven['current_revenue']:,.2f}"],
            ['Gelir Açığı', f"₺{breakeven['revenue_gap']:,.2f}"],
            ['Gerekli Artış', f"%{breakeven['required_increase']:.1f}"],
        ]

        table = Table(data, colWidths=[80 * mm, 80 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))

        elements.append(table)

        return elements

    def _create_risk_section(self, results: Dict[str, Any]) -> list:
        """Create risk analysis section"""
        elements = []

        if 'risk_analysis' not in results:
            return elements

        elements.append(Paragraph("RİSK ANALİZİ", self.styles['CustomSubtitle']))

        risk = results['risk_analysis']

        # Risk level with color
        risk_level = risk['risk_level'].upper()
        risk_color = {
            'LOW': colors.green,
            'MEDIUM': colors.orange,
            'HIGH': colors.red
        }.get(risk_level, colors.gray)

        risk_text = {
            'LOW': 'DÜŞÜK',
            'MEDIUM': 'ORTA',
            'HIGH': 'YÜKSEK'
        }.get(risk_level, risk_level)

        data = [
            ['Risk Seviyesi', f"{risk_text} ({risk['risk_score']}/100)"],
            ['Acil Durum Fonu', f"{risk['emergency_fund_months']:.1f} ay"],
        ]

        table = Table(data, colWidths=[80 * mm, 80 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('BACKGROUND', (1, 0), (1, 0), risk_color),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

        # Warnings
        if risk.get('warnings'):
            elements.append(Paragraph("<b>Uyarılar:</b>", self.styles['InfoText']))
            for warning in risk['warnings']:
                warning_symbol = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(warning['type'], '⚠️')

                elements.append(Paragraph(
                    f"{warning_symbol} {warning['message']}",
                    self.styles['WarningText']
                ))

        return elements

    def _create_targets_section(self, results: Dict[str, Any]) -> list:
        """Create daily targets section"""
        elements = []

        elements.append(Paragraph("GÜNLÜK SATIŞ HEDEFLERİ", self.styles['CustomSubtitle']))

        data = [['Ürün', 'Mevcut', 'Hedef', 'Artış']]

        for target in results['daily_targets']:
            data.append([
                target['product_name'],
                f"{target['current_daily']} adet",
                f"{target['target_daily']} adet",
                f"+{target['increase_needed']} (%{target['increase_percentage']:.1f})"
            ])

        table = Table(data, colWidths=[60 * mm, 33 * mm, 33 * mm, 34 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        return elements

    def _create_footer(self) -> list:
        """Create report footer/disclaimer"""
        elements = []

        elements.append(Spacer(1, 30))

        disclaimer = """
        <b>UYARI:</b> Bu rapor yalnızca bilgilendirme amaçlıdır ve yatırım tavsiyesi 
        niteliğinde değildir. Gerçek sonuçlar piyasa koşullarına, rekabete ve diğer 
        faktörlere bağlı olarak değişebilir. Herhangi bir iş kararı almadan önce 
        profesyonel danışmanlık almanız önerilir.
        """

        elements.append(Paragraph(disclaimer, self.styles['InfoText']))

        return elements