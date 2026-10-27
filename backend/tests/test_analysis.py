"""
Fault Analysis Tests for InsureVisionAI.
Tests telemetry-driven liability attribution, percentage sums, and contributing factors.
"""

from fastapi.testclient import TestClient


def test_get_demo_fault_analysis(client: TestClient, demo_auth_headers: dict):
    """Verify demo incident fault analysis matches specification."""
    response = client.get("/api/v1/analysis/INC-24012234", headers=demo_auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["incident_id"] == "INC-24012234"
    assert data["user_fault_percentage"] == 35
    assert data["other_vehicle_fault_percentage"] == 65
    assert data["confidence"] == 87
    assert data["analysis_type"] == "simulated"
    assert "not a legal determination of fault" in data["disclaimer"].lower()


def test_fault_percentage_sum_equals_100(client: TestClient, demo_auth_headers: dict):
    """Verify fault percentages strictly sum to 100% and stay within [0, 100]."""
    response = client.get("/api/v1/analysis/INC-24012234", headers=demo_auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    user_pct = data["user_fault_percentage"]
    other_pct = data["other_vehicle_fault_percentage"]
    
    assert 0 <= user_pct <= 100
    assert 0 <= other_pct <= 100
    assert user_pct + other_pct == 100


def test_get_contributing_factors(client: TestClient, demo_auth_headers: dict):
    """Verify contributing factors breakdown for an incident."""
    response = client.get("/api/v1/analysis/INC-24012234/factors", headers=demo_auth_headers)
    assert response.status_code == 200
    factors = response.json()
    assert isinstance(factors, list)
    assert len(factors) >= 3

    factor_names = [f["factor"] for f in factors]
    assert "Excessive Speed" in factor_names
    assert "Signal Violation" in factor_names
    assert "Late Braking" in factor_names

    for factor in factors:
        assert "responsible" in factor
        assert "description" in factor


def test_analysis_cross_user_rejection(
    client: TestClient,
    secondary_auth_headers: dict
):
    """Verify other users cannot access analysis of an incident they do not own."""
    response = client.get("/api/v1/analysis/INC-24012234", headers=secondary_auth_headers)
    assert response.status_code == 404

