# ASCII Arm Visualizer

A real-time webcam demo that converts your mirrored camera feed into monochrome ASCII art.

This revision is focused on **manual quality tuning**: an OpenCV slider controls ASCII sampling detail, and the output always fills the full ASCII window.

## Features

- Real-time webcam capture with OpenCV
- Monochrome grayscale-to-ASCII rendering
- Full-window ASCII output that preserves the full webcam composition
- Slider-only quality control for easy low/medium/high comparison
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
- **Detail trackbar** (in ASCII window): only active quality control

## Quality Behavior

- Slider controls **internal sampling resolution** (`sample_cols/sample_rows`)
- ASCII display grid remains full-window and stable
- Low slider values: coarse sampling, chunkier/blockier reconstruction
- High slider values: finer sampling, more detailed reconstruction
- On-screen overlay shows current slider value and effective sample/display grids for testing

## Webcam Permissions / MediaPipe Notes (macOS)

- On first run, macOS may prompt for camera access. Approve it for your terminal or IDE.
- If camera access was denied previously:
  - Open **System Settings → Privacy & Security → Camera**
  - Enable camera access for your terminal app (Terminal, iTerm, VS Code, etc.)
- MediaPipe remains in dependencies for the project, though gesture control is not active in this revision.

## Performance Tips

- Good lighting improves image contrast for clearer ASCII edges.
- If framerate drops, lower `max_sample_cols` in `config.py`.
