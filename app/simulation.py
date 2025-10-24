import math
from typing import Dict, List, Tuple

from shapely import affinity
from shapely.geometry import Polygon, box

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


def _as_polygon(points: List[Point]) -> Polygon:
    coords = [(p.x, p.y) for p in points]
    if len(coords) < 3:
        raise ValueError("Roof polygon must have at least three points")
    polygon = Polygon(coords)
    if not polygon.is_valid or polygon.area <= 0:
        raise ValueError("Roof polygon is invalid")
    return polygon


def _normalize_geometry(polygon: Polygon) -> Polygon:
    if polygon.is_empty:
        return polygon
    if polygon.geom_type == "Polygon":
        return polygon
    if polygon.geom_type == "MultiPolygon":
        return max(polygon.geoms, key=lambda geom: geom.area)
    raise ValueError("Unsupported geometry after polygon offset")


def _rotate_point(
    x: float, y: float, *, angle_rad: float, origin: Tuple[float, float]
) -> Tuple[float, float]:
    ox, oy = origin
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    tx = x - ox
    ty = y - oy
    rx = tx * cos_a - ty * sin_a
    ry = tx * sin_a + ty * cos_a
    return rx + ox, ry + oy


def layout_panels(sim_input: SimulationInput, panel: PanelType) -> List[PanelPlacement]:
    polygon = _as_polygon(sim_input.roof_polygon)

    # Offset polygon inward to honour the requested clearance
    offset_m = sim_input.polygon_offset_cm / 100.0
    if offset_m > 0:
        polygon = polygon.buffer(-offset_m)
        if polygon.is_empty:
            return []
        polygon = _normalize_geometry(polygon)

    if polygon.is_empty:
        return []

    points = sim_input.roof_polygon
    edge_index = sim_input.orientation_edge_index % len(points)
    start_point = points[edge_index]
    end_point = points[(edge_index + 1) % len(points)]
    angle_rad = math.atan2(end_point.y - start_point.y, end_point.x - start_point.x)
    angle_deg = math.degrees(angle_rad)

    rotation_origin = (polygon.centroid.x, polygon.centroid.y)
    rotated_polygon = affinity.rotate(
        polygon, -angle_deg, origin=rotation_origin, use_radians=False
    )

    min_x, min_y, max_x, max_y = rotated_polygon.bounds
    available_width = max_x - min_x
    available_height = max_y - min_y

    if available_width <= 0 or available_height <= 0:
        return []

    cols = int(math.floor((available_width + 1e-9) / panel.width)) if panel.width else 0
    rows = int(math.floor((available_height + 1e-9) / panel.height)) if panel.height else 0

    if cols == 0 or rows == 0:
        return []

    horizontal_gap = available_width - cols * panel.width
    vertical_gap = available_height - rows * panel.height

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
            candidate_x = offset_x + col * panel.width
            candidate_y = offset_y + row * panel.height
            candidate_rect = box(
                candidate_x,
                candidate_y,
                candidate_x + panel.width,
                candidate_y + panel.height,
            )
            if not rotated_polygon.covers(candidate_rect):
                continue

            world_x, world_y = _rotate_point(
                candidate_x,
                candidate_y,
                angle_rad=angle_rad,
                origin=rotation_origin,
            )

            placements.append(
                PanelPlacement(
                    panel_type_id=panel.id,
                    origin=Point(x=world_x, y=world_y),
                    rotation_deg=angle_deg,
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
