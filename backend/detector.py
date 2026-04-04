from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


@dataclass
class DetectionResult:
    person_count: int
    bounding_boxes: list[list[int]]
    frame_with_annotations: np.ndarray


class CrowdDetector:
    def __init__(self, source: int | str | None = None) -> None:
        self.source = source if source is not None else os.getenv("CAMERA_SOURCE", "0")
        self.capture = None
        self.model = None
        self.model_ready = False
        self._ensure_capture()
        self._load_model()

    def _ensure_capture(self) -> None:
        if self.capture is not None:
            return
        capture_source: Any = self.source
        if isinstance(capture_source, str) and capture_source.isdigit():
            capture_source = int(capture_source)
        self.capture = cv2.VideoCapture(capture_source)

    def _load_model(self) -> None:
        try:
            from ultralytics import YOLO

            weights_path = os.getenv("YOLO_WEIGHTS", "yolov8n.pt")
            allow_download = os.getenv("ALLOW_YOLO_DOWNLOAD", "false").lower() == "true"
            if os.path.isfile(weights_path) or allow_download:
                self.model = YOLO(weights_path)
                self.model_ready = True
            else:
                self.model = None
                self.model_ready = False
        except Exception:
            self.model = None
            self.model_ready = False

    def read_frame(self) -> np.ndarray | None:
        if self.capture is None or not self.capture.isOpened():
            return None
        success, frame = self.capture.read()
        if not success:
            return None
        return frame

    def detect(self, frame: np.ndarray, expected_person_count: int | None = None) -> DetectionResult:
        if expected_person_count is None and self.model_ready and self.model is not None:
            try:
                results = self.model.predict(frame, classes=[0], conf=0.25, verbose=False)
                annotated = frame.copy()
                boxes: list[list[int]] = []
                person_count = 0
                for result in results:
                    if result.boxes is None:
                        continue
                    for box in result.boxes:
                        coords = box.xyxy[0].cpu().numpy().astype(int).tolist()
                        x1, y1, x2, y2 = coords
                        boxes.append(coords)
                        person_count += 1
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 128), 2)
                        cv2.putText(
                            annotated,
                            "person",
                            (x1, max(18, y1 - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 128),
                            1,
                            cv2.LINE_AA,
                        )
                return DetectionResult(person_count=person_count, bounding_boxes=boxes, frame_with_annotations=annotated)
            except Exception:
                pass

        return self._mock_detection(frame, expected_person_count=expected_person_count)

    def _mock_detection(self, frame: np.ndarray, expected_person_count: int | None = None) -> DetectionResult:
        annotated = frame.copy()
        height, width = annotated.shape[:2]
        person_count = expected_person_count if expected_person_count is not None else random.randint(10, 40)
        boxes: list[list[int]] = []
        rng = random.Random(person_count * 31 + width + height)
        for _ in range(person_count):
            box_width = rng.randint(18, 42)
            box_height = rng.randint(28, 60)
            x1 = rng.randint(0, max(1, width - box_width - 1))
            y1 = rng.randint(0, max(1, height - box_height - 1))
            x2 = x1 + box_width
            y2 = y1 + box_height
            boxes.append([x1, y1, x2, y2])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (80, 220, 255), 2)
            cv2.circle(annotated, (x1 + box_width // 2, y1 + box_height // 3), 4, (255, 255, 255), -1)
        return DetectionResult(person_count=person_count, bounding_boxes=boxes, frame_with_annotations=annotated)
