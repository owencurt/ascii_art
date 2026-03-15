from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    window_original: str = "Original Feed"
    window_ascii: str = "ASCII Visualizer"
    output_dir: str = "outputs"


@dataclass(frozen=True)
class AsciiConfig:
    ascii_chars: str = "@%#*+=-:. "
    min_cols: int = 50
    max_cols: int = 180
    char_aspect_ratio: float = 0.5
    text_scale: float = 0.35
    text_thickness: int = 1
    bg_color: int = 0
    fg_color: int = 255


@dataclass(frozen=True)
class ControlConfig:
    deadband: float = 0.05
    min_raise: float = -0.2
    max_raise: float = 0.8
    smoothing_alpha: float = 0.15
    fallback_decay: float = 0.96
