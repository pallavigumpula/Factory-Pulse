# FactoryPulse – Smart Manufacturing Performance & OEE Monitoring Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen.svg)](https://pytest.org/)

FactoryPulse is an enterprise-grade Smart Manufacturing Performance & Overall Equipment Effectiveness (OEE) Monitoring Platform engineered for multi-plant discrete and continuous manufacturing operations. Developed for the **YottaFlex AI Forward Deployed Engineer Hackathon**.

The platform provides end-to-end operational visibility: from PLC equipment state telemetry and discrete production counts to deterministic OEE factor decomposition, automated anomaly detection, AI-assisted root cause analysis, and interactive analytics dashboards.

---

## 🏭 Table of Contents
1. [Architecture & Technology Stack](#-architecture--technology-stack)
2. [Key Features](#-key-features)
3. [OEE Calculation Methodology](#-oee-calculation-methodology)
4. [Deterministic Anomaly Detection Engine](#-deterministic-anomaly-detection-engine)
5. [Synthetic Manufacturing Dataset](#-synthetic-manufacturing-dataset)
6. [Project File Structure](#-project-file-structure)
7. [Installation & Setup Guide](#-installation--setup-guide)
8. [Database Configuration (MySQL & SQLite Auto-Fallback)](#-database-configuration)
9. [Running the Application](#-running-the-application)
10. [Running Automated Tests](#-running-automated-tests)
11. [API Documentation](#-api-documentation)
12. [Role-Based Access Control (RBAC) Accounts](#-role-based-access-control-rbac-accounts)

---

## 🏛 Architecture & Technology Stack

```mermaid
flowchart TD
    subgraph Frontend["Frontend Client (Responsive Web UI)"]
        UI[Single Page App - Vanilla JS / Bootstrap 5 / Plotly.js]
        Pages[Dashboard | Machines | OEE | Anomalies | Orders | Counts | Quality | Reports | Users]
        UI --> Pages
    end

    subgraph Backend["FastAPI REST Backend (Python 3.11)"]
        API[FastAPI Gateway / OpenAPI Docs]
        Auth[JWT Authentication & RBAC Middleware]
        OEE[Deterministic OEE Engine]
        Anomaly[Anomaly Detection & Ground Truth Evaluator]
        AI[AI Manufacturing Operations Assistant]
        Reports[CSV / JSON Report Exporter]
        
        API --> Auth
        API --> OEE
        API --> Anomaly
        API --> AI
        API --> Reports
    end

    subgraph Data["Persistence Layer (Hybrid SQL)"]
        DB_MySQL[(MySQL 8.0+ Enterprise)]
        DB_SQLite[(SQLite 3 Seamless Fallback)]
        Generator[Synthetic Dataset Generator (Seed: 20261022)]
    end

    Pages -->|HTTP REST / JWT Bearer| API
    OEE --> Data
    Anomaly --> Data
    Generator --> Data
```

### Core Technologies
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11.9) with Uvicorn ASGI server.
- **ORM & Database Modeling**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) with declarative mapping and strict relation constraints.
- **Database Support**: **MySQL 8.0+** via PyMySQL with intelligent automatic failover to local **SQLite** (`factorypulse.db`) if MySQL daemon is inactive or restricted.
- **Authentication & Security**: Zero-dependency RFC 7519 HMAC-SHA256 JWT tokens and salted PBKDF2-HMAC-SHA256 password hashing (100,000 iterations).
- **Frontend UI**: Responsive HTML5, CSS3, modern JavaScript (ES6+), [Bootstrap 5.3](https://getbootstrap.com/), Bootstrap Icons, and [Plotly.js](https://plot.ly/javascript/) for interactive telemetry and OEE factor waterfall charts.
- **Testing**: [pytest 9.2+](https://pytest.org/) automated test suite covering authentication, RBAC, master data, production operations, OEE engine edge-cases, and reports.

---

## ✨ Key Features

### 1. Master Data Management
- Complete hierarchy modeling: **Plants** ➔ **Production Lines** ➔ **Machines / Work Centers**.
- Comprehensive **Product Catalog** with engineering-standard `ideal_cycle_time_seconds` and unit-of-measure specifications.
- **Shift Calendars** with scheduled start/end times and statutory planned lunch/rest break minutes.
- **Downtime Reason Taxonomy** categorizing planned vs. unplanned losses across mechanical, electrical, operational, and material causes.

### 2. Production Execution & Operational Tracking
- **Production Orders (PO)**: Tracks planned target quantity, cumulative produced count, order status (`PLANNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`), and cycle progress.
- **Machine State Telemetry**: Continuous interval logging for machine operating modes (`RUNNING`, `STOPPED`, `IDLE`, `CHANGEOVER`, `MAINTENANCE`, `BREAK`).
- **Discrete Production Counts**: Auditable count logging for `GOOD`, `SCRAP`, and `REWORK` units.
- **Traceable Count Corrections**: Reductions or adjustments never overwrite historical count ledgers; corrections are recorded as explicit immutable audit events (`CORRECTION`) referencing `reference_count_id`.
- **Quality Inspections**: In-line sample quality audits tracking sample size, passed units, failed units, defect categories, and disposition (`PASSED`, `FAILED`, `CONDITIONAL`).

### 3. Real-Time OEE Analytics & Factor Decomposition
- Real-time decomposition of the standard **Availability × Performance × Quality** equation based on raw database telemetry.
- **Interval Merging Algorithm**: Handles overlapping or adjacent equipment telemetry states without double-counting duration.
- **Performance Capping & Anomaly Flagging**: Flags instances where calculated performance exceeds 100% due to incorrect standard cycle time or sensor bouncing.
- Multi-dimensional aggregation: View KPIs at **Plant**, **Line**, **Machine**, or **Shift** granularity across arbitrary date ranges.

### 4. Deterministic Anomaly Detection
- Rule-based detection scanner running against live operational records.
- Flags 5 core anomaly patterns with severity levels (`CRITICAL`, `HIGH`, `MEDIUM`):
  1. `OVERLAPPING_MACHINE_EVENT`: Overlapping timestamps for consecutive equipment states.
  2. `NEGATIVE_COUNT_WITHOUT_CORRECTION`: Count reduction logged without traceable correction link.
  3. `SCRAP_EXCEEDS_TOTAL_PRODUCTION`: Quality inspection defects exceeding total sample size.
  4. `INCORRECT_IDEAL_CYCLE_TIME`: Product configured with negative or zero ideal cycle time.
  5. `DOWNTIME_OVERLAPPING_PLANNED_BREAK`: Unplanned equipment stoppage concurrently logged during statutory shift break.
- Evaluates detected anomalies against synthetic ground truth labels (`data/ground_truth.json`) calculating **Precision**, **Recall**, and **F1-Score**.

### 5. AI Manufacturing Operations Assistant
- Operational intelligence query engine answering natural language questions based directly on actual database records:
  - *"Which machine has the highest downtime?"*
  - *"Which line achieved the best performance?"*
  - *"What are the major causes of production loss?"*
  - Root-cause insights and prioritized suggested actions (Autonomous Maintenance, SMED, Poka-Yoke).

### 6. Interactive Analytics Dashboard & Reporting
- Real-time gauge indicators and metric cards for Overall OEE, Availability, Performance, and Quality.
- Interactive Plotly.js charts: OEE Factor Decomposition, 7-Day Trend Analytics, Machine Status Matrix, and Downtime Pareto charts.
- Export operational reports as **CSV** or **JSON** attachments.

---

## 📐 OEE Calculation Methodology

The platform calculates Overall Equipment Effectiveness (OEE) using actual database transaction records:

$$\text{OEE} = \text{Availability} \times \text{Performance} \times \text{Quality}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Total Calendar Time Window                                                  │
├────────────────────────────────────────┬────────────────────────────────────┤
│ Planned Production Time (PPT)          │ Planned Break / Non-Scheduled Time │
├──────────────────────────┬─────────────┴────────────────────────────────────┤
│ Operating Time (Run)     │ Unplanned Downtime (Stoppages / Breakdowns)      │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ Net Operating Time       │ Speed / Micro-Stop Performance Loss              │
├────────────────────┬─────┴──────────────────────────────────────────────────┤
│ Fully Productive   │ Quality Scrap / Rework Loss                            │
└────────────────────┴────────────────────────────────────────────────────────┘
```

1. **Availability**:
   $$\text{Availability} = \frac{\text{Operating Time}}{\text{Planned Production Time}} \times 100\%$$
   - $\text{Operating Time}$ is calculated by merging all non-overlapping `RUNNING` event intervals.
   - $\text{Planned Production Time} = \text{Total Window Time} - \text{Planned Breaks}$.

2. **Performance**:
   $$\text{Performance} = \frac{\text{Total Units Produced} \times \text{Ideal Cycle Time (sec)}}{\text{Operating Time (sec)}} \times 100\%$$
   - Evaluates machine operating speed against engineering standard cycle time.
   - Values exceeding 100% are highlighted with a `performance_flagged` warning.

3. **Quality**:
   $$\text{Quality} = \frac{\text{Good Units Produced}}{\text{Total Units Produced}} \times 100\%$$
   - Where $\text{Total Units} = \text{Good} + \text{Scrap} + \text{Rework} + \sum(\text{Corrections})$.

---

## 🛡 Deterministic Anomaly Detection Engine

The anomaly detection engine scans operational tables and measures accuracy against injected ground-truth anomalies:

| Anomaly Type | Target Entity | Rule Logic | Severity |
|---|---|---|---|
| `OVERLAPPING_MACHINE_EVENT` | Machine | $\text{Start Time}_{i+1} < \text{End Time}_i$ | `HIGH` |
| `NEGATIVE_COUNT_WITHOUT_CORRECTION` | Production Order | $\text{Quantity} < 0 \land \text{Type} \neq \text{'CORRECTION'}$ | `CRITICAL` |
| `SCRAP_EXCEEDS_TOTAL_PRODUCTION` | Quality Inspection | $\text{Defects} > \text{Sample Size}$ | `CRITICAL` |
| `INCORRECT_IDEAL_CYCLE_TIME` | Product Master | $\text{Ideal Cycle Time} \le 0.0\text{s}$ | `HIGH` |
| `DOWNTIME_OVERLAPPING_PLANNED_BREAK` | Machine | $\text{Downtime Intersects Statutory Shift Break}$ | `MEDIUM` |

### Benchmark Evaluation Metrics
```
Total Ground Truth Anomalies: 5
Total Detected Anomalies:     5
True Positives:               5
False Positives:              0
False Negatives:              0
Precision:                    1.000 (100.0%)
Recall:                       1.000 (100.0%)
F1-Score:                     1.000 (100.0%)
```

---

## 💾 Synthetic Manufacturing Dataset

The dataset generator produces realistic manufacturing telemetry deterministically from seed `20261022`:

```powershell
# Generate starter dataset (5 days, 15 shifts, ~8,500 operations records)
python scripts/generate_data.py --mode starter

# Generate full benchmark dataset (90 days, 270 shifts, 500,000+ operations records)
python scripts/generate_data.py --mode full
```

### Dataset Structure
- `data/starter/` & `data/full/`:
  - `plants.csv`: Plant locations and timezone metadata.
  - `production_lines.csv`: Lines and target OEE thresholds.
  - `machines.csv`: 30 production machines with status flags.
  - `shifts.csv`: Shift timing schedules and break windows.
  - `products.csv`: Product catalog with standard cycle times.
  - `downtime_reasons.csv`: Downtime reason codes and loss categories.
  - `production_orders.csv`: Manufacturing work orders.
  - `machine_state_events.csv`: Timestamped machine state intervals.
  - `production_counts.csv`: Discrete piece counts and corrections.
  - `quality_inspections.csv`: QA sampling logs and defect audits.
  - `users.csv`: Role-based system accounts.
- `data/ground_truth.json` & `data/ground_truth.csv`: Labeled anomaly ground truth.

---

## 📂 Project File Structure

```
C:\CandidateWorkspace\
├── .env                              # Environment configuration
├── .env.example                      # Example configuration template
├── factorypulse.db                   # Primary SQLite database (auto-created)
├── requirements.txt                  # Python package requirements
├── README.md                         # Platform documentation
├── backend/
│   ├── app/
│   │   ├── config.py                 # Pydantic BaseSettings configuration
│   │   ├── database.py               # Engine factory with MySQL connection & SQLite auto-fallback
│   │   ├── dependencies.py           # JWT authentication and RBAC dependency injectors
│   │   ├── main.py                   # FastAPI application initialization and routing
│   │   ├── models/                   # SQLAlchemy ORM database models
│   │   │   ├── master_data.py        # Plant, Line, Machine, Shift, Product, DowntimeReason
│   │   │   ├── production.py         # ProductionOrder, MachineStateEvent, ProductionCount, QualityInspection
│   │   │   ├── anomaly.py            # DetectedAnomaly database entity
│   │   │   └── user.py               # User and Role model
│   │   ├── schemas/                  # Pydantic request / response schemas
│   │   ├── services/                 # Core domain logic
│   │   │   ├── oee_engine.py         # Deterministic OEE calculation engine
│   │   │   ├── anomaly_detector.py   # Anomaly scanner and evaluation engine
│   │   │   ├── ai_assistant.py       # Operations query answering engine
│   │   │   └── report_service.py     # CSV and JSON report serializes
│   │   ├── routers/                  # Modular FastAPI APIRouters under /api/v1
│   │   └── utils/                    # Security, hashing, and code generators
│   ├── data_generator/
│   │   └── generator.py              # Deterministic synthetic data generator
│   └── tests/                        # Automated pytest suite (23 unit/service tests)
├── database/
│   ├── schema.sql                    # MySQL 8+ DDL table schema definitions
│   └── seed.sql                      # Initial seed records for MySQL
├── docs/                             # Engineering design specifications
│   ├── oee_formula.md                # Mathematical OEE formula specification
│   ├── anomaly_detection.md          # Anomaly detection rules and evaluation metrics
│   ├── data_dictionary.md            # Complete database schema and field dictionary
│   ├── er_diagram.md                 # Entity Relationship Mermaid diagram
│   └── synthetic_data_methodology.md # Deterministic data generation methodology
├── frontend/                         # HTML5 / Bootstrap 5 / Plotly.js Frontend
│   ├── index.html                    # Single-page application root shell
│   ├── css/styles.css                # Custom UI styles and themes
│   └── js/                           # Frontend JavaScript modules
│       ├── api.js                    # Fetch client with JWT authorization header injection
│       ├── auth.js                   # Client-side session and authentication manager
│       ├── charts.js                 # Plotly.js visualization rendering engine
│       ├── app.js                    # Client-side router and navigation controller
│       └── pages/                    # Modular page view controllers
└── scripts/                          # Automation and operational CLI scripts
    ├── generate_data.py              # CLI for generating synthetic data
    ├── test_anomaly_check.py         # CLI for scanning anomalies and calculating metrics
    ├── run_tests.py                  # CLI test runner for pytest test suite
    └── verify_api.py                 # End-to-end full platform verification script
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- Windows 10/11 with **PowerShell**
- Python 3.11.x installed

### 2. Install Dependencies
Open Windows PowerShell in `C:\CandidateWorkspace`:

```powershell
python -m pip install -r requirements.txt
```

---

## 🗄 Database Configuration

FactoryPulse features a dual database strategy designed for zero-friction local development and production readiness:

### Option A: Local SQLite (Zero-Configuration, Out of the Box)
The platform defaults to `sqlite:///./factorypulse.db`. No installation or background service is required.

### Option B: MySQL 8.0+ Server (Production Mode)
1. Start MySQL Server (e.g. via Windows Services or `net start mysql`).
2. Create the database and execute schema:
   ```sql
   CREATE DATABASE factorypulse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Update `.env` with your MySQL credentials:
   ```ini
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=factorypulse_db
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/factorypulse_db?charset=utf8mb4
   ```

*Note: If MySQL is not running or unreachable, FactoryPulse automatically diagnoses the connection and gracefully falls back to local SQLite without crashing.*

---

## 💻 Running the Application

Start the FastAPI application and embedded Web UI:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Accessing the Platform:
- **Interactive Web Application**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI / Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Reference**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Automated Tests

Run the complete 23-test automated test suite:

```powershell
python scripts/run_tests.py
```
Or directly with pytest:
```powershell
python -m pytest -v
```

### Run Anomaly Detection Evaluation:
```powershell
python scripts/test_anomaly_check.py
```

### Run End-to-End Subsystem Verification:
```powershell
python scripts/verify_api.py
```

---

## 👥 Role-Based Access Control (RBAC) Accounts

The system includes pre-configured demo user accounts for testing:

| Username | Password | Role | Permissions |
|---|---|---|---|
| `admin` | `admin123` | **ADMIN** | Full administrative rights, user management, system settings |
| `operator1` | `operator123` | **OPERATOR** | Production orders, discrete count logging, machine state logging |
| `maint1` | `maint123` | **MAINTENANCE** | Equipment downtime tracking, maintenance event logging, anomaly review |
| `qc1` | `qc123` | **QUALITY** | In-line quality inspections, scrap logging, defect tracking |
| `planner1` | `planner123` | **PLANNER** | Production scheduling, master data viewing, OEE analytics |

---

## 🏆 Hackathon Submission Notes
- **Project**: FactoryPulse – Smart Manufacturing Performance & OEE Monitoring Platform
- **Contest**: YottaFlex AI Forward Deployed Engineer Hackathon
- **Data Integrity**: All dashboard calculations, OEE factor decomposition, and anomaly detections are computed deterministically from actual database records (no mock or hardcoded KPIs).
