"""Video overlay system for 2D image display in 3D scene."""

from typing import Optional, Tuple, Dict, Any
import numpy as np
import pygfx as gfx
from pathlib import Path

try:
    import imageio.v3 as iio
except ImportError:
    import imageio as iio


class VideoOverlay:
    """Manages 2D video/image overlay in the 3D scene.
    
    This class handles loading video files and displaying them as
    textured planes in the 3D scene, aligned with camera views.
    """
    
    def __init__(self, scene: gfx.Scene):
        """Initialize video overlay system.
        
        Args:
            scene: PyGFX scene to add overlays to.
        """
        self.scene = scene
        self.overlays: Dict[str, Dict[str, Any]] = {}
        self._video_readers: Dict[str, Any] = {}
    
    def add_video_overlay(
        self,
        overlay_id: str,
        video_path: str,
        camera_name: str,
        position: Tuple[float, float, float] = (0, 0, -10),
        size: Tuple[float, float] = (10, 7.5),
        opacity: float = 0.8
    ) -> gfx.Mesh:
        """Add a video overlay to the scene.
        
        Args:
            overlay_id: Unique identifier for this overlay.
            video_path: Path to video file.
            camera_name: Camera this overlay is associated with.
            position: Position relative to camera.
            size: Width and height of overlay plane.
            opacity: Overlay opacity (0-1).
            
        Returns:
            Created mesh object.
            
        Raises:
            ValueError: If overlay_id already exists.
        """
        if overlay_id in self.overlays:
            raise ValueError(f"Overlay '{overlay_id}' already exists")
        
        # Load video
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Open video reader
        reader = iio.imopen(str(video_path), "r")
        self._video_readers[overlay_id] = reader
        
        # Get first frame for texture
        first_frame = reader.read(index=0)
        height, width = first_frame.shape[:2]
        
        # Create plane geometry
        geometry = gfx.plane_geometry(
            width=size[0],
            height=size[1],
            width_segments=1,
            height_segments=1
        )
        
        # Create texture from first frame
        texture = gfx.Texture(first_frame, dim=2)
        
        # Create material
        material = gfx.MeshBasicMaterial(
            color_mode="texture",
            map=texture,
            opacity=opacity,
            side="front"
        )
        
        # Create mesh
        mesh = gfx.Mesh(geometry, material)
        mesh.local.position = position
        
        # Store overlay data
        self.overlays[overlay_id] = {
            "mesh": mesh,
            "texture": texture,
            "reader": reader,
            "camera_name": camera_name,
            "video_path": str(video_path),
            "size": size,
            "opacity": opacity,
            "frame_count": reader.properties().shape[0] if hasattr(reader.properties(), 'shape') else -1,
            "current_frame": 0,
            "width": width,
            "height": height
        }
        
        # Add to scene
        self.scene.add(mesh)
        
        return mesh
    
    def add_image_overlay(
        self,
        overlay_id: str,
        image_path: str,
        camera_name: str,
        position: Tuple[float, float, float] = (0, 0, -10),
        size: Optional[Tuple[float, float]] = None,
        opacity: float = 0.8
    ) -> gfx.Mesh:
        """Add a static image overlay to the scene.
        
        Args:
            overlay_id: Unique identifier for this overlay.
            image_path: Path to image file.
            camera_name: Camera this overlay is associated with.
            position: Position relative to camera.
            size: Width and height of overlay plane (auto if None).
            opacity: Overlay opacity (0-1).
            
        Returns:
            Created mesh object.
        """
        if overlay_id in self.overlays:
            raise ValueError(f"Overlay '{overlay_id}' already exists")
        
        # Load image
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read image
        image = iio.imread(str(image_path))
        height, width = image.shape[:2]
        
        # Auto-calculate size if not provided
        if size is None:
            aspect = width / height
            size = (10 * aspect, 10)
        
        # Create plane geometry
        geometry = gfx.plane_geometry(
            width=size[0],
            height=size[1],
            width_segments=1,
            height_segments=1
        )
        
        # Create texture
        texture = gfx.Texture(image, dim=2)
        
        # Create material
        material = gfx.MeshBasicMaterial(
            color_mode="texture",
            map=texture,
            opacity=opacity,
            side="front"
        )
        
        # Create mesh
        mesh = gfx.Mesh(geometry, material)
        mesh.local.position = position
        
        # Store overlay data
        self.overlays[overlay_id] = {
            "mesh": mesh,
            "texture": texture,
            "reader": None,  # No reader for static images
            "camera_name": camera_name,
            "image_path": str(image_path),
            "size": size,
            "opacity": opacity,
            "frame_count": 1,
            "current_frame": 0,
            "width": width,
            "height": height,
            "is_static": True
        }
        
        # Add to scene
        self.scene.add(mesh)
        
        return mesh
    
    def update_frame(self, overlay_id: str, frame_idx: int):
        """Update video overlay to specific frame.
        
        Args:
            overlay_id: Overlay identifier.
            frame_idx: Frame index to display.
        """
        if overlay_id not in self.overlays:
            return
        
        overlay = self.overlays[overlay_id]
        
        # Skip if static image
        if overlay.get("is_static", False):
            return
        
        reader = overlay["reader"]
        if reader is None:
            return
        
        # Clamp frame index
        if overlay["frame_count"] > 0:
            frame_idx = max(0, min(frame_idx, overlay["frame_count"] - 1))
        
        try:
            # Read frame
            frame = reader.read(index=frame_idx)
            
            # Update texture
            overlay["texture"].data[:] = frame
            overlay["texture"].update()
            overlay["current_frame"] = frame_idx
            
        except Exception as e:
            print(f"Error updating overlay frame: {e}")
    
    def set_overlay_opacity(self, overlay_id: str, opacity: float):
        """Set overlay opacity.
        
        Args:
            overlay_id: Overlay identifier.
            opacity: New opacity (0-1).
        """
        if overlay_id not in self.overlays:
            return
        
        overlay = self.overlays[overlay_id]
        overlay["mesh"].material.opacity = opacity
        overlay["opacity"] = opacity
    
    def set_overlay_visible(self, overlay_id: str, visible: bool):
        """Set overlay visibility.
        
        Args:
            overlay_id: Overlay identifier.
            visible: Whether overlay should be visible.
        """
        if overlay_id not in self.overlays:
            return
        
        self.overlays[overlay_id]["mesh"].visible = visible
    
    def align_to_camera(self, overlay_id: str, camera: gfx.Camera, distance: float = 10.0):
        """Align overlay to face camera.
        
        Args:
            overlay_id: Overlay identifier.
            camera: Camera to align to.
            distance: Distance from camera.
        """
        if overlay_id not in self.overlays:
            return
        
        overlay = self.overlays[overlay_id]
        mesh = overlay["mesh"]
        
        # Get camera forward vector
        forward = -camera.local.matrix[:3, 2]
        forward = forward / np.linalg.norm(forward)
        
        # Position overlay in front of camera
        mesh.local.position = camera.local.position + forward * distance
        
        # Make overlay face camera
        mesh.local.matrix[:3, :3] = camera.local.matrix[:3, :3]
    
    def project_3d_to_overlay(
        self,
        overlay_id: str,
        point_3d: np.ndarray,
        camera_matrix: np.ndarray
    ) -> Optional[Tuple[float, float]]:
        """Project 3D point to overlay coordinates.
        
        Args:
            overlay_id: Overlay identifier.
            point_3d: 3D point in world space.
            camera_matrix: Camera projection matrix.
            
        Returns:
            2D coordinates in overlay space or None if outside.
        """
        if overlay_id not in self.overlays:
            return None
        
        overlay = self.overlays[overlay_id]
        
        # Transform to camera space
        point_cam = camera_matrix @ np.append(point_3d, 1)
        
        # Perspective divide
        if point_cam[2] <= 0:
            return None
        
        x = point_cam[0] / point_cam[2]
        y = point_cam[1] / point_cam[2]
        
        # Map to overlay coordinates
        width, height = overlay["width"], overlay["height"]
        u = (x + 1) * 0.5 * width
        v = (1 - y) * 0.5 * height
        
        # Check bounds
        if 0 <= u <= width and 0 <= v <= height:
            return (u, v)
        
        return None
    
    def remove_overlay(self, overlay_id: str):
        """Remove an overlay from the scene.
        
        Args:
            overlay_id: Overlay identifier.
        """
        if overlay_id not in self.overlays:
            return
        
        overlay = self.overlays[overlay_id]
        
        # Remove from scene
        self.scene.remove(overlay["mesh"])
        
        # Close video reader if exists
        if overlay_id in self._video_readers:
            reader = self._video_readers.pop(overlay_id)
            if hasattr(reader, 'close'):
                reader.close()
        
        # Remove from overlays
        del self.overlays[overlay_id]
    
    def get_overlay_info(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an overlay.
        
        Args:
            overlay_id: Overlay identifier.
            
        Returns:
            Dictionary with overlay information or None.
        """
        if overlay_id not in self.overlays:
            return None
        
        overlay = self.overlays[overlay_id]
        
        return {
            "id": overlay_id,
            "camera_name": overlay["camera_name"],
            "size": overlay["size"],
            "opacity": overlay["opacity"],
            "frame_count": overlay["frame_count"],
            "current_frame": overlay["current_frame"],
            "width": overlay["width"],
            "height": overlay["height"],
            "is_static": overlay.get("is_static", False),
            "path": overlay.get("video_path") or overlay.get("image_path")
        }
    
    def cleanup(self):
        """Clean up all overlays and close video readers."""
        overlay_ids = list(self.overlays.keys())
        for overlay_id in overlay_ids:
            self.remove_overlay(overlay_id)