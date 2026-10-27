"""
Emergency SOS and Physical Assistance Routes for InsureVisionAI.
Handles rapid emergency alerting and simulated dispatch workflows for
rescue teams, roadside towing, and medical support.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from models.schemas import (
    AssistanceCreate,
    AssistanceResponse,
    AssistanceUpdate,
    SOSCreate,
    SOSResponse
)
from services.csv_storage import csv_storage
from utils.security import get_current_user
from utils.validators import ALLOWED_ASSISTANCE_TYPES, is_valid_status_transition

# Routers
sos_router = APIRouter(prefix="/sos", tags=["Emergency SOS"])
assistance_router = APIRouter(prefix="/assistance", tags=["Physical Assistance"])


# ==========================================
# Emergency SOS Endpoints
# ==========================================

@sos_router.post("", response_model=SOSResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    payload: SOSCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Record an emergency SOS signal.
    Captures incident ID, geolocation coordinates, and location description.
    Note: Prototype simulation only. Directs users to dial 112/108 for life-threatening emergencies.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    sos_id = f"SOS-{uuid.uuid4().hex[:6].upper()}"

    record = {
        "id": sos_id,
        "user_id": current_user["id"],
        "incident_id": payload.incident_id or "",
        "latitude": str(payload.latitude) if payload.latitude is not None else "",
        "longitude": str(payload.longitude) if payload.longitude is not None else "",
        "location": payload.location.strip(),
        "status": "Demo SOS request recorded",
        "created_at": now_iso
    }

    created = csv_storage.insert_record("sos_requests.csv", record)

    return SOSResponse(
        id=created["id"],
        user_id=created["user_id"],
        incident_id=created.get("incident_id") or None,
        latitude=float(created["latitude"]) if created.get("latitude") else None,
        longitude=float(created["longitude"]) if created.get("longitude") else None,
        location=created["location"],
        status=created["status"],
        created_at=created["created_at"]
    )


@sos_router.get("", response_model=List[SOSResponse])
def list_user_sos_requests(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all SOS alerts recorded for the authenticated user.
    """
    records = csv_storage.find_records("sos_requests.csv", user_id=current_user["id"])
    return [
        SOSResponse(
            id=r["id"],
            user_id=r["user_id"],
            incident_id=r.get("incident_id") or None,
            latitude=float(r["latitude"]) if r.get("latitude") else None,
            longitude=float(r["longitude"]) if r.get("longitude") else None,
            location=r["location"],
            status=r["status"],
            created_at=r["created_at"]
        )
        for r in records
    ]


@sos_router.get("/{request_id}", response_model=SOSResponse)
def get_sos_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve single SOS request by ID.
    Enforces user ownership.
    """
    record = csv_storage.get_by_id("sos_requests.csv", request_id)
    if not record or record.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SOS request '{request_id}' not found or unauthorized."
        )

    return SOSResponse(
        id=record["id"],
        user_id=record["user_id"],
        incident_id=record.get("incident_id") or None,
        latitude=float(record["latitude"]) if record.get("latitude") else None,
        longitude=float(record["longitude"]) if record.get("longitude") else None,
        location=record["location"],
        status=record["status"],
        created_at=record["created_at"]
    )


# ==========================================
# Physical Assistance Endpoints
# ==========================================

@assistance_router.post("", response_model=AssistanceResponse, status_code=status.HTTP_201_CREATED)
def request_assistance(
    payload: AssistanceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Dispatch a simulated physical assistance request (Rescue Team, Towing, or Medical Assistance).
    """
    if payload.assistance_type not in ALLOWED_ASSISTANCE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid assistance type. Must be one of: {list(ALLOWED_ASSISTANCE_TYPES)}"
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    req_id = f"AST-{uuid.uuid4().hex[:6].upper()}"

    record = {
        "id": req_id,
        "user_id": current_user["id"],
        "incident_id": payload.incident_id or "",
        "assistance_type": payload.assistance_type,
        "location": payload.location.strip(),
        "status": "Requested",
        "created_at": now_iso
    }

    created = csv_storage.insert_record("assistance_requests.csv", record)

    return AssistanceResponse(
        id=created["id"],
        user_id=created["user_id"],
        incident_id=created.get("incident_id") or None,
        assistance_type=created["assistance_type"],
        location=created["location"],
        status=created["status"],
        created_at=created["created_at"]
    )


@assistance_router.get("", response_model=List[AssistanceResponse])
def list_assistance_requests(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all assistance requests submitted by the authenticated user.
    """
    records = csv_storage.find_records("assistance_requests.csv", user_id=current_user["id"])
    return [
        AssistanceResponse(
            id=r["id"],
            user_id=r["user_id"],
            incident_id=r.get("incident_id") or None,
            assistance_type=r["assistance_type"],
            location=r["location"],
            status=r["status"],
            created_at=r["created_at"]
        )
        for r in records
    ]


@assistance_router.get("/{request_id}", response_model=AssistanceResponse)
def get_assistance_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve details of a specific assistance dispatch request.
    """
    record = csv_storage.get_by_id("assistance_requests.csv", request_id)
    if not record or record.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistance request '{request_id}' not found or unauthorized."
        )

    return AssistanceResponse(
        id=record["id"],
        user_id=record["user_id"],
        incident_id=record.get("incident_id") or None,
        assistance_type=record["assistance_type"],
        location=record["location"],
        status=record["status"],
        created_at=record["created_at"]
    )


@assistance_router.patch("/{request_id}", response_model=AssistanceResponse)
def update_assistance_status(
    request_id: str,
    payload: AssistanceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Advance assistance workflow status (Requested -> Accepted -> In Progress -> Completed/Cancelled).
    """
    record = csv_storage.get_by_id("assistance_requests.csv", request_id)
    if not record or record.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistance request '{request_id}' not found or unauthorized."
        )

    current_status = record.get("status", "Requested")
    new_status = payload.status

    if not is_valid_status_transition(current_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'."
        )

    updated = csv_storage.update_record(
        "assistance_requests.csv",
        request_id,
        {"status": new_status}
    )

    return AssistanceResponse(
        id=updated["id"],
        user_id=updated["user_id"],
        incident_id=updated.get("incident_id") or None,
        assistance_type=updated["assistance_type"],
        location=updated["location"],
        status=updated["status"],
        created_at=updated["created_at"]
    )
