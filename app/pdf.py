import base64
import io
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import PanelPlacement, PanelType, ReportRequest
from .simulation import PANEL_TYPES, bounding_box


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm


def _draw_roof_layout(c: canvas.Canvas, request: ReportRequest, placements: List[PanelPlacement], panel: PanelType) -> None:
    points = request.simulation.roof_polygon
    min_x, min_y, max_x, max_y = bounding_box(points)

    scale_x = (PAGE_WIDTH - 2 * MARGIN) / (max_x - min_x or 1)
    scale_y = (PAGE_HEIGHT - 2 * MARGIN) / (max_y - min_y or 1)
    scale = min(scale_x, scale_y)

    offset_x = MARGIN + (PAGE_WIDTH - 2 * MARGIN - (max_x - min_x) * scale) / 2
    offset_y = MARGIN + (PAGE_HEIGHT - 2 * MARGIN - (max_y - min_y) * scale) / 2

    c.setStrokeColor(colors.darkgray)
    c.setLineWidth(1)
    transformed = [
        ((p.x - min_x) * scale + offset_x, (p.y - min_y) * scale + offset_y)
        for p in points
    ]
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.polygon([coord for point in transformed for coord in point], stroke=1, fill=1)

    c.setFillColorRGB(0.4, 0.7, 0.4)
    for placement in placements:
        x = (placement.origin.x - min_x) * scale + offset_x
        y = (placement.origin.y - min_y) * scale + offset_y
        width = panel.width * scale
        height = panel.height * scale
        c.saveState()
        c.translate(x, y)
        c.rotate(placement.rotation_deg)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        c.restoreState()

    c.setFillColor(colors.black)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN + 5 * mm, "屋根レイアウト")


def _draw_simulation_summary(c: canvas.Canvas, request: ReportRequest, panel: PanelType) -> None:
    c.setFont("Helvetica", 16)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN, "年間発電シミュレーション")

    c.setFont("Helvetica", 12)
    lines = [
        f"パネルタイプ: {panel.name}",
        f"パネル枚数: {request.panel_count}",
        f"屋根の形状ポイント数: {len(request.simulation.roof_polygon)}",
        f"配置基準: {request.simulation.alignment.value}",
    ]

    if request.estimated_annual_output_kwh is not None:
        lines.insert(
            2,
            f"推定年間発電量: {request.estimated_annual_output_kwh:.1f} kWh",
        )
    for index, line in enumerate(lines):
        c.drawString(MARGIN, PAGE_HEIGHT - MARGIN - (index + 1) * 15, line)


def build_report(request: ReportRequest) -> str:
    panel = PANEL_TYPES.get(request.simulation.panel_type_id)
    if not panel:
        raise ValueError("Invalid panel type for report")

    placements = request.placements or []

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _draw_roof_layout(c, request, placements, panel)
    c.showPage()
    _draw_simulation_summary(c, request, panel)
    c.showPage()
    c.save()

    pdf_data = buffer.getvalue()
    encoded = base64.b64encode(pdf_data).decode("ascii")
    return encoded
