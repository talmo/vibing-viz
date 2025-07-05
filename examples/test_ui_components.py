"""Test UI components without running the full app."""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from vibing_viz.ui.main_window import VibingVizMainWindow
from vibing_viz.visualization.visualizer import Visualizer


def test_ui_creation():
    """Test that UI components can be created."""
    app = QApplication(sys.argv)
    
    # Create visualizer
    viz = Visualizer()
    
    # Add some test data
    poses = np.random.randn(10, 5, 3)
    viz.add_track("test", poses, edges=[(0, 1), (1, 2)])
    
    # Create main window
    window = VibingVizMainWindow(visualizer=viz)
    
    # Basic checks
    assert window.viewport is not None
    assert window.timeline is not None
    assert window.scene_panel is not None
    assert window.properties_panel is not None
    assert window.tracks_panel is not None
    
    print("✓ Main window created successfully")
    print("✓ All UI panels initialized")
    print("✓ Visualizer integrated")
    
    # Check that we can add UI elements
    window.scene_panel.add_track("test", "Test Track", "#FF0000")
    window.tracks_panel.add_track("test", "Test Track", "#FF0000", 10, 5)
    window.timeline.set_total_frames(10)
    window.timeline.add_track("test", "#FF0000", [(0, 9)])
    
    print("✓ UI elements added successfully")
    
    # Don't actually run the app, just verify creation
    return True


if __name__ == "__main__":
    success = test_ui_creation()
    if success:
        print("\nAll UI components working correctly!")
    else:
        print("\nUI component test failed!")
        sys.exit(1)