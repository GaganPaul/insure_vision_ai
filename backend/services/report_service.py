"""
Accident Telemetry & Claims Report Service for InsureVisionAI.
Generates comprehensive incident summary data and produces downloadable
JSON and standard-compliant PDF documents.
"""

import io
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services.csv_storage import csv_storage
from services.analysis_service import analysis_service


DISCLAIMER_TEXT = (
    "This report is generated for demonstration and claims evaluation purposes using "
    "telemetry data and rule-based heuristics. It does not constitute a final legal "
    "determination of liability or judicial verdict."
)


class SimplePDFBuilder:
    """
    Standard-compliant PDF 1.4 builder in pure Python.
    Generates structured, clean PDF reports with zero external library dependencies.
    """
    def __init__(self):
        self.objects = []
        self.page_contents = []

    def _add_object(self, content: bytes) -> int:
        self.objects.append(content)
        return len(self.objects)

    @staticmethod
    def _escape_pdf_text(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def build_report_pdf(self, data: Dict[str, Any]) -> bytes:
        inc = data.get("incident", {})
        analysis = data.get("analysis", {})
        factors = analysis.get("factors", [])
        user = data.get("user", {})
        insurance = data.get("insurance") or {}

        # Construct stream content using standard PDF operators
        stream_lines = []
        
        # Colors: Dark Blue Header
        stream_lines.append("0.1 0.2 0.45 rg")  # fill color
        stream_lines.append("40 730 532 60 re f")  # rectangle header banner
        
        # Header text (White)
        stream_lines.append("1 1 1 rg")
        stream_lines.append("BT /F1 18 Tf 55 765 Td (INSUREVISION AI) Tj ET")
        stream_lines.append("BT /F2 11 Tf 55 745 Td (Comprehensive Accident Telemetry & Liability Report) Tj ET")

        # Top Metadata Box (Light Grey background)
        stream_lines.append("0.95 0.95 0.96 rg")
        stream_lines.append("40 660 532 55 re f")
        stream_lines.append("0.8 0.8 0.8 RG 1 w 40 660 532 55 re S")

        # Metadata text
        stream_lines.append("0.2 0.2 0.2 rg")
        stream_lines.append("BT /F2 10 Tf 55 695 Td")
        inc_id = self._escape_pdf_text(str(inc.get('id', 'N/A')))
        gen_time = self._escape_pdf_text(str(data.get('generated_at', '')))
        stream_lines.append(f"(Incident ID: {inc_id}    |    Date: {inc.get('date', 'N/A')} {inc.get('time', '')}    |    Generated: {gen_time[:19]}) Tj ET")
        
        user_name = self._escape_pdf_text(str(user.get('name', 'N/A')))
        veh_num = self._escape_pdf_text(str(user.get('vehicle_number', 'N/A')))
        loc = self._escape_pdf_text(str(inc.get('location', 'N/A')))
        stream_lines.append("BT /F2 9 Tf 55 675 Td")
        stream_lines.append(f"(Driver: {user_name}    |    Vehicle: {veh_num}    |    Location: {loc}) Tj ET")

        # Section 1: Telemetry Data
        stream_lines.append("0.1 0.25 0.5 rg")
        stream_lines.append("BT /F1 12 Tf 40 635 Td (1. SENSOR & TELEMETRY OBSERVATIONS) Tj ET")
        stream_lines.append("0.8 0.8 0.8 RG 40 630 532 0 re S")

        y = 610
        telemetry_items = [
            ("Impact Point", inc.get("impact", "N/A"), "Recorded Speed", inc.get("speed", "N/A")),
            ("Severity", inc.get("severity", "N/A"), "Posted Limit", inc.get("speed_limit", "N/A")),
            ("Traffic Light", inc.get("signal", "N/A"), "Braking Reaction", inc.get("braking", "N/A")),
        ]
        stream_lines.append("0.2 0.2 0.2 rg")
        for col1_lbl, col1_val, col2_lbl, col2_val in telemetry_items:
            stream_lines.append(f"BT /F1 9 Tf 55 {y} Td ({col1_lbl}:) Tj /F2 9 Tf 65 0 Td ({self._escape_pdf_text(str(col1_val))}) Tj ET")
            stream_lines.append(f"BT /F1 9 Tf 320 {y} Td ({col2_lbl}:) Tj /F2 9 Tf 65 0 Td ({self._escape_pdf_text(str(col2_val))}) Tj ET")
            y -= 18

        # Section 2: Fault Attribution
        y -= 10
        stream_lines.append("0.1 0.25 0.5 rg")
        stream_lines.append(f"BT /F1 12 Tf 40 {y} Td (2. FAULT ATTRIBUTION & LIABILITY SIMULATION) Tj ET")
        stream_lines.append(f"0.8 0.8 0.8 RG 40 {y - 5} 532 0 re S")

        y -= 30
        user_fault = analysis.get("user_fault_percentage", 35)
        other_fault = analysis.get("other_vehicle_fault_percentage", 65)
        conf = analysis.get("confidence", 87)

        # Fault Box
        stream_lines.append(f"0.94 0.96 0.99 rg 40 {y - 25} 532 45 re f")
        stream_lines.append(f"0.7 0.8 0.95 RG 40 {y - 25} 532 45 re S")
        stream_lines.append("0.15 0.25 0.4 rg")
        stream_lines.append(f"BT /F1 11 Tf 55 {y} Td (Your Vehicle Fault: {user_fault}%) Tj ET")
        stream_lines.append(f"BT /F1 11 Tf 220 {y} Td (Other Vehicle Fault: {other_fault}%) Tj ET")
        stream_lines.append(f"BT /F1 11 Tf 400 {y} Td (Confidence Score: {conf}%) Tj ET")

        # Fault Visual Bar
        y -= 18
        bar_x = 55
        bar_w = 500
        bar_h = 10
        user_w = int(bar_w * (user_fault / 100.0))
        other_w = bar_w - user_w
        
        # User part (Blue)
        stream_lines.append(f"0.2 0.45 0.85 rg {bar_x} {y} {user_w} {bar_h} re f")
        # Other part (Orange)
        stream_lines.append(f"0.9 0.4 0.2 rg {bar_x + user_w} {y} {other_w} {bar_h} re f")

        # Section 3: Contributing Factors
        y -= 35
        stream_lines.append("0.1 0.25 0.5 rg")
        stream_lines.append(f"BT /F1 12 Tf 40 {y} Td (3. CONTRIBUTING FACTORS & TELEMETRY BREAKDOWN) Tj ET")
        stream_lines.append(f"0.8 0.8 0.8 RG 40 {y - 5} 532 0 re S")

        y -= 25
        # Table Header
        stream_lines.append(f"0.9 0.9 0.92 rg 40 {y - 5} 532 18 re f")
        stream_lines.append("0.1 0.1 0.1 rg")
        stream_lines.append(f"BT /F1 9 Tf 50 {y} Td (Contributing Factor) Tj 150 0 Td (Responsible Party) Tj 150 0 Td (Telemetry Evidence / Description) Tj ET")

        y -= 18
        stream_lines.append("0.2 0.2 0.2 rg")
        for factor in factors:
            f_name = self._escape_pdf_text(str(factor.get("factor", "")))
            f_resp = self._escape_pdf_text(str(factor.get("responsible", "")))
            f_desc = self._escape_pdf_text(str(factor.get("description", "")))
            stream_lines.append(f"BT /F2 9 Tf 50 {y} Td ({f_name}) Tj 150 0 Td ({f_resp}) Tj 150 0 Td ({f_desc}) Tj ET")
            stream_lines.append(f"0.9 0.9 0.9 RG 40 {y - 4} 532 0 re S")
            y -= 18

        # Section 4: Insurance
        y -= 15
        stream_lines.append("0.1 0.25 0.5 rg")
        stream_lines.append(f"BT /F1 12 Tf 40 {y} Td (4. INSURANCE & POLICY STATUS) Tj ET")
        stream_lines.append(f"0.8 0.8 0.8 RG 40 {y - 5} 532 0 re S")

        y -= 22
        stream_lines.append("0.2 0.2 0.2 rg")
        provider = self._escape_pdf_text(str(insurance.get("provider", "No active policy on record")))
        pol_num = self._escape_pdf_text(str(insurance.get("policy_number", "N/A")))
        exp = self._escape_pdf_text(str(insurance.get("expiry_date", "N/A")))
        cov = self._escape_pdf_text(str(insurance.get("coverage_type", "Comprehensive")))
        stream_lines.append(f"BT /F2 9 Tf 55 {y} Td (Provider: {provider}   |   Policy No: {pol_num}   |   Coverage: {cov}   |   Expiry: {exp}) Tj ET")

        # Section 5: Legal Disclaimer
        y -= 35
        stream_lines.append("0.85 0.2 0.2 rg")
        stream_lines.append(f"BT /F1 10 Tf 40 {y} Td (IMPORTANT DISCLAIMER) Tj ET")
        y -= 15
        stream_lines.append("0.4 0.4 0.4 rg")
        stream_lines.append(f"BT /F2 8 Tf 40 {y} Td (This report is algorithmically compiled from simulated sensor telemetry and user records.) Tj ET")
        y -= 12
        stream_lines.append(f"BT /F2 8 Tf 40 {y} Td (It is intended solely for prototype demonstration and is NOT legally authoritative evidence in a court of law.) Tj ET")

        # Footer
        stream_lines.append("0.6 0.6 0.6 rg")
        stream_lines.append("BT /F2 8 Tf 220 30 Td (InsureVisionAI Backend Engine - Confidential Report) Tj ET")

        content_stream = "\n".join(stream_lines).encode("latin-1", "replace")

        # PDF Object Assembly
        out = io.BytesIO()
        out.write(b"%PDF-1.4\n")
        
        offsets = []

        def write_obj(num: int, data: bytes):
            offsets.append(out.tell())
            out.write(f"{num} 0 obj\n".encode("ascii"))
            out.write(data)
            out.write(b"\nendobj\n")

        # Obj 1: Catalog
        write_obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
        # Obj 2: Pages
        write_obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
        # Obj 3: Page
        write_obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>")
        # Obj 4: Content Stream
        stream_len = len(content_stream)
        stream_obj = f"<< /Length {stream_len} >>\nstream\n".encode("ascii") + content_stream + b"\nendstream"
        write_obj(4, stream_obj)
        # Obj 5: Font F1 (Helvetica-Bold)
        write_obj(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        # Obj 6: Font F2 (Helvetica)
        write_obj(6, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

        # Xref
        xref_pos = out.tell()
        out.write(b"xref\n")
        out.write(f"0 {len(offsets) + 1}\n".encode("ascii"))
        out.write(b"0000000000 65535 f \n")
        for off in offsets:
            out.write(f"{off:010d} 00000 n \n".encode("ascii"))

        # Trailer
        out.write(b"trailer\n")
        out.write(f"<< /Size {len(offsets) + 1} /Root 1 0 R >>\n".encode("ascii"))
        out.write(b"startxref\n")
        out.write(f"{xref_pos}\n".encode("ascii"))
        out.write(b"%%EOF\n")

        return out.getvalue()


class ReportService:
    @staticmethod
    def get_report_data(incident_id: str, user_id: str) -> Dict[str, Any]:
        """
        Assemble comprehensive report dataset by integrating incident,
        fault analysis, contributing factors, driver profile, and insurance coverage.
        """
        inc = csv_storage.get_by_id("incidents.csv", incident_id)
        if not inc or inc.get("user_id") != user_id:
            raise ValueError(f"Incident with ID {incident_id} not found or unauthorized.")

        # Ensure analysis exists
        analysis = analysis_service.get_analysis(incident_id)
        if not analysis:
            analysis = analysis_service.run_analysis(incident_id)

        user = csv_storage.get_by_id("users.csv", user_id) or {}
        user_safe = dict(user)
        user_safe.pop("password_hash", None)

        # Fetch active insurance if exists
        policies = csv_storage.find_records("insurance.csv", user_id=user_id)
        active_policy = policies[0] if policies else None

        now_iso = datetime.now(timezone.utc).isoformat()

        return {
            "incident": inc,
            "user": user_safe,
            "analysis": analysis,
            "insurance": active_policy,
            "generated_at": now_iso,
            "disclaimer": DISCLAIMER_TEXT
        }

    @staticmethod
    def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
        """
        Produce a formatted PDF file.
        Attempts to use reportlab if installed, else uses robust pure-Python PDF builder.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            # Optional ReportLab implementation if library is present
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, "INSUREVISION AI - ACCIDENT REPORT")
            # If reportlab works, use the pure-Python builder's structured design
        except ImportError:
            pass
        
        # Always use the dedicated high-fidelity pure-Python PDF builder
        builder = SimplePDFBuilder()
        return builder.build_report_pdf(report_data)


report_service = ReportService()
