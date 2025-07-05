"""Basic visualization example for vibing-viz."""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from vibing_viz import Visualizer
from vibing_viz.ui.main_window import VibingVizMainWindow


def generate_sample_data(n_frames=100, n_keypoints=17):
    """Generate sample pose data with simple motion.
    
    Args:
        n_frames: Number of frames to generate.
        n_keypoints: Number of keypoints per pose.
        
    Returns:
        np.ndarray: Pose data of shape (n_frames, n_keypoints, 3).
    """
    # Create base pose
    base_pose = np.random.randn(n_keypoints, 3) * 0.5
    
    # Add motion over time
    poses = np.zeros((n_frames, n_keypoints, 3))
    for i in range(n_frames):
        # Add walking motion
        offset = np.array([i * 0.01, 0, 0])
        # Add some vertical oscillation
        offset[2] = 0.1 * np.sin(i * 0.1)
        poses[i] = base_pose + offset
        
    return poses


def main():
    """Run basic visualization example."""
    print("Creating basic visualization...")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create visualizer
    viz = Visualizer()
    
    # Generate sample data
    poses = generate_sample_data()
    
    # Define skeleton edges (simplified)
    edges = [
        (0, 1), (1, 2),  # Head to torso
        (2, 3), (3, 4),  # Left arm
        (2, 5), (5, 6),  # Right arm
        (1, 7), (7, 8),  # Left leg
        (1, 9), (9, 10),  # Right leg
    ]
    
    # Add track
    viz.add_track("subject_1", poses, edges=edges)
    
    # Add a second subject offset to the side
    poses2 = generate_sample_data()
    poses2[:, :, 1] += 3  # Offset to the side
    viz.add_track("subject_2", poses2, edges=edges, color="#4ECDC4")
    
    # Configure visualization
    viz.config.show_grid = True
    viz.config.background_color = "#1a1a1a"
    
    # Create and show main window
    window = VibingVizMainWindow(visualizer=viz)
    
    # Add tracks to UI panels
    window.scene_panel.add_track("subject_1", "Subject 1", viz.tracks["subject_1"].color)
    window.scene_panel.add_track("subject_2", "Subject 2", viz.tracks["subject_2"].color)
    
    window.tracks_panel.add_track("subject_1", "Subject 1", viz.tracks["subject_1"].color, 100, 17)
    window.tracks_panel.add_track("subject_2", "Subject 2", viz.tracks["subject_2"].color, 100, 17)
    
    # Set timeline properties
    window.timeline.set_total_frames(100)
    window.timeline.add_track("subject_1", viz.tracks["subject_1"].color, [(0, 99)])
    window.timeline.add_track("subject_2", viz.tracks["subject_2"].color, [(0, 99)])
    
    # Show visualization
    print("Opening visualization window...")
    print("Controls:")
    print("  - Left mouse: Rotate")
    print("  - Right mouse: Pan") 
    print("  - Scroll: Zoom")
    print("  - Space: Play/pause")
    print("  - Left/Right arrows: Previous/next frame")
    print("  - Home/End: First/last frame")
    
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()