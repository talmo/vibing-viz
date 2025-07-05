"""Demo of video export functionality."""

import sys
import numpy as np
from pathlib import Path
from vibing_viz import Visualizer
from vibing_viz.io.video_exporter import create_camera_trajectory


def create_circular_motion(n_frames: int = 120, n_keypoints: int = 17):
    """Create pose data with circular motion.
    
    Args:
        n_frames: Number of frames.
        n_keypoints: Number of keypoints.
        
    Returns:
        Pose array of shape (n_frames, n_keypoints, 3).
    """
    poses = np.zeros((n_frames, n_keypoints, 3))
    
    for i in range(n_frames):
        # Base circular motion
        angle = 2 * np.pi * (i / n_frames)
        radius = 2
        
        base_x = radius * np.cos(angle)
        base_y = radius * np.sin(angle)
        
        # Create humanoid-like pose
        poses[i] = np.random.randn(n_keypoints, 3) * 0.2
        
        # Head (top)
        poses[i, 0] = [base_x, base_y, 2.0]
        
        # Torso
        poses[i, 1] = [base_x, base_y, 1.5]
        poses[i, 2] = [base_x, base_y, 1.0]
        
        # Arms
        arm_spread = 0.5
        poses[i, 3] = [base_x - arm_spread, base_y, 1.3]
        poses[i, 4] = [base_x - arm_spread * 1.5, base_y, 1.0]
        poses[i, 5] = [base_x + arm_spread, base_y, 1.3]
        poses[i, 6] = [base_x + arm_spread * 1.5, base_y, 1.0]
        
        # Legs
        leg_spread = 0.3
        poses[i, 7] = [base_x - leg_spread, base_y, 0.7]
        poses[i, 8] = [base_x - leg_spread, base_y, 0.3]
        poses[i, 9] = [base_x + leg_spread, base_y, 0.7]
        poses[i, 10] = [base_x + leg_spread, base_y, 0.3]
    
    return poses


def create_camera_orbit_trajectory(n_frames: int, radius: float = 8, height: float = 5):
    """Create camera trajectory that orbits around origin.
    
    Args:
        n_frames: Number of frames.
        radius: Orbit radius.
        height: Camera height.
        
    Returns:
        Camera trajectory keyframes.
    """
    keyframes = {}
    
    # Create keyframes at regular intervals
    n_keyframes = 5
    for i in range(n_keyframes):
        frame = int((i / (n_keyframes - 1)) * (n_frames - 1))
        angle = 2 * np.pi * (i / (n_keyframes - 1))
        
        keyframes[frame] = {
            "position": [
                radius * np.cos(angle),
                radius * np.sin(angle),
                height
            ],
            "target": [0, 0, 1],
            "up": [0, 0, 1]
        }
    
    # Create interpolated trajectory
    trajectory = create_camera_trajectory(keyframes, n_frames, interpolation="smooth")
    
    return trajectory


def export_demo_video():
    """Run video export demo."""
    print("Video Export Demo")
    print("=================")
    
    # Create visualizer
    viz = Visualizer()
    
    # Generate data
    n_frames = 120
    poses = create_circular_motion(n_frames)
    
    # Define skeleton
    edges = [
        (0, 1), (1, 2),  # Head to torso
        (1, 3), (3, 4),  # Left arm
        (1, 5), (5, 6),  # Right arm
        (2, 7), (7, 8),  # Left leg
        (2, 9), (9, 10),  # Right leg
    ]
    
    # Add track
    viz.add_track("dancer", poses, edges=edges, color="#ff6b6b")
    
    # Configure visualization
    viz.config.show_grid = True
    viz.config.background_color = "#1a1a1a"
    
    # Create camera trajectory
    print("Creating camera trajectory...")
    camera_trajectory = create_camera_orbit_trajectory(n_frames)
    
    # Export options
    output_path = "demo_export.mp4"
    resolution = (1280, 720)
    fps = 30
    
    print(f"Exporting video to: {output_path}")
    print(f"Resolution: {resolution[0]}x{resolution[1]}")
    print(f"FPS: {fps}")
    print(f"Frames: {n_frames}")
    
    # Progress callback
    def progress_callback(progress):
        percent = int(progress * 100)
        bar_length = 40
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\rExporting: [{bar}] {percent}%", end="", flush=True)
    
    # Export video
    success = viz.export_video(
        output_path=output_path,
        start_frame=0,
        end_frame=n_frames - 1,
        resolution=resolution,
        fps=fps,
        camera_trajectory=camera_trajectory,
        progress_callback=progress_callback
    )
    
    print()  # New line after progress bar
    
    if success:
        print(f"✓ Video exported successfully: {output_path}")
        print(f"  File size: {Path(output_path).stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("✗ Video export failed")
    
    # Also export image sequence
    print("\nExporting image sequence...")
    
    image_dir = "demo_frames"
    success = viz.export_image_sequence(
        output_dir=image_dir,
        start_frame=0,
        end_frame=min(30, n_frames - 1),  # Just first 30 frames
        resolution=resolution,
        image_format="png",
        camera_trajectory=camera_trajectory,
        progress_callback=progress_callback
    )
    
    print()
    
    if success:
        print(f"✓ Image sequence exported to: {image_dir}/")
        frame_count = len(list(Path(image_dir).glob("*.png")))
        print(f"  Exported {frame_count} frames")
    else:
        print("✗ Image sequence export failed")


if __name__ == "__main__":
    export_demo_video()