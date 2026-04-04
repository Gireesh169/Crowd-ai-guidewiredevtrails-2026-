from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable

import cv2
import numpy as np


THREAT_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@dataclass
class AnalysisResult:
    threat_level: str
    confidence_score: float
    detected_behaviors: list[str] = field(default_factory=list)
    density: float = 0.0


class CrowdAnalyzer:
    def __init__(self) -> None:
        self.previous_gray: np.ndarray | None = None
        self.previous_points: np.ndarray | None = None
        self.previous_motion_score = 0.0

    def analyze(self, frame: np.ndarray, person_count: int, zone_area_m2: float = 12.0) -> AnalysisResult:
        density = 0.0 if zone_area_m2 <= 0 else person_count / zone_area_m2
        behaviors: list[str] = []
        threat_index = 0
        confidence_parts: list[float] = []

        if density > 6:
            threat_index = max(threat_index, 3)
            behaviors.append("critical_density")
            confidence_parts.append(0.45)
        elif density > 4:
            threat_index = max(threat_index, 2)
            behaviors.append("high_density")
            confidence_parts.append(0.35)
        elif density > 2:
            threat_index = max(threat_index, 1)
            behaviors.append("crowd_build_up")
            confidence_parts.append(0.2)

        motion_score, motion_behaviors = self._analyze_motion(frame)
        behaviors.extend(motion_behaviors)
        if motion_score > 0.75:
            threat_index = max(threat_index, 3)
            confidence_parts.append(0.4)
        elif motion_score > 0.45:
            threat_index = max(threat_index, 2)
            confidence_parts.append(0.3)
        elif motion_score > 0.2:
            threat_index = max(threat_index, 1)
            confidence_parts.append(0.15)

        if person_count >= 60:
            threat_index = max(threat_index, 3)
            behaviors.append("overcrowding")
            confidence_parts.append(0.25)
        elif person_count >= 35:
            threat_index = max(threat_index, 2)
            behaviors.append("dense_flow")
            confidence_parts.append(0.2)

        if density > 4 and motion_score > 0.35:
            behaviors.append("bottleneck_risk")
            threat_index = max(threat_index, 2)
            confidence_parts.append(0.2)

        if motion_score > 0.55:
            behaviors.append("rapid_movement")
        if "rapid_movement" in behaviors and density > 3:
            behaviors.append("rapid_direction_change")

        threat_level = THREAT_ORDER[min(threat_index, len(THREAT_ORDER) - 1)]
        confidence_score = self._score_confidence(confidence_parts, motion_score, density)
        behaviors = self._dedupe_behaviors(behaviors)
        return AnalysisResult(
            threat_level=threat_level,
            confidence_score=confidence_score,
            detected_behaviors=behaviors,
            density=round(density, 2),
        )

    def _analyze_motion(self, frame: np.ndarray) -> tuple[float, list[str]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        behaviors: list[str] = []
        if self.previous_gray is None:
            self.previous_gray = gray
            self.previous_points = cv2.goodFeaturesToTrack(gray, maxCorners=120, qualityLevel=0.01, minDistance=8)
            return 0.0, behaviors

        if self.previous_points is None or len(self.previous_points) < 8:
            self.previous_points = cv2.goodFeaturesToTrack(self.previous_gray, maxCorners=120, qualityLevel=0.01, minDistance=8)
            self.previous_gray = gray
            return 0.0, behaviors

        next_points, status, _ = cv2.calcOpticalFlowPyrLK(self.previous_gray, gray, self.previous_points, None)
        if next_points is None or status is None:
            self.previous_gray = gray
            self.previous_points = cv2.goodFeaturesToTrack(gray, maxCorners=120, qualityLevel=0.01, minDistance=8)
            return 0.0, behaviors

        good_new = next_points[status.flatten() == 1]
        good_old = self.previous_points[status.flatten() == 1]
        if len(good_new) == 0 or len(good_old) == 0:
            self.previous_gray = gray
            self.previous_points = cv2.goodFeaturesToTrack(gray, maxCorners=120, qualityLevel=0.01, minDistance=8)
            return 0.0, behaviors

        # OpenCV may return tracked points as (N, 1, 2); normalize to (N, 2).
        good_new = good_new.reshape(-1, 2)
        good_old = good_old.reshape(-1, 2)

        displacement = good_new - good_old
        magnitudes = np.linalg.norm(displacement, axis=1)
        mean_magnitude = float(np.mean(magnitudes)) if len(magnitudes) else 0.0
        std_magnitude = float(np.std(magnitudes)) if len(magnitudes) else 0.0

        if mean_magnitude > 9:
            behaviors.append("sudden_large_movement")
        if mean_magnitude > 6 and std_magnitude > 3:
            behaviors.append("directional_instability")
        if len(good_new) >= 8:
            angles = np.degrees(np.arctan2(displacement[:, 1], displacement[:, 0]))
            angle_variance = float(np.std(angles))
            if angle_variance > 65:
                behaviors.append("rapid_direction_change")

        motion_score = min(1.0, (mean_magnitude / 12.0) + (std_magnitude / 10.0))
        motion_score = max(motion_score, self.previous_motion_score * 0.85)
        self.previous_motion_score = motion_score
        self.previous_gray = gray
        self.previous_points = cv2.goodFeaturesToTrack(gray, maxCorners=120, qualityLevel=0.01, minDistance=8)
        return motion_score, behaviors

    def _score_confidence(self, confidence_parts: Iterable[float], motion_score: float, density: float) -> float:
        base = 0.25
        total = base + sum(confidence_parts)
        total += min(0.2, motion_score * 0.2)
        total += min(0.2, density / 25.0)
        return round(min(0.99, total), 2)

    def _dedupe_behaviors(self, behaviors: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for behavior in behaviors:
            if behavior not in seen:
                seen.add(behavior)
                deduped.append(behavior)
        return deduped
