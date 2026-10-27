# InsureVisionAI Backend Engine

InsureVisionAI is an intelligent, privacy-first road safety, accident analysis, insurance claim support, and emergency assistance backend platform built with **Python 3.11+**, **FastAPI**, and an atomic, thread-safe **CSV persistent storage engine**.

---

## 🌟 Key Capabilities

1. **Deterministic Incident Simulation & Ingestion**: Ingests vehicle telemetry (speed, posted limit, braking latency, traffic signals, impact zone) with automatic liability evaluation.
2. **Explainable Fault Attribution Engine**: Rule-based physics and telemetry heuristics compute fault percentages between the insured driver and third parties with accompanying contributing factor breakdown.
3. **Multi-Format Accident Reports**: Generates downloadable structured JSON and standard-compliant PDF accident dossiers for insurer claims submission.
4. **Rule-Based Virtual Assistant**: Safety-first guidance covering immediate accident steps, FIR protocols, towing, medical dispatch, and claim settlement.
5. **Proximity-Aware Emergency Services**: Haversine formula calculation for finding hospitals, authorized mechanics, 24/7 towing, and rescue services sorted by distance and estimated travel time.
6. **Simulated Assistance & SOS**: One-touch SOS logging with coordinate tracking and physical assistance dispatch lifecycle tracking (`Requested` → `Accepted` → `In Progress` → `Completed`).
7. **Policy & Insurance Hub**: Manages motor insurance policies (ICICI Lombard, HDFC ERGO, Bajaj Allianz, Tata AIG) and evaluates real-time coverage status.
8. **Secure Authentication & RBAC**: Strict JWT bearer authentication with bcrypt password hashing and user record isolation.

---

## 📁 Project Structure

```text
InsureVisionAI/
└── backend/
    ├── main.py                     # FastAPI application entrypoint & middleware
    ├── requirements.txt            # Application dependencies
    ├── pytest.ini                  # Pytest runner configuration
    ├── .env.example                # Environment variable template
    ├── .env                        # Active local configuration
    ├── README.md                   # Comprehensive backend documentation
    ├── routes/
    │   ├── auth.py                 # /api/v1/auth (signup, login, me, logout)
    │   ├── dashboard.py            # /api/v1/dashboard & safety tips
    │   ├── incidents.py            # /api/v1/incidents (CRUD & simulation)
    │   ├── analysis.py             # /api/v1/analysis (attribution & factors)
    │   ├── insurance.py            # /api/v1/insurance (policy management)
    │   ├── services.py             # /api/v1/services (nearby emergency search)
    │   ├── chat.py                 # /api/v1/chat (rule-based virtual assistant)
    │   ├── sos.py                  # /api/v1/sos & /api/v1/assistance
    │   ├── reports.py              # /api/v1/reports (JSON & PDF download)
    │   └── contacts.py             # /api/v1/contacts (emergency contacts)
    ├── models/
    │   └── schemas.py              # Pydantic v2 schemas and validation models
    ├── services/
    │   ├── csv_storage.py          # Atomic, thread-safe CSV persistence engine
    │   ├── incident_service.py     # Incident business logic & pagination
    │   ├── analysis_service.py     # Telemetry & liability calculation engine
    │   ├── report_service.py       # JSON compiler & pure-Python PDF builder
    │   └── chat_service.py         # Conversational assistant rules & intents
    ├── utils/
    │   ├── security.py             # Bcrypt hashing & PyJWT token utilities
    │   └── validators.py           # Email, phone, date & CSV sanitization
    ├── data/                       # Persistent CSV storage directory
    │   ├── users.csv               # User profiles and password hashes
    │   ├── incidents.csv           # Telemetry observations & accident logs
    │   ├── fault_analysis.csv      # Liability percentages & confidence
    │   ├── factors.csv             # Contributing factors & liability parties
    │   ├── insurance.csv           # Policy schedules and coverage types
    │   ├── services.csv            # Hospital, mechanic, and towing directory
    │   ├── safety_tips.csv         # Curated defensive driving tips
    │   ├── contacts.csv            # Trusted emergency contacts
    │   ├── sos_requests.csv        # Emergency SOS telemetry records
    │   └── assistance_requests.csv  # Towing & rescue team dispatch logs
    ├── reports/                    # Generated document storage
    └── tests/
        ├── conftest.py             # Test fixtures & isolated temporary CSVs
        ├── test_auth.py            # Signup, login, token & health tests
        ├── test_incidents.py       # Simulation, CRUD, and pagination tests
        ├── test_analysis.py        # Fault calculation & factor tests
        ├── test_insurance.py       # Insurance, services, SOS & report tests
        └── test_contacts.py        # Emergency contact management tests
```

