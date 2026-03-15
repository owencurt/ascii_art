from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .config import AsciiConfig


@dataclass
class AsciiFrame:
    image: np.ndarray
    text: str


class AsciiRenderer:
    def __init__(self, config: AsciiConfig) -> None:
        self.config = config
        self._font = cv2.FONT_HERSHEY_PLAIN

    def render(self, frame_bgr: np.ndarray, normalized_detail: float) -> AsciiFrame:
        cols = int(self.config.min_cols + normalized_detail * (self.config.max_cols - self.config.min_cols))
        cols = max(self.config.min_cols, min(self.config.max_cols, cols))

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        cell_w = max(1, width / cols)
        rows = max(1, int(height / (cell_w / self.config.char_aspect_ratio)))

        resized = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)

        ramp = np.array(list(self.config.ascii_chars))
        indices = np.clip((resized / 255.0) * (len(ramp) - 1), 0, len(ramp) - 1).astype(np.int32)
        chars = ramp[indices]

        lines = ["".join(row.tolist()) for row in chars]
        text = "\n".join(lines)

        canvas = np.full((height, width), self.config.bg_color, dtype=np.uint8)
        scale = self.config.text_scale
        thickness = self.config.text_thickness

        (sample_w, sample_h), baseline = cv2.getTextSize("A", self._font, scale, thickness)
        line_h = sample_h + baseline + 1
        total_text_h = rows * line_h
        y = max(sample_h + 4, (height - total_text_h) // 2 + sample_h)

        line_widths = [cv2.getTextSize(line, self._font, scale, thickness)[0][0] for line in lines]
        max_line_w = max(line_widths) if line_widths else 1
        x_start = max(4, (width - max_line_w) // 2)

        for line in lines:
            cv2.putText(canvas, line, (x_start, y), self._font, scale, self.config.fg_color, thickness, cv2.LINE_AA)
            y += line_h
            if y >= height:
                break

        rendered = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
        return AsciiFrame(image=rendered, text=text)
