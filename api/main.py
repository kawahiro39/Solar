"""
Solar Panel Layout Simulation API
Cloud Run backend for solar panel placement and power generation simulation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
import base64
from io import BytesIO

from panel_layout import PanelLayout
from solar_calc import SolarCalculator
from pdf_generator import PDFGenerator

app = Flask(__name__)
CORS(app, origins='*')  # Bubble HTML埋め込みのためCORS許可

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック用エンドポイント"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/calculate-panels', methods=['POST'])
def calculate_panels():
    """
    屋根の多角形内にパネルを配置し、配置情報を返す
    
    Request body:
    {
        "polygon": [[lat, lng], ...],  # 屋根の多角形座標
        "panel_width": float,           # パネル幅 (cm)
        "panel_height": float,          # パネル高さ (cm)
        "offset": float,                # オフセット/離隔 (cm)
        "location": {
            "lat": float,
            "lng": float,
            "address": string
        }
    }
    """
    try:
        data = request.json
        
        # パラメータ取得
        polygon = data.get('polygon', [])
        panel_width = data.get('panel_width', 165)  # デフォルト165cm
        panel_height = data.get('panel_height', 100)  # デフォルト100cm
        offset = data.get('offset', 10)  # デフォルト10cm
        location = data.get('location', {})
        
        if not polygon or len(polygon) < 3:
            return jsonify({"error": "Invalid polygon. At least 3 points required."}), 400
        
        # パネルレイアウト計算
        layout = PanelLayout(panel_width, panel_height, offset)
        panels = layout.calculate_layout(polygon)
        
        # 発電量計算
        solar_calc = SolarCalculator()
        power_data = solar_calc.calculate_power(
            location.get('lat', 35.6762),  # デフォルト東京
            location.get('lng', 139.6503),
            len(panels),
            panel_width * panel_height / 10000  # cm² to m²
        )
        
        response = {
            "panels": panels,
            "panel_count": len(panels),
            "total_area": len(panels) * (panel_width * panel_height / 10000),
            "power_estimation": power_data,
            "layout_bounds": layout.get_bounds(polygon)
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    レイアウト図と発電量シミュレーション結果のPDFを生成
    
    Request body:
    {
        "polygon": [[lat, lng], ...],
        "panels": [...],
        "power_data": {...},
        "map_image": "base64_encoded_image",
        "location": {...},
        "panel_specs": {...}
    }
    """
    try:
        data = request.json
        
        # PDFGenerator instance
        pdf_gen = PDFGenerator()
        
        # Generate PDF
        pdf_buffer = pdf_gen.generate(
            polygon=data.get('polygon', []),
            panels=data.get('panels', []),
            power_data=data.get('power_data', {}),
            map_image_base64=data.get('map_image', ''),
            location=data.get('location', {}),
            panel_specs=data.get('panel_specs', {})
        )
        
        # Return PDF as download
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'solar_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-solar-data', methods=['POST'])
def get_solar_data():
    """
    指定地点の日射量データを取得
    
    Request body:
    {
        "lat": float,
        "lng": float
    }
    """
    try:
        data = request.json
        lat = data.get('lat')
        lng = data.get('lng')
        
        if lat is None or lng is None:
            return jsonify({"error": "Latitude and longitude required"}), 400
        
        solar_calc = SolarCalculator()
        solar_data = solar_calc.get_irradiance_data(lat, lng)
        
        return jsonify(solar_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)