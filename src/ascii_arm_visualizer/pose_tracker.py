from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp


@dataclass
class ArmMeasurements:
    raise_amount: Optional[float]


class PoseTracker:
    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5) -> None:
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame_bgr):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self._pose.process(frame_rgb)
        frame_rgb.flags.writeable = True
        return self._extract_measurements(results)

    def _extract_measurements(self, results) -> ArmMeasurements:
        if not results.pose_landmarks:
            return ArmMeasurements(raise_amount=None)

        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[self._mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_wrist = landmarks[self._mp_pose.PoseLandmark.LEFT_WRIST.value]

        if min(left_shoulder.visibility, left_wrist.visibility) < 0.35:
            return ArmMeasurements(raise_amount=None)

        raise_amount = left_shoulder.y - left_wrist.y
        return ArmMeasurements(raise_amount=raise_amount)

    def close(self) -> None:
        self._pose.close()
