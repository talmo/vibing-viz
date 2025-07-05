"""Polygon surface rendering."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pygfx as gfx


class PolygonRenderer:
    """Renders polygon surfaces for pose data and static objects.
    
    This renderer handles both dynamic polygons (attached to pose keypoints)
    and static polygons (floors, walls, etc.).
    """
    
    def __init__(self, scene: gfx.Scene):
        """Initialize polygon renderer.
        
        Args:
            scene: PyGFX scene to add objects to.
        """
        self.scene = scene
        
        # Storage for polygon meshes
        self.track_polygons: Dict[str, Dict[int, gfx.Mesh]] = {}
        self.static_polygons: Dict[str, gfx.Mesh] = {}
        
        # Groups for organization
        self.dynamic_group = gfx.Group()
        self.static_group = gfx.Group()
        
        self.scene.add(self.dynamic_group)
        self.scene.add(self.static_group)
    
    def add_track_polygons(
        self,
        track_id: str,
        polygons: List[Dict[str, Any]],
        base_color: str
    ):
        """Add polygons for a track.
        
        Args:
            track_id: Track identifier.
            polygons: List of polygon definitions with 'indices' and optional 'color'.
            base_color: Base color for the track.
        """
        if track_id not in self.track_polygons:
            self.track_polygons[track_id] = {}
        
        for poly_idx, polygon_def in enumerate(polygons):
            indices = polygon_def["indices"]
            color = polygon_def.get("color", base_color + "80")  # Add transparency
            name = polygon_def.get("name", f"polygon_{poly_idx}")
            
            # Create mesh for this polygon
            mesh = self._create_polygon_mesh(len(indices), color)
            
            self.track_polygons[track_id][poly_idx] = mesh
            self.dynamic_group.add(mesh)
            
            # Store metadata
            mesh.metadata = {
                "indices": indices,
                "name": name
            }
    
    def add_static_polygon(
        self,
        name: str,
        vertices: np.ndarray,
        color: str = "#808080",
        opacity: float = 1.0,
        double_sided: bool = True
    ):
        """Add a static polygon surface.
        
        Args:
            name: Unique name for the polygon.
            vertices: Array of shape (n_vertices, 3) forming closed polygon.
            color: Surface color.
            opacity: Surface opacity.
            double_sided: Whether to render both sides.
        """
        # Triangulate the polygon
        triangles = self._triangulate_polygon(vertices)
        
        # Create geometry
        positions = vertices.astype(np.float32)
        indices = triangles.astype(np.uint32)
        
        geometry = gfx.Geometry(
            positions=positions.flatten(),
            indices=indices.flatten()
        )
        
        # Calculate normals
        normals = self._calculate_normals(vertices, triangles)
        geometry.normals = normals.flatten()
        
        # Create material
        material = gfx.MeshPhongMaterial(
            color=color,
            opacity=opacity,
            side="both" if double_sided else "front"
        )
        
        # Create mesh
        mesh = gfx.Mesh(geometry, material)
        self.static_polygons[name] = mesh
        self.static_group.add(mesh)
    
    def update_track_polygons(self, track_id: str, keypoints: np.ndarray):
        """Update polygon positions for a track.
        
        Args:
            track_id: Track identifier.
            keypoints: Current keypoint positions.
        """
        if track_id not in self.track_polygons:
            return
        
        for poly_idx, mesh in self.track_polygons[track_id].items():
            # Get polygon indices
            indices = mesh.metadata["indices"]
            
            # Extract vertices
            vertices = []
            all_valid = True
            
            for idx in indices:
                if idx < len(keypoints):
                    pos = keypoints[idx]
                    if not np.any(np.isnan(pos)):
                        vertices.append(pos)
                    else:
                        all_valid = False
                        break
                else:
                    all_valid = False
                    break
            
            if all_valid and len(vertices) >= 3:
                # Update mesh geometry
                vertices_array = np.array(vertices, dtype=np.float32)
                
                # Triangulate
                triangles = self._triangulate_polygon(vertices_array)
                
                # Update positions
                mesh.geometry.positions.data[:] = vertices_array.flatten()
                mesh.geometry.positions.update_range(0, len(vertices_array.flatten()))
                
                # Update indices if needed
                if len(triangles.flatten()) != len(mesh.geometry.indices.data):
                    mesh.geometry.indices = triangles.flatten()
                
                # Update normals
                normals = self._calculate_normals(vertices_array, triangles)
                mesh.geometry.normals.data[:] = normals.flatten()
                mesh.geometry.normals.update_range(0, len(normals.flatten()))
                
                mesh.visible = True
            else:
                mesh.visible = False
    
    def _create_polygon_mesh(self, n_vertices: int, color: str) -> gfx.Mesh:
        """Create an empty polygon mesh.
        
        Args:
            n_vertices: Number of vertices in the polygon.
            color: Polygon color.
            
        Returns:
            Empty mesh ready for updates.
        """
        # Create placeholder geometry
        positions = np.zeros((n_vertices, 3), dtype=np.float32)
        
        # Simple fan triangulation
        triangles = []
        for i in range(1, n_vertices - 1):
            triangles.extend([0, i, i + 1])
        
        geometry = gfx.Geometry(
            positions=positions.flatten(),
            indices=np.array(triangles, dtype=np.uint32)
        )
        
        # Add normals
        normals = np.zeros((n_vertices, 3), dtype=np.float32)
        normals[:, 2] = 1.0  # Default to pointing up
        geometry.normals = normals.flatten()
        
        # Create material
        material = gfx.MeshPhongMaterial(
            color=color,
            opacity=0.7,
            side="both"
        )
        
        mesh = gfx.Mesh(geometry, material)
        mesh.visible = False
        
        return mesh
    
    def _triangulate_polygon(self, vertices: np.ndarray) -> np.ndarray:
        """Triangulate a polygon using ear clipping (simple version).
        
        Args:
            vertices: Array of vertices forming a polygon.
            
        Returns:
            Array of triangle indices.
        """
        n = len(vertices)
        
        if n < 3:
            return np.array([], dtype=np.uint32)
        
        if n == 3:
            return np.array([[0, 1, 2]], dtype=np.uint32)
        
        # For simple convex polygons, use fan triangulation
        # For more complex cases, you'd implement ear clipping
        triangles = []
        
        # Check if polygon is roughly convex by checking cross products
        is_convex = self._is_convex(vertices)
        
        if is_convex:
            # Fan triangulation from first vertex
            for i in range(1, n - 1):
                triangles.append([0, i, i + 1])
        else:
            # Simple ear clipping for non-convex polygons
            # This is a simplified version - a full implementation would be more robust
            indices = list(range(n))
            
            while len(indices) > 3:
                removed = False
                
                for i in range(len(indices)):
                    prev_i = (i - 1) % len(indices)
                    next_i = (i + 1) % len(indices)
                    
                    # Check if this forms an ear
                    if self._is_ear(
                        vertices[indices[prev_i]],
                        vertices[indices[i]],
                        vertices[indices[next_i]],
                        vertices,
                        indices
                    ):
                        triangles.append([
                            indices[prev_i],
                            indices[i],
                            indices[next_i]
                        ])
                        indices.pop(i)
                        removed = True
                        break
                
                if not removed:
                    # Fallback to fan triangulation if ear clipping fails
                    for i in range(1, len(indices) - 1):
                        triangles.append([indices[0], indices[i], indices[i + 1]])
                    break
            
            # Add the last triangle
            if len(indices) == 3:
                triangles.append(indices)
        
        return np.array(triangles, dtype=np.uint32)
    
    def _is_convex(self, vertices: np.ndarray) -> bool:
        """Check if polygon is convex.
        
        Args:
            vertices: Polygon vertices.
            
        Returns:
            True if convex.
        """
        n = len(vertices)
        if n < 3:
            return False
        
        # Get the normal of the first triangle to determine winding
        v1 = vertices[1] - vertices[0]
        v2 = vertices[2] - vertices[1]
        reference_normal = np.cross(v1, v2)
        
        # Check all edges
        for i in range(n):
            v1 = vertices[(i + 1) % n] - vertices[i]
            v2 = vertices[(i + 2) % n] - vertices[(i + 1) % n]
            normal = np.cross(v1, v2)
            
            # Check if all cross products point in the same direction
            if np.dot(normal, reference_normal) < 0:
                return False
        
        return True
    
    def _is_ear(
        self,
        prev_v: np.ndarray,
        curr_v: np.ndarray,
        next_v: np.ndarray,
        all_vertices: np.ndarray,
        indices: List[int]
    ) -> bool:
        """Check if a vertex forms an ear in the polygon.
        
        Args:
            prev_v: Previous vertex.
            curr_v: Current vertex.
            next_v: Next vertex.
            all_vertices: All polygon vertices.
            indices: Current vertex indices.
            
        Returns:
            True if forms an ear.
        """
        # Check if triangle is clockwise
        area = np.cross(next_v - curr_v, prev_v - curr_v)[2]
        if area <= 0:
            return False
        
        # Check if any other vertex is inside this triangle
        for idx in indices:
            v = all_vertices[idx]
            if np.array_equal(v, prev_v) or np.array_equal(v, curr_v) or np.array_equal(v, next_v):
                continue
            
            if self._point_in_triangle(v, prev_v, curr_v, next_v):
                return False
        
        return True
    
    def _point_in_triangle(
        self,
        p: np.ndarray,
        a: np.ndarray,
        b: np.ndarray,
        c: np.ndarray
    ) -> bool:
        """Check if point is inside triangle (2D check using x,y).
        
        Args:
            p: Point to test.
            a, b, c: Triangle vertices.
            
        Returns:
            True if inside.
        """
        # Barycentric coordinates method
        v0 = c[:2] - a[:2]
        v1 = b[:2] - a[:2]
        v2 = p[:2] - a[:2]
        
        dot00 = np.dot(v0, v0)
        dot01 = np.dot(v0, v1)
        dot02 = np.dot(v0, v2)
        dot11 = np.dot(v1, v1)
        dot12 = np.dot(v1, v2)
        
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        
        return (u >= 0) and (v >= 0) and (u + v <= 1)
    
    def _calculate_normals(
        self,
        vertices: np.ndarray,
        triangles: np.ndarray
    ) -> np.ndarray:
        """Calculate vertex normals for smooth shading.
        
        Args:
            vertices: Vertex positions.
            triangles: Triangle indices.
            
        Returns:
            Array of vertex normals.
        """
        normals = np.zeros_like(vertices)
        
        # Calculate face normals and accumulate at vertices
        for tri in triangles:
            v0, v1, v2 = vertices[tri]
            
            # Calculate face normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)
            
            # Normalize
            length = np.linalg.norm(face_normal)
            if length > 0:
                face_normal /= length
            
            # Add to vertex normals
            normals[tri[0]] += face_normal
            normals[tri[1]] += face_normal
            normals[tri[2]] += face_normal
        
        # Normalize vertex normals
        for i in range(len(normals)):
            length = np.linalg.norm(normals[i])
            if length > 0:
                normals[i] /= length
            else:
                normals[i] = np.array([0, 0, 1])  # Default up
        
        return normals
    
    def set_track_visibility(self, track_id: str, visible: bool):
        """Set visibility for all track polygons.
        
        Args:
            track_id: Track identifier.
            visible: Whether to show polygons.
        """
        if track_id in self.track_polygons:
            for mesh in self.track_polygons[track_id].values():
                mesh.visible = visible
    
    def remove_track(self, track_id: str):
        """Remove all polygons for a track.
        
        Args:
            track_id: Track identifier.
        """
        if track_id in self.track_polygons:
            for mesh in self.track_polygons[track_id].values():
                self.dynamic_group.remove(mesh)
            del self.track_polygons[track_id]
    
    def remove_static_polygon(self, name: str):
        """Remove a static polygon.
        
        Args:
            name: Polygon name.
        """
        if name in self.static_polygons:
            mesh = self.static_polygons.pop(name)
            self.static_group.remove(mesh)