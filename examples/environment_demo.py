"""Demo of environment rendering features."""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from vibing_viz import Visualizer
from vibing_viz.ui.main_window import VibingVizMainWindow


def create_walking_animation(n_frames: int = 200, n_keypoints: int = 17):
    """Create walking animation data.
    
    Args:
        n_frames: Number of frames.
        n_keypoints: Number of keypoints.
        
    Returns:
        Pose array of shape (n_frames, n_keypoints, 3).
    """
    poses = np.zeros((n_frames, n_keypoints, 3))
    
    for i in range(n_frames):
        # Forward motion
        x_offset = i * 0.05
        
        # Walking cycle
        t = i * 0.1
        
        # Create humanoid pose
        # Head
        poses[i, 0] = [x_offset, 0, 1.8]
        
        # Torso
        poses[i, 1] = [x_offset, 0, 1.5]
        poses[i, 2] = [x_offset, 0, 1.2]
        poses[i, 3] = [x_offset, 0, 0.9]
        
        # Arms swing
        arm_swing = 0.3 * np.sin(t)
        poses[i, 4] = [x_offset - 0.3, arm_swing, 1.3]  # Left shoulder
        poses[i, 5] = [x_offset - 0.3, arm_swing + 0.2, 1.0]  # Left elbow
        poses[i, 6] = [x_offset + 0.3, -arm_swing, 1.3]  # Right shoulder
        poses[i, 7] = [x_offset + 0.3, -arm_swing - 0.2, 1.0]  # Right elbow
        
        # Legs walking
        leg_phase = 0.5 * np.sin(t)
        leg_lift = 0.1 * abs(np.sin(t))
        
        poses[i, 8] = [x_offset - 0.15, leg_phase, 0.6]  # Left hip
        poses[i, 9] = [x_offset - 0.15, leg_phase + 0.2, 0.3 + leg_lift]  # Left knee
        poses[i, 10] = [x_offset - 0.15, leg_phase + 0.3, 0]  # Left foot
        
        poses[i, 11] = [x_offset + 0.15, -leg_phase, 0.6]  # Right hip
        poses[i, 12] = [x_offset + 0.15, -leg_phase - 0.2, 0.3 + leg_lift * 0.5]  # Right knee
        poses[i, 13] = [x_offset + 0.15, -leg_phase - 0.3, 0]  # Right foot
        
        # Hands
        poses[i, 14] = poses[i, 5] + [0, 0.1, -0.1]  # Left hand
        poses[i, 15] = poses[i, 7] + [0, -0.1, -0.1]  # Right hand
        
        # Extra point (center of mass)
        poses[i, 16] = [x_offset, 0, 1.0]
    
    return poses


def main():
    """Run environment rendering demo."""
    print("Environment Rendering Demo")
    print("==========================")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create visualizer
    viz = Visualizer()
    
    # Create room environment
    print("Creating room environment...")
    viz.create_room(size=(15, 20, 4), floor_color="#303030", wall_color="#404040")
    
    # Add some furniture/obstacles
    print("Adding environment objects...")
    
    # Add a table
    viz.add_box("table", size=(2, 1, 0.8), position=(3, 2, 0.4), color="#8B4513")
    
    # Add chairs
    viz.add_box("chair1", size=(0.5, 0.5, 0.9), position=(2, 2, 0.45), color="#654321")
    viz.add_box("chair2", size=(0.5, 0.5, 0.9), position=(4, 2, 0.45), color="#654321")
    
    # Add a platform
    viz.add_box("platform", size=(3, 3, 0.3), position=(-3, -3, 0.15), color="#606060")
    
    # Add some small obstacles
    for i in range(3):
        viz.add_box(
            f"obstacle_{i}",
            size=(0.3, 0.3, 0.6),
            position=(1 + i * 2, -2, 0.3),
            color="#707070"
        )
    
    # Generate walking animation
    print("Generating walking animation...")
    n_frames = 200
    poses = create_walking_animation(n_frames)
    
    # Adjust path to avoid obstacles
    for i in range(n_frames):
        # Make path curve around obstacles
        x = poses[i, :, 0].mean()
        if 0 < x < 6:
            # Curve around obstacles
            y_offset = -1.5 * np.sin((x / 6) * np.pi)
            poses[i, :, 1] += y_offset
    
    # Define skeleton
    edges = [
        (0, 1), (1, 2), (2, 3),  # Spine
        (1, 4), (4, 5),  # Left arm
        (1, 6), (6, 7),  # Right arm
        (3, 8), (8, 9), (9, 10),  # Left leg
        (3, 11), (11, 12), (12, 13),  # Right leg
        (5, 14), (7, 15),  # Hands
    ]
    
    # Add walking person
    viz.add_track("walker", poses, edges=edges, color="#00ff00")
    
    # Add a second person standing still
    standing_poses = np.zeros((n_frames, 17, 3))
    standing_poses[:] = poses[0]  # Copy first frame
    standing_poses[:, :, 0] = -3  # Position at platform
    standing_poses[:, :, 1] = -3
    standing_poses[:, :, 2] += 0.3  # On platform
    
    viz.add_track("standing", standing_poses, edges=edges, color="#ff00ff")
    
    # Configure visualization
    viz.config.show_grid = False  # Floor already has grid
    viz.config.background_color = "#1a1a1a"
    
    # Create main window
    window = VibingVizMainWindow(visualizer=viz)
    
    # Add tracks to UI
    window.scene_panel.add_track("walker", "Walking Person", "#00ff00")
    window.scene_panel.add_track("standing", "Standing Person", "#ff00ff")
    
    # Add environment objects to scene panel
    window.scene_panel.add_environment("room_floor", "Floor")
    window.scene_panel.add_environment("room_wall_back", "Back Wall")
    window.scene_panel.add_environment("room_wall_front", "Front Wall")
    window.scene_panel.add_environment("room_wall_left", "Left Wall")
    window.scene_panel.add_environment("room_wall_right", "Right Wall")
    window.scene_panel.add_environment("table", "Table")
    window.scene_panel.add_environment("platform", "Platform")
    
    window.tracks_panel.add_track("walker", "Walking Person", "#00ff00", n_frames, 17)
    window.tracks_panel.add_track("standing", "Standing Person", "#ff00ff", n_frames, 17)
    
    window.timeline.set_total_frames(n_frames)
    window.timeline.add_track("walker", "#00ff00", [(0, n_frames-1)])
    window.timeline.add_track("standing", "#ff00ff", [(0, n_frames-1)])
    
    # Set initial camera view
    viz.set_camera_view("perspective", animate=False)
    
    print("\nControls:")
    print("  - Space: Play/pause animation")
    print("  - Left/Right arrows: Step through frames")
    print("  - Mouse: Orbit camera")
    print("  - Front/Side/Top buttons: Change view")
    print("\nThe green figure walks through the room, avoiding obstacles.")
    print("The purple figure stands on the platform.")
    
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()