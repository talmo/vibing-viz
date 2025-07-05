"""Scene management for PyGFX visualization."""

from typing import Dict, Any, Optional
import numpy as np
import pygfx as gfx
import pylinalg as la

from vibing_viz.core.transforms import CoordinateTransform


class SceneManager:
    """Manages the PyGFX scene and rendering setup.
    
    This class handles scene creation, lighting, camera setup,
    and coordinate system management.
    """
    
    def __init__(self):
        """Initialize scene manager."""
        # Create scene
        self.scene = gfx.Scene()
        
        # Scene objects registry
        self.objects: Dict[str, gfx.WorldObject] = {}
        
        # Camera management
        self.cameras: Dict[str, gfx.Camera] = {}
        self.active_camera: Optional[gfx.Camera] = None
        
        # Coordinate transform
        self.world_transform = CoordinateTransform()
        
        # Background color
        self._background_color = "#1a1a1a"
        
        # Setup default lighting
        self._setup_lighting()
        
        # Create default camera
        self._create_default_camera()
    
    def _setup_lighting(self):
        """Setup default scene lighting."""
        # Ambient light for base illumination
        ambient = gfx.AmbientLight(intensity=0.4)
        self.scene.add(ambient)
        self.objects["ambient_light"] = ambient
        
        # Main directional light (sun)
        sun = gfx.DirectionalLight(intensity=0.6)
        sun.local.position = np.array([10, 10, 10])
        sun.look_at((0, 0, 0))
        self.scene.add(sun)
        self.objects["sun_light"] = sun
        
        # Fill light from opposite direction
        fill = gfx.DirectionalLight(intensity=0.2, color="#8888ff")
        fill.local.position = np.array([-5, 5, -5])
        fill.look_at((0, 0, 0))
        self.scene.add(fill)
        self.objects["fill_light"] = fill
    
    def _create_default_camera(self):
        """Create default perspective camera."""
        camera = gfx.PerspectiveCamera(50, 16 / 9)
        camera.local.position = np.array([5, 5, 5])
        camera.look_at((0, 0, 0))
        
        self.cameras["default"] = camera
        self.active_camera = camera
    
    @property
    def background_color(self) -> str:
        """Get background color."""
        return self._background_color
    
    @background_color.setter
    def background_color(self, color: str):
        """Set background color."""
        self._background_color = color
        # This will be applied to the renderer
    
    def add_camera(
        self,
        name: str,
        camera_type: str = "perspective",
        position: Optional[np.ndarray] = None,
        look_at_target: Optional[np.ndarray] = None,
        fov: float = 50,
        **kwargs
    ) -> gfx.Camera:
        """Add a camera to the scene.
        
        Args:
            name: Camera identifier.
            camera_type: "perspective" or "orthographic".
            position: Camera position in world space.
            look_at_target: Point to look at.
            fov: Field of view (for perspective cameras).
            **kwargs: Additional camera parameters.
            
        Returns:
            Created camera object.
        """
        if camera_type == "perspective":
            camera = gfx.PerspectiveCamera(fov, **kwargs)
        else:
            camera = gfx.OrthographicCamera(**kwargs)
        
        if position is not None:
            camera.local.position = position
        
        if look_at_target is not None:
            camera.look_at(look_at_target)
        
        self.cameras[name] = camera
        return camera
    
    def set_active_camera(self, name: str):
        """Set the active camera.
        
        Args:
            name: Camera name.
            
        Raises:
            KeyError: If camera not found.
        """
        if name not in self.cameras:
            raise KeyError(f"Camera '{name}' not found")
        self.active_camera = self.cameras[name]
    
    def add_object(self, name: str, obj: gfx.WorldObject):
        """Add an object to the scene.
        
        Args:
            name: Object identifier.
            obj: PyGFX world object.
        """
        self.scene.add(obj)
        self.objects[name] = obj
    
    def remove_object(self, name: str):
        """Remove an object from the scene.
        
        Args:
            name: Object identifier.
        """
        if name in self.objects:
            obj = self.objects.pop(name)
            self.scene.remove(obj)
    
    def create_grid(
        self,
        size: float = 10,
        divisions: int = 10,
        color: str = "#444444",
        center_color: str = "#666666"
    ) -> gfx.Group:
        """Create a grid helper.
        
        Args:
            size: Grid size in world units.
            divisions: Number of grid divisions.
            color: Grid line color.
            center_color: Center line color.
            
        Returns:
            Group containing grid lines.
        """
        grid = gfx.Group()
        
        # Calculate step
        step = size / divisions
        half_size = size / 2
        
        # Create grid lines
        positions = []
        colors = []
        
        for i in range(divisions + 1):
            # Position along axis
            pos = -half_size + i * step
            
            # Determine color (center lines are different)
            is_center = i == divisions // 2
            line_color = center_color if is_center else color
            
            # X-axis lines
            positions.extend([
                [-half_size, pos, 0],
                [half_size, pos, 0],
            ])
            colors.extend([line_color, line_color])
            
            # Y-axis lines
            positions.extend([
                [pos, -half_size, 0],
                [pos, half_size, 0],
            ])
            colors.extend([line_color, line_color])
        
        # Create line segments
        positions_array = np.array(positions, dtype=np.float32)
        geometry = gfx.Geometry(positions=positions_array)
        material = gfx.LineMaterial(color=color, line_width=1)
        lines = gfx.Line(geometry, material, mode="segments")
        
        grid.add(lines)
        
        # Apply world transform
        if self.world_transform.transform is not None:
            grid.local.matrix = self.world_transform.transform
        
        return grid
    
    def create_axes_helper(
        self,
        size: float = 1,
        line_width: float = 3
    ) -> gfx.Group:
        """Create coordinate axes helper.
        
        Args:
            size: Length of each axis.
            line_width: Width of axis lines.
            
        Returns:
            Group containing axis lines.
        """
        axes = gfx.Group()
        
        # X axis - Red
        x_positions = np.array([[0, 0, 0], [size, 0, 0]], dtype=np.float32)
        x_geom = gfx.Geometry(positions=x_positions)
        x_mat = gfx.LineMaterial(color="#ff0000", line_width=line_width)
        x_line = gfx.Line(x_geom, x_mat)
        axes.add(x_line)
        
        # Y axis - Green
        y_positions = np.array([[0, 0, 0], [0, size, 0]], dtype=np.float32)
        y_geom = gfx.Geometry(positions=y_positions)
        y_mat = gfx.LineMaterial(color="#00ff00", line_width=line_width)
        y_line = gfx.Line(y_geom, y_mat)
        axes.add(y_line)
        
        # Z axis - Blue
        z_positions = np.array([[0, 0, 0], [0, 0, size]], dtype=np.float32)
        z_geom = gfx.Geometry(positions=z_positions)
        z_mat = gfx.LineMaterial(color="#0000ff", line_width=line_width)
        z_line = gfx.Line(z_geom, z_mat)
        axes.add(z_line)
        
        return axes
    
    def get_scene_bounds(self) -> tuple[np.ndarray, np.ndarray]:
        """Calculate scene bounding box.
        
        Returns:
            Tuple of (min_point, max_point).
        """
        if not self.objects:
            return np.zeros(3), np.zeros(3)
        
        all_bounds = []
        
        for obj in self.objects.values():
            if hasattr(obj, "get_world_bounding_box"):
                bbox = obj.get_world_bounding_box()
                if bbox is not None:
                    all_bounds.append(bbox)
        
        if not all_bounds:
            return np.zeros(3), np.zeros(3)
        
        # Combine all bounds
        min_points = np.array([b[0] for b in all_bounds])
        max_points = np.array([b[1] for b in all_bounds])
        
        scene_min = np.min(min_points, axis=0)
        scene_max = np.max(max_points, axis=0)
        
        return scene_min, scene_max
    
    def fit_camera_to_scene(self, camera_name: Optional[str] = None, padding: float = 1.2):
        """Adjust camera to fit all objects in view.
        
        Args:
            camera_name: Camera to adjust (None for active camera).
            padding: Extra space factor around objects.
        """
        camera = self.cameras.get(camera_name) if camera_name else self.active_camera
        if camera is None:
            return
        
        # Get scene bounds
        scene_min, scene_max = self.get_scene_bounds()
        center = (scene_min + scene_max) / 2
        size = np.linalg.norm(scene_max - scene_min)
        
        if size < 0.001:  # Empty or tiny scene
            size = 10
        
        # Position camera to see entire scene
        distance = size * padding
        camera.local.position = center + np.array([distance, distance, distance])
        camera.look_at(center)
        
        # Adjust camera parameters
        if hasattr(camera, "zoom"):
            camera.zoom = 1.0
        
        # Set near/far planes
        camera.near = size * 0.01
        camera.far = size * 100