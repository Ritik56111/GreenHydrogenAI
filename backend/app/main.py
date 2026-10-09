from datetime import datetime, timedelta
from pathlib import Path
import math
import random

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor


app = FastAPI(
    title="GreenHydrogen AI API",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Input(BaseModel):
    solar: float = Field(ge=0)
    wind: float = Field(ge=0)
    hydro: float = Field(ge=0)
    temperature: float = 25
    humidity: float = Field(default=50, ge=0, le=100)
    electrolyzer_efficiency: float = Field(
        default=0.78, gt=0, le=1
    )


def calc(s, w, h, t, hu, eff=0.78):
    total = max(0, s + w + h)
    tf = 1 - min(abs(t - 28) / 100, 0.18)
    hf = 1 - min(abs(hu - 50) / 500, 0.10)
    return max(0, total * 0.0235 * tf * hf * eff)


def efficiency(s, w, h, eff=0.78):
    return round(
        min(
            0.98,
            0.45 + 0.32 * min(1, (s + w + h) / 180)
            + 0.23 * eff,
        ) * 100,
        1,
    )


def carbon(h):
    return round(max(0, h) * 3.6, 2)


# Generate sample historical data
H = []
now = datetime.now().replace(
    minute=0, second=0, microsecond=0
)

for i in range(72):
    ts = now - timedelta(hours=71 - i)
    hr = ts.hour

    s = (
        max(0, 120 * math.sin(math.pi * (hr - 6) / 12))
        if 6 <= hr <= 18
        else 0
    )
    s *= random.uniform(0.8, 1.12)

    w = random.uniform(25, 85)
    h = random.uniform(15, 45)
    t = 25 + 8 * math.sin((hr - 8) * math.pi / 12)
    t += random.uniform(-2, 2)
    hu = random.uniform(35, 80)
    ef = random.uniform(0.68, 0.86)

    hyd = calc(s, w, h, t, hu, ef)

    H.append({
        "timestamp": ts.isoformat(),
        "solar": round(s, 2),
        "wind": round(w, 2),
        "hydro": round(h, 2),
        "temperature": round(t, 2),
        "humidity": round(hu, 2),
        "hydrogen": round(hyd, 2),
        "efficiency": efficiency(s, w, h, ef),
        "carbon_saving": carbon(hyd),
    })


# Train the prototype prediction model
rng = np.random.default_rng(42)
X = []
y = []

for _ in range(900):
    s = rng.uniform(0, 140)
    w = rng.uniform(0, 90)
    h = rng.uniform(0, 50)
    t = rng.uniform(15, 42)
    hu = rng.uniform(20, 90)
    ef = rng.uniform(0.6, 0.9)

    X.append([s, w, h, t, hu, ef])
    y.append(
        calc(s, w, h, t, hu, ef)
        + rng.normal(0, 0.06)
    )

model = RandomForestRegressor(
    n_estimators=180,
    random_state=42,
    max_depth=11,
).fit(X, np.maximum(y, 0))


def analyze(x):
    vals = {
        "Solar": x.solar,
        "Wind": x.wind,
        "Hydro": x.hydro,
    }

    dominant = max(vals, key=vals.get)
    total = sum(vals.values())

    hyd = calc(
        x.solar, x.wind, x.hydro,
        x.temperature, x.humidity,
        x.electrolyzer_efficiency,
    )

    ef = efficiency(
        x.solar, x.wind, x.hydro,
        x.electrolyzer_efficiency,
    )

    insights = [
        f"{dominant} is the dominant renewable source "
        "in the current scenario."
    ]
    recommendations = []

    if total <= 0:
        insights.append("No renewable energy is currently available.")
        recommendations.append(
            "Increase renewable energy availability before "
            "running the electrolyzer."
        )
    else:
        recommendations.append(
            f"Prioritize {dominant} during high-availability periods."
        )

    if x.electrolyzer_efficiency < 0.70:
        insights.append("Electrolyzer efficiency is relatively low.")
        recommendations.append(
            "Review electrolyzer efficiency and operating conditions."
        )

    if x.temperature > 35:
        insights.append("High temperature may affect operating conditions.")
        recommendations.append(
            "Monitor temperature and cooling requirements."
        )

    if x.humidity > 80:
        insights.append("Humidity is high in the current scenario.")
        recommendations.append(
            "Monitor environmental conditions and equipment."
        )

    return {
        "dominant_source": dominant,
        "total_renewable": round(total, 2),
        "hydrogen": round(hyd, 2),
        "efficiency": ef,
        "confidence": 0.90,
        "insights": insights,
        "recommendations": recommendations,
    }


def anomalies(x):
    checks = [
        {
            "name": "Solar energy",
            "value": x.solar,
            "threshold": 140,
        },
        {
            "name": "Wind energy",
            "value": x.wind,
            "threshold": 90,
        },
        {
            "name": "Hydro energy",
            "value": x.hydro,
            "threshold": 50,
        },
        {
            "name": "Temperature",
            "value": x.temperature,
            "threshold": 42,
        },
    ]

    detected = []

    for item in checks:
        if item["value"] > item["threshold"]:
            detected.append({
                "parameter": item["name"],
                "value": item["value"],
                "message": (
                    f'{item["name"]} exceeds the prototype '
                    "reference threshold."
                ),
            })

    return {
        "anomaly_detected": bool(detected),
        "count": len(detected),
        "anomalies": detected,
        "message": (
            "Review detected conditions."
            if detected
            else "No threshold anomalies detected."
        ),
    }


# API routes
@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.get("/api/dashboard")
def dashboard():
    x = H[-1]
    result = analyze(
        Input(**{
            k: x[k]
            for k in [
                "solar", "wind", "hydro",
                "temperature", "humidity",
            ]
        })
    )

    return {
        "solar": x["solar"],
        "wind": x["wind"],
        "hydro": x["hydro"],
        "total_renewable": round(
            x["solar"] + x["wind"] + x["hydro"], 2
        ),
        "hydrogen": x["hydrogen"],
        "efficiency": x["efficiency"],
        "carbon_saving": x["carbon_saving"],
        "ai_confidence": result["confidence"],
        "dominant_source": result["dominant_source"],
    }


@app.get("/api/history")
def history():
    return H


@app.post("/api/predict")
def predict(x: Input):
    hyd = max(
        0,
        float(model.predict([[
            x.solar,
            x.wind,
            x.hydro,
            x.temperature,
            x.humidity,
            x.electrolyzer_efficiency,
        ]])[0]),
    )

    return {
        "hydrogen": round(hyd, 2),
        "efficiency": efficiency(
            x.solar, x.wind, x.hydro,
            x.electrolyzer_efficiency,
        ),
        "carbon_saving": carbon(hyd),
        "model": "Random Forest prototype model",
    }


@app.post("/api/ai/analyze")
def ai_analysis(x: Input):
    return analyze(x)


@app.post("/api/anomaly")
def anomaly(x: Input):
    return anomalies(x)


@app.post("/api/optimize")
def optimize(x: Input):
    vals = {
        "Solar": x.solar,
        "Wind": x.wind,
        "Hydro": x.hydro,
    }

    dominant = max(vals, key=vals.get)

    base = calc(
        x.solar, x.wind, x.hydro,
        x.temperature, x.humidity,
        x.electrolyzer_efficiency,
    )

    new_eff = min(
        0.95, x.electrolyzer_efficiency + 0.07
    )

    improved = calc(
        x.solar * 1.08,
        x.wind * 1.04,
        x.hydro,
        x.temperature,
        x.humidity,
        new_eff,
    )

    gain = (
        round((improved - base) / base * 100, 1)
        if base else 0
    )

    return {
        "recommended_source": dominant,
        "baseline_hydrogen": round(base, 2),
        "optimized_hydrogen": round(improved, 2),
        "estimated_improvement": gain,
        "recommendations": [
            f"Prioritize {dominant} during high-availability periods.",
            "Shift flexible electrolyzer load toward renewable-rich windows.",
            "Monitor efficiency before increasing simulated load.",
        ],
    }


@app.post("/api/forecast")
def forecast(x: Input):
    base = x.solar + x.wind + x.hydro

    hyd = calc(
        x.solar, x.wind, x.hydro,
        x.temperature, x.humidity,
        x.electrolyzer_efficiency,
    )

    rows = []

    for hour in range(1, 25):
        factor = 0.78 + 0.18 * ((hour % 8) / 7)

        rows.append({
            "hour": hour,
            "renewable": round(base * factor, 2),
            "hydrogen": round(hyd * factor, 2),
        })

    return {"forecast": rows}


@app.post("/api/what-if")
def what_if(x: Input):
    base = calc(
        x.solar, x.wind, x.hydro,
        x.temperature, x.humidity,
        x.electrolyzer_efficiency,
    )

    new_eff = min(
        0.95, x.electrolyzer_efficiency + 0.08
    )

    scenario = calc(
        x.solar * 1.15,
        x.wind * 1.08,
        x.hydro,
        x.temperature,
        x.humidity,
        new_eff,
    )

    gain = (
        round((scenario - base) / base * 100, 1)
        if base else 0
    )

    return {
        "current_hydrogen": round(base, 2),
        "scenario_hydrogen": round(scenario, 2),
        "hydrogen_improvement": gain,
        "current_efficiency": round(
            x.electrolyzer_efficiency * 100, 1
        ),
        "scenario_efficiency": round(new_eff * 100, 1),
        "carbon_saving": carbon(scenario),
    }


# Serve the built React frontend from the same server.
# main.py is in backend/app; parents[2] is the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
ASSETS_DIR = FRONTEND_DIST / "assets"

if FRONTEND_DIST.is_dir():
    if ASSETS_DIR.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=str(ASSETS_DIR)),
            name="frontend-assets",
        )

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend_routes(full_path: str):
        requested_file = FRONTEND_DIST / full_path

        if requested_file.is_file():
            return FileResponse(str(requested_file))

        return FileResponse(str(FRONTEND_DIST / "index.html"))
