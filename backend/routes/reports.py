"""
Accident Report Generation and Download Routes for InsureVisionAI.
Provides structured JSON inspection and binary PDF downloads.
"""

import json
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from services.incident_service import incident_service
from services.report_service import report_service
from utils.security import get_current_user

router = APIRouter(prefix="/reports", tags=["Accident Reports"])


@router.get("/{incident_id}")
def get_incident_report(
    incident_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve comprehensive accident report data in JSON format.
    Combines telemetry observations, rule-based fault attribution,
    contributing factors, and insurance status.
    """
    try:
        data = report_service.get_report_data(incident_id, current_user["id"])
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/download")
def download_incident_report(
    incident_id: str,
    format: str = Query("pdf", description="Download format: 'pdf' or 'json'"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a formatted accident report.
    Supports binary PDF generation and structured JSON exports.
    """
    try:
        report_data = report_service.get_report_data(incident_id, current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    clean_format = format.lower().strip()

    if clean_format == "json":
        json_bytes = json.dumps(report_data, indent=2).encode("utf-8")
        filename = f"InsureVisionAI_Report_{incident_id}.json"
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    elif clean_format == "pdf":
        pdf_bytes = report_service.generate_pdf_report(report_data)
        filename = f"InsureVisionAI_Report_{incident_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{format}'. Supported formats are 'pdf' and 'json'."
        )