---

## ⚙️ Environment Setup & Installation

### 1. Prerequisites
- Python 3.11 or higher
- PowerShell, Command Prompt, or Bash

### 2. Create and Activate Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Activate on Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default `.env` settings:
```env
APP_NAME=InsureVisionAI
APP_ENV=development
API_V1_PREFIX=/api/v1
JWT_SECRET_KEY=insure_vision_ai_super_secret_jwt_key_2026_demo_secure_key_123456
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
HOST=127.0.0.1
PORT=8000
```

---

## 🚀 Running the Application

Start the development server with Uvicorn:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Once started:
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🔑 Pre-Seeded Demo Credentials

All data files are automatically initialized on startup without duplicating records. Use the demo account below for evaluation:

| Attribute | Demo Account Value |
| :--- | :--- |
| **Email** | `nuzair@email.com` |
| **Password** | `123456` |
| **Name** | Nuzair |
| **Vehicle** | Four-Wheeler (Car) - `KA-01-MJ-5023` |
| **Pre-Seeded Incident** | `INC-24012234` (MG Road Junction, Bangalore) |
| **Insurance Provider** | ICICI Lombard (`POL-2025-884920`) |

---

## 💾 CSV Storage Engine Architecture

The persistence layer (`services/csv_storage.py`) implements a zero-database storage abstraction using standard CSV files:

- **Automatic Initialization**: On server startup, all 10 CSV schemas and headers are verified. Demo records are inserted **only** if the corresponding file is newly created or empty.
- **Atomic File Writes**: Records are serialized to an ephemeral temporary file (`tempfile.mkstemp`) within the data directory, flushed, synced via `os.fsync()`, and atomically swapped into place using `os.replace()`. This prevents file corruption during server restarts or sudden terminations.
- **Thread Concurrency**: Reentrant locks (`threading.RLock`) are maintained per CSV file to serialize concurrent request threads within the application worker.
- **Formula Injection Mitigation**: All textual fields undergo sanitization (`utils/validators.py`) to prevent CSV formula injection (`=`, `+`, `-`, `@`) when files are opened in external spreadsheet software.

### Limitations of CSV Storage
1. **Multi-Process Concurrency**: Process-level thread locks synchronize threads within a single Python process. Running multiple Uvicorn workers (`--workers 4`) without OS-level file locking can cause race conditions during concurrent writes. For scale, migrate the storage layer to PostgreSQL.
2. **Lack of Relational FK Enforcement**: Referential integrity (e.g. deleting an incident also deletes associated factors) is managed programmatically at the application service tier.
3. **Query Complexity**: Filtering operations perform table scans ($O(N)$), which is optimal for prototype datasets (<10,000 rows) but not intended for big-data analytical workloads.

---

## 📡 API Reference Overview

All application routes are served under `/api/v1`:

### 1. Authentication (`/api/v1/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/signup` | Register new user account | No |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access token | No |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Yes |
| `POST` | `/api/v1/auth/logout` | Client token invalidation advisory | Yes |

### 2. Dashboard & Safety Tips
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard` | Aggregated user stats, latest incident & coverage | Yes |
| `GET` | `/api/v1/safety-tips` | List all 12 defensive road safety tips | No |
| `GET` | `/api/v1/safety-tips/daily` | Deterministic daily safety tip rotation | No |

### 3. Incidents (`/api/v1/incidents`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/incidents` | List user incidents with severity/status filters & pagination | Yes |
| `GET` | `/api/v1/incidents/{incident_id}` | Retrieve incident details by ID | Yes |
| `POST` | `/api/v1/incidents/simulate` | Simulate an accident with deterministic sensor telemetry | Yes |
| `PATCH` | `/api/v1/incidents/{incident_id}` | Partially update incident details | Yes |
| `DELETE` | `/api/v1/incidents/{incident_id}` | Delete incident and its analysis records | Yes |

