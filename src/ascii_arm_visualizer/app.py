from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2

from .ascii_renderer import AsciiFrame, AsciiRenderer
from .config import AppConfig, AsciiConfig, ControlConfig
from .control_mapper import DetailController
from .pose_tracker import PoseTracker


class AsciiArmVisualizerApp:
    def __init__(self) -> None:
        self.app_config = AppConfig()
        self.ascii_renderer = AsciiRenderer(AsciiConfig())
        self.controller = DetailController(ControlConfig())
        self.pose_tracker = PoseTracker()
        self.mirror_mode = True
        self.control_mode = "arm"
        self.manual_detail = 0.35
        self.last_ascii_frame: AsciiFrame | None = None

        Path(self.app_config.output_dir).mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        cap = cv2.VideoCapture(self.app_config.camera_index)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam. Check camera permissions and availability.")

        cv2.namedWindow(self.app_config.window_original, cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow(self.app_config.window_ascii, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar(self.app_config.detail_trackbar, self.app_config.window_ascii, int(self.manual_detail * 100), 100, self._on_slider)

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    continue

                if self.mirror_mode:
                    frame = cv2.flip(frame, 1)

                arm = self.pose_tracker.process(frame)
                detail = self._effective_detail(arm.raise_amount)
                ascii_frame = self.ascii_renderer.render(frame, detail)

                view = ascii_frame.image.copy()
                self._draw_overlay(view, ascii_frame, detail, arm.raise_amount)
                self.last_ascii_frame = AsciiFrame(image=view, text=ascii_frame.text, cols=ascii_frame.cols, rows=ascii_frame.rows)

                cv2.imshow(self.app_config.window_original, frame)
                cv2.imshow(self.app_config.window_ascii, view)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("m"):
                    self.mirror_mode = not self.mirror_mode
                if key == ord("c"):
                    self.control_mode = "manual" if self.control_mode == "arm" else "arm"
                if key == ord("s"):
                    if self.last_ascii_frame is not None:
                        self._save_ascii_snapshot(self.last_ascii_frame)
        finally:
            cap.release()
            self.pose_tracker.close()
            cv2.destroyAllWindows()

    def _effective_detail(self, raise_amount: float | None) -> float:
        if self.control_mode == "manual":
            return self.manual_detail

        detail = self.controller.update(raise_amount).normalized_detail
        cv2.setTrackbarPos(self.app_config.detail_trackbar, self.app_config.window_ascii, int(detail * 100))
        return detail

    def _draw_overlay(self, ascii_image, ascii_frame: AsciiFrame, detail: float, raise_amount: float | None) -> None:
        lines = [
            f"Mode: {self.control_mode.upper()} (c to toggle)",
            f"Detail: {detail:.2f}   Grid: {ascii_frame.cols}x{ascii_frame.rows}",
            f"Pose: {'tracking' if raise_amount is not None else 'lost'}",
            "q quit   m mirror   s save",
        ]

        y = 20
        for line in lines:
            cv2.putText(ascii_image, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
            y += 20

    def _on_slider(self, value: int) -> None:
        self.manual_detail = value / 100.0

    def _save_ascii_snapshot(self, ascii_frame: AsciiFrame) -> None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = Path(self.app_config.output_dir) / f"ascii_{stamp}.png"
        txt_path = Path(self.app_config.output_dir) / f"ascii_{stamp}.txt"

        cv2.imwrite(str(img_path), ascii_frame.image)
        txt_path.write_text(ascii_frame.text, encoding="utf-8")
        print(f"Saved: {img_path} and {txt_path}")
