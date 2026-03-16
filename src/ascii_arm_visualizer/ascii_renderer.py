from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .config import AsciiConfig


@dataclass
class AsciiFrame:
    image: np.ndarray
    text: str
    cols: int
    rows: int


class AsciiRenderer:
    def __init__(self, config: AsciiConfig) -> None:
        self.config = config
        self._font = cv2.FONT_HERSHEY_PLAIN

    def render(self, frame_bgr: np.ndarray, normalized_detail: float) -> AsciiFrame:
        cols = int(self.config.min_cols + normalized_detail * (self.config.max_cols - self.config.min_cols))
        cols = max(self.config.min_cols, min(self.config.max_cols, cols))

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        cell_w = max(1.0, width / cols)
        rows = max(1, int(height / (cell_w / self.config.char_aspect_ratio)))

        downsampled = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)
        chars = self._intensity_to_chars(downsampled)

        lines = ["".join(row.tolist()) for row in chars]
        text = "\n".join(lines)

        canvas = np.full((height, width), self.config.bg_color, dtype=np.uint8)
        self._draw_ascii_lines(canvas, lines, cols, rows)
        rendered = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
        return AsciiFrame(image=rendered, text=text, cols=cols, rows=rows)

    def _intensity_to_chars(self, gray_small: np.ndarray) -> np.ndarray:
        ramp = np.array(list(self.config.ascii_chars))
        indices = np.clip((gray_small / 255.0) * (len(ramp) - 1), 0, len(ramp) - 1).astype(np.int32)
        return ramp[indices]

    def _draw_ascii_lines(self, canvas: np.ndarray, lines: list[str], cols: int, rows: int) -> None:
        height, width = canvas.shape
        thickness = self.config.text_thickness

        (char_w, char_h), baseline = cv2.getTextSize("M", self._font, 1.0, thickness)
        char_w = max(char_w, 1)
        line_h_unit = max(char_h + baseline + 1, 1)

        target_w = width * self.config.fill_ratio
        target_h = height * self.config.fill_ratio

        scale_w = target_w / (cols * char_w)
        scale_h = target_h / (rows * line_h_unit)
        scale = max(self.config.min_text_scale, min(self.config.max_text_scale, min(scale_w, scale_h)))
        scale *= self.config.base_text_scale

        (scaled_char_w, scaled_char_h), scaled_baseline = cv2.getTextSize("M", self._font, scale, thickness)
        line_h = max(scaled_char_h + scaled_baseline + 1, 1)
        block_w = max(1, int(cols * scaled_char_w))
        block_h = max(1, int(rows * line_h))

        x = max(4, (width - block_w) // 2)
        y = max(scaled_char_h + 4, (height - block_h) // 2 + scaled_char_h)

        for line in lines:
            cv2.putText(canvas, line, (x, y), self._font, scale, self.config.fg_color, thickness, cv2.LINE_AA)
            y += line_h
            if y >= height:
                break
