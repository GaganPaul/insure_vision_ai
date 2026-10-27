"""
Insurance Management API Routes for InsureVisionAI.
Handles insurance policy registration, updates, retrieval, and deletion.
Enforces user isolation and data validation.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from models.schemas import InsuranceCreate, InsuranceResponse, InsuranceUpdate
from services.csv_storage import csv_storage
from utils.security import get_current_user
from utils.validators import is_valid_date

router = APIRouter(prefix="/insurance", tags=["Insurance Management"])


@router.get("", response_model=List[InsuranceResponse])
def get_user_policies(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve all insurance policies owned by the authenticated user.
    """
    return csv_storage.find_records("insurance.csv", user_id=current_user["id"])


@router.post("", response_model=InsuranceResponse, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: InsuranceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Register a new insurance policy.
    Validates expiry date and associates the policy with the authenticated user.
    """
    if not is_valid_date(payload.expiry_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid expiry date format. Expected YYYY-MM-DD."
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    policy_id = f"INS-{uuid.uuid4().hex[:6].upper()}"

    record = {
        "id": policy_id,
        "user_id": current_user["id"],
        "provider": payload.provider.strip(),
        "policy_number": payload.policy_number.strip(),
        "expiry_date": payload.expiry_date.strip(),
        "vehicle_type": payload.vehicle_type.strip(),
        "coverage_type": payload.coverage_type.strip(),
        "updated_at": now_iso
    }

    created = csv_storage.insert_record("insurance.csv", record)
    return created


@router.put("/{insurance_id}", response_model=InsuranceResponse)
def update_policy(
    insurance_id: str,
    payload: InsuranceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing insurance policy.
    Enforces user ownership.
    """
    existing = csv_storage.get_by_id("insurance.csv", insurance_id)
    if not existing or existing.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID '{insurance_id}' not found or unauthorized."
        )

    updates = payload.model_dump(exclude_unset=True)
    if "expiry_date" in updates and updates["expiry_date"]:
        if not is_valid_date(updates["expiry_date"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid expiry date format. Expected YYYY-MM-DD."
            )

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    updated = csv_storage.update_record("insurance.csv", insurance_id, updates)
    return updated


@router.delete("/{insurance_id}", status_code=status.HTTP_200_OK)
def delete_policy(
    insurance_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Remove an insurance policy.
    Enforces user ownership.
    """
    existing = csv_storage.get_by_id("insurance.csv", insurance_id)
    if not existing or existing.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID '{insurance_id}' not found or unauthorized."
        )

    csv_storage.delete_record("insurance.csv", insurance_id)
    return {"message": f"Policy {insurance_id} deleted successfully."}
