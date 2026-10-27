"""
Incident Management Service for InsureVisionAI.
Handles incident creation, simulation, querying, updating, and deletion with strict user ownership.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.csv_storage import csv_storage
from services.analysis_service import analysis_service


class IncidentService:
    @staticmethod
    def get_user_incidents(
        user_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Dict[str, str]], int]:
        """
        Fetch paginated incidents for a specific user with optional filters.
        """
        all_user_incidents = csv_storage.find_records("incidents.csv", user_id=user_id)
        
        # Apply filters
        filtered = []
        for inc in all_user_incidents:
            if severity and inc.get("severity", "").lower() != severity.lower():
                continue
            if status and inc.get("status", "").lower() != status.lower():
                continue
            filtered.append(inc)
        
        # Sort by date/created_at descending
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        total = len(filtered)
        start_idx = max(0, (page - 1) * limit)
        end_idx = start_idx + limit
        paginated = filtered[start_idx:end_idx]
        
        return paginated, total

    @staticmethod
    def get_incident_by_id(incident_id: str, user_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieve incident ensuring user ownership. Returns None if not found or unauthorized.
        """
        inc = csv_storage.get_by_id("incidents.csv", incident_id)
        if not inc:
            return None
        if inc.get("user_id") != user_id:
            # Unauthorized access to another user's private incident
            return None
        return inc

    @staticmethod
    def simulate_incident(user_id: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a simulated incident record with realistic deterministic telemetry.
        Automatically triggers fault analysis.
        """
        now = datetime.now(timezone.utc)
        incident_id = f"INC-{now.strftime('%y%m%d')}{uuid.uuid4().hex[:4].upper()}"
        
        params = custom_params or {}
        incident_record = {
            "id": incident_id,
            "user_id": user_id,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "location": params.get("location", "MG Road Junction, Bangalore"),
            "severity": params.get("severity", "Minor"),
            "speed": params.get("speed", "48 km/h"),
            "speed_limit": params.get("speed_limit", "40 km/h"),
            "braking": params.get("braking", "Minor Delay"),
            "signal": params.get("signal", "Red"),
            "impact": params.get("impact", "Front Right"),
            "status": "Detected",
            "created_at": now.isoformat()
        }
        
        created = csv_storage.insert_record("incidents.csv", incident_record)
        
        # Auto-run analysis for simulated incident
        analysis = analysis_service.run_analysis(incident_id)
        
        return {
            "incident": created,
            "analysis": analysis
        }

    @staticmethod
    def update_incident(incident_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Update incident if owned by user."""
        inc = csv_storage.get_by_id("incidents.csv", incident_id)
        if not inc or inc.get("user_id") != user_id:
            return None
        
        # Don't allow changing ownership or ID
        updates.pop("id", None)
        updates.pop("user_id", None)
        updates.pop("created_at", None)
        
        return csv_storage.update_record("incidents.csv", incident_id, updates)

    @staticmethod
    def delete_incident(incident_id: str, user_id: str) -> bool:
        """Delete incident and associated analysis records if owned by user."""
        inc = csv_storage.get_by_id("incidents.csv", incident_id)
        if not inc or inc.get("user_id") != user_id:
            return False
        
        # Delete from incidents.csv
        success = csv_storage.delete_record("incidents.csv", incident_id)
        
        if success:
            # Also clean up fault analysis and factors
            analyses = csv_storage.find_records("fault_analysis.csv", incident_id=incident_id)
            for a in analyses:
                csv_storage.delete_record("fault_analysis.csv", a.get("id", ""))
            
            factors = csv_storage.find_records("factors.csv", incident_id=incident_id)
            for f in factors:
                csv_storage.delete_record("factors.csv", f.get("id", ""))
        
        return success


incident_service = IncidentService()
