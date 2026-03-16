from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2

from .ascii_renderer import AsciiFrame, AsciiRenderer
from .config import AppConfig, AsciiConfig


class AsciiArmVisualizerApp:
    def __init__(self) -> None:
        self.app_config = AppConfig()
        self.ascii_renderer = AsciiRenderer(AsciiConfig())
        self.mirror_mode = True
        self.manual_detail = 0.5
        self.last_ascii_frame: AsciiFrame | None = None

        Path(self.app_config.output_dir).mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        cap = cv2.VideoCapture(self.app_config.camera_index)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam. Check camera permissions and availability.")

        cv2.namedWindow(self.app_config.window_original, cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow(self.app_config.window_ascii, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar(
            self.app_config.detail_trackbar,
            self.app_config.window_ascii,
            int(self.manual_detail * 100),
            100,
            self._on_slider,
        )

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    continue

                if self.mirror_mode:
                    frame = cv2.flip(frame, 1)

                ascii_frame = self.ascii_renderer.render(frame, self.manual_detail)
                view = ascii_frame.image.copy()
                self._draw_overlay(view, ascii_frame)
                self.last_ascii_frame = AsciiFrame(
                    image=view,
                    text=ascii_frame.text,
                    display_cols=ascii_frame.display_cols,
                    display_rows=ascii_frame.display_rows,
                    sample_cols=ascii_frame.sample_cols,
                    sample_rows=ascii_frame.sample_rows,
                )

                cv2.imshow(self.app_config.window_original, frame)
                cv2.imshow(self.app_config.window_ascii, view)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord("m"):
                    self.mirror_mode = not self.mirror_mode
                if key == ord("s") and self.last_ascii_frame is not None:
                    self._save_ascii_snapshot(self.last_ascii_frame)
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def _draw_overlay(self, ascii_image, ascii_frame: AsciiFrame) -> None:
        lines = [
            f"Detail slider: {int(self.manual_detail * 100)}",
            f"Sample grid: {ascii_frame.sample_cols}x{ascii_frame.sample_rows}",
            f"Display grid: {ascii_frame.display_cols}x{ascii_frame.display_rows}",
            "Controls: q quit   m mirror   s save",
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
