# EcoReminder — Smart Dustbin Alert & Waste Management System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Flask](https://img.shields.io/badge/framework-Flask-000000)

EcoReminder is a modern, full-stack web application designed to streamline urban sanitation. It enables citizens to report overflowing dustbins via GPS-tagged interactive maps, empowers sanitation officers to manage collection routes with proof photo verification, and provides city administrators with real-time analytics, CSV report exporting, and officer dispatching.

---

## 🌟 Key Features

### 🟢 Citizen Portal
- **Interactive Map Picker**: Drag markers or click anywhere on the Leaflet.js map to pinpoint exact dustbin coordinates.
- **GPS Auto-Detection**: One-click "Detect My Location" using browser HTML5 Geolocation API.
- **Urgency Classification**: Categorize reports by priority level (*Low*, *Medium*, *High*, *Critical*).
- **Live Status Tracker**: Monitor progress from `Pending` -> `In Progress` -> `Collected`.
- **Photo Proof Verification**: View side-by-side Before/After photos comparing report images against collector proof photos.

### 🔵 Sanitation Officer Portal
- **Assigned Route Maps**: View all assigned collection tasks pinned on an interactive city map.
- **Status Updating**: Transition tasks to `In Progress` and `Collected`.
- **Proof Photo Upload**: Upload clean-up proof images upon waste pickup with live thumbnail preview.

### 🔴 Admin & Municipal Panel
- **Real-Time Analytics**: Chart.js doughnut graphs displaying status distributions.
- **City-Wide Pin Network**: Live map showing all active and collected bin markers color-coded by status.
- **Collector Management**: Add, view, and remove sanitation officer accounts directly from the UI.
- **CSV Data Export**: Download complete complaint reports in `.csv` format for municipal auditing.

### 🌙 Dark / Light Mode Support
- Seamless theme toggle with persistent user preference stored in `localStorage`.

---

## 🚀 Quick Start (Local Setup)

### 1) Clone Repository
```bash
git clone https://github.com/YAGAVI2006/Ecoremainder.git
cd Ecoremainder
```

### 2) Create Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3) Run Application
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## 🔐 Default Demo Credentials

| Role | Username / Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | System Analytics, CSV Export, Officer Dispatch, Assignment |
| **Collector** | `john@ecoreminder.com` | `collector123` | Assigned Tasks Route Map, Status Updating, Proof Upload |
| **Citizen** | `citizen@ecoreminder.com` | `citizen123` | GPS Bin Reporting, Live History Tracking, Profile Settings |

---

## 🐳 Docker Deployment

To launch EcoReminder using Docker Compose:

```bash
docker-compose up --build -d
```
App will be served on **http://localhost:5000**.

---

## 🧪 Running Tests

To run the automated integration and database unit test suites:

```bash
python -m unittest discover -s tests
```

---

## 📂 Project Structure

```
EcoReminder/
├── app.py                      # Flask main controller & route handlers
├── db.py                       # Modular database connection & access helpers
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build instructions
├── docker-compose.yml          # Container orchestration manifest
├── .github/workflows/ci.yml    # GitHub Actions CI pipeline
├── docs/                       # Architecture & ERD documentation
│   └── ARCHITECTURE.md
├── scripts/                    # Utility scripts (backup & demo seed)
│   ├── backup_db.py
│   └── seed_demo.py
├── utils/                      # Security & validation utilities
│   └── security.py
├── tests/                      # Automated test suites
│   ├── test_routes.py
│   └── test_db.py
├── static/
│   ├── css/style.css           # Eco-Modern design system & dark mode CSS
│   ├── js/app.js               # Leaflet maps & client-side table filter JS
│   └── js/theme.js             # Theme switcher logic
└── templates/                  # Jinja2 HTML templates
    ├── base.html
    ├── index.html
    ├── report.html
    ├── citizen_dashboard.html
    ├── collector_dashboard.html
    ├── admin_dashboard.html
    ├── profile.html
    ├── 404.html
    └── 500.html
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for details.
