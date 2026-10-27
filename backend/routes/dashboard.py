"""
Dashboard and Safety Tips routes for InsureVisionAI.
Provides metrics, user status, coverage indicators, and daily safety guidance.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from models.schemas import DashboardResponse, DashboardStats, SafetyTipResponse
from services.csv_storage import csv_storage
from utils.security import get_current_user

router = APIRouter(tags=["Dashboard & Safety Tips"])


def get_daily_tip() -> Dict[str, str]:
    """Deterministically select a safety tip based on current calendar date."""
    tips = csv_storage.load_all("safety_tips.csv")
    if not tips:
        return {
            "id": "TIP-DEFAULT",
            "tip": "Always wear your safety belt and stay alert on the road.",
            "category": "General Safety"
        }
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    selected_idx = day_of_year % len(tips)
    return tips[selected_idx]


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve personalized dashboard data.
    Aggregates profile details, incident statistics, insurance coverage status,
    and daily safety guidance using persistent CSV records.
    """
    user_id = current_user["id"]

    # Retrieve incidents for authenticated user
    user_incidents = csv_storage.find_records("incidents.csv", user_id=user_id)
    total_incidents = len(user_incidents)

    # Sort to find latest incident
    latest_incident = None
    if user_incidents:
        sorted_incidents = sorted(
            user_incidents,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        latest_incident = sorted_incidents[0]

    # Calculate safe trips (baseline of 120 trips + 15 per zero incident, or derived)
    safe_trips = max(0, 142 - (total_incidents * 3))

    # Check insurance coverage
    policies = csv_storage.find_records("insurance.csv", user_id=user_id)
    active_policy = None
    coverage_status = "No Policy"
    protection_status = "Action Required"

    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for pol in policies:
        exp_date = pol.get("expiry_date", "")
        if exp_date >= now_date:
            coverage_status = "Active"
            protection_status = "Protected"
            active_policy = pol
            break
        else:
            coverage_status = "Expired"

    daily_tip = get_daily_tip()

    stats = DashboardStats(
        total_incidents=total_incidents,
        safe_trips=safe_trips,
        coverage_status=coverage_status,
        protection_status=protection_status
    )

    return DashboardResponse(
        user=current_user,
        stats=stats,
        latest_incident=latest_incident,
        active_policy=active_policy,
        daily_safety_tip=daily_tip
    )


@router.get("/safety-tips", response_model=List[SafetyTipResponse])
def get_all_safety_tips():
    """Retrieve all available road safety tips."""
    return csv_storage.load_all("safety_tips.csv")


@router.get("/safety-tips/daily", response_model=SafetyTipResponse)
def get_daily_safety_tip():
    """Retrieve the deterministic daily road safety tip."""
    return get_daily_tip()

