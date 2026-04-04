from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Generator

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crowdshield.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    zone = Column(String(32), default="Zone A", nullable=False)
    threat_level = Column(String(16), nullable=False)
    person_count = Column(Integer, nullable=False)
    density = Column(String(16), nullable=False)
    confidence = Column(String(16), nullable=False)
    behaviors_json = Column(Text, nullable=False, default="[]")
    message = Column(Text, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)

    @property
    def behaviors(self) -> list[str]:
        try:
            return json.loads(self.behaviors_json or "[]")
        except json.JSONDecodeError:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "zone": self.zone,
            "threat_level": self.threat_level,
            "person_count": self.person_count,
            "density": float(self.density),
            "confidence": float(self.confidence),
            "behaviors": self.behaviors,
            "message": self.message,
            "acknowledged": self.acknowledged,
        }


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
