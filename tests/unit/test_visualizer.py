"""Tests for the main visualizer."""

import pytest
import numpy as np

from vibing_viz import Visualizer


class TestVisualizer:
    """Test Visualizer class."""
    
    def test_init(self):
        """Test visualizer initialization."""
        viz = Visualizer()
        
        assert viz.tracks == {}
        assert viz.cameras == {}
        assert viz._current_frame == 0
        assert viz.scene_manager is not None
        assert viz.pose_renderer is not None
        assert viz.polygon_renderer is not None
    
    def test_add_track(self, sample_poses, sample_edges):
        """Test adding a track."""
        viz = Visualizer()
        
        # Add track
        viz.add_track(
            track_id="test_track",
            poses=sample_poses,
            edges=sample_edges
        )
        
        # Check track was added
        assert "test_track" in viz.tracks
        track = viz.tracks["test_track"]
        
        assert track.track_id == "test_track"
        assert track.n_frames == 100
        assert track.n_keypoints == 17
        assert track.edges == sample_edges
    
    def test_add_track_with_color(self, sample_poses):
        """Test adding track with custom color."""
        viz = Visualizer()
        
        viz.add_track(
            track_id="colored_track",
            poses=sample_poses,
            color="#FF0000",
            keypoint_size=10.0
        )
        
        track = viz.tracks["colored_track"]
        assert track.color == "#FF0000"
        assert track.keypoint_size == 10.0
    
    def test_add_duplicate_track(self, sample_poses):
        """Test error on duplicate track ID."""
        viz = Visualizer()
        
        viz.add_track("track1", sample_poses)
        
        with pytest.raises(ValueError, match="already exists"):
            viz.add_track("track1", sample_poses)
    
    def test_add_camera(self, camera_matrix):
        """Test adding a camera."""
        viz = Visualizer()
        
        viz.add_camera(
            name="test_camera",
            extrinsics=camera_matrix,
            fov=60.0
        )
        
        assert "test_camera" in viz.cameras
        camera = viz.cameras["test_camera"]
        
        assert camera.name == "test_camera"
        assert np.array_equal(camera.extrinsics, camera_matrix)
        assert camera.fov == 60.0
    
    def test_set_frame(self, sample_poses):
        """Test setting current frame."""
        viz = Visualizer()
        viz.add_track("track1", sample_poses)
        
        # Set frame
        viz.set_frame(50)
        assert viz._current_frame == 50
        
        # Frame should be clamped to valid range
        viz.set_frame(-1)
        assert viz._current_frame == -1  # Not clamped in basic implementation
    
    def test_get_total_frames(self, sample_poses):
        """Test getting total frame count."""
        viz = Visualizer()
        
        # Empty visualizer
        assert viz.get_total_frames() == 0
        
        # Add tracks with different lengths
        viz.add_track("track1", sample_poses[:50])  # 50 frames
        assert viz.get_total_frames() == 50
        
        viz.add_track("track2", sample_poses)  # 100 frames
        assert viz.get_total_frames() == 100
    
    def test_config(self):
        """Test visualizer configuration."""
        viz = Visualizer()
        
        # Default config
        assert viz.config.show_grid == True
        assert viz.config.background_color == "#1a1a1a"
        
        # Modify config
        viz.config.show_grid = False
        viz.config.show_trails = True
        viz.config.trail_length = 20
        
        assert viz.config.show_grid == False
        assert viz.config.show_trails == True
        assert viz.config.trail_length == 20