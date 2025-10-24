from typing import Dict, List, Tuple

from .models import (
    Alignment,
    PanelManufacturer,
    PanelPlacement,
    PanelSeries,
    PanelType,
    Point,
    SimulationInput,
    SimulationResult,
)


def _panel(
    *,
    id: str,
    name: str,
    width_mm: float,
    height_mm: float,
    capacity_w: float,
) -> PanelType:
    return PanelType(
        id=id,
        name=name,
        width=width_mm / 1000.0,
        height=height_mm / 1000.0,
        capacity_kw=capacity_w / 1000.0,
    )


# Predefined panel catalog organised by manufacturer -> series -> panels
PANEL_CATALOG: Dict[str, PanelManufacturer] = {
    "canadian-solar": PanelManufacturer(
        id="canadian-solar",
        name="カナディアンソーラー",
        series={
            "tophiku6": PanelSeries(
                id="tophiku6",
                name="TOPHiKu6",
                panels={
                    "CS6.2-48TM-455": _panel(
                        id="CS6.2-48TM-455",
                        name="CS6.2-48TM-455",
                        width_mm=1134,
                        height_mm=1762,
                        capacity_w=455,
                    ),
                    "CS6.2-36TM-340": _panel(
                        id="CS6.2-36TM-340",
                        name="CS6.2-36TM-340",
                        width_mm=1134,
                        height_mm=1334,
                        capacity_w=340,
                    ),
                    "CS6.2-32TM-300": _panel(
                        id="CS6.2-32TM-300",
                        name="CS6.2-32TM-300",
                        width_mm=767,
                        height_mm=1762,
                        capacity_w=300,
                    ),
                },
            )
        },
    ),
    "generic": PanelManufacturer(
        id="generic",
        name="汎用パネル",
        series={
            "reference": PanelSeries(
                id="reference",
                name="リファレンス",
                panels={
                    "compact": PanelType(
                        id="compact",
                        name="Compact 320W",
                        width=0.99,
                        height=1.65,
                        capacity_kw=0.32,
                    ),
                    "standard": PanelType(
                        id="standard",
                        name="Standard 400W",
                        width=1.0,
                        height=1.7,
                        capacity_kw=0.4,
                    ),
                    "premium": PanelType(
                        id="premium",
                        name="Premium 450W",
                        width=1.05,
                        height=1.8,
                        capacity_kw=0.45,
                    ),
                    "wide": PanelType(
                        id="wide",
                        name="Wide 500W",
                        width=1.2,
                        height=1.6,
                        capacity_kw=0.5,
                    ),
                    "ultra": PanelType(
                        id="ultra",
                        name="Ultra 550W",
                        width=1.1,
                        height=2.1,
                        capacity_kw=0.55,
                    ),
                },
            )
        },
    ),
}


def _flatten_panel_catalog() -> Dict[str, PanelType]:
    flattened: Dict[str, PanelType] = {}
    for manufacturer in PANEL_CATALOG.values():
        for series in manufacturer.series.values():
            for panel_id, panel in series.panels.items():
                flattened[panel_id] = panel
    return flattened


PANEL_TYPES: Dict[str, PanelType] = _flatten_panel_catalog()

SOLAR_IRRADIANCE_KWH_M2 = 1200  # Approximate annual irradiance
PERFORMANCE_RATIO = 0.75


def polygon_area(points: List[Point]) -> float:
    area = 0.0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i].x * points[j].y
        area -= points[j].x * points[i].y
    return abs(area) / 2.0


def bounding_box(points: List[Point]) -> Tuple[float, float, float, float]:
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def layout_panels(sim_input: SimulationInput, panel: PanelType) -> List[PanelPlacement]:
    min_x, min_y, max_x, max_y = bounding_box(sim_input.roof_polygon)
    roof_width = max_x - min_x
    roof_height = max_y - min_y

    cols = int(roof_width / panel.width) if panel.width else 0
    rows = int(roof_height / panel.height) if panel.height else 0

    if cols == 0 or rows == 0:
        return []

    horizontal_gap = roof_width - cols * panel.width
    vertical_gap = roof_height - rows * panel.height

    if sim_input.alignment == Alignment.LEFT:
        offset_x = min_x
    elif sim_input.alignment == Alignment.RIGHT:
        offset_x = min_x + horizontal_gap
    else:
        offset_x = min_x + horizontal_gap / 2.0

    offset_y = min_y + vertical_gap / 2.0

    placements: List[PanelPlacement] = []
    for row in range(rows):
        for col in range(cols):
            origin_x = offset_x + col * panel.width
            origin_y = offset_y + row * panel.height
            placements.append(
                PanelPlacement(
                    panel_type_id=panel.id,
                    origin=Point(x=origin_x, y=origin_y),
                )
            )
    return placements


def simulate(sim_input: SimulationInput) -> SimulationResult:
    panel = PANEL_TYPES.get(sim_input.panel_type_id)
    if not panel:
        raise ValueError(f"Unknown panel type: {sim_input.panel_type_id}")

    placements = layout_panels(sim_input, panel)
    panel_count = len(placements)

    usable_area = panel.width * panel.height * panel_count
    total_capacity_kw = panel.capacity_kw * panel_count

    effective_area = usable_area * PERFORMANCE_RATIO
    estimated_annual_output_kwh = effective_area * SOLAR_IRRADIANCE_KWH_M2 / 1000

    return SimulationResult(
        usable_area=usable_area,
        panel_count=panel_count,
        total_capacity_kw=total_capacity_kw,
        estimated_annual_output_kwh=estimated_annual_output_kwh,
        panel_width=panel.width,
        panel_height=panel.height,
        panel_capacity_kw=panel.capacity_kw,
        placements=placements,
    )
