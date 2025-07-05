"""Demo of camera system and video overlay features."""

import sys
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from vibing_viz import Visualizer
from vibing_viz.ui.main_window import VibingVizMainWindow


def create_sample_video_frames(output_path: str, n_frames: int = 30, size: tuple = (640, 480)):
    """Create a sample video file for testing.
    
    Args:
        output_path: Path to save video.
        n_frames: Number of frames to generate.
        size: Video dimensions (width, height).
    """
    import imageio.v3 as iio
    
    frames = []
    for i in range(n_frames):
        # Create a frame with moving circle
        frame = np.zeros((*size[::-1], 3), dtype=np.uint8)
        frame[:, :] = [50, 50, 50]  # Dark gray background
        
        # Draw circle
        center_x = int(size[0] * (0.2 + 0.6 * (i / n_frames)))
        center_y = size[1] // 2
        radius = 30
        
        y, x = np.ogrid[:size[1], :size[0]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        frame[mask] = [255, 100, 100]  # Red circle
        
        # Add frame number
        frame[10:30, 10:10+len(str(i))*10] = 255
        
        frames.append(frame)
    
    # Write video
    iio.imwrite(output_path, frames, fps=30)
    print(f"Created sample video: {output_path}")


def create_test_image(output_path: str, size: tuple = (640, 480)):
    """Create a test image for overlay.
    
    Args:
        output_path: Path to save image.
        size: Image dimensions.
    """
    import imageio.v3 as iio
    
    # Create checkerboard pattern
    image = np.zeros((*size[::-1], 3), dtype=np.uint8)
    square_size = 40
    
    for i in range(0, size[1], square_size):
        for j in range(0, size[0], square_size):
            if (i // square_size + j // square_size) % 2 == 0:
                image[i:i+square_size, j:j+square_size] = [200, 200, 200]
            else:
                image[i:i+square_size, j:j+square_size] = [100, 100, 100]
    
    # Add border
    image[:5, :] = [255, 0, 0]
    image[-5:, :] = [255, 0, 0]
    image[:, :5] = [255, 0, 0]
    image[:, -5:] = [255, 0, 0]
    
    iio.imwrite(output_path, image)
    print(f"Created test image: {output_path}")


def main():
    """Run camera and overlay demo."""
    print("Camera and Video Overlay Demo")
    print("=============================")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create test media files
    video_path = "test_video.mp4"
    image_path = "test_overlay.png"
    
    if not Path(video_path).exists():
        print("Creating sample video...")
        create_sample_video_frames(video_path)
    
    if not Path(image_path).exists():
        print("Creating test image...")
        create_test_image(image_path)
    
    # Create visualizer
    viz = Visualizer()
    
    # Generate pose data
    n_frames = 30
    n_keypoints = 17
    poses = np.zeros((n_frames, n_keypoints, 3))
    
    for i in range(n_frames):
        # Create a pose that moves in a circle
        angle = 2 * np.pi * (i / n_frames)
        radius = 3
        
        # Base position
        base_x = radius * np.cos(angle)
        base_y = radius * np.sin(angle)
        
        # Add keypoints in a humanoid shape
        poses[i] = np.random.randn(n_keypoints, 3) * 0.3
        poses[i, :, 0] += base_x
        poses[i, :, 1] += base_y
        poses[i, :, 2] += 1.5  # Lift above ground
    
    # Define skeleton
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Spine
        (2, 5), (5, 6), (6, 7),  # Left arm
        (2, 8), (8, 9), (9, 10),  # Right arm
        (0, 11), (11, 12), (12, 13),  # Left leg
        (0, 14), (14, 15), (15, 16),  # Right leg
    ]
    
    # Add track
    viz.add_track("demo_track", poses, edges=edges, color="#00ff00")
    
    # Add video overlay
    try:
        viz.add_video_overlay("video_overlay", video_path, opacity=0.5)
        print("Added video overlay")
    except Exception as e:
        print(f"Could not add video overlay: {e}")
    
    # Add image overlay
    try:
        viz.add_image_overlay("image_overlay", image_path, opacity=0.3)
        print("Added image overlay")
    except Exception as e:
        print(f"Could not add image overlay: {e}")
    
    # Configure visualization
    viz.config.show_grid = True
    viz.config.background_color = "#2a2a2a"
    
    # Create main window
    window = VibingVizMainWindow(visualizer=viz)
    
    # Add track to UI
    window.scene_panel.add_track("demo_track", "Demo Track", "#00ff00")
    window.tracks_panel.add_track("demo_track", "Demo Track", "#00ff00", n_frames, n_keypoints)
    window.timeline.set_total_frames(n_frames)
    window.timeline.add_track("demo_track", "#00ff00", [(0, n_frames-1)])
    
    # Show instructions
    print("\nControls:")
    print("  - Front/Side/Top buttons: Switch camera views")
    print("  - Space: Play/pause animation")
    print("  - Left/Right arrows: Step through frames")
    print("  - Mouse: Orbit camera (drag), Pan (right-drag), Zoom (scroll)")
    print("\nNote: Video overlay will update with frame changes")
    
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()