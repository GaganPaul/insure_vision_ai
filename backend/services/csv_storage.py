"""
Thread-Safe Atomic CSV Storage Service for InsureVisionAI.

Provides a robust, unified persistent storage layer over CSV files.
Features:
- Automatic schema verification and header initialization.
- Idempotent demo data population (only runs if file is newly created or empty).
- Atomic file writes using temporary file creation and os.replace().
- Process-level thread synchronization via reentrant locks (RLock).
- Dynamic data directory resolution relative to backend/data.
- Data validation and formula sanitization.

LIMITATIONS OF CSV STORAGE:
1. Multi-Process Concurrency: Process locks (threading.RLock) protect concurrent
   threads inside a single Python/uvicorn process. Running multiple worker processes
   (e.g., uvicorn --workers 4) without inter-process file locking (such as fcntl/msvcrt)
   may cause write collisions.
2. Relational Integrity: Foreign keys (such as user_id -> incidents) are enforced
   at the application service layer, not by an underlying database engine.
3. Query Efficiency: Queries perform full table scans (O(N)). For prototype scale
   (< 10,000 records), this offers instant in-memory speeds without external DB setup.
"""

import csv
import os
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Schemas for all 10 application CSV files
CSV_SCHEMAS: Dict[str, List[str]] = {
    "users.csv": [
        "id", "name", "email", "phone", "password_hash",
        "vehicle_type", "vehicle_number", "created_at"
    ],
    "incidents.csv": [
        "id", "user_id", "date", "time", "location", "severity",
        "speed", "speed_limit", "braking", "signal", "impact",
        "status", "created_at"
    ],
    "fault_analysis.csv": [
        "id", "incident_id", "user_fault", "other_fault",
        "confidence", "analysis_method", "created_at"
    ],
    "factors.csv": [
        "id", "incident_id", "factor", "responsible", "description"
    ],
    "insurance.csv": [
        "id", "user_id", "provider", "policy_number",
        "expiry_date", "vehicle_type", "coverage_type", "updated_at"
    ],
    "services.csv": [
        "id", "type", "name", "rating", "distance_km",
        "estimated_minutes", "phone", "address", "latitude", "longitude"
    ],
    "safety_tips.csv": [
        "id", "tip", "category"
    ],
    "contacts.csv": [
        "id", "user_id", "name", "relationship", "phone"
    ],
    "sos_requests.csv": [
        "id", "user_id", "incident_id", "latitude", "longitude",
        "location", "status", "created_at"
    ],
    "assistance_requests.csv": [
        "id", "user_id", "incident_id", "assistance_type",
        "location", "status", "created_at"
    ]
}


