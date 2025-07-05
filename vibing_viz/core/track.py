"""Track management for pose sequences."""

from typing import Optional, List, Tuple, Dict, Any
import numpy as np

from vibing_viz.core.pose_data import PoseSequence


class Track:
    """Represents a single tracked subject.
    
    A track contains pose data for one subject across time, along with
    metadata like skeleton structure and visualization properties.
    
    Attributes:
        track_id: Unique identifier for this track.
        pose_sequence: The pose data for this track.
        edges: Skeleton edge connections.
        polygons: Surface polygon definitions.
        metadata: Additional track metadata.
    """
    
    def __init__(
        self,
        track_id: str,
        pose_sequence: PoseSequence,
        edges: Optional[List[Tuple[int, int]]] = None,
        polygons: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize track.
        
        Args:
            track_id: Unique identifier for this track.
            pose_sequence: PoseSequence containing the track's pose data.
            edges: List of (start_idx, end_idx) tuples defining skeleton edges.
            polygons: List of polygon definitions with 'indices' and optional 'name'.
            metadata: Additional metadata dictionary.
        """
        self.track_id = track_id
        self.pose_sequence = pose_sequence
        self.edges = edges or []
        self.polygons = polygons or []
        self.metadata = metadata or {}
        
        # Visualization properties
        self._color: Optional[str] = None
        self._visible: bool = True
        self._opacity: float = 1.0
        self._keypoint_size: float = 5.0
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate track data consistency."""
        n_keypoints = self.pose_sequence.n_keypoints
        
        # Validate edges
        for i, (start, end) in enumerate(self.edges):
            if not (0 <= start < n_keypoints and 0 <= end < n_keypoints):
                raise ValueError(
                    f"Edge {i} connects invalid keypoints: ({start}, {end}). "
                    f"Valid range is 0-{n_keypoints-1}"
                )
        
        # Validate polygons
        for i, polygon in enumerate(self.polygons):
            if "indices" not in polygon:
                raise ValueError(f"Polygon {i} missing required 'indices' field")
            
            indices = polygon["indices"]
            if any(idx < 0 or idx >= n_keypoints for idx in indices):
                raise ValueError(
                    f"Polygon {i} has invalid keypoint indices. "
                    f"Valid range is 0-{n_keypoints-1}"
                )
    
    @property
    def color(self) -> Optional[str]:
        """Track color for visualization."""
        return self._color
    
    @color.setter
    def color(self, value: str) -> None:
        """Set track color."""
        self._color = value
    
    @property
    def visible(self) -> bool:
        """Whether track is visible."""
        return self._visible
    
    @visible.setter
    def visible(self, value: bool) -> None:
        """Set track visibility."""
        self._visible = bool(value)
    
    @property
    def opacity(self) -> float:
        """Track opacity (0-1)."""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value: float) -> None:
        """Set track opacity."""
        self._opacity = max(0.0, min(1.0, float(value)))
    
    @property
    def keypoint_size(self) -> float:
        """Size of keypoint markers."""
        return self._keypoint_size
    
    @keypoint_size.setter
    def keypoint_size(self, value: float) -> None:
        """Set keypoint marker size."""
        self._keypoint_size = max(0.1, float(value))
    
    @property
    def n_frames(self) -> int:
        """Number of frames in this track."""
        return self.pose_sequence.n_frames
    
    @property
    def n_keypoints(self) -> int:
        """Number of keypoints per frame."""
        return self.pose_sequence.n_keypoints
    
    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get spatial bounds of the track.
        
        Returns:
            Tuple of (min_coords, max_coords), each shape (3,).
        """
        data = self.pose_sequence.to_numpy()
        if data.size == 0:
            return np.zeros(3), np.zeros(3)
        
        # Reshape to (n_frames * n_keypoints, 3) and ignore NaNs
        flat_data = data.reshape(-1, 3)
        valid_mask = ~np.any(np.isnan(flat_data), axis=1)
        
        if not np.any(valid_mask):
            return np.zeros(3), np.zeros(3)
        
        valid_data = flat_data[valid_mask]
        return valid_data.min(axis=0), valid_data.max(axis=0)