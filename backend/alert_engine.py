from __future__ import annotations

import json
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from typing import Any

from sqlalchemy.orm import Session

from backend.database import Alert


@dataclass
class AlertPayload:
    zone: str
    threat_level: str
    person_count: int
    density: float
    confidence: float
    behaviors: list[str]
    message: str


class AlertEngine:
    def __init__(self, db_factory) -> None:
        self.db_factory = db_factory
        self.last_alert: dict[str, Any] | None = None
        self.last_dispatch_signature: tuple[str, str] | None = None

    def maybe_dispatch(self, payload: AlertPayload) -> dict[str, Any] | None:
        if payload.threat_level not in {"HIGH", "CRITICAL"}:
            return None

        signature = (payload.zone, payload.threat_level)
        if self.last_dispatch_signature == signature:
            return self.last_alert

        self.last_dispatch_signature = signature
        alert = self._store_alert(payload)
        self._print_alert(alert)
        self._send_email(alert)
        self.last_alert = alert
        return alert

    def _store_alert(self, payload: AlertPayload) -> dict[str, Any]:
        db: Session = self.db_factory()
        try:
            record = Alert(
                timestamp=datetime.utcnow(),
                zone=payload.zone,
                threat_level=payload.threat_level,
                person_count=payload.person_count,
                density=f"{payload.density:.2f}",
                confidence=f"{payload.confidence:.2f}",
                behaviors_json=json.dumps(payload.behaviors),
                message=payload.message,
                acknowledged=False,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record.to_dict()
        finally:
            db.close()

    def _print_alert(self, alert: dict[str, Any]) -> None:
        print("\n=== CROWDSHIELD DISPATCH ===")
        print(f"Time: {alert['timestamp']}")
        print(f"Zone: {alert['zone']}")
        print(f"Threat: {alert['threat_level']}")
        print(f"People: {alert['person_count']}")
        print(f"Density: {alert['density']}")
        print(f"Confidence: {alert['confidence']}")
        print(f"Behaviors: {', '.join(alert['behaviors']) if alert['behaviors'] else 'none'}")
        print(f"Message: {alert['message']}")
        print("===========================\n")

    def _send_email(self, alert: dict[str, Any]) -> None:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        recipient = os.getenv("ALERT_RECIPIENT")
        sender = os.getenv("ALERT_SENDER", smtp_username or "alerts@crowdshield.local")

        if not smtp_host or not smtp_username or not smtp_password or not recipient:
            return

        message = EmailMessage()
        message["Subject"] = f"CrowdShield Alert - {alert['threat_level']}"
        message["From"] = sender
        message["To"] = recipient
        message.set_content(
            "CrowdShield AI detected a crowd panic risk.\n\n"
            f"Zone: {alert['zone']}\n"
            f"Threat: {alert['threat_level']}\n"
            f"People: {alert['person_count']}\n"
            f"Density: {alert['density']}\n"
            f"Confidence: {alert['confidence']}\n"
            f"Behaviors: {', '.join(alert['behaviors']) if alert['behaviors'] else 'none'}\n"
            f"Message: {alert['message']}\n"
        )

        try:
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                    server.login(smtp_username, smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_username, smtp_password)
                    server.send_message(message)
        except Exception as exc:
            print(f"Mock email skipped: {exc}")

    def get_last_alert(self) -> dict[str, Any] | None:
        return self.last_alert
