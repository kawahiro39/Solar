from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class Point(BaseModel):
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")


class PanelType(BaseModel):
    id: str
    name: str
    width: float = Field(..., description="Panel width in meters")
    height: float = Field(..., description="Panel height in meters")
    capacity_kw: float = Field(..., description="Panel peak power in kW")


class PanelSeries(BaseModel):
    id: str
    name: str
    panels: Dict[str, PanelType]
    allow_mixing_within_series: bool = Field(
        True,
        description="Whether panels within this series can be mixed in a layout",
    )


class PanelManufacturer(BaseModel):
    id: str
    name: str
    series: Dict[str, PanelSeries]


class SimulationInput(BaseModel):
    roof_polygon: List[Point] = Field(..., min_items=3)
    panel_type_id: str
    alignment: Alignment
    orientation_edge_index: int = Field(
        0,
        description="Index of the polygon edge used to orient the panel layout",
        ge=0,
    )
    polygon_offset_cm: float = Field(
        0.0,
        description="Inset distance from the polygon boundary in centimetres",
        ge=0.0,
    )

    @validator("roof_polygon")
    def ensure_polygon_closed(cls, value: List[Point]) -> List[Point]:
        if len(value) < 3:
            raise ValueError("Roof polygon must have at least three points")
        return value

    @validator("orientation_edge_index")
    def ensure_edge_index(cls, value: int, values: Dict[str, List[Point]]) -> int:
        points: List[Point] = values.get("roof_polygon", [])  # type: ignore[arg-type]
        if points and value >= len(points):
            raise ValueError("orientation_edge_index must reference an existing edge")
        return value


class PanelPlacement(BaseModel):
    panel_type_id: str
    origin: Point
    rotation_deg: float = Field(
        0.0,
        description="Rotation of the panel placement in degrees, counter-clockwise",
    )


class SimulationResult(BaseModel):
    usable_area: float
    panel_count: int
    total_capacity_kw: float
    estimated_annual_output_kwh: float
    panel_width: float
    panel_height: float
    panel_capacity_kw: float
    placements: List[PanelPlacement]


class ReportRequest(BaseModel):
    simulation: SimulationInput
    panel_count: Optional[int] = None
    estimated_annual_output_kwh: Optional[float] = None
    placements: Optional[List[PanelPlacement]] = None


class ReportResponse(BaseModel):
    filename: str
    content_type: str
    data_base64: str
