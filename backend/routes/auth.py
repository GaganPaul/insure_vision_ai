"""
Authentication routes for InsureVisionAI.
Provides user registration, login with JWT issuance, and profile retrieval.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from models.schemas import Token, UserLogin, UserResponse, UserSignup
from services.csv_storage import csv_storage
from utils.security import create_access_token, get_current_user, hash_password, verify_password
from utils.validators import is_valid_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data: UserSignup):
    """
    Register a new user account.
    Validates email format, checks for duplicates, securely hashes password,
    and persists record in users.csv.
    """
    clean_email = data.email.strip().lower()
    if not is_valid_email(clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address format."
        )

    # Check for duplicate email
    existing = csv_storage.find_records("users.csv", email=clean_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()

    new_user = {
        "id": user_id,
        "name": data.name.strip(),
        "email": clean_email,
        "phone": (data.phone or "").strip(),
        "password_hash": hash_password(data.password),
        "vehicle_type": (data.vehicle_type or "Four-Wheeler (Car)").strip(),
        "vehicle_number": (data.vehicle_number or "").strip(),
        "created_at": now_iso
    }

    created = csv_storage.insert_record("users.csv", new_user)
    
    # Return safe user
    safe_user = dict(created)
    safe_user.pop("password_hash", None)
    return safe_user


@router.post("/login", response_model=Token)
def login(data: UserLogin):
    """
    Authenticate user with email and password.
    Returns a signed JWT bearer access token upon verification.
    """
    clean_email = data.email.strip().lower()
    matched_users = csv_storage.find_records("users.csv", email=clean_email)
    if not matched_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = matched_users[0]
    stored_hash = user.get("password_hash", "")
    
    if not verify_password(data.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate token
    token = create_access_token(data={"sub": user["id"], "email": user["email"]})
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve authenticated user's profile.
    Derived securely from verified JWT credentials.
    """
    return current_user


@router.post("/logout")
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout endpoint.
    Because standard JWTs are stateless, client applications should discard the stored token.
    """
    return {
        "message": "Successfully logged out. Please discard your client token.",
        "user_id": current_user.get("id")
    }
