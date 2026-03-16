from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .config import AsciiConfig


@dataclass
class AsciiFrame:
    image: np.ndarray
    text: str
    display_cols: int
    display_rows: int
    sample_cols: int
    sample_rows: int


class AsciiRenderer:
    def __init__(self, config: AsciiConfig) -> None:
        self.config = config
        self._font = cv2.FONT_HERSHEY_PLAIN

    def render(self, frame_bgr: np.ndarray, normalized_detail: float) -> AsciiFrame:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        display_cols, display_rows, line_h, char_h = self._display_grid(width, height)
        sample_cols, sample_rows = self._sample_grid(width, height, display_cols, normalized_detail)

        sampled = cv2.resize(gray, (sample_cols, sample_rows), interpolation=cv2.INTER_AREA)
        expanded = cv2.resize(sampled, (display_cols, display_rows), interpolation=cv2.INTER_NEAREST)
        chars = self._intensity_to_chars(expanded)

        lines = ["".join(row.tolist()) for row in chars]
        text = "\n".join(lines)

        canvas = np.full((height, width), self.config.bg_color, dtype=np.uint8)
        self._draw_ascii_lines(canvas, lines, display_cols, display_rows, line_h, char_h)
        rendered = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

        return AsciiFrame(
            image=rendered,
            text=text,
            display_cols=display_cols,
            display_rows=display_rows,
            sample_cols=sample_cols,
            sample_rows=sample_rows,
        )

    def _display_grid(self, width: int, height: int) -> tuple[int, int, int, int]:
        (char_w, char_h), baseline = cv2.getTextSize("M", self._font, self.config.font_scale, self.config.text_thickness)
        char_w = max(char_w, 1)
        line_h = max(char_h + baseline + 1, 1)

        display_cols = max(1, int((width * self.config.fill_ratio) / char_w))
        display_rows = max(1, int((height * self.config.fill_ratio) / line_h))
        return display_cols, display_rows, line_h, char_h

    def _sample_grid(self, width: int, height: int, display_cols: int, normalized_detail: float) -> tuple[int, int]:
        detail = np.clip(normalized_detail, 0.0, 1.0) ** self.config.detail_gamma
        max_cols = min(self.config.max_sample_cols, display_cols)
        min_cols = min(self.config.min_sample_cols, max_cols)
        sample_cols = int(min_cols + detail * (max_cols - min_cols))
        sample_cols = max(1, min(max_cols, sample_cols))

        sample_rows = max(1, int(sample_cols * (height / width) * self.config.char_aspect_ratio))
        return sample_cols, sample_rows

    def _intensity_to_chars(self, gray_grid: np.ndarray) -> np.ndarray:
        ramp = np.array(list(self.config.ascii_chars))
        indices = np.clip((gray_grid / 255.0) * (len(ramp) - 1), 0, len(ramp) - 1).astype(np.int32)
        return ramp[indices]

    def _draw_ascii_lines(
        self,
        canvas: np.ndarray,
        lines: list[str],
        display_cols: int,
        display_rows: int,
        line_h: int,
        char_h: int,
    ) -> None:
        height, width = canvas.shape
        (char_w, _), _ = cv2.getTextSize("M", self._font, self.config.font_scale, self.config.text_thickness)
        block_w = max(1, int(display_cols * max(char_w, 1)))
        block_h = max(1, int(display_rows * line_h))

        x = max(0, (width - block_w) // 2)
        y = max(char_h, (height - block_h) // 2 + char_h)

        for line in lines:
            cv2.putText(
                canvas,
                line,
                (x, y),
                self._font,
                self.config.font_scale,
                self.config.fg_color,
                self.config.text_thickness,
                cv2.LINE_AA,
            )
            y += line_h
            if y >= height:
                break
