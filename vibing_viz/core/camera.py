"""Camera models and utilities."""

from typing import Optional, Tuple
import numpy as np


class Camera:
    """Represents a camera with intrinsic and extrinsic parameters.
    
    Attributes:
        name: Camera identifier.
        extrinsics: 4x4 transformation matrix (world to camera).
        intrinsics: 3x3 intrinsic matrix (optional).
        resolution: (width, height) in pixels.
        fov: Field of view in degrees (for visualization).
    """
    
    def __init__(
        self,
        name: str,
        extrinsics: np.ndarray,
        intrinsics: Optional[np.ndarray] = None,
        resolution: Tuple[int, int] = (1920, 1080),
        fov: float = 60.0,
    ):
        """Initialize camera.
        
        Args:
            name: Camera identifier.
            extrinsics: 4x4 transformation matrix.
            intrinsics: Optional 3x3 intrinsic matrix.
            resolution: Image resolution (width, height).
            fov: Field of view for visualization.
        """
        self.name = name
        self.extrinsics = np.array(extrinsics, dtype=np.float64)
        self.intrinsics = (
            np.array(intrinsics, dtype=np.float64) 
            if intrinsics is not None 
            else None
        )
        self.resolution = resolution
        self.fov = fov
        
        self._validate()
    
    def _validate(self):
        """Validate camera parameters."""
        # Check extrinsics
        if self.extrinsics.shape != (4, 4):
            raise ValueError(
                f"Extrinsics must be 4x4 matrix, got {self.extrinsics.shape}"
            )
        
        # Check intrinsics if provided
        if self.intrinsics is not None:
            if self.intrinsics.shape != (3, 3):
                raise ValueError(
                    f"Intrinsics must be 3x3 matrix, got {self.intrinsics.shape}"
                )
    
    @property
    def position(self) -> np.ndarray:
        """Get camera position in world coordinates.
        
        Returns:
            3D position vector.
        """
        # Camera position is the translation part of the inverse extrinsics
        return -self.extrinsics[:3, :3].T @ self.extrinsics[:3, 3]
    
    @property
    def forward(self) -> np.ndarray:
        """Get camera forward direction in world coordinates.
        
        Returns:
            3D direction vector (normalized).
        """
        # Forward is -Z in camera space, transformed to world
        cam_forward = np.array([0, 0, -1])
        world_forward = self.extrinsics[:3, :3].T @ cam_forward
        return world_forward / np.linalg.norm(world_forward)
    
    @property
    def up(self) -> np.ndarray:
        """Get camera up direction in world coordinates.
        
        Returns:
            3D direction vector (normalized).
        """
        # Up is +Y in camera space
        cam_up = np.array([0, 1, 0])
        world_up = self.extrinsics[:3, :3].T @ cam_up
        return world_up / np.linalg.norm(world_up)
    
    @property
    def right(self) -> np.ndarray:
        """Get camera right direction in world coordinates.
        
        Returns:
            3D direction vector (normalized).
        """
        # Right is +X in camera space
        cam_right = np.array([1, 0, 0])
        world_right = self.extrinsics[:3, :3].T @ cam_right
        return world_right / np.linalg.norm(world_right)
    
    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio from resolution.
        
        Returns:
            Width / height ratio.
        """
        return self.resolution[0] / self.resolution[1]
    
    def world_to_camera(self, points: np.ndarray) -> np.ndarray:
        """Transform points from world to camera coordinates.
        
        Args:
            points: Points in world coordinates, shape (..., 3).
            
        Returns:
            Points in camera coordinates, shape (..., 3).
        """
        # Convert to homogeneous coordinates
        shape = points.shape
        points_flat = points.reshape(-1, 3)
        points_homo = np.hstack([points_flat, np.ones((len(points_flat), 1))])
        
        # Transform
        cam_points = (self.extrinsics @ points_homo.T).T[:, :3]
        
        return cam_points.reshape(shape)
    
    def camera_to_world(self, points: np.ndarray) -> np.ndarray:
        """Transform points from camera to world coordinates.
        
        Args:
            points: Points in camera coordinates, shape (..., 3).
            
        Returns:
            Points in world coordinates, shape (..., 3).
        """
        # Inverse transform
        inv_extrinsics = np.linalg.inv(self.extrinsics)
        
        shape = points.shape
        points_flat = points.reshape(-1, 3)
        points_homo = np.hstack([points_flat, np.ones((len(points_flat), 1))])
        
        world_points = (inv_extrinsics @ points_homo.T).T[:, :3]
        
        return world_points.reshape(shape)
    
    def project_to_image(self, points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Project 3D points to 2D image coordinates.
        
        Args:
            points: 3D points in world coordinates, shape (..., 3).
            
        Returns:
            Tuple of:
                - 2D image coordinates, shape (..., 2)
                - Valid mask (points in front of camera), shape (...)
        """
        if self.intrinsics is None:
            raise ValueError("Cannot project without intrinsic parameters")
        
        # Transform to camera coordinates
        cam_points = self.world_to_camera(points)
        
        # Check which points are in front of camera
        shape = cam_points.shape[:-1]
        cam_points_flat = cam_points.reshape(-1, 3)
        valid_mask = cam_points_flat[:, 2] > 0
        
        # Project using intrinsics
        image_points = np.zeros((len(cam_points_flat), 2))
        if np.any(valid_mask):
            valid_points = cam_points_flat[valid_mask]
            proj_points = (self.intrinsics @ valid_points.T).T
            image_points[valid_mask] = proj_points[:, :2] / proj_points[:, 2:3]
        
        # Reshape back
        image_points = image_points.reshape(shape + (2,))
        valid_mask = valid_mask.reshape(shape)
        
        return image_points, valid_mask
    
    def get_frustum_points(self, near: float = 0.1, far: float = 10.0) -> np.ndarray:
        """Get corners of the camera frustum.
        
        Args:
            near: Near plane distance.
            far: Far plane distance.
            
        Returns:
            Array of shape (8, 3) with frustum corners in world coordinates.
        """
        # Calculate frustum dimensions
        aspect = self.aspect_ratio
        fov_rad = np.radians(self.fov)
        
        # Near plane dimensions
        near_height = 2 * near * np.tan(fov_rad / 2)
        near_width = near_height * aspect
        
        # Far plane dimensions
        far_height = 2 * far * np.tan(fov_rad / 2)
        far_width = far_height * aspect
        
        # Frustum corners in camera space
        corners_cam = np.array([
            # Near plane
            [-near_width/2, -near_height/2, -near],
            [near_width/2, -near_height/2, -near],
            [near_width/2, near_height/2, -near],
            [-near_width/2, near_height/2, -near],
            # Far plane
            [-far_width/2, -far_height/2, -far],
            [far_width/2, -far_height/2, -far],
            [far_width/2, far_height/2, -far],
            [-far_width/2, far_height/2, -far],
        ])
        
        # Transform to world coordinates
        return self.camera_to_world(corners_cam)