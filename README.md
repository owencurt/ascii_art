# ASCII Arm Visualizer

A real-time webcam demo that turns your camera feed into monochrome ASCII art while tracking your **left wrist height relative to your left shoulder**.
Raise your left arm and the ASCII gets denser/more detailed. Lower it and the art becomes coarser.

The app opens two OpenCV windows:
1. Mirrored original webcam feed
2. Live ASCII-rendered output

## Features

- Real-time webcam capture with OpenCV
- Pose tracking with MediaPipe Pose
- Smooth, continuous control of ASCII detail using left-arm raise amount
- Noise-resistant smoothing and fallback behavior when landmarks are briefly lost
- Mirror mode toggle for selfie-style interaction
- Save current ASCII output as both image (`.png`) and text (`.txt`)

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

If that import style is inconvenient in your shell, this also works:

```bash
PYTHONPATH=src python -m ascii_arm_visualizer
```

## Controls

- `q`: quit
- `m`: toggle mirror mode
- `s`: save current ASCII frame as:
  - `outputs/ascii_<timestamp>.png`
  - `outputs/ascii_<timestamp>.txt`

## Arm-Control Behavior

- Control signal: `left_shoulder_y - left_wrist_y`
- Wrist higher than shoulder => larger signal => denser ASCII
- Wrist lower => smaller signal => coarser ASCII
- Signal is clamped, normalized, and smoothed with exponential filtering to prevent flicker
- If landmarks disappear temporarily, detail decays smoothly instead of jumping

## Webcam Permissions / MediaPipe Notes (macOS)

- On first run, macOS may prompt for camera access. Approve it for your terminal or IDE.
- If camera access was denied previously:
  - Open **System Settings → Privacy & Security → Camera**
  - Enable camera access for your terminal app (Terminal, iTerm, VS Code, etc.)
- MediaPipe wheels are distributed for modern Python/macOS combinations; if installation fails, verify:
  - Python version compatibility
  - CPU architecture (Apple Silicon vs Intel)
  - `pip` is up-to-date

## Performance Tips

- Good lighting improves pose stability.
- Keep your upper body in frame, especially left shoulder and left wrist.
- If framerate drops, reduce webcam resolution in code or lower `max_cols` in `config.py`.
