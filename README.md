# 🏥 CarePulse AI — Hospital Workforce Management & Intelligent Scheduling System

> **Academic Course**: Advanced Neural Network Architectures (2307411T)  
> **Domain**: Healthcare & Biomedical AI  
> **Primary Track**: **Track B – Sequential Models** (PyTorch Stacked LSTM & GRU)  
> **Supporting Engine**: Constraint Optimization Engine (Google OR-Tools CP-SAT)  
> **Team Allocation**: 2-Member Team Project

---

## 🎯 Project Motive & Objective

Hospitals operate under unpredictable patient demand surges, fluctuating bed occupancy rates, and complex clinical staffing requirements. Conventional static scheduling creates uneven staff allocation, chronic nurse burnout, excessive overtime costs, and dangerous regulatory rest violations.

**CarePulse AI** is an end-to-end hospital workforce management system that:
1. **Intelligently predicts staffing requirements** based on hourly patient volume, department workload, room/bed infrastructure capacity, and historical hospital admission time-series.
2. **Maintains complete records** of healthcare employees, clinical roles (Doctors, Nurses, Technicians, Admin), specialty qualifications, contractual hour caps, and ward infrastructure.
3. **Automatically optimizes shift scheduling and staff allocation** using mathematical constraint programming (Google OR-Tools CP-SAT) to satisfy mandatory rest periods ($\ge 11$h), single shift per day limits, and consecutive working day caps ($\le 5$ days) while minimizing understaffing and overtime penalties.
4. **Monitors workforce workload patterns in real time**, flags impending staff shortages, and computes a **Composite Burnout Risk Index (0–100)** to recommend balanced schedules and safeguard healthcare professional well-being.
5. **Provides a clean, intuitive, clinical portal** built with modern React 18 / TypeScript and a light healthcare theme (clinical teal, emerald, and warm slate) designed for hospital administrators and clinical directors.

---

## 🏥 Clinical Infrastructure & Department Acuity Ratios

| Department | Ward Code | Physical Rooms | Total Beds | Min Staff / Shift | Acuity Ratio (Doctor) | Acuity Ratio (Nurse) |
|---|---|---|---|---|---|---|
| **Emergency Department** | `ED` | 18 Rooms | 32 Beds | 4 Staff | 1 Doctor / 8 Patients | 1 Nurse / 4 Patients |
| **General Medical Ward** | `GMW` | 24 Rooms | 48 Beds | 3 Staff | 1 Doctor / 10 Patients | 1 Nurse / 6 Patients |
| **Intensive Care Unit** | `ICU` | 12 Rooms | 16 Beds | 3 Staff | 1 Doctor / 4 Patients | 1 Nurse / 2 Patients |
| **Pediatrics Unit** | `PED` | 16 Rooms | 26 Beds | 3 Staff | 1 Doctor / 8 Patients | 1 Nurse / 5 Patients |

---

## 🔬 Deep Learning Benchmark (Track B Evaluation)

Evaluated strictly on chronological holdout test data (70% train, 15% validation, 15% test) to prevent temporal data leakage:

| Architecture | Model Family | Lookback Window | MAE (Patients/hr) | RMSE | MAPE (%) | $R^2$ Score | Status |
|---|---|---|---|---|---|---|---|
| **PyTorch Stacked GRU** | Recurrent Sequential | 168 Hours (7 Days) | **3.03** | **4.52** | **7.62%** | **0.928** | **Production Selected** |
| **PyTorch Stacked LSTM**| Recurrent Sequential | 168 Hours (7 Days) | 3.21 | 4.83 | 8.14% | 0.907 | Candidate Architecture |
| **ARIMA (1,1,1)** | Statistical Time-Series | 168 Hours | 4.78 | 6.21 | 12.30% | 0.820 | Statistical Baseline |
| **Seasonal Naive** | Persistence Baseline | 24 Hours Lag | 6.12 | 8.44 | 16.70% | 0.712 | Heuristic Baseline |

---

## 💻 Tech Stack

- **Deep Learning**: Python 3.10+, PyTorch (`torch`), NumPy, Pandas, Scikit-Learn
- **Constraint Optimization**: Google OR-Tools (`ortools.sat.python.cp_model`)
- **Backend API**: FastAPI, SQLAlchemy, Pydantic v2, Uvicorn, SQLite / PostgreSQL
- **Frontend Portal**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons, Framer Motion
- **State Management**: Centralized React Context (`HospitalContext`) with auto-persistence in `localStorage`

---

## 🚀 Quickstart & How to Run the Website

### Step 1: Start the FastAPI Backend
```powershell
cd "p:\ANNA PROJECT\hospital-workforce-optimization\backend"
python -m uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Step 2: Start the React Frontend Portal
```powershell
cd "p:\ANNA PROJECT\hospital-workforce-optimization\frontend"
npm run dev
```
Open your browser at: `http://localhost:5173`

*(Note: The frontend includes full offline mock fallbacks and local storage persistence, ensuring 100% uptime with zero crashes during evaluations!)*

---

## 🧭 Live Features & Interactive Demonstration Guide

| Module | What You Can Do Live |
|---|---|
| **1. Overview & Control** | View real-time KPIs (staff count, shift coverage, bed occupancy %, active alerts), 24h patient arrival area chart, and one-click **"Run Auto-Scheduler"** trigger. |
| **2. AI Demand Forecast** | Change department, select model (GRU vs LSTM vs ARIMA), adjust **Surge Scenario Slider (-30% to +50%)**, and click **"Apply Targets to Shift Scheduler"** to dynamically recalculate required doctors and nurses! |
| **3. Shift Scheduler** | View the interactive 7-day multi-shift roster. Click on **any shift** to open the **Shift Inspector Modal**: add staff, remove staff, adjust headcount targets, and see coverage update in real time. Click **"Re-Run Constraint Optimizer"** to re-solve via CP-SAT. |
| **4. Staff Directory** | Search staff, filter by role/ward, click **"Add Healthcare Professional"** to register a new doctor/nurse, edit existing personnel, or toggle active/inactive status. |
| **5. Departments & Beds** | Interactive **Bed Occupancy Slider** for each unit to simulate surges; edit physical room capacity, total beds, and patient-to-staff ratios; add new clinical departments. |
| **6. Workforce Health** | Live **Composite Burnout Risk Index (0–100)** calculated from actual assigned shifts; filter by risk level; resolve or dismiss active safety alerts; click **"Auto-Rebalance Burnout Risk"** to protect fatigued staff. |
| **7. Audit & Reports** | Download live schedule CSV, staff burnout audit CSV, and benchmark matrix CSV with one click; printable summary report formatted for clinical administrators. |
