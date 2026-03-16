from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    window_original: str = "Original Feed"
    window_ascii: str = "ASCII Visualizer"
    detail_trackbar: str = "Detail"
    output_dir: str = "outputs"


@dataclass(frozen=True)
class AsciiConfig:
    ascii_chars: str = "@%#*+=-:. "
    min_sample_cols: int = 24
    max_sample_cols: int = 220
    char_aspect_ratio: float = 0.5
    font_scale: float = 0.55
    text_thickness: int = 1
    bg_color: int = 0
    fg_color: int = 255
    fill_ratio: float = 0.98
    detail_gamma: float = 1.8
