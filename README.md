# Panorama360 Navigator

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green)
![License](https://img.shields.io/badge/license-academic-lightgrey)

An interactive tool for navigating **360° equirectangular images and videos** using perspective projection. The application converts a full spherical view into a planar viewport that the user can pan, tilt, and zoom in real time.

---

## Features

- Load and navigate **equirectangular images** (JPG, PNG, BMP) and **videos** (MP4, AVI, MOV, MKV)
- **Pan and tilt** the view using on-screen arrow buttons or keyboard arrow keys
- **Zoom in/out** by adjusting the field of view (FOV) from 20° to 120°
- **Pause/resume** video playback while still being able to navigate the paused frame
- Real-time **progress bar** for video playback
- Live display of current **coordinates** (θ, φ) and FOV

---

## Tech Stack

| Component | Library |
|-----------|---------|
| GUI | Python `tkinter` (built-in) |
| Image processing | `OpenCV` |
| Numerical computation | `NumPy` |
| Image display | `Pillow` |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/panorama360-navigator.git
cd panorama360-navigator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

> **Note:** Python 3.8 or higher is required. `tkinter` is included in the standard library.

---

## Usage

1. Launch the app with `python main.py`
2. A file picker dialog will open — select a 360° image or video file
3. The main window displays the perspective view
4. Navigate using:
   - **Arrow buttons** or **keyboard arrow keys** to pan/tilt (±10° per step)
   - **`+` / `-` buttons** to zoom in/out (±10° FOV per step)
   - **`⏸` button** to pause/resume video; you can still navigate while paused
5. The coordinate label shows the current viewing direction `θ` (latitude, 0–180°) and `φ` (longitude, −180° to +180°) along with the active FOV

Sample media files are provided in the `media/` folder (image only; videos are excluded from the repo due to file size — add your own `.mp4` files to `media/`).

---

## Project Structure

```
panorama360-navigator/
├── main.py              # Entry point — launches the application
├── NavigationApp.py     # Tkinter GUI and application logic
├── MapPlanar.py         # Equirectangular-to-planar projection (standard version)
├── MapPlanar2.py        # Alternative implementation using tensor operations
├── requirements.txt     # Python dependencies
├── media/
│   └── img360.jpg       # Sample 360° image
└── docs/
    └── report.pdf       # Full project report (algorithm details, results)
```

---

## How It Works

The core algorithm performs **equirectangular-to-planar projection** in four steps:

1. **Tangent-plane sampling** — a grid of pixel coordinates is mapped onto a virtual flat screen placed tangent to the unit sphere at the viewing direction, scaled by `tan(FOV/2)`.
2. **Normalization** — each point is projected onto the sphere surface (unit norm), yielding 3D direction vectors.
3. **Rotation** — a combined rotation matrix `R = R_z(φ) · R_y(θ)` rotates the direction vectors to the desired viewpoint.
4. **Remapping** — the rotated vectors are converted back to spherical coordinates (longitude, latitude), mapped to pixel positions in the equirectangular source, and sampled with bilinear interpolation via `cv2.remap`.

Two implementations are provided:
- **`MapPlanar.py`** — explicit per-component computation
- **`MapPlanar2.py`** — compact tensor-based version using `np.tensordot`

---

## Academic Context

This project was developed as **Assignment 1** for the *Computer Vision* course (Master's degree, 1st year) at the University of Palermo.

**Authors:** Salvatore Spezia, Roberto Dioguardi, Ernesto Davì

For algorithm details, evaluation, and screenshots, see [`docs/report.pdf`](docs/report.pdf).
