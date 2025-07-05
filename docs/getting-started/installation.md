# Installation

## Requirements

- Python 3.12 or higher
- Operating System: macOS, Linux, or Windows
- GPU with WebGPU support (recommended for best performance)

## Install from PyPI

The easiest way to install Vibing-Viz is using pip:

```bash
pip install vibing-viz
```

## Development Installation

For development or to get the latest features:

### 1. Clone the Repository

```bash
git clone https://github.com/talmo/vibing-viz.git
cd vibing-viz
```

### 2. Install uv (Package Manager)

We use [uv](https://github.com/astral-sh/uv) for fast, reliable package management:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Set Up Development Environment

```bash
# Run the setup script
./scripts/setup_dev.sh

# Or manually:
uv sync --all-extras
uv run pre-commit install
```

### 4. Verify Installation

```bash
# Run tests
uv run pytest

# Run example
uv run python examples/basic_visualization.py
```

## Platform-Specific Notes

### macOS (Apple Silicon)

Vibing-Viz is fully optimized for Apple Silicon. No additional configuration needed.

### Linux

You may need to install additional system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxkbcommon-x11-0 \
    libdbus-1-3

# For headless servers
sudo apt-get install -y xvfb
```

### Windows

Windows 10/11 with modern GPU drivers should work out of the box. If you encounter issues:

1. Update your GPU drivers
2. Install [Visual C++ Redistributables](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads)

## Troubleshooting

### Import Error: No module named 'vibing_viz'

Make sure you've activated your virtual environment:

```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### Qt Platform Plugin Error

If you see errors about Qt platform plugins:

```bash
# Linux
export QT_QPA_PLATFORM=offscreen

# macOS/Windows
# Should work without configuration
```

### WebGPU Not Available

If you get WebGPU-related errors:

1. Update your GPU drivers
2. Try software rendering:
   ```bash
   export PYGFX_WGPU_ADAPTER_NAME=llvmpipe
   ```

## Next Steps

- Follow the [Quick Start Guide](quickstart.md) to create your first visualization
- Browse the [Examples](examples.md) for more advanced usage
- Read the [User Guide](../guide/overview.md) for comprehensive documentation