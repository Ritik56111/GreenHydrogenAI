# GreenHydrogen AI — Judge Demo Edition

Software-first AI decision-support prototype for **AI-Based Green Hydrogen Production Optimization and Monitoring**.

## Included features
- Executive monitoring dashboard
- AI Intelligence / explainable system analysis
- Random Forest hydrogen-yield prediction prototype
- Smart optimization recommendations
- What-If scenario simulator
- 24-hour forecast
- AI anomaly detection and severity alerts
- Renewable energy mix and trends
- Efficiency and estimated carbon-saving indicators
- FastAPI REST API + interactive Swagger docs
- React + Vite + Recharts frontend

## Important scope
This is a **software simulation and decision-support prototype**, not a physical hydrogen production plant. Values are simulated/modelled for demonstration and should not be treated as industrial control instructions.

## Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs` to test APIs.

## Frontend
Open a second terminal:
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open `http://localhost:5173`.

## Demo flow for judges
Dashboard → AI Intelligence → Prediction → Optimization → What-If Simulator → Forecast → Anomaly Detection.
