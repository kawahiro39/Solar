from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import ReportRequest, ReportResponse, SimulationInput, SimulationResult
from .pdf import build_report
from .simulation import PANEL_TYPES, simulate

app = FastAPI(title="Solar Layout Simulator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/panel-types", response_model=Dict[str, Dict])
def get_panel_types() -> Dict[str, Dict]:
    return {panel_id: panel.dict() for panel_id, panel in PANEL_TYPES.items()}


@app.post("/simulate", response_model=SimulationResult)
def run_simulation(sim_input: SimulationInput) -> SimulationResult:
    try:
        return simulate(sim_input)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/report", response_model=ReportResponse)
def generate_report(request: ReportRequest) -> ReportResponse:
    try:
        encoded_pdf = build_report(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ReportResponse(
        filename="solar-simulation-report.pdf",
        content_type="application/pdf",
        data_base64=encoded_pdf,
    )


@app.get("/")
def health() -> Dict[str, str]:
    return {"status": "ok"}
