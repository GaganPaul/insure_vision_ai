"""
Pydantic schemas and models for InsureVisionAI.
Defines request and response structures with validation across all modules.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# Authentication & User Schemas
# ==========================================

class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: EmailStr = Field(..., description="Valid unique email address")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    phone: Optional[str] = Field(None, description="Contact phone number")
    vehicle_type: Optional[str] = Field("Four-Wheeler (Car)", description="Type of vehicle")
    vehicle_number: Optional[str] = Field(None, description="Vehicle registration number")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = ""
    vehicle_type: Optional[str] = ""
    vehicle_number: Optional[str] = ""
    created_at: str


# ==========================================
# Incident Schemas
# ==========================================

class IncidentBase(BaseModel):
    date: str = Field(..., description="Date of incident YYYY-MM-DD")
    time: str = Field(..., description="Time of incident HH:MM")
    location: str = Field(..., description="Location of incident")
    severity: str = Field("Minor", description="Severity (Minor, Moderate, Severe)")
    speed: str = Field(..., description="Speed at time of event e.g. '48 km/h'")
    speed_limit: str = Field(..., description="Posted speed limit e.g. '40 km/h'")
    braking: str = Field(..., description="Braking telemetry e.g. 'Minor Delay'")
    signal: str = Field(..., description="Traffic signal status e.g. 'Red'")
    impact: str = Field(..., description="Impact point e.g. 'Front Right'")


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    speed: Optional[str] = None
    speed_limit: Optional[str] = None
    braking: Optional[str] = None
    signal: Optional[str] = None
    impact: Optional[str] = None
    status: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: str
    user_id: str
    status: str
    created_at: str


class IncidentSimulateRequest(BaseModel):
    location: Optional[str] = "MG Road Junction, Bangalore"
    speed: Optional[str] = "48 km/h"
    speed_limit: Optional[str] = "40 km/h"
    braking: Optional[str] = "Minor Delay"
    signal: Optional[str] = "Red"
    impact: Optional[str] = "Front Right"
    severity: Optional[str] = "Minor"


# ==========================================
# Fault Analysis Schemas
# ==========================================

class ContributingFactor(BaseModel):
    factor: str
    responsible: str
    description: str


class FaultAnalysisResponse(BaseModel):
    incident_id: str
    user_fault_percentage: int = Field(..., ge=0, le=100)
    other_vehicle_fault_percentage: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    factors: List[ContributingFactor]
    analysis_type: str = "simulated"
    disclaimer: str = "This demonstration is not a legal determination of fault."


# ==========================================
# Insurance Schemas
# ==========================================

class InsuranceBase(BaseModel):
    provider: str = Field(..., description="Insurance company name")
    policy_number: str = Field(..., description="Policy number")
    expiry_date: str = Field(..., description="Policy expiry date YYYY-MM-DD")
    vehicle_type: str = Field(..., description="Vehicle type")
    coverage_type: str = Field(..., description="Coverage type (e.g. Comprehensive, Third-Party)")


class InsuranceCreate(InsuranceBase):
    pass


class InsuranceUpdate(BaseModel):
    provider: Optional[str] = None
    policy_number: Optional[str] = None
    expiry_date: Optional[str] = None
    vehicle_type: Optional[str] = None
    coverage_type: Optional[str] = None


class InsuranceResponse(InsuranceBase):
    id: str
    user_id: str
    updated_at: str


# ==========================================
# Nearby Services Schemas
# ==========================================

class ServiceResponse(BaseModel):
    id: str
    type: str
    name: str
    rating: float
    distance_km: float
    estimated_minutes: int
    phone: str
    address: str
    latitude: float
    longitude: float
    is_demo: bool = True
    disclaimer: str = "Demo service listing. Real-time availability is not guaranteed."


# ==========================================
# Physical Assistance Schemas
# ==========================================

class AssistanceCreate(BaseModel):
    incident_id: Optional[str] = None
    assistance_type: str = Field(..., description="Type: 'Rescue Team', 'Towing', or 'Medical Assistance'")
    location: str = Field(..., description="Current location description")


class AssistanceUpdate(BaseModel):
    status: str = Field(..., description="New status: 'Accepted', 'In Progress', 'Completed', or 'Cancelled'")


class AssistanceResponse(BaseModel):
    id: str
    user_id: str
    incident_id: Optional[str] = ""
    assistance_type: str
    location: str
    status: str
    created_at: str
    simulation_note: str = "Simulated assistance workflow. Real emergency services have not been dispatched."


# ==========================================
# Emergency SOS Schemas
# ==========================================

class SOSCreate(BaseModel):
    incident_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: str = Field(..., description="Current location description")


class SOSResponse(BaseModel):
    id: str
    user_id: str
    incident_id: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: str
    status: str
    created_at: str
    disclaimer: str = "Demo SOS request recorded. This is a prototype and does not contact 112/108 emergency dispatch."


# ==========================================
# Emergency Contacts Schemas
# ==========================================

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    relationship: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., min_length=5, max_length=20)


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone: Optional[str] = None


class ContactResponse(BaseModel):
    id: str
    user_id: str
    name: str
    relationship: str
    phone: str


# ==========================================
# Safety Tips Schemas
# ==========================================

class SafetyTipResponse(BaseModel):
    id: str
    tip: str
    category: str


# ==========================================
# Virtual Assistant (Chat) Schemas
# ==========================================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt or question")


class ChatResponse(BaseModel):
    reply: str
    mode: str = "rule_based"
    suggested_actions: Optional[List[str]] = None
    disclaimer: str = "This virtual assistant provides simulated guidance and does not substitute for professional emergency or legal advice."


# ==========================================
# Dashboard Schemas
# ==========================================

class DashboardStats(BaseModel):
    total_incidents: int
    safe_trips: int
    coverage_status: str
    protection_status: str


class DashboardResponse(BaseModel):
    user: UserResponse
    stats: DashboardStats
    latest_incident: Optional[IncidentResponse] = None
    active_policy: Optional[InsuranceResponse] = None
    daily_safety_tip: SafetyTipResponse


# ==========================================
# Accident Report Schemas
# ==========================================

class ReportSummary(BaseModel):
    incident: IncidentResponse
    user: UserResponse
    analysis: FaultAnalysisResponse
    insurance: Optional[InsuranceResponse] = None
    generated_at: str
    disclaimer: str

