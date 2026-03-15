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
        self.last_ascii_frame: AsciiFrame | None = None

        Path(self.app_config.output_dir).mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        cap = cv2.VideoCapture(self.app_config.camera_index)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam. Check camera permissions and availability.")

        cv2.namedWindow(self.app_config.window_original, cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow(self.app_config.window_ascii, cv2.WINDOW_AUTOSIZE)

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    continue

                if self.mirror_mode:
                    frame = cv2.flip(frame, 1)

                arm = self.pose_tracker.process(frame)
                detail_state = self.controller.update(arm.raise_amount)
                ascii_frame = self.ascii_renderer.render(frame, detail_state.normalized_detail)
                self.last_ascii_frame = ascii_frame

                cv2.imshow(self.app_config.window_original, frame)
                cv2.imshow(self.app_config.window_ascii, ascii_frame.image)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("m"):
                    self.mirror_mode = not self.mirror_mode
                if key == ord("s"):
                    self._save_ascii_snapshot(ascii_frame)
        finally:
            cap.release()
            self.pose_tracker.close()
            cv2.destroyAllWindows()

    def _save_ascii_snapshot(self, ascii_frame: AsciiFrame) -> None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = Path(self.app_config.output_dir) / f"ascii_{stamp}.png"
        txt_path = Path(self.app_config.output_dir) / f"ascii_{stamp}.txt"

        cv2.imwrite(str(img_path), ascii_frame.image)
        txt_path.write_text(ascii_frame.text, encoding="utf-8")
        print(f"Saved: {img_path} and {txt_path}")
