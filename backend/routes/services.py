"""
Nearby Emergency Services Routes for InsureVisionAI.
Provides directory and proximity search for hospitals, mechanics, towing,
and rescue teams with Haversine distance calculations.
"""

import math
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from models.schemas import ServiceResponse
from services.csv_storage import csv_storage

router = APIRouter(prefix="/services", tags=["Nearby Emergency Services"])


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two coordinates in kilometers
    using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


@router.get("", response_model=List[ServiceResponse])
def get_nearby_services(
    type: Optional[str] = Query(None, description="Filter by service type: 'hospital', 'mechanic', 'towing', 'rescue'"),
    latitude: Optional[float] = Query(None, description="Current latitude"),
    longitude: Optional[float] = Query(None, description="Current longitude"),
    radius_km: Optional[float] = Query(None, description="Search radius in kilometers")
):
    """
    Query nearby emergency and roadside services.
    Supports filtering by service type and calculates approximate distances
    using the Haversine formula when coordinates are supplied.
    """
    services = csv_storage.load_all("services.csv")
    results = []

    for srv in services:
        # Filter by type if requested
        if type and srv.get("type", "").lower() != type.lower():
            continue

        srv_lat = float(srv.get("latitude", 0.0))
        srv_lon = float(srv.get("longitude", 0.0))
        base_dist = float(srv.get("distance_km", 2.0))
        base_mins = int(srv.get("estimated_minutes", 10))

        # If user coordinates are provided, compute geographic distance
        if latitude is not None and longitude is not None and srv_lat and srv_lon:
            computed_dist = haversine_distance(latitude, longitude, srv_lat, srv_lon)
            if radius_km and computed_dist > radius_km:
                continue
            # Assume 30 km/h average city transit speed
            computed_mins = max(1, int(round((computed_dist / 30.0) * 60)))
            dist_km = computed_dist
            est_mins = computed_mins
        else:
            dist_km = base_dist
            est_mins = base_mins

        results.append(
            ServiceResponse(
                id=srv.get("id", ""),
                type=srv.get("type", ""),
                name=srv.get("name", ""),
                rating=float(srv.get("rating", 4.5)),
                distance_km=dist_km,
                estimated_minutes=est_mins,
                phone=srv.get("phone", ""),
                address=srv.get("address", ""),
                latitude=srv_lat,
                longitude=srv_lon,
                is_demo=True
            )
        )

    # Sort results by distance ascending if coordinates provided
    if latitude is not None and longitude is not None:
        results.sort(key=lambda s: s.distance_km)

    return results


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service_by_id(service_id: str):
    """
    Retrieve single service details.
    """
    srv = csv_storage.get_by_id("services.csv", service_id)
    if not srv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID '{service_id}' not found."
        )

    return ServiceResponse(
        id=srv.get("id", ""),
        type=srv.get("type", ""),
        name=srv.get("name", ""),
        rating=float(srv.get("rating", 4.5)),
        distance_km=float(srv.get("distance_km", 2.0)),
        estimated_minutes=int(srv.get("estimated_minutes", 10)),
        phone=srv.get("phone", ""),
        address=srv.get("address", ""),
        latitude=float(srv.get("latitude", 0.0)),
        longitude=float(srv.get("longitude", 0.0)),
        is_demo=True
    )

