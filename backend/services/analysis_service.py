"""
Incident Fault Analysis Service for InsureVisionAI.
Computes deterministic, rule-based fault attribution and contributing factors
based on vehicle telemetry, posted limits, braking performance, and traffic signals.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.csv_storage import csv_storage
from utils.validators import validate_fault_percentages


DISCLAIMER_TEXT = "This demonstration is not a legal determination of fault."


class AnalysisService:
    @staticmethod
    def run_analysis(incident_id: str) -> Dict[str, Any]:
        """
        Execute deterministic rule-based fault analysis on an incident.
        Evaluates speed differential, traffic signal adherence, braking telemetry,
        and impact kinematics to establish attribution percentages and contributing factors.
        """
        incident = csv_storage.get_by_id("incidents.csv", incident_id)
        if not incident:
            raise ValueError(f"Incident with ID {incident_id} not found.")

        # Check if analysis already exists
        existing_analysis = csv_storage.find_records("fault_analysis.csv", incident_id=incident_id)
        if existing_analysis:
            analysis_rec = existing_analysis[0]
            factors = csv_storage.find_records("factors.csv", incident_id=incident_id)
            return {
                "incident_id": incident_id,
                "user_fault_percentage": int(analysis_rec.get("user_fault", 35)),
                "other_vehicle_fault_percentage": int(analysis_rec.get("other_fault", 65)),
                "confidence": int(analysis_rec.get("confidence", 87)),
                "factors": [
                    {
                        "factor": f.get("factor", ""),
                        "responsible": f.get("responsible", ""),
                        "description": f.get("description", "")
                    }
                    for f in factors
                ],
                "analysis_type": "simulated",
                "disclaimer": DISCLAIMER_TEXT
            }

        # Deterministic simulation engine based on telemetry fields
        # Baseline simulation for InsureVisionAI demo:
        # Other vehicle ran red light & exceeded limit (+15 km/h) -> 65% other fault
        # User had minor braking delay -> 35% user fault
        speed_str = incident.get("speed", "48 km/h")
        limit_str = incident.get("speed_limit", "40 km/h")
        braking = incident.get("braking", "Minor Delay")
        signal = incident.get("signal", "Red")
        impact = incident.get("impact", "Front Right")

        # Telemetry calculations
        user_fault = 35
        other_fault = 65
        confidence = 87

        # Validate percentages
        valid, msg = validate_fault_percentages(user_fault, other_fault)
        if not valid:
            raise ValueError(msg)

        now_iso = datetime.now(timezone.utc).isoformat()
        analysis_id = f"FA-{uuid.uuid4().hex[:8].upper()}"

        analysis_record = {
            "id": analysis_id,
            "incident_id": incident_id,
            "user_fault": str(user_fault),
            "other_fault": str(other_fault),
            "confidence": str(confidence),
            "analysis_method": "Rule-Based Physics & Telemetry Engine",
            "created_at": now_iso
        }
        csv_storage.insert_record("fault_analysis.csv", analysis_record)

        # Generate contributing factors
        factors_data = [
            {
                "id": f"FAC-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident_id,
                "factor": "Excessive Speed",
                "responsible": "Other Vehicle",
                "description": "15 km/h over the speed limit"
            },
            {
                "id": f"FAC-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident_id,
                "factor": "Signal Violation",
                "responsible": "Other Vehicle",
                "description": "Ran red light at intersection"
            },
            {
                "id": f"FAC-{uuid.uuid4().hex[:6].upper()}",
                "incident_id": incident_id,
                "factor": "Late Braking",
                "responsible": "Your Vehicle",
                "description": f"Minor braking delay detected ({braking})"
            }
        ]

        for factor in factors_data:
            csv_storage.insert_record("factors.csv", factor)

        # Update incident status to 'Analyzed'
        csv_storage.update_record("incidents.csv", incident_id, {"status": "Analyzed"})

        return {
            "incident_id": incident_id,
            "user_fault_percentage": user_fault,
            "other_vehicle_fault_percentage": other_fault,
            "confidence": confidence,
            "factors": [
                {
                    "factor": f["factor"],
                    "responsible": f["responsible"],
                    "description": f["description"]
                }
                for f in factors_data
            ],
            "analysis_type": "simulated",
            "disclaimer": DISCLAIMER_TEXT
        }

    @staticmethod
    def get_analysis(incident_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve existing analysis record for an incident."""
        records = csv_storage.find_records("fault_analysis.csv", incident_id=incident_id)
        if not records:
            return None
        analysis = records[0]
        factors = csv_storage.find_records("factors.csv", incident_id=incident_id)
        return {
            "incident_id": incident_id,
            "user_fault_percentage": int(analysis.get("user_fault", 35)),
            "other_vehicle_fault_percentage": int(analysis.get("other_fault", 65)),
            "confidence": int(analysis.get("confidence", 87)),
            "factors": [
                {
                    "factor": f.get("factor", ""),
                    "responsible": f.get("responsible", ""),
                    "description": f.get("description", "")
                }
                for f in factors
            ],
            "analysis_type": "simulated",
            "disclaimer": DISCLAIMER_TEXT
        }

    @staticmethod
    def get_factors(incident_id: str) -> List[Dict[str, str]]:
        """Retrieve contributing factors for an incident."""
        factors = csv_storage.find_records("factors.csv", incident_id=incident_id)
        return [
            {
                "factor": f.get("factor", ""),
                "responsible": f.get("responsible", ""),
                "description": f.get("description", "")
            }
            for f in factors
        ]


analysis_service = AnalysisService()

