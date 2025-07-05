# Welcome to Vibing-Viz

<div align="center">
    <img src="https://raw.githubusercontent.com/talmo/vibing-viz/main/docs/assets/logo.png" alt="Vibing-Viz Logo" width="200">
</div>

## 3D Visualization for Pose Tracking Kinematics

Vibing-Viz is a powerful Python library for visualizing and analyzing 3D pose tracking data. Built on top of PyGFX and Qt, it provides an intuitive interface for exploring multi-subject tracking data with support for temporal playback, multiple camera views, and high-quality video export.

## ✨ Key Features

<div class="grid cards" markdown>

-   :material-account-multiple: **Multi-Subject Tracking**  
    Visualize multiple subjects simultaneously with automatic color differentiation

-   :material-video-multiple: **Multi-Camera Support**  
    View from multiple camera angles with video overlay capabilities

-   :material-play-circle: **Temporal Playback**  
    Smooth playback controls with timeline visualization

-   :material-palette: **Customizable Rendering**  
    Configure colors, sizes, and visual styles to suit your needs

-   :material-export: **Export Capabilities**  
    Export high-quality videos with camera trajectories or transformed pose data

-   :material-speedometer: **High Performance**  
    Optimized for large datasets with 100,000+ frames

</div>

## 🚀 Quick Start

```python
import vibing_viz as vv
import numpy as np

# Create visualizer
viz = vv.Visualizer()

# Add pose data
poses = np.random.randn(100, 17, 3)  # 100 frames, 17 keypoints
viz.add_track("subject_1", poses)

# Show visualization
viz.show()
```

## 📚 Learn More

<div class="grid cards" markdown>

-   :material-download: **[Installation](getting-started/installation.md)**  
    Get started with pip or development installation

-   :material-rocket-launch: **[Quick Start Guide](getting-started/quickstart.md)**  
    Learn the basics in 5 minutes

-   :material-book-open-variant: **[User Guide](guide/overview.md)**  
    Comprehensive guide to all features

-   :material-api: **[API Reference](api/core.md)**  
    Detailed API documentation

</div>

## 🤝 Contributing

We welcome contributions! Check out our [Contributing Guide](development/contributing.md) to get started.

## 📄 License

Vibing-Viz is released under the [BSD 3-Clause License](https://github.com/talmo/vibing-viz/blob/main/LICENSE).