"""
PDF Generator Module
レイアウト図と発電量シミュレーション結果のPDF生成
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, blue, green
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
from typing import Dict, List

class PDFGenerator:
    def __init__(self):
        """PDF生成クラス"""
        self.page_width, self.page_height = A4
        
    def generate(self, polygon: List[List[float]], panels: List[Dict],
                power_data: Dict, map_image_base64: str, 
                location: Dict, panel_specs: Dict) -> BytesIO:
        """
        PDFを生成
        
        Args:
            polygon: 屋根の多角形座標
            panels: パネル配置情報
            power_data: 発電量データ
            map_image_base64: Google Mapsの画像（Base64）
            location: 設置場所情報
            panel_specs: パネル仕様
            
        Returns:
            PDF BytesIOバッファ
        """
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # ページ1: レイアウト図
        self._create_layout_page(pdf, map_image_base64, panels, polygon, location, panel_specs)
        
        # ページ2: 発電量シミュレーション
        self._create_simulation_page(pdf, power_data, location, panel_specs)
        
        pdf.save()
        buffer.seek(0)
        return buffer
    
    def _create_layout_page(self, pdf: canvas.Canvas, map_image_base64: str, 
                           panels: List[Dict], polygon: List[List[float]], 
                           location: Dict, panel_specs: Dict):
        """レイアウト図ページを作成"""
        # タイトル
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(50, self.page_height - 50, "Solar Panel Layout Plan")
        
        # 日付と場所
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, self.page_height - 80, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        if location.get('address'):
            pdf.drawString(50, self.page_height - 95, f"Location: {location['address']}")
        
        # Google Maps画像を描画
        if map_image_base64:
            try:
                # Base64デコード
                image_data = base64.b64decode(map_image_base64.split(',')[1] if ',' in map_image_base64 else map_image_base64)
                image = Image.open(BytesIO(image_data))
                
                # 画像を一時保存
                temp_image = BytesIO()
                image.save(temp_image, format='PNG')
                temp_image.seek(0)
                
                # PDFに画像を描画
                pdf.drawImage(temp_image, 50, 300, width=500, height=300, preserveAspectRatio=True)
            except Exception as e:
                pdf.drawString(50, 450, f"Map image could not be loaded: {str(e)}")
        
        # パネル配置情報
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, 270, "Panel Configuration")
        
        pdf.setFont("Helvetica", 11)
        info_y = 250
        
        # パネル情報を表示
        panel_info = [
            f"Total Panels: {len(panels)}",
            f"Panel Size: {panel_specs.get('width', 'N/A')}cm x {panel_specs.get('height', 'N/A')}cm",
            f"Offset: {panel_specs.get('offset', 'N/A')}cm",
            f"Total Area: {power_data.get('panel_info', {}).get('total_area_m2', 'N/A')} m²"
        ]
        
        for info in panel_info:
            pdf.drawString(70, info_y, info)
            info_y -= 20
        
        # 凡例
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(350, 270, "Legend")
        
        pdf.setFont("Helvetica", 10)
        # 屋根エリア
        pdf.setFillColor(HexColor('#FF000033'))
        pdf.rect(370, 245, 20, 10, fill=1)
        pdf.setFillColor(black)
        pdf.drawString(400, 248, "Roof Area")
        
        # パネルエリア
        pdf.setFillColor(HexColor('#0000FF33'))
        pdf.rect(370, 225, 20, 10, fill=1)
        pdf.setFillColor(black)
        pdf.drawString(400, 228, "Solar Panels")
        
        pdf.showPage()
    
    def _create_simulation_page(self, pdf: canvas.Canvas, power_data: Dict, 
                               location: Dict, panel_specs: Dict):
        """発電量シミュレーションページを作成"""
        # タイトル
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(50, self.page_height - 50, "Power Generation Simulation")
        
        # 年間発電量
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, self.page_height - 100, "Annual Generation Forecast")
        
        yearly_total = power_data.get('yearly_total_kwh', 0)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.setFillColor(green)
        pdf.drawString(70, self.page_height - 135, f"{yearly_total:,.0f} kWh/year")
        pdf.setFillColor(black)
        
        # システム仕様
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, self.page_height - 180, "System Specifications")
        
        pdf.setFont("Helvetica", 11)
        specs_y = self.page_height - 200
        
        panel_info = power_data.get('panel_info', {})
        specs = [
            f"Number of Panels: {panel_info.get('count', 'N/A')}",
            f"Total Panel Area: {panel_info.get('total_area_m2', 'N/A')} m²",
            f"System Capacity: {panel_info.get('total_rated_power_kw', 'N/A')} kW",
            f"Panel Efficiency: {power_data.get('assumptions', {}).get('panel_efficiency', 'N/A')}",
            f"System Efficiency: {power_data.get('assumptions', {}).get('system_efficiency', 'N/A')}"
        ]
        
        for spec in specs:
            pdf.drawString(70, specs_y, spec)
            specs_y -= 20
        
        # 月別発電量グラフ（簡易的な棒グラフ）
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, self.page_height - 350, "Monthly Generation Forecast")
        
        # グラフエリア
        graph_x = 70
        graph_y = 200
        graph_width = 450
        graph_height = 150
        
        # 軸を描画
        pdf.setStrokeColor(black)
        pdf.line(graph_x, graph_y, graph_x + graph_width, graph_y)  # X軸
        pdf.line(graph_x, graph_y, graph_x, graph_y + graph_height)  # Y軸
        
        # 月別データを描画
        monthly_data = power_data.get('monthly_data', [])
        if monthly_data:
            max_generation = max([m['generation_kwh'] for m in monthly_data])
            bar_width = graph_width / 12
            
            pdf.setFont("Helvetica", 8)
            
            for i, month_data in enumerate(monthly_data):
                month = month_data['month']
                generation = month_data['generation_kwh']
                
                # バーの高さを計算
                bar_height = (generation / max_generation) * graph_height if max_generation > 0 else 0
                
                # バーを描画
                bar_x = graph_x + i * bar_width
                pdf.setFillColor(HexColor('#4CAF50'))
                pdf.rect(bar_x + 5, graph_y, bar_width - 10, bar_height, fill=1)
                
                # 月ラベル
                pdf.setFillColor(black)
                pdf.drawString(bar_x + bar_width/2 - 5, graph_y - 15, str(month))
                
                # 値ラベル
                pdf.drawString(bar_x + bar_width/2 - 15, graph_y + bar_height + 5, f"{generation:.0f}")
        
        # Y軸ラベル
        pdf.setFont("Helvetica", 10)
        pdf.drawString(20, graph_y + graph_height/2, "kWh")
        
        # 設置場所情報
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, 100, f"Location: Lat {location.get('lat', 'N/A')}, Lng {location.get('lng', 'N/A')}")
        
        # 注意事項
        pdf.setFont("Helvetica", 8)
        pdf.drawString(50, 60, "Note: This is a simulation based on average solar irradiance data.")
        pdf.drawString(50, 45, "Actual generation may vary depending on weather conditions and system maintenance.")
        
        pdf.showPage()