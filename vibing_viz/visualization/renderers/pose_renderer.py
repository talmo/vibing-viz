"""Pose rendering components."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pygfx as gfx

from vibing_viz.core.track import Track
from vibing_viz.utils.colors import ColorManager


class PoseRenderer:
    """Renders pose keypoints and skeletons.
    
    This renderer handles the visualization of individual pose keypoints
    as spheres and skeleton edges as lines.
    """
    
    def __init__(self, scene: gfx.Scene):
        """Initialize pose renderer.
        
        Args:
            scene: PyGFX scene to add objects to.
        """
        self.scene = scene
        self.color_manager = ColorManager()
        
        # Storage for rendered objects per track
        self.track_groups: Dict[str, gfx.Group] = {}
        self.keypoint_meshes: Dict[str, Dict[int, gfx.Mesh]] = {}
        self.edge_lines: Dict[str, Dict[int, gfx.Line]] = {}
        
        # Track references
        self.tracks: Dict[str, Track] = {}
        
        # Default rendering settings
        self.default_keypoint_size = 5.0
        self.default_edge_width = 3.0
        self.keypoint_segments = 16  # Sphere quality
    
    def add_track(self, track: Track):
        """Add a track to be rendered.
        
        Args:
            track: Track object to render.
        """
        track_id = track.track_id
        
        # Store track reference
        self.tracks[track_id] = track
        
        # Create group for this track
        group = gfx.Group()
        self.scene.add(group)
        self.track_groups[track_id] = group
        
        # Assign color if not set
        if track.color is None:
            track.color = self.color_manager.get_track_color(track_id)
        
        # Create keypoint meshes
        self._create_keypoint_meshes(track)
        
        # Create edge lines
        if track.edges:
            self._create_edge_lines(track)
    
    def _create_keypoint_meshes(self, track: Track):
        """Create sphere meshes for keypoints.
        
        Args:
            track: Track to create keypoints for.
        """
        track_id = track.track_id
        group = self.track_groups[track_id]
        n_keypoints = track.n_keypoints
        
        self.keypoint_meshes[track_id] = {}
        
        # Get keypoint colors (can be gradient or single color)
        colors = self.color_manager.get_keypoint_gradient(
            track.color, n_keypoints, gradient_type="brightness"
        )
        
        for i in range(n_keypoints):
            # Create sphere geometry
            geometry = gfx.sphere_geometry(
                radius=track.keypoint_size,
                width_segments=self.keypoint_segments,
                height_segments=self.keypoint_segments // 2
            )
            
            # Create material
            material = gfx.MeshPhongMaterial(
                color=colors[i],
                emissive=colors[i],
                opacity=track.opacity
            )
            
            # Create mesh
            mesh = gfx.Mesh(geometry, material)
            mesh.visible = False  # Will be shown when frame is set
            
            self.keypoint_meshes[track_id][i] = mesh
            group.add(mesh)
    
    def _create_edge_lines(self, track: Track):
        """Create lines for skeleton edges.
        
        Args:
            track: Track to create edges for.
        """
        track_id = track.track_id
        group = self.track_groups[track_id]
        
        self.edge_lines[track_id] = {}
        
        # Edge color (slightly darker than keypoints)
        edge_color = self.color_manager.adjust_brightness(track.color, 0.8)
        
        for edge_idx, (start, end) in enumerate(track.edges):
            # Create line geometry (2 points)
            positions = np.zeros((2, 3), dtype=np.float32)
            geometry = gfx.Geometry(positions=positions)
            
            # Create material
            material = gfx.LineMaterial(
                color=edge_color,
                thickness=self.default_edge_width,
                opacity=track.opacity
            )
            
            # Create line
            line = gfx.Line(geometry, material)
            line.visible = False
            
            self.edge_lines[track_id][edge_idx] = {
                "line": line,
                "start": start,
                "end": end
            }
            group.add(line)
    
    def update_frame(self, track_id: str, frame_idx: int):
        """Update visualization for a specific frame.
        
        Args:
            track_id: Track identifier.
            frame_idx: Frame index to display.
        """
        if track_id not in self.track_groups:
            return
        
        # Get track data
        track = self._get_track(track_id)
        if track is None:
            return
        
        # Get pose for this frame
        pose_frame = track.pose_sequence.get_frame(frame_idx)
        if pose_frame is None:
            # Hide track if no data
            self.track_groups[track_id].visible = False
            return
        
        self.track_groups[track_id].visible = track.visible
        
        # Update keypoints
        self._update_keypoints(track_id, pose_frame.keypoints)
        
        # Update edges
        if track_id in self.edge_lines:
            self._update_edges(track_id, pose_frame.keypoints)
    
    def _update_keypoints(self, track_id: str, keypoints: np.ndarray):
        """Update keypoint positions.
        
        Args:
            track_id: Track identifier.
            keypoints: Array of keypoint positions.
        """
        meshes = self.keypoint_meshes.get(track_id, {})
        
        for i, mesh in meshes.items():
            if i < len(keypoints):
                pos = keypoints[i]
                # Check for NaN values
                if not np.any(np.isnan(pos)):
                    mesh.local.position = pos
                    mesh.visible = True
                else:
                    mesh.visible = False
            else:
                mesh.visible = False
    
    def _update_edges(self, track_id: str, keypoints: np.ndarray):
        """Update edge line positions.
        
        Args:
            track_id: Track identifier.
            keypoints: Array of keypoint positions.
        """
        edge_data = self.edge_lines.get(track_id, {})
        
        for edge_idx, edge_info in edge_data.items():
            line = edge_info["line"]
            start_idx = edge_info["start"]
            end_idx = edge_info["end"]
            
            # Check if both keypoints are valid
            if start_idx < len(keypoints) and end_idx < len(keypoints):
                start_pos = keypoints[start_idx]
                end_pos = keypoints[end_idx]
                
                if not (np.any(np.isnan(start_pos)) or np.any(np.isnan(end_pos))):
                    # Update line positions
                    positions = np.array([start_pos, end_pos], dtype=np.float32)
                    line.geometry.positions.data[:] = positions.flatten()
                    line.geometry.positions.update_range(0, 6)
                    line.visible = True
                else:
                    line.visible = False
            else:
                line.visible = False
    
    def set_track_visibility(self, track_id: str, visible: bool):
        """Set track visibility.
        
        Args:
            track_id: Track identifier.
            visible: Whether to show the track.
        """
        if track_id in self.track_groups:
            self.track_groups[track_id].visible = visible
    
    def set_track_opacity(self, track_id: str, opacity: float):
        """Set track opacity.
        
        Args:
            track_id: Track identifier.
            opacity: Opacity value (0-1).
        """
        # Update keypoint materials
        if track_id in self.keypoint_meshes:
            for mesh in self.keypoint_meshes[track_id].values():
                mesh.material.opacity = opacity
        
        # Update edge materials
        if track_id in self.edge_lines:
            for edge_info in self.edge_lines[track_id].values():
                edge_info["line"].material.opacity = opacity
    
    def remove_track(self, track_id: str):
        """Remove a track from rendering.
        
        Args:
            track_id: Track identifier.
        """
        if track_id in self.track_groups:
            # Remove from scene
            group = self.track_groups.pop(track_id)
            self.scene.remove(group)
            
            # Clean up references
            self.keypoint_meshes.pop(track_id, None)
            self.edge_lines.pop(track_id, None)
    
    def _get_track(self, track_id: str) -> Optional[Track]:
        """Get track object.
        
        Args:
            track_id: Track identifier.
            
        Returns:
            Track object or None.
        """
        return self.tracks.get(track_id)
    
    def set_quality(self, quality: str):
        """Set rendering quality.
        
        Args:
            quality: "low", "medium", or "high".
        """
        quality_settings = {
            "low": {"segments": 8, "edge_width": 2},
            "medium": {"segments": 16, "edge_width": 3},
            "high": {"segments": 32, "edge_width": 4}
        }
        
        if quality in quality_settings:
            settings = quality_settings[quality]
            self.keypoint_segments = settings["segments"]
            self.default_edge_width = settings["edge_width"]