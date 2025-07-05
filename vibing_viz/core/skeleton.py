"""Skeleton definitions for pose visualization."""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np


class Skeleton:
    """Defines the structure of a skeleton.
    
    A skeleton consists of keypoint definitions and the edges that
    connect them to form a skeletal structure.
    
    Attributes:
        name: Name of the skeleton type (e.g., "COCO", "Custom").
        keypoint_names: List of keypoint names.
        edges: List of (start_idx, end_idx) connections.
        keypoint_colors: Optional per-keypoint colors.
        edge_colors: Optional per-edge colors.
    """
    
    def __init__(
        self,
        name: str,
        keypoint_names: List[str],
        edges: List[Tuple[int, int]],
        keypoint_colors: Optional[List[str]] = None,
        edge_colors: Optional[List[str]] = None,
    ):
        """Initialize skeleton.
        
        Args:
            name: Name of the skeleton type.
            keypoint_names: List of keypoint names.
            edges: List of (start_idx, end_idx) tuples.
            keypoint_colors: Optional colors per keypoint.
            edge_colors: Optional colors per edge.
        """
        self.name = name
        self.keypoint_names = keypoint_names
        self.edges = edges
        self.keypoint_colors = keypoint_colors
        self.edge_colors = edge_colors
        
        self._validate()
        
    def _validate(self):
        """Validate skeleton structure."""
        n_keypoints = len(self.keypoint_names)
        
        # Validate edges
        for i, (start, end) in enumerate(self.edges):
            if not (0 <= start < n_keypoints and 0 <= end < n_keypoints):
                raise ValueError(
                    f"Edge {i} connects invalid keypoints: ({start}, {end}). "
                    f"Valid range is 0-{n_keypoints-1}"
                )
        
        # Validate colors if provided
        if self.keypoint_colors is not None:
            if len(self.keypoint_colors) != n_keypoints:
                raise ValueError(
                    f"Number of keypoint colors ({len(self.keypoint_colors)}) "
                    f"must match number of keypoints ({n_keypoints})"
                )
        
        if self.edge_colors is not None:
            if len(self.edge_colors) != len(self.edges):
                raise ValueError(
                    f"Number of edge colors ({len(self.edge_colors)}) "
                    f"must match number of edges ({len(self.edges)})"
                )
    
    @property
    def n_keypoints(self) -> int:
        """Number of keypoints in the skeleton."""
        return len(self.keypoint_names)
    
    @property
    def n_edges(self) -> int:
        """Number of edges in the skeleton."""
        return len(self.edges)
    
    def get_keypoint_index(self, name: str) -> int:
        """Get index of keypoint by name.
        
        Args:
            name: Keypoint name.
            
        Returns:
            Index of the keypoint.
            
        Raises:
            ValueError: If keypoint name not found.
        """
        try:
            return self.keypoint_names.index(name)
        except ValueError:
            raise ValueError(f"Keypoint '{name}' not found in skeleton")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with skeleton data.
        """
        return {
            "name": self.name,
            "keypoint_names": self.keypoint_names,
            "edges": self.edges,
            "keypoint_colors": self.keypoint_colors,
            "edge_colors": self.edge_colors,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skeleton":
        """Create skeleton from dictionary.
        
        Args:
            data: Dictionary with skeleton data.
            
        Returns:
            Skeleton instance.
        """
        return cls(**data)


# Pre-defined skeleton templates
SKELETONS = {
    "COCO-17": Skeleton(
        name="COCO-17",
        keypoint_names=[
            "nose", "left_eye", "right_eye", "left_ear", "right_ear",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hip", "right_hip",
            "left_knee", "right_knee", "left_ankle", "right_ankle"
        ],
        edges=[
            # Head
            (0, 1), (0, 2), (1, 3), (2, 4),
            # Arms
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
            # Torso
            (5, 11), (6, 12), (11, 12),
            # Legs
            (11, 13), (13, 15), (12, 14), (14, 16),
        ]
    ),
    
    "BODY-25": Skeleton(
        name="BODY-25",
        keypoint_names=[
            "nose", "neck", "right_shoulder", "right_elbow", "right_wrist",
            "left_shoulder", "left_elbow", "left_wrist", "mid_hip",
            "right_hip", "right_knee", "right_ankle", "left_hip",
            "left_knee", "left_ankle", "right_eye", "left_eye",
            "right_ear", "left_ear", "left_big_toe", "left_small_toe",
            "left_heel", "right_big_toe", "right_small_toe", "right_heel"
        ],
        edges=[
            # Head/Neck
            (0, 1), (0, 15), (0, 16), (15, 17), (16, 18),
            # Arms
            (1, 2), (2, 3), (3, 4), (1, 5), (5, 6), (6, 7),
            # Torso
            (1, 8), (8, 9), (8, 12), (9, 10), (12, 13),
            # Legs
            (10, 11), (13, 14),
            # Feet
            (11, 22), (11, 23), (11, 24),
            (14, 19), (14, 20), (14, 21),
        ]
    ),
    
    "SIMPLE": Skeleton(
        name="SIMPLE",
        keypoint_names=[
            "head", "neck", "left_shoulder", "right_shoulder",
            "left_elbow", "right_elbow", "left_wrist", "right_wrist",
            "left_hip", "right_hip", "left_knee", "right_knee",
            "left_ankle", "right_ankle"
        ],
        edges=[
            # Head to neck
            (0, 1),
            # Shoulders
            (1, 2), (1, 3),
            # Arms
            (2, 4), (4, 6), (3, 5), (5, 7),
            # Torso
            (2, 8), (3, 9), (8, 9),
            # Legs
            (8, 10), (10, 12), (9, 11), (11, 13),
        ]
    ),
}