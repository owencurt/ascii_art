# ASCII Arm Visualizer

A real-time webcam demo that converts your mirrored camera feed into monochrome ASCII art.

This version is focused on portrait readability: it improves local contrast, preserves facial edges better, and keeps full-window ASCII composition while the slider changes internal sampling detail.

## Features

- Real-time webcam capture with OpenCV
- Full-window monochrome ASCII output representing the full frame
- Slider-only quality control (no gesture control in active pipeline)
- Portrait-friendly preprocessing (CLAHE + mild denoise + tone balancing)
- Optional edge emphasis and portrait emphasis toggles for live tuning
- Save current ASCII output as image (`.png`) and text (`.txt`)

## Project Structure

```text
ascii_art/
├── README.md
├── requirements.txt
└── src/
    └── ascii_arm_visualizer/
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        ├── ascii_renderer.py
        ├── config.py
        ├── control_mapper.py
        └── pose_tracker.py
```

## Setup (macOS)

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

From the repository root:

```bash
python -m src.ascii_arm_visualizer
```

Alternative:

```bash
PYTHONPATH=src python -m ascii_arm_visualizer
```

## Controls

- `q`: quit
- `m`: toggle mirror mode
- `s`: save current ASCII frame as:
  - `outputs/ascii_<timestamp>.png`
  - `outputs/ascii_<timestamp>.txt`
- **Detail trackbar** (in ASCII window): active quality control
- `1`: toggle contrast preprocessing
- `2`: toggle edge emphasis
- `3`: toggle portrait emphasis

## Quality Behavior

- Output footprint stays full-window and stable.
- Slider changes **internal sampling** (`sample_cols/sample_rows`) only.
- Low slider values: coarser/chunkier reconstruction.
- High slider values: finer facial and boundary detail.
- On-screen overlay shows current detail plus sampling/display grid values.

## Webcam Permissions / MediaPipe Notes (macOS)

- On first run, macOS may prompt for camera access. Approve it for your terminal or IDE.
- If camera access was denied previously:
  - Open **System Settings → Privacy & Security → Camera**
  - Enable camera access for your terminal app (Terminal, iTerm, VS Code, etc.)
- MediaPipe remains in dependencies for the project, though gesture control is not active in this revision.

## Performance Tips

- Keep your face and upper torso in frame for best portrait emphasis.
- If framerate drops, lower `max_sample_cols` in `config.py`.
- If edges look too strong, toggle edge emphasis with `2`.
