# Vibing-Viz

[![CI](https://github.com/talmo/vibing-viz/actions/workflows/ci.yml/badge.svg)](https://github.com/talmo/vibing-viz/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/talmo/vibing-viz/branch/main/graph/badge.svg)](https://codecov.io/gh/talmo/vibing-viz)
[![PyPI](https://img.shields.io/pypi/v/vibing-viz)](https://pypi.org/project/vibing-viz/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: BSD-3](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Professional 3D visualization tool for pose tracking kinematics with a modern Qt interface.

## ✨ Features

### Core Visualization
- 🎯 **Real-time 3D rendering** using PyGFX (WebGPU-based) for smooth performance
- 👥 **Multi-track support** with automatic color assignment and differentiation
- 🦴 **Skeleton visualization** with customizable edges, keypoint sizes, and opacity
- 🎨 **Polygon/surface rendering** for body parts, regions, or custom shapes
- ⏯️ **Temporal playback** with variable speed control and frame-by-frame navigation

### User Interface
- 🖥️ **Professional Qt5 interface** with Adobe-style dark theme
- 📐 **Dockable panels** for flexible workspace arrangement
- 📊 **Custom timeline widget** with track visualization, zoom, and scrubbing
- 🌳 **Scene hierarchy panel** for managing all objects
- ⚙️ **Properties editor** for real-time adjustments
- 🎚️ **Track management** with individual visibility/opacity controls

### Camera & Environment
- 📷 **Multiple camera support** (perspective/orthographic) with smooth transitions
- 👁️ **Predefined views** (front, side, top, perspective) with animation
- 🏠 **Environment rendering**: floors, walls, rooms, and custom objects
- 📹 **Video overlay system** for reference footage with transparency

### Import/Export
- 🎬 **Video export** to MP4/AVI with custom camera trajectories
- 🖼️ **Image sequence export** for post-processing workflows
- 📊 **Progress tracking** with cancel support
- 🎥 **Configurable resolution** (up to 4K) and framerate

## Installation

```bash
pip install vibing-viz
```

### Development Installation

```bash
git clone https://github.com/talmo/vibing-viz.git
cd vibing-viz
uv sync --all-extras
```

## Quick Start

### Command Line
```python
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from vibing_viz import Visualizer
from vibing_viz.ui.main_window import VibingVizMainWindow

# Create Qt application
app = QApplication(sys.argv)

# Create visualizer
viz = Visualizer()

# Add pose data (n_frames, n_keypoints, 3)
poses = np.random.randn(100, 17, 3)
edges = [(0, 1), (1, 2), (2, 3)]  # Define skeleton

viz.add_track("subject_1", poses, edges=edges)

# Add environment
viz.add_floor()
viz.create_room(size=(10, 10, 3))

# Create and show main window
window = VibingVizMainWindow(visualizer=viz)
window.show()

# Run application
sys.exit(app.exec_())
```

## Advanced Usage

### Multiple Tracks with Custom Colors

```python
# Add multiple synchronized tracks
colors = ["#ff6b6b", "#4ecdc4", "#ffe66d"]
for i, color in enumerate(colors):
    poses = create_dance_moves(dancer_id=i)
    viz.add_track(f"dancer_{i}", poses, edges=edges, color=color)
```

### Camera Views and Animation

```python
# Switch between predefined views
viz.set_camera_view("front")
viz.set_camera_view("perspective", animate=True)

# Save custom camera position
viz.add_camera_view("my_angle")

# Create camera trajectory for export
from vibing_viz.io import create_camera_trajectory
keyframes = {
    0: {"position": [5, -5, 3], "target": [0, 0, 1]},
    60: {"position": [-5, -5, 3], "target": [0, 0, 1]},
    120: {"position": [0, -8, 5], "target": [0, 0, 1]}
}
trajectory = create_camera_trajectory(keyframes, total_frames=120)
```

### Environment and Props

```python
# Create a stage environment
viz.create_room(size=(12, 10, 4))
viz.add_box("platform", size=(8, 6, 0.5), position=(0, 0, 0.25))

# Add video overlay
viz.add_video_overlay("reference", "dance_video.mp4", opacity=0.5)
```

### Export Video with Progress

```python
# Export with custom settings
def progress_callback(value):
    print(f"Export progress: {value*100:.1f}%")

viz.export_video(
    "output.mp4",
    resolution=(1920, 1080),
    fps=60,
    camera_trajectory=trajectory,
    progress_callback=progress_callback
)
```

## Documentation

Full documentation is available at [talmo.github.io/vibing-viz](https://talmo.github.io/vibing-viz).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Set up development environment
uv sync --all-extras
uv run pre-commit install

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check --fix .
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Vibing-Viz in your research, please cite:

```bibtex
@software{vibing-viz,
  author = {Pereira, Talmo},
  title = {Vibing-Viz: 3D Visualization for Pose Tracking Kinematics},
  url = {https://github.com/talmo/vibing-viz},
  year = {2024}
}
```