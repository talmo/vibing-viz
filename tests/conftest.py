"""Pytest configuration and fixtures."""

import pytest
import numpy as np
from PyQt5.QtWidgets import QApplication

from vibing_viz import PoseSequence


@pytest.fixture
def sample_poses():
    """Generate sample pose data for testing.
    
    Returns:
        np.ndarray: Array of shape (100, 17, 3) with random pose data.
    """
    return np.random.randn(100, 17, 3)


@pytest.fixture
def sample_edges():
    """Sample skeleton edges for COCO-like skeleton.
    
    Returns:
        list: List of (start_idx, end_idx) tuples.
    """
    return [
        (0, 1), (0, 2),  # Head to shoulders
        (1, 3), (3, 5),  # Left arm
        (2, 4), (4, 6),  # Right arm
        (5, 7), (6, 8),  # Torso
        (7, 9), (9, 11),  # Left leg
        (8, 10), (10, 12),  # Right leg
    ]


@pytest.fixture
def sample_pose_sequence(sample_poses):
    """Create a sample PoseSequence object.
    
    Args:
        sample_poses: Fixture providing pose data.
        
    Returns:
        PoseSequence: Initialized pose sequence.
    """
    return PoseSequence(sample_poses)


@pytest.fixture(scope="session")
def qt_app():
    """Create QApplication for Qt tests.
    
    Yields:
        QApplication: Qt application instance.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def camera_matrix():
    """Sample camera extrinsics matrix.
    
    Returns:
        np.ndarray: 4x4 transformation matrix.
    """
    # Looking down from above
    matrix = np.eye(4)
    matrix[:3, 3] = [0, 0, 5]  # Position at (0, 0, 5)
    matrix[:3, :3] = np.array([
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0]
    ])  # Look down
    return matrix