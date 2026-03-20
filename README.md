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