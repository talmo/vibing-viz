"""Tests for pose data structures."""

import pytest
import numpy as np

from vibing_viz.core.pose_data import PoseFrame, PoseSequence


class TestPoseFrame:
    """Test PoseFrame class."""
    
    def test_init_valid(self):
        """Test valid initialization."""
        keypoints = np.random.randn(17, 3)
        frame = PoseFrame(keypoints=keypoints, frame_idx=0)
        
        assert frame.frame_idx == 0
        assert np.array_equal(frame.keypoints, keypoints)
        assert frame.timestamp is None
        assert frame.confidence is None
    
    def test_init_with_optional_fields(self):
        """Test initialization with optional fields."""
        keypoints = np.random.randn(17, 3)
        confidence = np.random.rand(17)
        
        frame = PoseFrame(
            keypoints=keypoints,
            frame_idx=10,
            timestamp=0.33,
            confidence=confidence
        )
        
        assert frame.timestamp == 0.33
        assert np.array_equal(frame.confidence, confidence)
    
    def test_invalid_keypoints_shape(self):
        """Test error on invalid keypoints shape."""
        with pytest.raises(ValueError, match="shape"):
            PoseFrame(keypoints=np.random.randn(17), frame_idx=0)
        
        with pytest.raises(ValueError, match="shape"):
            PoseFrame(keypoints=np.random.randn(17, 2), frame_idx=0)
    
    def test_mismatched_confidence(self):
        """Test error on mismatched confidence scores."""
        keypoints = np.random.randn(17, 3)
        confidence = np.random.rand(10)  # Wrong size
        
        with pytest.raises(ValueError, match="Confidence scores must match"):
            PoseFrame(
                keypoints=keypoints,
                frame_idx=0,
                confidence=confidence
            )


class TestPoseSequence:
    """Test PoseSequence class."""
    
    def test_init_empty(self):
        """Test empty initialization."""
        seq = PoseSequence()
        
        assert seq.n_frames == 0
        assert seq.n_keypoints == 0
        assert not seq.is_streaming
    
    def test_init_with_data(self, sample_poses):
        """Test initialization with batch data."""
        seq = PoseSequence(sample_poses)
        
        assert seq.n_frames == 100
        assert seq.n_keypoints == 17
        assert not seq.is_streaming
    
    def test_set_batch_data(self, sample_poses):
        """Test setting batch data."""
        seq = PoseSequence()
        seq.set_batch_data(sample_poses)
        
        assert seq.n_frames == len(sample_poses)
        assert seq.n_keypoints == sample_poses.shape[1]
    
    def test_invalid_batch_data(self):
        """Test error on invalid batch data."""
        seq = PoseSequence()
        
        # Wrong number of dimensions
        with pytest.raises(ValueError, match="shape"):
            seq.set_batch_data(np.random.randn(100, 17))
        
        # Wrong last dimension
        with pytest.raises(ValueError, match="shape"):
            seq.set_batch_data(np.random.randn(100, 17, 2))
    
    def test_append_frame(self):
        """Test streaming mode with append."""
        seq = PoseSequence()
        
        # First frame
        frame1 = PoseFrame(np.random.randn(17, 3), frame_idx=0)
        seq.append_frame(frame1)
        
        assert seq.n_frames == 1
        assert seq.n_keypoints == 17
        assert seq.is_streaming
        
        # Second frame
        frame2 = PoseFrame(np.random.randn(17, 3), frame_idx=1)
        seq.append_frame(frame2)
        
        assert seq.n_frames == 2
    
    def test_append_incompatible_frame(self):
        """Test error on incompatible frame append."""
        seq = PoseSequence()
        
        # First frame with 17 keypoints
        frame1 = PoseFrame(np.random.randn(17, 3), frame_idx=0)
        seq.append_frame(frame1)
        
        # Try to append frame with different number of keypoints
        frame2 = PoseFrame(np.random.randn(20, 3), frame_idx=1)
        with pytest.raises(ValueError, match="keypoints"):
            seq.append_frame(frame2)
    
    def test_get_frame(self, sample_poses):
        """Test frame retrieval."""
        seq = PoseSequence(sample_poses)
        
        # Valid indices
        frame = seq.get_frame(0)
        assert frame is not None
        assert frame.frame_idx == 0
        
        frame = seq.get_frame(50)
        assert frame is not None
        assert frame.frame_idx == 50
        
        # Invalid indices
        assert seq.get_frame(-1) is None
        assert seq.get_frame(100) is None
    
    def test_to_numpy(self, sample_poses):
        """Test conversion back to numpy."""
        seq = PoseSequence(sample_poses)
        data = seq.to_numpy()
        
        assert data.shape == sample_poses.shape
        # Data should be equal but not the same object
        assert np.allclose(data, sample_poses)
        assert data is not sample_poses
    
    def test_to_numpy_empty(self):
        """Test numpy conversion of empty sequence."""
        seq = PoseSequence()
        data = seq.to_numpy()
        
        assert data.shape == (0, 0, 3)