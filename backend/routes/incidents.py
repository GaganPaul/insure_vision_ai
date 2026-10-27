"""
Incident Management API Routes for InsureVisionAI.
Supports incident creation, sensor simulation, querying, updating, and deletion.
Enforces user isolation and authorization.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from models.schemas import (
    IncidentCreate,
    IncidentResponse,
    IncidentSimulateRequest,
    IncidentUpdate
)
from services.incident_service import incident_service
from utils.security import get_current_user

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=Dict[str, Any])
def list_incidents(
    severity: Optional[str] = Query(None, description="Filter by severity (Minor, Moderate, Severe)"),
    status: Optional[str] = Query(None, description="Filter by status (Detected, Analyzed, Closed)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Records per page"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve paginated incident history for the authenticated user.
    """
    items, total = incident_service.get_user_incidents(
        user_id=current_user["id"],
        severity=severity,
        status=status,
        page=page,
        limit=limit
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve single incident details.
    Enforces record ownership; returns 404 if not found or unauthorized.
    """
    inc = incident_service.get_incident_by_id(incident_id, current_user["id"])
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found."
        )
    return inc


@router.post("/simulate", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def simulate_incident(
    payload: Optional[IncidentSimulateRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Simulate an accident event using deterministic telemetry data.
    Automatically logs the incident and runs initial fault analysis.
    """
    custom_params = payload.model_dump() if payload else {}
    result = incident_service.simulate_incident(current_user["id"], custom_params)
    return result


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Partially update incident details.
    Requires record ownership.
    """
    updates = payload.model_dump(exclude_unset=True)
    updated = incident_service.update_incident(incident_id, current_user["id"], updates)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found or cannot be modified."
        )
    return updated


@router.delete("/{incident_id}", status_code=status.HTTP_200_OK)
def delete_incident(
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete an incident and associated analysis.
    Requires record ownership.
    """
    success = incident_service.delete_incident(incident_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found or unauthorized."
        )
    return {"message": f"Incident {incident_id} successfully deleted."}
