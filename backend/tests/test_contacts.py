"""
Emergency Contacts API Tests for InsureVisionAI.
"""

from fastapi.testclient import TestClient


def test_get_demo_contacts(client: TestClient, demo_auth_headers: dict):
    """Verify demo user's pre-seeded emergency contacts."""
    response = client.get("/api/v1/contacts", headers=demo_auth_headers)
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) >= 2
    names = [c["name"] for c in contacts]
    assert "Priya Sharma" in names
    assert "Rohan Paul" in names


def test_create_and_delete_contact(client: TestClient, demo_auth_headers: dict):
    """Verify contact creation, updating, and deletion."""
    create_payload = {
        "name": "Dr. Sameer Joshi",
        "relationship": "Family Doctor",
        "phone": "+91 98444 55566"
    }
    create_resp = client.post("/api/v1/contacts", json=create_payload, headers=demo_auth_headers)
    assert create_resp.status_code == 201
    contact = create_resp.json()
    assert contact["name"] == "Dr. Sameer Joshi"
    contact_id = contact["id"]

    # Update
    patch_resp = client.put(
        f"/api/v1/contacts/{contact_id}",
        json={"relationship": "Primary Physician"},
        headers=demo_auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["relationship"] == "Primary Physician"

    # Delete
    del_resp = client.delete(f"/api/v1/contacts/{contact_id}", headers=demo_auth_headers)
    assert del_resp.status_code == 200

    # Ensure deleted
    contacts_after = client.get("/api/v1/contacts", headers=demo_auth_headers).json()
    assert contact_id not in [c["id"] for c in contacts_after]
