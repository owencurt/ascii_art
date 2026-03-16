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
        self._face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def render(
        self,
        frame_bgr: np.ndarray,
        normalized_detail: float,
        enable_contrast: bool = True,
        enable_edges: bool = True,
        enable_portrait: bool = True,
    ) -> AsciiFrame:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        display_cols, display_rows, line_h, char_h = self._display_grid(width, height)
        sample_cols, sample_rows = self._sample_grid(width, height, display_cols, normalized_detail)

        processed = self._preprocess(gray, enable_contrast=enable_contrast)
        if enable_portrait:
            processed = self._apply_portrait_emphasis(processed)
        if enable_edges:
            processed = self._apply_edge_emphasis(processed)

        sampled = cv2.resize(processed, (sample_cols, sample_rows), interpolation=cv2.INTER_AREA)
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

        display_cols = max(1, width // char_w)
        display_rows = max(1, height // line_h)
        return display_cols, display_rows, line_h, char_h

    def _sample_grid(self, width: int, height: int, display_cols: int, normalized_detail: float) -> tuple[int, int]:
        detail = np.clip(normalized_detail, 0.0, 1.0) ** self.config.detail_gamma
        max_cols = min(self.config.max_sample_cols, display_cols)
        min_cols = min(self.config.min_sample_cols, max_cols)
        sample_cols = int(min_cols + detail * (max_cols - min_cols))
        sample_cols = max(1, min(max_cols, sample_cols))
        sample_rows = max(1, int(sample_cols * (height / width) * self.config.char_aspect_ratio))
        return sample_cols, sample_rows

    def _preprocess(self, gray: np.ndarray, enable_contrast: bool) -> np.ndarray:
        work = gray.copy()
        if enable_contrast:
            clahe = cv2.createCLAHE(
                clipLimit=self.config.clahe_clip_limit,
                tileGridSize=(self.config.clahe_tile_grid, self.config.clahe_tile_grid),
            )
            work = clahe.apply(work)

        work = cv2.GaussianBlur(work, (0, 0), self.config.denoise_sigma)
        work_f = work.astype(np.float32)
        work_f = np.power(np.clip(work_f / 255.0, 0.0, 1.0), 0.92) * 255.0
        return np.clip(work_f, 0, 255).astype(np.uint8)

    def _apply_edge_emphasis(self, gray: np.ndarray) -> np.ndarray:
        sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(sobel_x, sobel_y)
        mag = cv2.GaussianBlur(mag, (0, 0), 0.8)
        edge = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        base = gray.astype(np.float32)
        edge_f = edge.astype(np.float32)
        blended = base * (1.0 - self.config.edge_strength) + np.minimum(base + edge_f * 0.9, 255.0) * self.config.edge_strength
        return np.clip(blended, 0, 255).astype(np.uint8)

    def _apply_portrait_emphasis(self, gray: np.ndarray) -> np.ndarray:
        h, w = gray.shape
        mask = np.full((h, w), self.config.background_dim, dtype=np.float32)

        faces = self._detect_faces(gray)
        if faces:
            for x, y, fw, fh in faces:
                cx = x + fw // 2
                cy = y + fh // 2
                rx = int(fw * 1.3)
                ry = int(fh * 1.6)
                self._paint_ellipse_boost(mask, cx, cy, rx, ry)
        else:
            cx, cy = w // 2, int(h * 0.42)
            rx, ry = int(w * 0.28), int(h * 0.33)
            self._paint_ellipse_boost(mask, cx, cy, rx, ry)

        mask = cv2.GaussianBlur(mask, (0, 0), 18.0)
        boosted = gray.astype(np.float32) * mask
        return np.clip(boosted, 0, 255).astype(np.uint8)

    def _detect_faces(self, gray: np.ndarray) -> list[tuple[int, int, int, int]]:
        if self._face_detector.empty():
            return []
        small = cv2.resize(gray, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        faces = self._face_detector.detectMultiScale(small, scaleFactor=1.15, minNeighbors=4, minSize=(40, 40))
        return [(int(x * 2), int(y * 2), int(w * 2), int(h * 2)) for (x, y, w, h) in faces]

    def _paint_ellipse_boost(self, mask: np.ndarray, cx: int, cy: int, rx: int, ry: int) -> None:
        overlay = np.zeros_like(mask, dtype=np.float32)
        cv2.ellipse(overlay, (cx, cy), (max(rx, 1), max(ry, 1)), 0, 0, 360, 1.0, -1)
        boost = 1.0 + self.config.portrait_strength * overlay
        np.maximum(mask, boost, out=mask)

    def _intensity_to_chars(self, gray_grid: np.ndarray) -> np.ndarray:
        ramp = np.array(list(self.config.ascii_chars))
        indices = np.clip((gray_grid.astype(np.float32) / 255.0) * (len(ramp) - 1), 0, len(ramp) - 1).astype(np.int32)
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

        x = 0 if block_w >= width else (width - block_w) // 2
        y = char_h if block_h >= height else (height - block_h) // 2 + char_h

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