### 4. Fault Analysis (`/api/v1/analysis`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/analysis/{incident_id}` | Compute fault percentages & factor breakdown | Yes |
| `GET` | `/api/v1/analysis/{incident_id}` | Retrieve stored fault analysis | Yes |
| `GET` | `/api/v1/analysis/{incident_id}/factors` | Retrieve list of contributing factors | Yes |

### 5. Insurance Management (`/api/v1/insurance`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/insurance` | List authenticated user's policies | Yes |
| `POST` | `/api/v1/insurance` | Register a new policy (ICICI Lombard, HDFC ERGO, etc.) | Yes |
| `PUT` | `/api/v1/insurance/{insurance_id}` | Update existing policy details | Yes |
| `DELETE` | `/api/v1/insurance/{insurance_id}` | Remove an insurance policy | Yes |

### 6. Nearby Emergency Services (`/api/v1/services`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/services` | Query nearby hospitals, mechanics, towing & rescue (Haversine) | No |
| `GET` | `/api/v1/services/{service_id}` | Retrieve single service details | No |

### 7. Emergency SOS & Physical Assistance
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/sos` | Trigger emergency SOS alert with coordinates | Yes |
| `GET` | `/api/v1/sos` | List user's SOS history | Yes |
| `GET` | `/api/v1/sos/{request_id}` | Retrieve single SOS record | Yes |
| `POST` | `/api/v1/assistance` | Request Rescue Team, Towing, or Medical Assistance | Yes |
| `GET` | `/api/v1/assistance` | List user's assistance requests | Yes |
| `GET` | `/api/v1/assistance/{request_id}` | Retrieve single assistance dispatch details | Yes |
| `PATCH` | `/api/v1/assistance/{request_id}` | Advance workflow status (Accepted → In Progress → Completed) | Yes |

### 8. Virtual Assistant (`/api/v1/chat`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/chat` | Rule-based conversational guidance & suggested actions | No |

### 9. Accident Reports (`/api/v1/reports`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/reports/{incident_id}` | Comprehensive incident report data (JSON) | Yes |
| `GET` | `/api/v1/reports/{incident_id}/download` | Download report as formatted PDF or JSON (`?format=pdf\|json`) | Yes |

### 10. Emergency Contacts (`/api/v1/contacts`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/contacts` | List trusted emergency contacts | Yes |
| `POST` | `/api/v1/contacts` | Add new emergency contact | Yes |
| `PUT` | `/api/v1/contacts/{contact_id}` | Update existing contact | Yes |
| `DELETE` | `/api/v1/contacts/{contact_id}` | Remove emergency contact | Yes |

---

## 🧪 Running Automated Tests

The test suite runs against an isolated temporary directory using Pytest and FastAPI's `TestClient`, leaving your demo records completely untouched.

```bash
pytest tests -v
```

All 30 tests cover:
- Health checks and system integrity
- User signup, duplicate rejection, and bcrypt authentication
- JWT generation, validation, and forged token rejection
- Incident simulation, CRUD operations, and cross-user data isolation
- Fault percentage bounds (0–100%) and sum equality ($100\%$)
- Contributing factor breakdown and legal disclaimers
- Insurance policy lifecycle and date validation
- Nearby services Haversine distance computations
- SOS alert tracking and assistance state transitions
- Pure-Python binary PDF document generation (`%PDF-1.4`)
- Contact management and CSV persistence verification

---

## ⚠️ Prototype Scope & Limitations

1. **Simulated Heuristics**: The fault attribution engine utilizes deterministic rule-based algorithms rather than a trained deep-learning computer vision model. Output percentages are for demonstration purposes and are explicitly not legally authoritative.
2. **Emergency Protocol Notice**: The SOS and Assistance endpoints record dispatch requests for simulation purposes. For real-world emergencies, motorists must dial **112** (Unified Emergency) or **108** (Ambulance) directly.
3. **Stateless JWT Invalidation**: Standard JWTs expire according to `ACCESS_TOKEN_EXPIRE_MINUTES`. Immediate revocation on logout requires a token denylist or Redis cache in production.
4. **Third-Party Integrations**: Insurer claim submissions and roadside listings represent prototype records and do not connect to external insurer underwriting APIs or live GPS fleets.

