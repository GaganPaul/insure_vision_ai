"""
Insurance, Services, SOS, Reports, and Persistence Tests for InsureVisionAI.
"""

from fastapi.testclient import TestClient


def test_get_demo_insurance(client: TestClient, demo_auth_headers: dict):
    """Verify pre-seeded insurance policy is returned for demo user."""
    response = client.get("/api/v1/insurance", headers=demo_auth_headers)
    assert response.status_code == 200
    policies = response.json()
    assert len(policies) >= 1
    policy = policies[0]
    assert policy["provider"] == "ICICI Lombard"
    assert policy["policy_number"] == "POL-2025-884920"


def test_create_insurance_policy(client: TestClient, demo_auth_headers: dict):
    """Verify registration of a new insurance policy."""
    payload = {
        "provider": "HDFC ERGO",
        "policy_number": "HDFC-2026-99001",
        "expiry_date": "2027-06-30",
        "vehicle_type": "Four-Wheeler (Car)",
        "coverage_type": "Zero Depreciation Comprehensive"
    }
    response = client.post("/api/v1/insurance", json=payload, headers=demo_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["provider"] == "HDFC ERGO"
    assert data["policy_number"] == "HDFC-2026-99001"
    assert "id" in data


def test_invalid_insurance_expiry_date(client: TestClient, demo_auth_headers: dict):
    """Verify invalid date format is rejected."""
    payload = {
        "provider": "Bajaj Allianz",
        "policy_number": "BA-12345",
        "expiry_date": "31/12/2026",  # Invalid, requires YYYY-MM-DD
        "vehicle_type": "Car",
        "coverage_type": "Comprehensive"
    }
    response = client.post("/api/v1/insurance", json=payload, headers=demo_auth_headers)
    assert response.status_code == 400


def test_nearby_services_filtering(client: TestClient):
    """Verify nearby services filter by type and distance."""
    # Filter by hospital
    hosp_resp = client.get("/api/v1/services?type=hospital")
    assert hosp_resp.status_code == 200
    hospitals = hosp_resp.json()
    assert len(hospitals) >= 2
    for h in hospitals:
        assert h["type"] == "hospital"
        assert h["is_demo"] is True

    # Filter with coordinates (MG Road, Bangalore: 12.9716, 77.5946)
    coord_resp = client.get("/api/v1/services?latitude=12.9716&longitude=77.5946&radius_km=10")
    assert coord_resp.status_code == 200
    nearby = coord_resp.json()
    assert len(nearby) >= 1
    # Check distance calculation
    for s in nearby:
        assert s["distance_km"] <= 10.0
        assert s["estimated_minutes"] >= 1


def test_emergency_sos_dispatch(client: TestClient, demo_auth_headers: dict):
    """Verify SOS request recording and status message."""
    payload = {
        "incident_id": "INC-24012234",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "location": "MG Road Junction, Bangalore"
    }
    response = client.post("/api/v1/sos", json=payload, headers=demo_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Demo SOS request recorded"
    assert "disclaimer" in data


def test_assistance_request_workflow(client: TestClient, demo_auth_headers: dict):
    """Verify physical assistance creation and valid lifecycle status transitions."""
    create_payload = {
        "incident_id": "INC-24012234",
        "assistance_type": "Towing",
        "location": "MG Road, Bangalore"
    }
    resp = client.post("/api/v1/assistance", json=create_payload, headers=demo_auth_headers)
    assert resp.status_code == 201
    ast = resp.json()
    assert ast["status"] == "Requested"
    req_id = ast["id"]

    # Transition to Accepted
    patch1 = client.patch(f"/api/v1/assistance/{req_id}", json={"status": "Accepted"}, headers=demo_auth_headers)
    assert patch1.status_code == 200
    assert patch1.json()["status"] == "Accepted"

    # Transition to In Progress
    patch2 = client.patch(f"/api/v1/assistance/{req_id}", json={"status": "In Progress"}, headers=demo_auth_headers)
    assert patch2.status_code == 200
    assert patch2.json()["status"] == "In Progress"

    # Invalid jump (In Progress -> Requested is not allowed)
    invalid_patch = client.patch(f"/api/v1/assistance/{req_id}", json={"status": "Requested"}, headers=demo_auth_headers)
    assert invalid_patch.status_code == 400


def test_accident_report_json_and_pdf(client: TestClient, demo_auth_headers: dict):
    """Verify accident report retrieval and PDF download."""
    # JSON Report
    json_resp = client.get("/api/v1/reports/INC-24012234", headers=demo_auth_headers)
    assert json_resp.status_code == 200
    report = json_resp.json()
    assert "incident" in report
    assert "analysis" in report
    assert "user" in report

    # PDF Download
    pdf_resp = client.get("/api/v1/reports/INC-24012234/download?format=pdf", headers=demo_auth_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-1.4")
    assert len(pdf_resp.content) > 500


def test_chat_virtual_assistant(client: TestClient):
    """Verify rule-based chat responds with safety guidance."""
    resp = client.post("/api/v1/chat", json={"message": "What should I do after an accident?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Check for Injuries" in data["reply"]
    assert data["mode"] == "rule_based"
    assert "disclaimer" in data


def test_dashboard_aggregation(client: TestClient, demo_auth_headers: dict):
    """Verify dashboard summarizes actual incident counts and coverage status."""
    resp = client.get("/api/v1/dashboard", headers=demo_auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["stats"]["total_incidents"] >= 1
    assert data["stats"]["coverage_status"] in ("Active", "Expired", "No Policy")
    assert "daily_safety_tip" in data
