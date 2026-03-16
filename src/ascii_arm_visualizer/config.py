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
    min_cols: int = 20
    max_cols: int = 180
    char_aspect_ratio: float = 0.5
    base_text_scale: float = 1.0
    min_text_scale: float = 0.35
    max_text_scale: float = 2.2
    text_thickness: int = 1
    bg_color: int = 0
    fg_color: int = 255
    fill_ratio: float = 0.96


@dataclass(frozen=True)
class ControlConfig:
    deadband: float = 0.04
    min_raise: float = -0.25
    max_raise: float = 0.9
    detail_gamma: float = 1.35
    smoothing_alpha: float = 0.18
    fallback_decay: float = 0.97
