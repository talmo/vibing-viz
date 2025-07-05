"""Comprehensive demo showcasing all Vibing-Viz features."""

import sys
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from vibing_viz import Visualizer
from vibing_viz.ui.main_window import VibingVizMainWindow


def create_dance_animation(n_frames: int = 300, n_dancers: int = 3):
    """Create synchronized dance animation for multiple dancers.
    
    Args:
        n_frames: Number of frames.
        n_dancers: Number of dancers.
        
    Returns:
        List of pose arrays, one per dancer.
    """
    all_poses = []
    
    for dancer_idx in range(n_dancers):
        poses = np.zeros((n_frames, 17, 3))
        
        # Position dancers in a line
        x_offset = (dancer_idx - n_dancers // 2) * 3
        
        for i in range(n_frames):
            t = i * 0.05
            
            # Different dance moves in sequence
            move_phase = (i // 60) % 5
            
            # Base position
            base_x = x_offset
            base_y = 0
            
            if move_phase == 0:
                # Swaying
                base_x += 0.3 * np.sin(t * 2)
            elif move_phase == 1:
                # Stepping
                base_y = 0.5 * np.sin(t * 4) * (dancer_idx % 2 * 2 - 1)
            elif move_phase == 2:
                # Spinning
                angle = t * 2
                radius = 0.5
                base_x += radius * np.cos(angle)
                base_y += radius * np.sin(angle)
            elif move_phase == 3:
                # Jumping
                jump_height = abs(np.sin(t * 3)) * 0.5
                poses[i, :, 2] += jump_height
            else:
                # Wave motion
                wave_offset = np.sin(t + dancer_idx * np.pi / 3) * 0.3
                base_x += wave_offset
            
            # Head
            poses[i, 0] = [base_x, base_y, 1.8]
            
            # Torso
            poses[i, 1] = [base_x, base_y, 1.5]
            poses[i, 2] = [base_x, base_y, 1.2]
            poses[i, 3] = [base_x, base_y, 0.9]
            
            # Arms - synchronized movement
            arm_angle = np.sin(t * 2 + dancer_idx * 0.5) * 0.8
            arm_height = 1.3 + np.sin(t * 3) * 0.2
            
            poses[i, 4] = [base_x - 0.4 * np.cos(arm_angle), base_y - 0.4 * np.sin(arm_angle), arm_height]
            poses[i, 5] = [base_x - 0.6 * np.cos(arm_angle), base_y - 0.6 * np.sin(arm_angle), arm_height - 0.3]
            poses[i, 6] = [base_x + 0.4 * np.cos(arm_angle), base_y + 0.4 * np.sin(arm_angle), arm_height]
            poses[i, 7] = [base_x + 0.6 * np.cos(arm_angle), base_y + 0.6 * np.sin(arm_angle), arm_height - 0.3]
            
            # Legs
            leg_angle = np.sin(t * 2) * 0.3
            poses[i, 8] = [base_x - 0.15, base_y, 0.6]
            poses[i, 9] = [base_x - 0.15 - 0.1 * np.sin(leg_angle), base_y, 0.3]
            poses[i, 10] = [base_x - 0.15 - 0.1 * np.sin(leg_angle), base_y, 0]
            
            poses[i, 11] = [base_x + 0.15, base_y, 0.6]
            poses[i, 12] = [base_x + 0.15 + 0.1 * np.sin(leg_angle), base_y, 0.3]
            poses[i, 13] = [base_x + 0.15 + 0.1 * np.sin(leg_angle), base_y, 0]
            
            # Hands
            poses[i, 14] = poses[i, 5]
            poses[i, 15] = poses[i, 7]
            
            # Center
            poses[i, 16] = [base_x, base_y, 1.0]
        
        all_poses.append(poses)
    
    return all_poses


def main():
    """Run comprehensive demo."""
    print("Vibing-Viz Full Feature Demo")
    print("============================")
    print()
    print("This demo showcases:")
    print("- Multiple synchronized dancers")
    print("- Environment with stage and lighting")
    print("- Camera movements")
    print("- Timeline and playback controls")
    print("- Export capabilities")
    print()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create visualizer
    viz = Visualizer()
    
    # Create stage environment
    print("Creating stage environment...")
    
    # Add floor (stage)
    viz.add_floor("stage", size=(12, 8), position=(0, 0, -0.1), color="#2a2a2a", show_grid=True)
    
    # Add back wall
    viz.add_wall("backdrop", size=(12, 6), position=(0, 4, 3), color="#1a1a1a")
    
    # Add side walls (partial)
    viz.add_wall("wall_left", size=(4, 6), position=(-6, 2, 3), rotation=(0, np.pi/2, 0), color="#252525")
    viz.add_wall("wall_right", size=(4, 6), position=(6, 2, 3), rotation=(0, -np.pi/2, 0), color="#252525")
    
    # Add stage platform
    viz.add_box("platform", size=(10, 6, 0.2), position=(0, 0, -0.1), color="#3a3a3a")
    
    # Add stage props (speakers)
    viz.add_box("speaker_left", size=(0.8, 0.6, 1.2), position=(-5, 3, 0.6), color="#1a1a1a")
    viz.add_box("speaker_right", size=(0.8, 0.6, 1.2), position=(5, 3, 0.6), color="#1a1a1a")
    
    # Generate dance animation
    print("Generating dance animations...")
    n_frames = 300
    all_poses = create_dance_animation(n_frames, n_dancers=3)
    
    # Define skeleton
    edges = [
        (0, 1), (1, 2), (2, 3),  # Spine
        (1, 4), (4, 5),  # Left arm
        (1, 6), (6, 7),  # Right arm
        (3, 8), (8, 9), (9, 10),  # Left leg
        (3, 11), (11, 12), (12, 13),  # Right leg
    ]
    
    # Add dancers with different colors
    colors = ["#ff6b6b", "#4ecdc4", "#ffe66d"]
    dancer_names = ["Dancer 1", "Dancer 2", "Dancer 3"]
    
    for i, (poses, color, name) in enumerate(zip(all_poses, colors, dancer_names)):
        viz.add_track(f"dancer_{i+1}", poses, edges=edges, color=color, keypoint_size=7)
    
    # Configure visualization
    viz.config.show_grid = False  # Stage has its own grid
    viz.config.background_color = "#0a0a0a"
    
    # Create main window
    print("Setting up UI...")
    window = VibingVizMainWindow(visualizer=viz)
    
    # Add all items to UI panels
    for i, (color, name) in enumerate(zip(colors, dancer_names)):
        window.scene_panel.add_track(f"dancer_{i+1}", name, color)
        window.tracks_panel.add_track(f"dancer_{i+1}", name, color, n_frames, 17)
        window.timeline.add_track(f"dancer_{i+1}", color, [(0, n_frames-1)])
    
    # Add environment objects to scene panel
    window.scene_panel.add_environment("stage", "Stage Floor")
    window.scene_panel.add_environment("backdrop", "Backdrop")
    window.scene_panel.add_environment("platform", "Stage Platform")
    
    # Set timeline
    window.timeline.set_total_frames(n_frames)
    
    # Set initial camera view
    viz.set_camera_view("perspective", animate=False)
    
    # Show window
    print("Opening visualization...")
    print()
    print("Controls:")
    print("  - Space: Play/pause animation")
    print("  - Left/Right arrows: Step through frames")
    print("  - Mouse: Orbit/pan/zoom camera")
    print("  - Timeline: Scrub through animation")
    print("  - Front/Side/Top: Camera presets")
    print("  - File → Export Video: Save animation as video")
    print()
    print("The dancers perform synchronized movements in 5 phases:")
    print("1. Swaying")
    print("2. Stepping")
    print("3. Spinning")
    print("4. Jumping")
    print("5. Wave motion")
    
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()