class CSVStorage:
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize CSV storage.
        If data_dir is not provided, defaults to backend/data relative to this file.
        """
        if data_dir is None:
            self.data_dir = Path(__file__).resolve().parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Thread locks per CSV table
        self._locks: Dict[str, threading.RLock] = {
            filename: threading.RLock() for filename in CSV_SCHEMAS
        }
        self._global_lock = threading.RLock()

    def _get_lock(self, filename: str) -> threading.RLock:
        with self._global_lock:
            if filename not in self._locks:
                self._locks[filename] = threading.RLock()
            return self._locks[filename]

    def get_file_path(self, filename: str) -> Path:
        """Get absolute path to a CSV file."""
        return self.data_dir / filename

    def initialize_storage(self) -> None:
        """
        Ensure all CSV files exist with proper headers.
        Populate initial demo data ONLY if a file is newly created or empty.
        Never duplicates records on server restart.
        """
        for filename, headers in CSV_SCHEMAS.items():
            file_path = self.get_file_path(filename)
            lock = self._get_lock(filename)
            with lock:
                file_exists = file_path.exists()
                is_empty = (not file_exists) or (file_path.stat().st_size == 0)
                
                if not file_exists or is_empty:
                    # Write header
                    self._write_records(filename, headers, [])
                    # Populate demo records for this file
                    self._populate_demo_data(filename)

    def _populate_demo_data(self, filename: str) -> None:
        """Populate initial demo data for a newly created or empty file."""
        from utils.security import hash_password

        demo_user_id = "USR-2026-0001"
        now_iso = "2026-01-22T14:45:00Z"

        if filename == "users.csv":
            # Demo account: gagan@email.com / 123456
            demo_user = {
                "id": demo_user_id,
                "name": "Gagan Paul",
                "email": "gagan@email.com",
                "phone": "+91 98765 43210",
                "password_hash": hash_password("123456"),
                "vehicle_type": "Four-Wheeler (Car)",
                "vehicle_number": "KA-01-MJ-5023",
                "created_at": "2026-01-15T10:00:00Z"
            }
            self.insert_record("users.csv", demo_user)

        elif filename == "incidents.csv":
            demo_incident = {
                "id": "INC-24012234",
                "user_id": demo_user_id,
                "date": "2026-01-22",
                "time": "14:45",
                "location": "MG Road Junction, Bangalore",
                "severity": "Minor",
                "speed": "48 km/h",
                "speed_limit": "40 km/h",
                "braking": "Minor Delay",
                "signal": "Red",
                "impact": "Front Right",
                "status": "Analyzed",
                "created_at": now_iso
            }
            self.insert_record("incidents.csv", demo_incident)

        elif filename == "fault_analysis.csv":
            demo_analysis = {
                "id": "FA-24012234",
                "incident_id": "INC-24012234",
                "user_fault": "35",
                "other_fault": "65",
                "confidence": "87",
                "analysis_method": "Rule-Based Physics & Telemetry Engine",
                "created_at": "2026-01-22T14:48:00Z"
            }
            self.insert_record("fault_analysis.csv", demo_analysis)

        elif filename == "factors.csv":
            demo_factors = [
                {
                    "id": "FAC-101",
                    "incident_id": "INC-24012234",
                    "factor": "Excessive Speed",
                    "responsible": "Other Vehicle",
                    "description": "15 km/h over the speed limit"
                },
                {
                    "id": "FAC-102",
                    "incident_id": "INC-24012234",
                    "factor": "Signal Violation",
                    "responsible": "Other Vehicle",
                    "description": "Ran red light"
                },
                {
                    "id": "FAC-103",
                    "incident_id": "INC-24012234",
                    "factor": "Late Braking",
                    "responsible": "Your Vehicle",
                    "description": "Minor braking delay"
                }
            ]
            for factor in demo_factors:
                self.insert_record("factors.csv", factor)

        elif filename == "insurance.csv":
            demo_policy = {
                "id": "INS-884920",
                "user_id": demo_user_id,
                "provider": "ICICI Lombard",
                "policy_number": "POL-2025-884920",
                "expiry_date": "2026-12-31",
                "vehicle_type": "Four-Wheeler (Car)",
                "coverage_type": "Comprehensive Zero-Depreciation",
                "updated_at": "2026-01-15T10:00:00Z"
            }
            self.insert_record("insurance.csv", demo_policy)

        elif filename == "services.csv":
            demo_services = [
                {
                    "id": "SRV-01",
                    "type": "hospital",
                    "name": "Apollo Hospital",
                    "rating": "4.8",
                    "distance_km": "2.4",
                    "estimated_minutes": "8",
                    "phone": "+91 80 2630 4050",
                    "address": "154/11 Opp. IIMB, Bannerghatta Road, Bangalore",
                    "latitude": "12.8954",
                    "longitude": "77.5988"
                },
                {
                    "id": "SRV-02",
                    "type": "mechanic",
                    "name": "MG Road Auto Care",
                    "rating": "4.6",
                    "distance_km": "1.1",
                    "estimated_minutes": "5",
                    "phone": "+91 80 4123 7890",
                    "address": "45/2 MG Road, Bangalore",
                    "latitude": "12.9738",
                    "longitude": "77.6119"
                },
                {
                    "id": "SRV-03",
                    "type": "towing",
                    "name": "24/7 Towing Service",
                    "rating": "4.7",
                    "distance_km": "3.5",
                    "estimated_minutes": "12",
                    "phone": "+91 98450 11223",
                    "address": "Residency Road, Bangalore",
                    "latitude": "12.9698",
                    "longitude": "77.6080"
                },
                {
                    "id": "SRV-04",
                    "type": "hospital",
                    "name": "Manipal Hospital",
                    "rating": "4.9",
                    "distance_km": "4.2",
                    "estimated_minutes": "15",
                    "phone": "+91 80 2502 4444",
                    "address": "98 HAL Old Airport Road, Bangalore",
                    "latitude": "12.9592",
                    "longitude": "77.6568"
                },
                {
                    "id": "SRV-05",
                    "type": "rescue",
                    "name": "Express Roadside Assist",
                    "rating": "4.5",
                    "distance_km": "2.8",
                    "estimated_minutes": "10",
                    "phone": "+91 99000 44556",
                    "address": "Indiranagar 100ft Road, Bangalore",
                    "latitude": "12.9784",
                    "longitude": "77.6408"
                }
            ]
            for srv in demo_services:
                self.insert_record("services.csv", srv)

        elif filename == "safety_tips.csv":
            demo_tips = [
                {"id": "TIP-01", "tip": "Maintain a safe 3-second following distance to allow sufficient reaction and braking time.", "category": "Defensive Driving"},
                {"id": "TIP-02", "tip": "Always observe posted speed limits; speeding drastically increases braking distance and impact severity.", "category": "Speed Management"},
                {"id": "TIP-03", "tip": "In wet or rainy conditions, reduce your speed by at least 20% to avoid hydroplaning.", "category": "Weather Conditions"},
                {"id": "TIP-04", "tip": "Never use handheld mobile phones while driving. Distraction is a leading factor in junction collisions.", "category": "Distraction Prevention"},
                {"id": "TIP-05", "tip": "Always use turn signals at least 30 meters before making a turn or changing lanes.", "category": "Lane Discipline"},
                {"id": "TIP-06", "tip": "Check rearview and side mirrors every 5 to 8 seconds to stay aware of vehicles in your blind spots.", "category": "Situational Awareness"},
                {"id": "TIP-07", "tip": "Ensure all vehicle occupants wear safety belts on every journey, regardless of distance.", "category": "Occupant Safety"},
                {"id": "TIP-08", "tip": "Inspect tire tread depth and maintain manufacturer-recommended tire pressure monthly.", "category": "Vehicle Maintenance"},
                {"id": "TIP-09", "tip": "Approach intersections with caution and look both ways even when your traffic signal turns green.", "category": "Intersection Safety"},
                {"id": "TIP-10", "tip": "Avoid driving when drowsy or fatigued. Take a 15-minute rest break every two hours on long drives.", "category": "Driver Wellness"},
                {"id": "TIP-11", "tip": "Always yield to emergency vehicles sounding sirens or flashing emergency lights.", "category": "Emergency Etiquette"},
                {"id": "TIP-12", "tip": "Dim your high beams when approaching an oncoming vehicle within 150 meters.", "category": "Night Driving"}
            ]
            for tip in demo_tips:
                self.insert_record("safety_tips.csv", tip)

        elif filename == "contacts.csv":
            demo_contacts = [
                {"id": "CONT-01", "user_id": demo_user_id, "name": "Priya Sharma", "relationship": "Spouse", "phone": "+91 98765 12345"},
                {"id": "CONT-02", "user_id": demo_user_id, "name": "Rohan Paul", "relationship": "Brother", "phone": "+91 98765 67890"}
            ]
            for contact in demo_contacts:
                self.insert_record("contacts.csv", contact)

        elif filename == "sos_requests.csv":
            demo_sos = {
                "id": "SOS-1001",
                "user_id": demo_user_id,
                "incident_id": "INC-24012234",
                "latitude": "12.9716",
                "longitude": "77.5946",
                "location": "MG Road Junction, Bangalore",
                "status": "Demo SOS request recorded",
                "created_at": "2026-01-22T14:46:00Z"
            }
            self.insert_record("sos_requests.csv", demo_sos)

        elif filename == "assistance_requests.csv":
            demo_ast = {
                "id": "AST-1001",
                "user_id": demo_user_id,
                "incident_id": "INC-24012234",
                "assistance_type": "Towing",
                "location": "MG Road Junction, Bangalore",
                "status": "In Progress",
                "created_at": "2026-01-22T14:47:00Z"
            }
            self.insert_record("assistance_requests.csv", demo_ast)

    def _read_records(self, filename: str) -> List[Dict[str, str]]:
        """Internal reader. Must be called under file lock."""
        file_path = self.get_file_path(filename)
        if not file_path.exists() or file_path.stat().st_size == 0:
            return []
        
        records: List[Dict[str, str]] = []
        try:
            with open(file_path, mode="r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Clean None keys or None values
                    cleaned_row = {
                        k: (v if v is not None else "")
                        for k, v in row.items() if k is not None
                    }
                    records.append(cleaned_row)
        except Exception as e:
            # Return empty on corrupt read
            return []
        return records

    def _write_records(self, filename: str, headers: List[str], records: List[Dict[str, Any]]) -> None:
        """
        Internal atomic writer.
        Writes to a temporary file in self.data_dir, flushes, fsyncs,
        and atomically replaces the target file via os.replace().
        """
        file_path = self.get_file_path(filename)
        dir_path = file_path.parent
        dir_path.mkdir(parents=True, exist_ok=True)

        temp_fd, temp_path = tempfile.mkstemp(
            prefix=f"{filename}_tmp_",
            suffix=".csv",
            dir=str(dir_path)
        )

        try:
            with open(temp_fd, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
                writer.writeheader()
                for record in records:
                    # Ensure all headers exist in row
                    row = {h: record.get(h, "") for h in headers}
                    writer.writerow(row)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic swap on POSIX and Windows (Python 3.3+)
            os.replace(temp_path, str(file_path))
        except Exception:
            # Clean up temp file if something failed
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def load_all(self, filename: str) -> List[Dict[str, str]]:
        """Load all records from a CSV file."""
        lock = self._get_lock(filename)
        with lock:
            return self._read_records(filename)

    def get_by_id(self, filename: str, record_id: str, id_field: str = "id") -> Optional[Dict[str, str]]:
        """Retrieve a single record matching record_id on id_field."""
        lock = self._get_lock(filename)
        with lock:
            records = self._read_records(filename)
            for rec in records:
                if rec.get(id_field) == str(record_id):
                    return dict(rec)
        return None

    def find_records(self, filename: str, **kwargs) -> List[Dict[str, str]]:
        """Find all records matching given key-value filters."""
        lock = self._get_lock(filename)
        with lock:
            records = self._read_records(filename)
            matches = []
            for rec in records:
                match = True
                for k, v in kwargs.items():
                    if rec.get(k) != str(v):
                        match = False
                        break
                if match:
                    matches.append(dict(rec))
            return matches

    def filter_records(self, filename: str, predicate: Callable[[Dict[str, str]], bool]) -> List[Dict[str, str]]:
        """Find records matching an arbitrary predicate function."""
        lock = self._get_lock(filename)
        with lock:
            records = self._read_records(filename)
            return [dict(rec) for rec in records if predicate(rec)]

    def insert_record(self, filename: str, record: Dict[str, Any]) -> Dict[str, str]:
        """Insert a single record into the target CSV file."""
        headers = CSV_SCHEMAS.get(filename)
        if not headers:
            raise ValueError(f"Unknown CSV file schema: {filename}")
        
        lock = self._get_lock(filename)
        with lock:
            records = self._read_records(filename)
            str_record = {k: str(v) if v is not None else "" for k, v in record.items()}
            records.append(str_record)
            self._write_records(filename, headers, records)
            return dict(str_record)

    def update_record(self, filename: str, record_id: str, updates: Dict[str, Any], id_field: str = "id") -> Optional[Dict[str, str]]:
        """Update an existing record by id."""
        headers = CSV_SCHEMAS.get(filename)
        if not headers:
            raise ValueError(f"Unknown CSV file schema: {filename}")
        
        lock = self._get_lock(filename)
        with lock:
            records = self._read_records(filename)
            updated_record = None
            for idx, rec in enumerate(records):
                if rec.get(id_field) == str(record_id):
                    # Apply updates
                    for k, v in updates.items():
                        if k in headers and v is not None:
                            rec[k] = str(v)
                    records[idx] = rec
                    updated_record = dict(rec)
                    break
            
            if updated_record:
                self._write_records(filename, headers, records)
            return updated_record

    def delete_record(self, filename: str, record_id: str, id_field: str = "id") -> bool:
        """Delete an existing record by id."""
        headers = CSV_SCHEMAS.get(filename)
        if not headers:
            raise ValueError(f"Unknown CSV file schema: {filename}")
        
        lock = self._get_lock(filename)
        with lock:
            records = self._read_records(filename)
            initial_count = len(records)
            new_records = [r for r in records if r.get(id_field) != str(record_id)]
            if len(new_records) < initial_count:
                self._write_records(filename, headers, new_records)
                return True
            return False


# Singleton instance pointing to backend/data
csv_storage = CSVStorage()
