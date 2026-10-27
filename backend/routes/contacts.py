"""
Emergency Contacts Management Routes for InsureVisionAI.
Handles trusted contact additions, updates, listing, and deletion.
"""

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from models.schemas import ContactCreate, ContactResponse, ContactUpdate
from services.csv_storage import csv_storage
from utils.security import get_current_user
from utils.validators import is_valid_phone

router = APIRouter(prefix="/contacts", tags=["Emergency Contacts"])


@router.get("", response_model=List[ContactResponse])
def get_user_contacts(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all emergency contacts registered for the authenticated user.
    """
    return csv_storage.find_records("contacts.csv", user_id=current_user["id"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a new emergency contact.
    Validates name, relationship, and contact number.
    """
    clean_phone = payload.phone.strip()
    if not is_valid_phone(clean_phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format."
        )

    contact_id = f"CONT-{uuid.uuid4().hex[:6].upper()}"
    record = {
        "id": contact_id,
        "user_id": current_user["id"],
        "name": payload.name.strip(),
        "relationship": payload.relationship.strip(),
        "phone": clean_phone
    }

    created = csv_storage.insert_record("contacts.csv", record)
    return created


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    payload: ContactUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing emergency contact.
    Enforces user ownership.
    """
    existing = csv_storage.get_by_id("contacts.csv", contact_id)
    if not existing or existing.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact '{contact_id}' not found or unauthorized."
        )

    updates = payload.model_dump(exclude_unset=True)
    if "phone" in updates and updates["phone"]:
        if not is_valid_phone(updates["phone"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format."
            )

    updated = csv_storage.update_record("contacts.csv", contact_id, updates)
    return updated


@router.delete("/{contact_id}", status_code=status.HTTP_200_OK)
def delete_contact(
    contact_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete an emergency contact.
    Enforces user ownership.
    """
    existing = csv_storage.get_by_id("contacts.csv", contact_id)
    if not existing or existing.get("user_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact '{contact_id}' not found or unauthorized."
        )

    csv_storage.delete_record("contacts.csv", contact_id)
    return {"message": f"Contact {contact_id} successfully deleted."}
