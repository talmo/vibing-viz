"""Camera management and controls."""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pygfx as gfx

from vibing_viz.core.camera import Camera


class CameraView:
    """Represents a specific camera view configuration.
    
    Attributes:
        name: View name (e.g., "Front", "Top", "Custom 1").
        position: Camera position in world space.
        target: Look-at target position.
        up: Up vector.
        fov: Field of view for perspective cameras.
        zoom: Zoom level for orthographic cameras.
    """
    
    def __init__(
        self,
        name: str,
        position: np.ndarray,
        target: np.ndarray,
        up: np.ndarray = np.array([0, 0, 1]),
        fov: float = 60.0,
        zoom: float = 1.0
    ):
        """Initialize camera view.
        
        Args:
            name: View name.
            position: Camera position.
            target: Look-at target.
            up: Up vector.
            fov: Field of view.
            zoom: Zoom level.
        """
        self.name = name
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.fov = fov
        self.zoom = zoom


class CameraManager:
    """Manages multiple cameras and view presets.
    
    This class handles camera creation, switching between views,
    and managing camera animations.
    """
    
    def __init__(self, scene: gfx.Scene):
        """Initialize camera manager.
        
        Args:
            scene: PyGFX scene to add cameras to.
        """
        self.scene = scene
        self.cameras: Dict[str, gfx.Camera] = {}
        self.camera_objects: Dict[str, Camera] = {}
        self.active_camera_name: Optional[str] = None
        
        # Predefined views
        self.views: Dict[str, CameraView] = {}
        self._create_default_views()
        
        # Animation state
        self._animating = False
        self._animation_start_time = 0.0
        self._animation_duration = 1.0
        self._start_view: Optional[CameraView] = None
        self._target_view: Optional[CameraView] = None
    
    def _create_default_views(self):
        """Create default camera views."""
        # Standard views
        self.views["front"] = CameraView(
            "Front",
            position=[0, -10, 5],
            target=[0, 0, 0],
            up=[0, 0, 1]
        )
        
        self.views["side"] = CameraView(
            "Side",
            position=[10, 0, 5],
            target=[0, 0, 0],
            up=[0, 0, 1]
        )
        
        self.views["top"] = CameraView(
            "Top",
            position=[0, 0, 15],
            target=[0, 0, 0],
            up=[0, 1, 0]
        )
        
        self.views["perspective"] = CameraView(
            "Perspective",
            position=[8, -8, 6],
            target=[0, 0, 0],
            up=[0, 0, 1]
        )
    
    def add_camera(
        self,
        name: str,
        camera_type: str = "perspective",
        position: Optional[np.ndarray] = None,
        target: Optional[np.ndarray] = None
    ) -> gfx.Camera:
        """Add a new camera to the scene.
        
        Args:
            name: Camera name.
            camera_type: "perspective" or "orthographic".
            position: Initial position.
            target: Initial look-at target.
            
        Returns:
            Created PyGFX camera.
        """
        # Create PyGFX camera
        if camera_type == "perspective":
            camera = gfx.PerspectiveCamera(fov=60)
        else:
            camera = gfx.OrthographicCamera()
        
        # Set initial position
        if position is not None:
            camera.local.position = position
        else:
            camera.local.position = [5, -5, 5]
        
        # Look at target
        if target is not None:
            self._look_at(camera, target)
        
        # Store camera
        self.cameras[name] = camera
        self.scene.add(camera)
        
        # Create Camera object for metadata
        # Build extrinsics matrix from camera transform
        extrinsics = np.eye(4)
        extrinsics[:3, :3] = camera.local.matrix[:3, :3]
        extrinsics[:3, 3] = camera.local.position
        
        self.camera_objects[name] = Camera(
            name=name,
            extrinsics=extrinsics,
            fov=60.0 if camera_type == "perspective" else 0.0
        )
        
        # Set as active if first camera
        if self.active_camera_name is None:
            self.active_camera_name = name
        
        return camera
    
    def get_active_camera(self) -> Optional[gfx.Camera]:
        """Get the currently active camera.
        
        Returns:
            Active PyGFX camera or None.
        """
        if self.active_camera_name:
            return self.cameras.get(self.active_camera_name)
        return None
    
    def set_active_camera(self, name: str):
        """Set the active camera.
        
        Args:
            name: Camera name to activate.
            
        Raises:
            ValueError: If camera doesn't exist.
        """
        if name not in self.cameras:
            raise ValueError(f"Camera '{name}' not found")
        self.active_camera_name = name
    
    def apply_view(self, view_name: str, animate: bool = True, duration: float = 1.0):
        """Apply a predefined view to the active camera.
        
        Args:
            view_name: Name of the view to apply.
            animate: Whether to animate the transition.
            duration: Animation duration in seconds.
        """
        if view_name not in self.views:
            raise ValueError(f"View '{view_name}' not found")
        
        view = self.views[view_name]
        camera = self.get_active_camera()
        
        if camera is None:
            return
        
        if animate and duration > 0:
            # Start animation
            self._start_view_animation(camera, view, duration)
        else:
            # Apply immediately
            camera.local.position = view.position.copy()
            self._look_at(camera, view.target, view.up)
    
    def _start_view_animation(self, camera: gfx.Camera, target_view: CameraView, duration: float):
        """Start camera view animation.
        
        Args:
            camera: Camera to animate.
            target_view: Target view configuration.
            duration: Animation duration.
        """
        # Capture current state
        self._start_view = CameraView(
            "current",
            position=camera.local.position.copy(),
            target=self._get_camera_target(camera),
            up=self._get_camera_up(camera)
        )
        
        self._target_view = target_view
        self._animation_duration = duration
        self._animation_start_time = 0.0  # Will be set by update
        self._animating = True
    
    def update_animation(self, time: float) -> bool:
        """Update camera animation.
        
        Args:
            time: Current time in seconds.
            
        Returns:
            True if animation is still running.
        """
        if not self._animating:
            return False
        
        camera = self.get_active_camera()
        if camera is None:
            self._animating = False
            return False
        
        # Initialize start time
        if self._animation_start_time == 0.0:
            self._animation_start_time = time
        
        # Calculate progress
        elapsed = time - self._animation_start_time
        t = min(elapsed / self._animation_duration, 1.0)
        
        # Smooth easing
        t = self._ease_in_out(t)
        
        # Interpolate position
        position = (1 - t) * self._start_view.position + t * self._target_view.position
        target = (1 - t) * self._start_view.target + t * self._target_view.target
        
        # Apply to camera
        camera.local.position = position
        self._look_at(camera, target, self._target_view.up)
        
        # Check if complete
        if t >= 1.0:
            self._animating = False
            return False
        
        return True
    
    def _ease_in_out(self, t: float) -> float:
        """Smooth easing function.
        
        Args:
            t: Progress (0-1).
            
        Returns:
            Eased progress.
        """
        return t * t * (3.0 - 2.0 * t)
    
    def _look_at(self, camera: gfx.Camera, target: np.ndarray, up: np.ndarray = np.array([0, 0, 1])):
        """Make camera look at target.
        
        Args:
            camera: Camera to orient.
            target: Target position.
            up: Up vector.
        """
        position = camera.local.position
        
        # Calculate forward vector
        forward = target - position
        forward = forward / np.linalg.norm(forward)
        
        # Calculate right vector
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        
        # Recalculate up
        up = np.cross(right, forward)
        
        # Build rotation matrix
        rotation_matrix = np.eye(4)
        rotation_matrix[:3, 0] = right
        rotation_matrix[:3, 1] = up
        rotation_matrix[:3, 2] = -forward
        
        # Apply to camera
        camera.local.matrix = rotation_matrix
        camera.local.position = position
    
    def _get_camera_target(self, camera: gfx.Camera) -> np.ndarray:
        """Get what the camera is looking at.
        
        Args:
            camera: Camera to query.
            
        Returns:
            Target position.
        """
        # Get forward vector from camera matrix
        forward = -camera.local.matrix[:3, 2]
        # Project forward from camera position
        return camera.local.position + forward * 10.0
    
    def _get_camera_up(self, camera: gfx.Camera) -> np.ndarray:
        """Get camera up vector.
        
        Args:
            camera: Camera to query.
            
        Returns:
            Up vector.
        """
        return camera.local.matrix[:3, 1]
    
    def create_camera_frustum(self, camera_name: str, color: str = "#ffff00", opacity: float = 0.3) -> gfx.Group:
        """Create visual representation of camera frustum.
        
        Args:
            camera_name: Name of camera to visualize.
            color: Frustum color.
            opacity: Frustum opacity.
            
        Returns:
            Group containing frustum geometry.
        """
        if camera_name not in self.cameras:
            raise ValueError(f"Camera '{camera_name}' not found")
        
        camera = self.cameras[camera_name]
        camera_obj = self.camera_objects[camera_name]
        
        # Create frustum group
        frustum_group = gfx.Group()
        
        # Camera body (small box)
        body_geo = gfx.box_geometry(0.3, 0.2, 0.2)
        body_mat = gfx.MeshPhongMaterial(color=color)
        body_mesh = gfx.Mesh(body_geo, body_mat)
        frustum_group.add(body_mesh)
        
        if isinstance(camera, gfx.PerspectiveCamera):
            # Create frustum pyramid
            fov_rad = np.radians(camera_obj.fov)
            aspect = 1.5  # Assume aspect ratio
            near = 0.5
            far = 5.0
            
            # Calculate frustum corners
            tan_half_fov = np.tan(fov_rad / 2)
            near_height = near * tan_half_fov
            near_width = near_height * aspect
            far_height = far * tan_half_fov
            far_width = far_height * aspect
            
            # Create lines for frustum edges
            positions = np.array([
                # Near plane corners
                [-near_width, -near_height, -near],
                [near_width, -near_height, -near],
                [near_width, near_height, -near],
                [-near_width, near_height, -near],
                # Far plane corners
                [-far_width, -far_height, -far],
                [far_width, -far_height, -far],
                [far_width, far_height, -far],
                [-far_width, far_height, -far],
            ], dtype=np.float32)
            
            # Define edges
            edges = [
                # Near plane
                (0, 1), (1, 2), (2, 3), (3, 0),
                # Far plane
                (4, 5), (5, 6), (6, 7), (7, 4),
                # Connecting edges
                (0, 4), (1, 5), (2, 6), (3, 7)
            ]
            
            # Create line segments
            for start, end in edges:
                line_pos = np.array([positions[start], positions[end]])
                line_geo = gfx.Geometry(positions=line_pos)
                line_mat = gfx.LineMaterial(color=color, thickness=2)
                line = gfx.Line(line_geo, line_mat)
                frustum_group.add(line)
        
        # Position frustum at camera location
        frustum_group.local.matrix = camera.local.matrix.copy()
        
        return frustum_group
    
    def save_view(self, name: str):
        """Save current camera view as a preset.
        
        Args:
            name: Name for the saved view.
        """
        camera = self.get_active_camera()
        if camera is None:
            return
        
        self.views[name] = CameraView(
            name,
            position=camera.local.position.copy(),
            target=self._get_camera_target(camera),
            up=self._get_camera_up(camera)
        )
    
    def get_view_names(self) -> List[str]:
        """Get list of available view names.
        
        Returns:
            List of view names.
        """
        return list(self.views.keys())