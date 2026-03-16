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
    ascii_chars: str = "@#W$9876543210?!abc;:+=-,._ "
    min_sample_cols: int = 26
    max_sample_cols: int = 240
    char_aspect_ratio: float = 0.5
    font_scale: float = 0.56
    text_thickness: int = 1
    bg_color: int = 0
    fg_color: int = 255
    detail_gamma: float = 1.6
    clahe_clip_limit: float = 2.3
    clahe_tile_grid: int = 8
    denoise_sigma: float = 0.8
    edge_strength: float = 0.42
    portrait_strength: float = 0.26
    background_dim: float = 0.86
