from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field

import cv2
import numpy as np


ZONE_SEQUENCE = ["Zone A", "Zone B", "Zone C", "Zone D"]


@dataclass
class CrowdSimulator:
    width: int = 960
    height: int = 540
    zone_area_m2: float = 12.0
    start_time: float = field(default_factory=time.monotonic)
    _people: list[dict] = field(default_factory=list)
    _last_zone_index: int = 0

    def generate(self) -> dict:
        elapsed = time.monotonic() - self.start_time
        panic_phase = (elapsed % 60.0) < 10.0
        person_count = random.randint(55, 80) if panic_phase else random.randint(10, 50)
        zone_index = int(elapsed // 15) % len(ZONE_SEQUENCE)
        self._last_zone_index = zone_index
        self._sync_people(person_count, panic_phase)
        frame = self._render_frame(elapsed, panic_phase, person_count)
        return {
            "frame": frame,
            "person_count": person_count,
            "zone_area_m2": self.zone_area_m2,
            "zone": ZONE_SEQUENCE[zone_index],
            "panic_phase": panic_phase,
        }

    def current_zone(self) -> str:
        return ZONE_SEQUENCE[self._last_zone_index]

    def _sync_people(self, desired_count: int, panic_phase: bool) -> None:
        while len(self._people) < desired_count:
            self._people.append(
                {
                    "x": random.uniform(80, self.width - 80),
                    "y": random.uniform(80, self.height - 80),
                    "vx": random.uniform(-1.2, 1.2),
                    "vy": random.uniform(-1.2, 1.2),
                    "tone": random.randint(110, 220),
                }
            )
        if len(self._people) > desired_count:
            self._people = self._people[:desired_count]

        center_x = self.width / 2
        center_y = self.height / 2
        for index, person in enumerate(self._people):
            wobble = math.sin((time.monotonic() * 2.2) + index) * 0.5
            if panic_phase:
                dx = person["x"] - center_x
                dy = person["y"] - center_y
                distance = max(1.0, math.hypot(dx, dy))
                drift_x = (dx / distance) * 4.5 + random.uniform(-4.2, 4.2)
                drift_y = (dy / distance) * 4.5 + random.uniform(-4.2, 4.2)
            else:
                drift_x = person["vx"] + random.uniform(-0.8, 0.8)
                drift_y = person["vy"] + random.uniform(-0.8, 0.8)

            person["x"] = self._clamp(person["x"] + drift_x + wobble, 40, self.width - 40)
            person["y"] = self._clamp(person["y"] + drift_y + wobble, 40, self.height - 40)
            if random.random() < 0.06:
                person["vx"] = random.uniform(-1.8, 1.8)
                person["vy"] = random.uniform(-1.8, 1.8)

    def _render_frame(self, elapsed: float, panic_phase: bool, person_count: int) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._paint_background(frame, panic_phase)
        self._draw_floor_guides(frame)
        for person in self._people:
            center = (int(person["x"]), int(person["y"]))
            color = (40, 230, 120) if not panic_phase else (0, 120, 255)
            cv2.circle(frame, center, 10, color, -1)
            cv2.circle(frame, center, 15, (255, 255, 255), 1)
            cv2.line(frame, (center[0], center[1] - 14), (center[0], center[1] - 28), (220, 220, 220), 2)
            cv2.line(frame, (center[0] - 10, center[1] - 4), (center[0] + 10, center[1] - 4), (220, 220, 220), 2)
        self._draw_overlay(frame, elapsed, panic_phase, person_count)
        return frame

    def _paint_background(self, frame: np.ndarray, panic_phase: bool) -> None:
        top_color = np.array([18, 18, 30], dtype=np.float32)
        bottom_color = np.array([32, 24, 44], dtype=np.float32) if not panic_phase else np.array([45, 14, 18], dtype=np.float32)
        for y in range(self.height):
            ratio = y / max(1, self.height - 1)
            row = (top_color * (1 - ratio) + bottom_color * ratio).astype(np.uint8)
            frame[y, :, :] = row
        if panic_phase:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (self.width, self.height), (0, 0, 255), -1)
            frame[:] = cv2.addWeighted(frame, 0.82, overlay, 0.18, 0)

    def _draw_floor_guides(self, frame: np.ndarray) -> None:
        for x in range(0, self.width, 80):
            cv2.line(frame, (x, 0), (x, self.height), (45, 55, 72), 1)
        for y in range(0, self.height, 80):
            cv2.line(frame, (0, y), (self.width, y), (45, 55, 72), 1)

    def _draw_overlay(self, frame: np.ndarray, elapsed: float, panic_phase: bool, person_count: int) -> None:
        label = "PANIC SPIKE" if panic_phase else "NORMAL FLOW"
        accent = (0, 75, 255) if panic_phase else (55, 220, 120)
        cv2.rectangle(frame, (18, 18), (310, 122), (10, 14, 24), -1)
        cv2.rectangle(frame, (18, 18), (310, 122), accent, 2)
        cv2.putText(frame, "CrowdShield AI Simulation", (34, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 240, 255), 2)
        cv2.putText(frame, f"State: {label}", (34, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.65, accent, 2)
        cv2.putText(frame, f"People: {person_count}", (34, 98), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (235, 240, 255), 2)
        cv2.putText(frame, f"Time: {elapsed:05.1f}s", (34, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 188, 200), 1)

    def _clamp(self, value: float, lower: float, upper: float) -> float:
        return max(lower, min(upper, value))
