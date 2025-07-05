"""Vibing-Viz: 3D visualization for pose tracking kinematics.

A powerful visualization tool for analyzing pose tracking data with
support for multiple subjects, camera views, and temporal playback.
"""

from vibing_viz.__version__ import __version__
from vibing_viz.core.pose_data import PoseFrame, PoseSequence
from vibing_viz.core.track import Track
from vibing_viz.visualization.visualizer import Visualizer

__all__ = [
    "__version__",
    "PoseFrame",
    "PoseSequence",
    "Track",
    "Visualizer",
]