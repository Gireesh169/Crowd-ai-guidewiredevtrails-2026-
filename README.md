<<<<<<< HEAD
# CrowdShield AI

CrowdShield AI is a full-stack crowd panic detection demo built for hackathons. It combines computer vision, optical-flow analysis, a real-time FastAPI/WebSocket backend, and a polished React dashboard to simulate how an emergency monitoring station could detect dangerous crowd behavior and trigger alerts.

## What It Does

- Detects people in camera frames with YOLOv8 when a local model is available.
- Falls back to offline-safe simulation mode when no webcam or model is available.
- Analyzes motion and density to classify the scene as `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- Logs alerts to SQLite and exposes alert history through the API.
- Streams annotated frames and threat updates to the dashboard over WebSockets.
- Sends mock email alerts using `smtplib` when SMTP credentials are configured.
- Visualizes four zones on a Leaflet-based map centered on Hyderabad, India.

## Project Structure

- `backend/main.py` - FastAPI app, REST endpoints, WebSocket feed.
- `backend/detector.py` - YOLOv8 detection plus offline-safe mock detection.
- `backend/analyzer.py` - Crowd density and motion analysis.
- `backend/alert_engine.py` - Alert logging and dispatch.
- `backend/database.py` - SQLite models and session helpers.
- `backend/simulate_crowd.py` - Synthetic crowd generator for offline demos.
- `frontend/src/App.jsx` - Dashboard shell and WebSocket client.
- `frontend/src/components/*` - Live feed, alert panel, stats, threat badge, and map.

## Setup

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Start the full stack:

```bash
bash start.sh
```

The script will:

- create a Python virtual environment if needed,
- install backend Python dependencies,
- install frontend npm dependencies,
- start FastAPI on port `8000`,
- start Vite on port `5173`,
- open the dashboard in your browser.

## Deploy (Recommended: Docker)

`apt` and `certbot` commands are for Ubuntu servers, not macOS. For a reliable deploy path from any machine, use Docker Compose.

1. Ensure Docker Desktop (or Docker Engine + Compose) is installed.
2. From the project root, create your runtime env file:

```bash
cp .env.example .env
```

3. Build and run containers:

```bash
docker compose up -d --build
```

4. Open the app:

```text
http://localhost
```

5. Check logs if needed:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

6. Stop services:

```bash
docker compose down
```

### Container Architecture

- `backend` container runs FastAPI/Uvicorn on port `8000`.
- `frontend` container runs Nginx on port `80`, serves built React files, and proxies:
  - `/api/*` -> backend
  - `/ws/*` -> backend WebSocket
- SQLite is persisted in a Docker volume (`crowdshield_data`) at `/app/data`.

### Optional: Deploy to a Cloud VM

1. Provision an Ubuntu VM with Docker and Compose.
2. Clone the repo and copy `.env`.
3. Run `docker compose up -d --build`.
4. Open VM port `80` in firewall/security group.
5. Point your domain A record to VM public IP.
6. For HTTPS, place Caddy or Traefik in front, or use managed TLS at your ingress/load balancer.

## Environment Variables

- `SIMULATION_MODE` - set to `true` for offline demo mode.
- `CAMERA_SOURCE` - webcam index or video file path.
- `YOLO_WEIGHTS` - path to a local YOLOv8 weights file.
- `ALLOW_YOLO_DOWNLOAD` - allow Ultralytics to download weights automatically.
- `DATABASE_URL` - optional DB override. Defaults to SQLite in local mode; Docker defaults to `/app/data/crowdshield.db`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` - optional email settings.
- `ALERT_RECIPIENT` - destination for alert emails.
- `ALERT_SENDER` - optional sender address.

## How It Works

### Backend Flow

1. The detector reads from a webcam, video file, or simulated frame source.
2. The analyzer measures crowd density and frame-to-frame movement.
3. If risk crosses `HIGH` or `CRITICAL`, the alert engine stores the event in SQLite and prints a structured dispatch message.
4. The WebSocket stream emits JSON updates every 500 ms, including an annotated frame encoded as base64.

### Frontend Flow

1. The dashboard opens a WebSocket connection to `/ws/feed`.
2. The live feed updates with the annotated frame and telemetry.
3. The threat badge, metrics, alert history, and zone map update in real time.
4. Operators can acknowledge alerts directly from the dashboard.

## API Endpoints

- `GET /api/status` - backend health and uptime.
- `GET /api/alerts` - alert history from SQLite.
- `POST /api/alerts/acknowledge/{id}` - mark an alert as acknowledged.
- `GET /api/last-alert` - most recent dispatched alert.
- `WS /ws/feed` - real-time stream with frame data and analysis.

## Hackathon Demo Script

1. Open the dashboard and point out that the system is fully local and offline-safe.
2. Show the live feed, threat badge, and stats updating in real time.
3. Explain that the simulator injects a panic spike every minute for 10 seconds.
4. Wait for the threat level to move from `LOW` to `HIGH` or `CRITICAL`.
5. Highlight the alert panel and the console dispatch message.
6. Acknowledge the alert from the dashboard and show the status update.
7. Finish by showing the zone map and explaining how the same pipeline could drive real cameras in a deployed environment.

## Notes

- If you have a local YOLOv8 weights file, place it at the path in `YOLO_WEIGHTS`.
- If no model or webcam is available, the simulation pipeline keeps the demo running.
- The mock email dispatch is skipped gracefully when SMTP settings are missing.
=======
## Adversarial Defense & Anti-Spoofing Strategy

### The Threat
A coordinated syndicate of bad actors can use GPS-spoofing apps to falsely 
place themselves inside a panic/danger zone while physically sitting at home, 
triggering false emergency payouts and draining the liquidity pool. 
Our architecture treats GPS as one low-trust signal among many — not ground truth.

---

### 1. Differentiation: Genuine victim vs. Bad actor

A real person caught in a crowd panic produces a consistent, corroborating 
set of signals across multiple independent data streams. A spoofer produces 
GPS data that is inconsistent with all the others. We exploit that gap.

| Signal | Genuine person in panic | GPS Spoofer |
|---|---|---|
| Accelerometer / gyroscope | Erratic movement, running pattern | Flat / stationary — device not moving |
| Device mock location flag | OFF | Often left ON accidentally |
| GPS drift pattern | Organic micro-drift in chaotic crowd | Unnaturally stable — programmatic signature |
| Audio (microphone) | Crowd noise, screaming, sirens | Silence or home background noise |
| Heart rate (wearable) | Elevated — 120–160 BPM | Resting — 60–80 BPM |
| Network cell tower | Towers near danger zone | Towers near home address |
| Historical claim record | Zero or very low prior claims | Anomalous spike matching syndicate pattern |
| App session behavior | Active movement, SOS taps | Idle session opened just before claim window |

---

### 2. Data Points Beyond Basic GPS

**Device-level forensics**
- Android `mock_location` flag / iOS `simulatedLocation` API state
- GPS signal-to-noise ratio — spoofed signals are unnaturally clean
- Accelerometer, barometer, gyroscope readings — a panicking person shows it
- Microphone ambient audio — crowd noise vs. home silence

**Network & infrastructure signals**
- Cell tower IDs cross-checked against claimed GPS location
- IP address geolocation + VPN/proxy detection flag
- Wi-Fi SSID fingerprint — home router = not in danger zone

**Behavioral telemetry**
- Location trajectory for last 2 hours — did they naturally enter the zone?
- Claim submission timing — mass spike within minutes of alert = syndicate signal
- Session events — did the app open, stay idle, then submit? Bot-like behavior

**Cross-claim graph analysis**
- Claims from same IP subnet, device cluster, or proxy arriving in same 
  10-minute window flagged as coordinated ring
- Graph Neural Network (GNN) assigns ring-membership probability score
- Isolation Forest detects individual anomaly score per claim

---

### 3. UX Balance: Flagged claims without penalizing honest people

**Core principle: the burden of proof for fraud must never fall on the 
victim during a crisis. A flagged claim is a hold, not a denial.**

**Three-tier response system:**

**Tier 1 — Auto-approve (risk score < 0.3)**
Payout or emergency response releases instantly. Zero friction for the 
clear majority of genuine cases.

**Tier 2 — Soft hold (risk score 0.3 – 0.7)**
Person receives a plain-language notification:
*"Your alert is under a brief verification check. Help is being dispatched 
to your area. You may request immediate callback."*
A human reviewer makes the final call — not just the algorithm.
Person can optionally submit one corroborating detail (photo, audio clip).
This is voluntary — never mandatory — to avoid penalizing people with 
poor network connectivity in a real emergency.

**Tier 3 — Block + escalate (risk score > 0.7)**
Claim withheld and escalated for investigation. Person still receives 
a transparent, non-accusatory message with a clear appeal pathway.

**Network-drop grace window:**
In real emergencies, connectivity degrades. If a device shows intermittent 
data (signal dropout consistent with a crisis zone), this LOWERS the fraud 
score rather than raising it. Silence can be evidence of a real emergency.

**Appeal portal:**
Any flagged person can initiate an appeal with one tap. All appeal outcomes 
feed back into the model as labeled training data — continuously improving 
precision and reducing false positives over time.

**False-positive rate SLA:**
We monitor the ratio of overturned appeals to total flagged claims weekly.
If false-positive rate exceeds 5%, scoring thresholds auto-recalibrate.

---

### Architecture Summary

> GPS coordinates enter our system as one low-trust signal among a dozen. 
> Cross-referencing device sensors, network triangulation, audio analysis, 
> behavioral history, and inter-claim graph topology means a coordinated 
> spoof ring must compromise ALL of these simultaneously — a dramatically 
> higher cost than bypassing GPS alone. Genuine victims in genuine emergencies 
> produce a naturally coherent signal set. Fraudsters do not.
>>>>>>> 7a94ddc51d11f121c34fdc8085d036b1d78a9876
