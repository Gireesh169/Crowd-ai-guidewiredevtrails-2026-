from __future__ import annotations

import base64
import os
import time
import asyncio
from datetime import datetime
from typing import Any

import cv2
import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.alert_engine import AlertEngine, AlertPayload
from backend.analyzer import CrowdAnalyzer
from backend.database import Alert, SessionLocal, get_db, init_db
from backend.detector import CrowdDetector
from backend.simulate_crowd import CrowdSimulator

load_dotenv()

app = FastAPI(title="CrowdShield AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")


class AcknowledgeResponse(BaseModel):
    success: bool
    alert: dict[str, Any]


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    app.state.detector = CrowdDetector(source=CAMERA_SOURCE)
    app.state.analyzer = CrowdAnalyzer()
    app.state.simulator = CrowdSimulator()
    app.state.alert_engine = AlertEngine(SessionLocal)
    app.state.last_frame_stats = {
        "person_count": 0,
        "density": 0.0,
        "threat_level": "LOW",
        "confidence": 0.0,
        "behaviors": [],
        "frame_base64": "",
        "zone": "Zone A",
        "fps": 0.0,
    }


def _serialize_frame(frame: np.ndarray) -> str:
    success, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    if not success:
        return ""
    return base64.b64encode(buffer.tobytes()).decode("utf-8")


def _get_alert_count(db: Session) -> int:
    return db.query(Alert).filter(Alert.acknowledged.is_(False)).count()


@app.get("/api/status")
def status(db: Session = Depends(get_db)) -> dict[str, Any]:
    uptime = int(time.time() - START_TIME)
    return {
        "healthy": True,
        "simulation_mode": SIMULATION_MODE,
        "camera_source": CAMERA_SOURCE,
        "uptime_seconds": uptime,
        "active_alerts": _get_alert_count(db),
        "last_threat_level": app.state.last_frame_stats.get("threat_level", "LOW"),
        "backend_time": datetime.utcnow().isoformat(),
    }


@app.get("/api/alerts")
def list_alerts(limit: int = 20, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
    return [alert.to_dict() for alert in alerts]


@app.post("/api/alerts/acknowledge/{alert_id}")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)) -> AcknowledgeResponse:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return AcknowledgeResponse(success=True, alert=alert.to_dict())


@app.get("/api/last-alert")
def last_alert() -> dict[str, Any]:
    alert = app.state.alert_engine.get_last_alert()
    if alert is None:
        return {"alert": None}
    return {"alert": alert}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "CrowdShield AI", "status": "online"}


@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    detector: CrowdDetector = app.state.detector
    analyzer: CrowdAnalyzer = app.state.analyzer
    simulator: CrowdSimulator = app.state.simulator
    alert_engine: AlertEngine = app.state.alert_engine
    previous_time = time.perf_counter()
    try:
        while True:
            loop_started = time.perf_counter()
            if SIMULATION_MODE:
                simulated = simulator.generate()
                base_frame = simulated["frame"]
                person_count = simulated["person_count"]
                zone_area_m2 = simulated["zone_area_m2"]
                zone = simulated["zone"]
                detection = detector.detect(base_frame, expected_person_count=person_count)
                annotated_frame = detection.frame_with_annotations
            else:
                zone = simulator.current_zone()
                raw_frame = detector.read_frame()
                if raw_frame is None:
                    simulated = simulator.generate()
                    raw_frame = simulated["frame"]
                    person_count = simulated["person_count"]
                    zone_area_m2 = simulated["zone_area_m2"]
                    zone = simulated["zone"]
                    detection = detector.detect(raw_frame, expected_person_count=person_count)
                    annotated_frame = detection.frame_with_annotations
                else:
                    detection = detector.detect(raw_frame)
                    person_count = detection.person_count
                    zone_area_m2 = simulator.zone_area_m2
                    annotated_frame = detection.frame_with_annotations

            analysis = analyzer.analyze(annotated_frame, person_count, zone_area_m2=zone_area_m2)
            message = (
                f"{analysis.threat_level} crowd risk detected in {zone} with {person_count} people and density {analysis.density:.2f} people/m²."
            )
            dispatch = alert_engine.maybe_dispatch(
                AlertPayload(
                    zone=zone,
                    threat_level=analysis.threat_level,
                    person_count=person_count,
                    density=analysis.density,
                    confidence=analysis.confidence_score,
                    behaviors=analysis.detected_behaviors,
                    message=message,
                )
            )

            current_time = time.perf_counter()
            fps = 1.0 / max(0.001, current_time - previous_time)
            previous_time = current_time

            db = SessionLocal()
            try:
                active_alerts = _get_alert_count(db)
            finally:
                db.close()

            frame_base64 = _serialize_frame(annotated_frame)
            app.state.last_frame_stats = {
                "person_count": person_count,
                "density": analysis.density,
                "threat_level": analysis.threat_level,
                "confidence": analysis.confidence_score,
                "behaviors": analysis.detected_behaviors,
                "frame_base64": frame_base64,
                "zone": zone,
                "fps": round(fps, 1),
            }

            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "person_count": person_count,
                "density": analysis.density,
                "threat_level": analysis.threat_level,
                "confidence": analysis.confidence_score,
                "behaviors": analysis.detected_behaviors,
                "frame_base64": frame_base64,
                "zone": zone,
                "camera_id": CAMERA_SOURCE,
                "fps": round(fps, 1),
                "active_alerts": active_alerts,
                "last_alert": dispatch,
            }
            await websocket.send_json(payload)
            elapsed = time.perf_counter() - loop_started
            await asyncio.sleep(max(0.0, 0.5 - elapsed))
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.close(code=1011, reason=str(exc))
