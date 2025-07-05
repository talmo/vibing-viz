"""Coordinate system transformations."""

from typing import Tuple, Union, Optional
import numpy as np


def euler_to_rotation_matrix(
    angles: Union[Tuple[float, float, float], np.ndarray],
    order: str = "XYZ"
) -> np.ndarray:
    """Convert Euler angles to rotation matrix.
    
    Args:
        angles: Rotation angles in radians (rx, ry, rz).
        order: Order of rotations (e.g., "XYZ", "ZYX").
        
    Returns:
        3x3 rotation matrix.
    """
    rx, ry, rz = angles
    
    # Individual rotation matrices
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ])
    
    Ry = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ])
    
    Rz = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ])
    
    # Combine based on order
    rotations = {"X": Rx, "Y": Ry, "Z": Rz}
    R = np.eye(3)
    for axis in order:
        R = rotations[axis] @ R
    
    return R


def create_transform_matrix(
    translation: Optional[np.ndarray] = None,
    rotation: Optional[np.ndarray] = None,
    scale: Optional[Union[float, np.ndarray]] = None,
    rotation_order: str = "XYZ"
) -> np.ndarray:
    """Create 4x4 transformation matrix.
    
    Args:
        translation: 3D translation vector.
        rotation: Euler angles in radians or 3x3 rotation matrix.
        scale: Uniform scale or per-axis scale factors.
        rotation_order: Order for Euler angles (if rotation is angles).
        
    Returns:
        4x4 transformation matrix.
    """
    T = np.eye(4)
    
    # Apply scale
    if scale is not None:
        if isinstance(scale, (int, float)):
            scale = np.array([scale, scale, scale])
        else:
            scale = np.array(scale)
        T[:3, :3] = np.diag(scale)
    
    # Apply rotation
    if rotation is not None:
        if rotation.shape == (3,):
            # Euler angles
            R = euler_to_rotation_matrix(rotation, rotation_order)
        else:
            # Rotation matrix
            R = rotation
        T[:3, :3] = R @ T[:3, :3]
    
    # Apply translation
    if translation is not None:
        T[:3, 3] = translation
    
    return T


def decompose_transform_matrix(
    matrix: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Decompose 4x4 matrix into translation, rotation, and scale.
    
    Args:
        matrix: 4x4 transformation matrix.
        
    Returns:
        Tuple of (translation, rotation_matrix, scale).
    """
    # Extract translation
    translation = matrix[:3, 3]
    
    # Extract rotation and scale
    M = matrix[:3, :3]
    
    # Compute scale
    scale = np.array([
        np.linalg.norm(M[:, 0]),
        np.linalg.norm(M[:, 1]),
        np.linalg.norm(M[:, 2])
    ])
    
    # Remove scale to get rotation
    rotation = M.copy()
    rotation[:, 0] /= scale[0]
    rotation[:, 1] /= scale[1]
    rotation[:, 2] /= scale[2]
    
    return translation, rotation, scale


def apply_transform(
    points: np.ndarray,
    transform: np.ndarray
) -> np.ndarray:
    """Apply transformation to 3D points.
    
    Args:
        points: Points array of shape (..., 3).
        transform: 4x4 transformation matrix.
        
    Returns:
        Transformed points of same shape.
    """
    shape = points.shape
    points_flat = points.reshape(-1, 3)
    
    # Convert to homogeneous coordinates
    points_homo = np.hstack([points_flat, np.ones((len(points_flat), 1))])
    
    # Apply transform
    transformed = (transform @ points_homo.T).T[:, :3]
    
    return transformed.reshape(shape)


def align_coordinate_systems(
    source_up: str = "Z",
    source_forward: str = "Y",
    target_up: str = "Y",
    target_forward: str = "-Z"
) -> np.ndarray:
    """Create transformation to align coordinate systems.
    
    Args:
        source_up: Source system's up axis ("X", "Y", "Z", "-X", "-Y", "-Z").
        source_forward: Source system's forward axis.
        target_up: Target system's up axis.
        target_forward: Target system's forward axis.
        
    Returns:
        4x4 transformation matrix.
    """
    # Define basis vectors
    axes = {
        "X": np.array([1, 0, 0]),
        "Y": np.array([0, 1, 0]),
        "Z": np.array([0, 0, 1]),
        "-X": np.array([-1, 0, 0]),
        "-Y": np.array([0, -1, 0]),
        "-Z": np.array([0, 0, -1]),
    }
    
    # Get source basis
    src_up = axes[source_up]
    src_forward = axes[source_forward]
    src_right = np.cross(src_forward, src_up)
    
    # Get target basis
    tgt_up = axes[target_up]
    tgt_forward = axes[target_forward]
    tgt_right = np.cross(tgt_forward, tgt_up)
    
    # Build rotation matrix
    src_basis = np.column_stack([src_right, src_up, src_forward])
    tgt_basis = np.column_stack([tgt_right, tgt_up, tgt_forward])
    
    rotation = tgt_basis @ np.linalg.inv(src_basis)
    
    # Create 4x4 matrix
    transform = np.eye(4)
    transform[:3, :3] = rotation
    
    return transform


class CoordinateTransform:
    """Manages coordinate system transformations for the scene.
    
    This class helps convert between different coordinate conventions
    (e.g., Y-up vs Z-up) and apply user-defined transformations.
    """
    
    def __init__(self):
        """Initialize with identity transform."""
        self.transform = np.eye(4)
        self.inverse_transform = np.eye(4)
    
    def set_transform(
        self,
        translation: Optional[np.ndarray] = None,
        rotation: Optional[np.ndarray] = None,
        scale: Optional[Union[float, np.ndarray]] = None,
        rotation_order: str = "XYZ"
    ):
        """Set the transformation.
        
        Args:
            translation: 3D translation vector.
            rotation: Euler angles or rotation matrix.
            scale: Uniform or per-axis scale.
            rotation_order: Order for Euler angles.
        """
        self.transform = create_transform_matrix(
            translation, rotation, scale, rotation_order
        )
        self.inverse_transform = np.linalg.inv(self.transform)
    
    def set_from_matrix(self, matrix: np.ndarray):
        """Set transformation from 4x4 matrix.
        
        Args:
            matrix: 4x4 transformation matrix.
        """
        self.transform = matrix.copy()
        self.inverse_transform = np.linalg.inv(matrix)
    
    def apply(self, points: np.ndarray) -> np.ndarray:
        """Apply transformation to points.
        
        Args:
            points: Points array of shape (..., 3).
            
        Returns:
            Transformed points.
        """
        return apply_transform(points, self.transform)
    
    def apply_inverse(self, points: np.ndarray) -> np.ndarray:
        """Apply inverse transformation to points.
        
        Args:
            points: Points array of shape (..., 3).
            
        Returns:
            Inverse transformed points.
        """
        return apply_transform(points, self.inverse_transform)