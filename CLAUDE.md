# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vibing-Viz is a 3D visualization application for pose tracking kinematics built with PyGFX and Qt.

## Key Technologies

- **Python 3.12+**: Core language
- **PyGFX**: 3D visualization library based on WebGPU
- **PyQt5**: GUI framework
- **sleap-io**: Video I/O handling
- **NumPy**: Data structures (poses as arrays of shape (n_frames, n_nodes, 3))
- **uv**: Package management

## Development Commands

```bash
# Install development environment
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=vibing_viz

# Format code
uv run black .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .

# Build documentation
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve

# Run examples
uv run python examples/basic_visualization.py
```

## Code Style

- **Formatting**: Black (line length 88)
- **Linting**: Ruff with Google docstring convention
- **Type hints**: Use throughout, checked with mypy
- **Docstrings**: Google style for all public APIs

Example docstring:
```python
def add_track(self, track_id: str, poses: np.ndarray, 
              edges: Optional[List[Tuple[int, int]]] = None) -> None:
    """Add a new track to the visualization.
    
    Args:
        track_id: Unique identifier for this track.
        poses: Array of shape (n_frames, n_keypoints, 3) containing 3D positions.
        edges: List of (start_idx, end_idx) tuples defining skeleton connectivity.
    
    Raises:
        ValueError: If track_id already exists or poses has invalid shape.
    """
```

## Architecture Notes

### Core Components

1. **PoseSequence**: Core data structure, designed to support both batch and streaming modes
2. **Visualizer**: Main API entry point, manages scene and rendering
3. **MultiTrackRenderer**: Handles multiple subjects with automatic color assignment
4. **TimelineWidget**: Qt widget for temporal navigation and track visualization

### Performance Considerations

- Designed for 100k+ frames with 1-200 keypoints
- LOD (Level of Detail) system for large datasets
- Frame caching for smooth playback
- Future-ready for real-time streaming

### Key Design Decisions

1. **Data Format**: Internal NumPy arrays, no external format dependencies
2. **UI**: Standalone Qt application with dockable panels (Adobe-style)
3. **Export**: Video via sleap-io, data as NumPy arrays
4. **Coordinates**: Right-handed coordinate system, Z-up

## Testing Guidelines

- Write tests for all new features
- Use pytest fixtures for common test data
- Qt tests should use the `qt_app` fixture
- Mock expensive operations (rendering, file I/O)

## Common Patterns

### Adding a New Renderer
```python
class NewRenderer:
    def __init__(self, scene: gfx.Scene):
        self.scene = scene
        self.meshes = {}
    
    def update(self, data):
        # Update visualization
        pass
```

### Adding a UI Panel
```python
class NewPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Add widgets
```

## Future Features (Not Yet Implemented)

- Real-time streaming support
- Pose editing capabilities
- Event annotation system
- Distance/angle measurements
- Kinematics analysis (velocity, acceleration)
- 1D timeseries plotting