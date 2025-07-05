"""Environment rendering for floors, walls, and static objects."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pygfx as gfx


class EnvironmentObject:
    """Base class for environment objects."""
    
    def __init__(
        self,
        object_id: str,
        object_type: str,
        position: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1),
        color: str = "#808080",
        opacity: float = 1.0,
        cast_shadow: bool = True,
        receive_shadow: bool = True
    ):
        """Initialize environment object.
        
        Args:
            object_id: Unique identifier.
            object_type: Type of object (floor, wall, box, etc).
            position: Position in world space.
            rotation: Rotation in radians (x, y, z).
            scale: Scale factors.
            color: Object color.
            opacity: Object opacity.
            cast_shadow: Whether object casts shadows.
            receive_shadow: Whether object receives shadows.
        """
        self.object_id = object_id
        self.object_type = object_type
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)
        self.color = color
        self.opacity = opacity
        self.cast_shadow = cast_shadow
        self.receive_shadow = receive_shadow
        self.mesh: Optional[gfx.Mesh] = None


class Floor(EnvironmentObject):
    """Floor plane object."""
    
    def __init__(
        self,
        object_id: str,
        size: Tuple[float, float] = (20, 20),
        position: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#404040",
        grid_visible: bool = True,
        grid_color: str = "#606060",
        grid_divisions: int = 20
    ):
        """Initialize floor.
        
        Args:
            object_id: Unique identifier.
            size: Floor size (width, depth).
            position: Floor position.
            color: Floor color.
            grid_visible: Whether to show grid.
            grid_color: Grid line color.
            grid_divisions: Number of grid divisions.
        """
        super().__init__(object_id, "floor", position=position, color=color)
        self.size = size
        self.grid_visible = grid_visible
        self.grid_color = grid_color
        self.grid_divisions = grid_divisions


class Wall(EnvironmentObject):
    """Wall object."""
    
    def __init__(
        self,
        object_id: str,
        size: Tuple[float, float] = (10, 5),
        position: Tuple[float, float, float] = (0, 5, 2.5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#505050"
    ):
        """Initialize wall.
        
        Args:
            object_id: Unique identifier.
            size: Wall size (width, height).
            position: Wall position.
            rotation: Wall rotation.
            color: Wall color.
        """
        super().__init__(object_id, "wall", position=position, rotation=rotation, color=color)
        self.size = size


class Box(EnvironmentObject):
    """Box object."""
    
    def __init__(
        self,
        object_id: str,
        size: Tuple[float, float, float] = (1, 1, 1),
        position: Tuple[float, float, float] = (0, 0, 0.5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#606060"
    ):
        """Initialize box.
        
        Args:
            object_id: Unique identifier.
            size: Box dimensions (width, depth, height).
            position: Box position.
            rotation: Box rotation.
            color: Box color.
        """
        super().__init__(object_id, "box", position=position, rotation=rotation, color=color)
        self.size = size


class EnvironmentRenderer:
    """Renders environment objects like floors, walls, and static objects."""
    
    def __init__(self, scene: gfx.Scene):
        """Initialize environment renderer.
        
        Args:
            scene: PyGFX scene to add objects to.
        """
        self.scene = scene
        self.objects: Dict[str, EnvironmentObject] = {}
        self.object_groups: Dict[str, gfx.Group] = {}
        
        # Create main environment group
        self.environment_group = gfx.Group()
        self.scene.add(self.environment_group)
        
        # Default materials
        self._create_default_materials()
    
    def _create_default_materials(self):
        """Create default materials for different object types."""
        self.default_materials = {
            "floor": lambda color, opacity: gfx.MeshPhongMaterial(
                color=color,
                opacity=opacity,
                side="both"
            ),
            "wall": lambda color, opacity: gfx.MeshPhongMaterial(
                color=color,
                opacity=opacity,
                side="both"
            ),
            "box": lambda color, opacity: gfx.MeshPhongMaterial(
                color=color,
                opacity=opacity
            )
        }
    
    def add_floor(
        self,
        object_id: str,
        size: Tuple[float, float] = (20, 20),
        position: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#404040",
        grid_visible: bool = True,
        grid_color: str = "#606060",
        grid_divisions: int = 20
    ) -> Floor:
        """Add a floor to the environment.
        
        Args:
            object_id: Unique identifier.
            size: Floor size (width, depth).
            position: Floor position.
            color: Floor color.
            grid_visible: Whether to show grid.
            grid_color: Grid line color.
            grid_divisions: Number of grid divisions.
            
        Returns:
            Created floor object.
        """
        floor = Floor(object_id, size, position, color, grid_visible, grid_color, grid_divisions)
        
        # Create floor group
        floor_group = gfx.Group()
        
        # Create floor plane
        geometry = gfx.plane_geometry(
            width=size[0],
            height=size[1],
            width_segments=1,
            height_segments=1
        )
        
        material = self.default_materials["floor"](color, floor.opacity)
        mesh = gfx.Mesh(geometry, material)
        
        # Rotate to horizontal
        mesh.local.euler = (np.pi/2, 0, 0)
        mesh.local.position = position
        
        floor.mesh = mesh
        floor_group.add(mesh)
        
        # Add grid if enabled
        if grid_visible:
            grid = self._create_grid(size, grid_divisions, grid_color, position[2] + 0.001)
            floor_group.add(grid)
        
        # Store and add to scene
        self.objects[object_id] = floor
        self.object_groups[object_id] = floor_group
        self.environment_group.add(floor_group)
        
        return floor
    
    def add_wall(
        self,
        object_id: str,
        size: Tuple[float, float] = (10, 5),
        position: Tuple[float, float, float] = (0, 5, 2.5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#505050"
    ) -> Wall:
        """Add a wall to the environment.
        
        Args:
            object_id: Unique identifier.
            size: Wall size (width, height).
            position: Wall position.
            rotation: Wall rotation in radians.
            color: Wall color.
            
        Returns:
            Created wall object.
        """
        wall = Wall(object_id, size, position, rotation, color)
        
        # Create wall geometry
        geometry = gfx.plane_geometry(
            width=size[0],
            height=size[1],
            width_segments=1,
            height_segments=1
        )
        
        material = self.default_materials["wall"](color, wall.opacity)
        mesh = gfx.Mesh(geometry, material)
        
        # Apply transforms
        mesh.local.position = position
        mesh.local.euler = rotation
        
        wall.mesh = mesh
        
        # Store and add to scene
        self.objects[object_id] = wall
        self.object_groups[object_id] = mesh
        self.environment_group.add(mesh)
        
        return wall
    
    def add_box(
        self,
        object_id: str,
        size: Tuple[float, float, float] = (1, 1, 1),
        position: Tuple[float, float, float] = (0, 0, 0.5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#606060"
    ) -> Box:
        """Add a box to the environment.
        
        Args:
            object_id: Unique identifier.
            size: Box dimensions (width, depth, height).
            position: Box position.
            rotation: Box rotation in radians.
            color: Box color.
            
        Returns:
            Created box object.
        """
        box = Box(object_id, size, position, rotation, color)
        
        # Create box geometry
        geometry = gfx.box_geometry(
            width=size[0],
            height=size[2],
            depth=size[1]
        )
        
        material = self.default_materials["box"](color, box.opacity)
        mesh = gfx.Mesh(geometry, material)
        
        # Apply transforms
        mesh.local.position = position
        mesh.local.euler = rotation
        
        box.mesh = mesh
        
        # Store and add to scene
        self.objects[object_id] = box
        self.object_groups[object_id] = mesh
        self.environment_group.add(mesh)
        
        return box
    
    def add_custom_mesh(
        self,
        object_id: str,
        vertices: np.ndarray,
        faces: np.ndarray,
        position: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        scale: Tuple[float, float, float] = (1, 1, 1),
        color: str = "#808080",
        opacity: float = 1.0
    ) -> EnvironmentObject:
        """Add a custom mesh object.
        
        Args:
            object_id: Unique identifier.
            vertices: Vertex positions array.
            faces: Face indices array.
            position: Object position.
            rotation: Object rotation.
            scale: Object scale.
            color: Object color.
            opacity: Object opacity.
            
        Returns:
            Created environment object.
        """
        obj = EnvironmentObject(
            object_id, "custom", 
            position=position, 
            rotation=rotation, 
            scale=scale,
            color=color, 
            opacity=opacity
        )
        
        # Create geometry from vertices and faces
        geometry = gfx.Geometry(
            positions=vertices.astype(np.float32),
            indices=faces.astype(np.uint32)
        )
        
        # Calculate normals if not provided
        if not hasattr(geometry, 'normals') or geometry.normals is None:
            geometry.normals = self._calculate_normals(vertices, faces)
        
        material = gfx.MeshPhongMaterial(
            color=color,
            opacity=opacity
        )
        
        mesh = gfx.Mesh(geometry, material)
        
        # Apply transforms
        mesh.local.position = position
        mesh.local.euler = rotation
        mesh.local.scale = scale
        
        obj.mesh = mesh
        
        # Store and add to scene
        self.objects[object_id] = obj
        self.object_groups[object_id] = mesh
        self.environment_group.add(mesh)
        
        return obj
    
    def _create_grid(
        self, 
        size: Tuple[float, float], 
        divisions: int, 
        color: str,
        height: float = 0
    ) -> gfx.Group:
        """Create a grid of lines.
        
        Args:
            size: Grid size (width, depth).
            divisions: Number of divisions.
            color: Grid line color.
            height: Height of grid above floor.
            
        Returns:
            Group containing grid lines.
        """
        grid_group = gfx.Group()
        
        width, depth = size
        
        # Calculate spacing
        x_spacing = width / divisions
        z_spacing = depth / divisions
        
        # Create lines along X
        for i in range(divisions + 1):
            z = -depth/2 + i * z_spacing
            positions = np.array([
                [-width/2, 0, z],
                [width/2, 0, z]
            ], dtype=np.float32)
            
            geometry = gfx.Geometry(positions=positions)
            material = gfx.LineMaterial(color=color, thickness=1)
            line = gfx.Line(geometry, material)
            line.local.position = (line.local.position[0], height, line.local.position[2])
            grid_group.add(line)
        
        # Create lines along Z
        for i in range(divisions + 1):
            x = -width/2 + i * x_spacing
            positions = np.array([
                [x, 0, -depth/2],
                [x, 0, depth/2]
            ], dtype=np.float32)
            
            geometry = gfx.Geometry(positions=positions)
            material = gfx.LineMaterial(color=color, thickness=1)
            line = gfx.Line(geometry, material)
            line.local.position = (line.local.position[0], height, line.local.position[2])
            grid_group.add(line)
        
        return grid_group
    
    def _calculate_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Calculate vertex normals from faces.
        
        Args:
            vertices: Vertex positions.
            faces: Face indices.
            
        Returns:
            Vertex normals array.
        """
        normals = np.zeros_like(vertices)
        
        # Calculate face normals
        for face in faces:
            v0, v1, v2 = vertices[face]
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)
            face_normal /= np.linalg.norm(face_normal) + 1e-8
            
            # Add to vertex normals
            for idx in face:
                normals[idx] += face_normal
        
        # Normalize vertex normals
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        normals /= (norms + 1e-8)
        
        return normals.astype(np.float32)
    
    def set_object_visible(self, object_id: str, visible: bool):
        """Set object visibility.
        
        Args:
            object_id: Object identifier.
            visible: Whether object should be visible.
        """
        if object_id in self.object_groups:
            self.object_groups[object_id].visible = visible
    
    def set_object_opacity(self, object_id: str, opacity: float):
        """Set object opacity.
        
        Args:
            object_id: Object identifier.
            opacity: New opacity (0-1).
        """
        if object_id in self.objects:
            obj = self.objects[object_id]
            obj.opacity = opacity
            if obj.mesh and hasattr(obj.mesh, 'material'):
                obj.mesh.material.opacity = opacity
    
    def set_object_color(self, object_id: str, color: str):
        """Set object color.
        
        Args:
            object_id: Object identifier.
            color: New color.
        """
        if object_id in self.objects:
            obj = self.objects[object_id]
            obj.color = color
            if obj.mesh and hasattr(obj.mesh, 'material'):
                obj.mesh.material.color = color
    
    def remove_object(self, object_id: str):
        """Remove an object from the environment.
        
        Args:
            object_id: Object identifier.
        """
        if object_id in self.objects:
            # Remove from scene
            if object_id in self.object_groups:
                obj_group = self.object_groups[object_id]
                self.environment_group.remove(obj_group)
                del self.object_groups[object_id]
            
            # Remove from storage
            del self.objects[object_id]
    
    def clear(self):
        """Remove all environment objects."""
        object_ids = list(self.objects.keys())
        for object_id in object_ids:
            self.remove_object(object_id)
    
    def create_room(
        self,
        size: Tuple[float, float, float] = (10, 10, 3),
        floor_color: str = "#404040",
        wall_color: str = "#505050",
        add_ceiling: bool = False
    ):
        """Create a simple room with floor and walls.
        
        Args:
            size: Room dimensions (width, depth, height).
            floor_color: Floor color.
            wall_color: Wall color.
            add_ceiling: Whether to add a ceiling.
        """
        width, depth, height = size
        
        # Add floor
        self.add_floor("room_floor", (width, depth), (0, 0, 0), floor_color)
        
        # Add walls
        # Back wall
        self.add_wall(
            "room_wall_back",
            (width, height),
            (0, depth/2, height/2),
            (0, 0, 0),
            wall_color
        )
        
        # Front wall (with transparency for viewing)
        front_wall = self.add_wall(
            "room_wall_front",
            (width, height),
            (0, -depth/2, height/2),
            (0, np.pi, 0),
            wall_color
        )
        front_wall.opacity = 0.2
        self.set_object_opacity("room_wall_front", 0.2)
        
        # Left wall
        self.add_wall(
            "room_wall_left",
            (depth, height),
            (-width/2, 0, height/2),
            (0, np.pi/2, 0),
            wall_color
        )
        
        # Right wall
        self.add_wall(
            "room_wall_right",
            (depth, height),
            (width/2, 0, height/2),
            (0, -np.pi/2, 0),
            wall_color
        )
        
        # Add ceiling if requested
        if add_ceiling:
            ceiling = self.add_floor(
                "room_ceiling",
                (width, depth),
                (0, 0, height),
                wall_color,
                grid_visible=False
            )
            # Flip ceiling
            if ceiling.mesh:
                ceiling.mesh.local.euler = (-np.pi/2, 0, 0)