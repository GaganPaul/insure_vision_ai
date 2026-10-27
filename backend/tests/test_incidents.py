"""
Incident Management Tests for InsureVisionAI.
Tests incident retrieval, simulation, pagination, filtering, and cross-user authorization.
"""

from fastapi.testclient import TestClient


def test_get_demo_incident(client: TestClient, demo_auth_headers: dict):
    """Verify pre-seeded demo incident can be retrieved by demo user."""
    response = client.get("/api/v1/incidents/INC-24012234", headers=demo_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "INC-24012234"
    assert data["location"] == "MG Road Junction, Bangalore"
    assert data["severity"] == "Minor"
    assert data["speed"] == "48 km/h"
    assert data["speed_limit"] == "40 km/h"


def test_simulate_incident(client: TestClient, demo_auth_headers: dict):
    """Verify incident simulation endpoint generates a new incident and fault analysis."""
    payload = {
        "location": "Indiranagar 100ft Road, Bangalore",
        "speed": "50 km/h",
        "speed_limit": "40 km/h",
        "braking": "Delayed Braking",
        "signal": "Yellow",
        "impact": "Side Right"
    }
    response = client.post("/api/v1/incidents/simulate", json=payload, headers=demo_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "incident" in data
    assert "analysis" in data
    
    inc = data["incident"]
    assert inc["id"].startswith("INC-")
    assert inc["location"] == "Indiranagar 100ft Road, Bangalore"
    
    analysis = data["analysis"]
    assert analysis["user_fault_percentage"] + analysis["other_vehicle_fault_percentage"] == 100
    assert len(analysis["factors"]) >= 1


def test_list_incidents_with_filters(client: TestClient, demo_auth_headers: dict):
    """Verify filtering and pagination on incident listing."""
    response = client.get(
        "/api/v1/incidents?severity=Minor&page=1&limit=5",
        headers=demo_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["limit"] == 5
    for item in data["items"]:
        assert item["severity"] == "Minor"


def test_update_incident(client: TestClient, demo_auth_headers: dict):
    """Verify partial updating of an owned incident."""
    patch_payload = {"status": "Resolved", "severity": "Moderate"}
    response = client.patch(
        "/api/v1/incidents/INC-24012234",
        json=patch_payload,
        headers=demo_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Resolved"
    assert data["severity"] == "Moderate"


def test_cross_user_isolation(
    client: TestClient,
    demo_auth_headers: dict,
    secondary_auth_headers: dict
):
    """
    Verify strict user data isolation:
    Secondary user must NOT be able to view or delete Demo user's incident.
    """
    # Secondary user attempts to access demo user's incident
    response = client.get("/api/v1/incidents/INC-24012234", headers=secondary_auth_headers)
    assert response.status_code == 404

    # Secondary user attempts to delete demo user's incident
    delete_resp = client.delete("/api/v1/incidents/INC-24012234", headers=secondary_auth_headers)
    assert delete_resp.status_code == 404


def test_delete_incident(client: TestClient, demo_auth_headers: dict):
    """Verify owner can delete an incident and associated analysis."""
    # First simulate a temporary incident
    sim_resp = client.post("/api/v1/incidents/simulate", json={}, headers=demo_auth_headers)
    assert sim_resp.status_code == 201
    temp_id = sim_resp.json()["incident"]["id"]

    # Delete it
    del_resp = client.delete(f"/api/v1/incidents/{temp_id}", headers=demo_auth_headers)
    assert del_resp.status_code == 200

    # Ensure it's now gone
    get_resp = client.get(f"/api/v1/incidents/{temp_id}", headers=demo_auth_headers)
    assert get_resp.status_code == 404

