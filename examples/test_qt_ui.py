"""Test Qt UI components."""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from vibing_viz.ui.main_window import VibingVizMainWindow
from vibing_viz.visualization.visualizer import Visualizer
from vibing_viz.core.pose_data import PoseFrame, PoseSequence
from vibing_viz.core.track import Track


def create_test_data():
    """Create test pose data."""
    n_frames = 100
    n_keypoints = 17
    
    # Create simple walking motion
    poses = np.zeros((n_frames, n_keypoints, 3))
    for i in range(n_frames):
        keypoints = np.random.randn(n_keypoints, 3) * 0.5
        keypoints[:, 0] += i * 0.05  # Move forward
        keypoints[:, 2] = np.abs(keypoints[:, 2]) + 0.5  # Keep above ground
        poses[i] = keypoints
    
    return poses


def main():
    """Run Qt UI test."""
    app = QApplication(sys.argv)
    
    # Create visualizer
    viz = Visualizer()
    
    # Add test data
    poses1 = create_test_data()
    edges = [(i, i+1) for i in range(16)]
    
    viz.add_track("subject_1", poses1, edges=edges, color="#FF6B6B")
    
    # Add second track
    poses2 = create_test_data()
    poses2[:, :, 1] += 3  # Offset to the side
    
    viz.add_track("subject_2", poses2, edges=edges, color="#4ECDC4")
    
    # Create main window
    window = VibingVizMainWindow(visualizer=viz)
    
    # Add tracks to UI panels
    window.scene_panel.add_track("subject_1", "Subject 1", "#FF6B6B")
    window.scene_panel.add_track("subject_2", "Subject 2", "#4ECDC4")
    
    window.tracks_panel.add_track("subject_1", "Subject 1", "#FF6B6B", 100, 17)
    window.tracks_panel.add_track("subject_2", "Subject 2", "#4ECDC4", 100, 17)
    
    # Set timeline properties
    window.timeline.set_total_frames(100)
    window.timeline.add_track("subject_1", "#FF6B6B", [(0, 99)])
    window.timeline.add_track("subject_2", "#4ECDC4", [(0, 99)])
    
    # Show window
    window.show()
    
    # Run app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()