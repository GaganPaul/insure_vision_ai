"""
Fault Analysis API Routes for InsureVisionAI.
Computes and returns telemetry-driven fault attribution, confidence metrics,
and contributing factors.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from models.schemas import ContributingFactor, FaultAnalysisResponse
from services.analysis_service import analysis_service
from services.incident_service import incident_service
from utils.security import get_current_user

router = APIRouter(prefix="/analysis", tags=["Fault Analysis"])


@router.post("/{incident_id}", response_model=FaultAnalysisResponse)
def compute_incident_analysis(
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Execute simulated fault analysis on a specific incident.
    Calculates driver vs other vehicle responsibility percentages and contributing factors.
    """
    # Enforce ownership check on incident
    inc = incident_service.get_incident_by_id(incident_id, current_user["id"])
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found or unauthorized."
        )

    try:
        analysis = analysis_service.run_analysis(incident_id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{incident_id}", response_model=FaultAnalysisResponse)
def get_incident_analysis(
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve existing fault analysis results for an incident.
    """
    inc = incident_service.get_incident_by_id(incident_id, current_user["id"])
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found or unauthorized."
        )

    analysis = analysis_service.get_analysis(incident_id)
    if not analysis:
        # If not yet analyzed, automatically run it
        analysis = analysis_service.run_analysis(incident_id)

    return analysis


@router.get("/{incident_id}/factors", response_model=List[ContributingFactor])
def get_incident_factors(
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve individual contributing factors for an incident.
    """
    inc = incident_service.get_incident_by_id(incident_id, current_user["id"])
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found or unauthorized."
        )

    factors = analysis_service.get_factors(incident_id)
    if not factors:
        # Run analysis to generate factors
        analysis = analysis_service.run_analysis(incident_id)
        factors = analysis.get("factors", [])

    return factors
