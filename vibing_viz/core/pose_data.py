"""Core data structures for pose data management."""

from dataclasses import dataclass
from typing import Optional, List
import numpy as np


@dataclass
class PoseFrame:
    """Single frame of pose data.
    
    Attributes:
        keypoints: Array of shape (n_keypoints, 3) containing 3D positions.
        frame_idx: Frame index in the sequence.
        timestamp: Optional timestamp in seconds.
        confidence: Optional confidence scores per keypoint.
    """
    
    keypoints: np.ndarray
    frame_idx: int
    timestamp: Optional[float] = None
    confidence: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        if self.keypoints.ndim != 2 or self.keypoints.shape[1] != 3:
            raise ValueError(
                f"Keypoints must have shape (n_keypoints, 3), "
                f"got {self.keypoints.shape}"
            )
        
        if self.confidence is not None:
            if self.confidence.shape[0] != self.keypoints.shape[0]:
                raise ValueError(
                    f"Confidence scores must match number of keypoints. "
                    f"Got {self.confidence.shape[0]} scores for "
                    f"{self.keypoints.shape[0]} keypoints"
                )


class PoseSequence:
    """Manages pose data with efficient access patterns.
    
    This class supports both batch loading (all frames at once) and
    streaming mode (frames added one at a time). It provides efficient
    access patterns and caching for large datasets.
    
    Attributes:
        is_streaming: Whether the sequence is in streaming mode.
    """
    
    def __init__(self, data: Optional[np.ndarray] = None):
        """Initialize pose sequence.
        
        Args:
            data: Optional array of shape (n_frames, n_keypoints, 3).
                If provided, initializes in batch mode.
        """
        self._frames: List[PoseFrame] = []
        self._frame_cache = {}
        self._is_streaming = False
        
        if data is not None:
            self.set_batch_data(data)
    
    @property
    def is_streaming(self) -> bool:
        """Whether the sequence is in streaming mode."""
        return self._is_streaming
    
    @property
    def n_frames(self) -> int:
        """Number of frames in the sequence."""
        return len(self._frames)
    
    @property
    def n_keypoints(self) -> int:
        """Number of keypoints per frame."""
        if self._frames:
            return self._frames[0].keypoints.shape[0]
        return 0
    
    def set_batch_data(self, data: np.ndarray) -> None:
        """Load all frames at once (batch mode).
        
        Args:
            data: Array of shape (n_frames, n_keypoints, 3).
            
        Raises:
            ValueError: If data has invalid shape.
        """
        if data.ndim != 3 or data.shape[2] != 3:
            raise ValueError(
                f"Data must have shape (n_frames, n_keypoints, 3), "
                f"got {data.shape}"
            )
        
        self._is_streaming = False
        self._frames = [
            PoseFrame(keypoints=data[i].copy(), frame_idx=i)
            for i in range(len(data))
        ]
        self._frame_cache.clear()
        
    def append_frame(self, frame: PoseFrame) -> None:
        """Add single frame (streaming mode).
        
        Args:
            frame: PoseFrame to append.
            
        Raises:
            ValueError: If frame has incompatible number of keypoints.
        """
        if self._frames and frame.keypoints.shape[0] != self.n_keypoints:
            raise ValueError(
                f"Frame has {frame.keypoints.shape[0]} keypoints, "
                f"expected {self.n_keypoints}"
            )
        
        self._is_streaming = True
        frame.frame_idx = len(self._frames)
        self._frames.append(frame)
        
    def get_frame(self, idx: int) -> Optional[PoseFrame]:
        """Get frame by index with caching.
        
        Args:
            idx: Frame index.
            
        Returns:
            PoseFrame at given index, or None if out of bounds.
        """
        if 0 <= idx < len(self._frames):
            return self._frames[idx]
        return None
    
    def to_numpy(self) -> np.ndarray:
        """Convert to numpy array.
        
        Returns:
            Array of shape (n_frames, n_keypoints, 3).
        """
        if not self._frames:
            return np.empty((0, 0, 3))
        
        return np.stack([frame.keypoints for frame in self._frames])