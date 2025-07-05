"""Main visualizer class."""

from typing import Optional, List, Tuple, Dict, Any, Callable
import numpy as np
import pygfx as gfx
from wgpu.gui.auto import WgpuCanvas

from vibing_viz.core.pose_data import PoseSequence
from vibing_viz.core.track import Track
from vibing_viz.core.camera import Camera
from vibing_viz.visualization.scene_manager import SceneManager
from vibing_viz.visualization.renderers.pose_renderer import PoseRenderer
from vibing_viz.visualization.renderers.polygon_renderer import PolygonRenderer
from vibing_viz.visualization.renderers.environment_renderer import EnvironmentRenderer
from vibing_viz.visualization.camera_manager import CameraManager
from vibing_viz.visualization.video_overlay import VideoOverlay


class VisualizerConfig:
    """Configuration for the visualizer."""
    
    def __init__(self):
        """Initialize default configuration."""
        self.show_grid = True
        self.show_trails = False
        self.trail_length = 10
        self.background_color = "#1a1a1a"
        self.show_camera_planes = True
        self.camera_plane_opacity = 0.7


class Visualizer:
    """Main visualization interface for pose tracking data.
    
    This is the primary entry point for creating 3D visualizations
    of pose tracking data. It manages tracks, cameras, and rendering.
    """
    
    def __init__(self):
        """Initialize the visualizer."""
        self.tracks: Dict[str, Track] = {}
        self.config = VisualizerConfig()
        self._current_frame = 0
        
        # Initialize scene and renderers
        self.scene_manager = SceneManager()
        self.pose_renderer = PoseRenderer(self.scene_manager.scene)
        self.polygon_renderer = PolygonRenderer(self.scene_manager.scene)
        self.environment_renderer = EnvironmentRenderer(self.scene_manager.scene)
        
        # Initialize camera manager and video overlay
        self.camera_manager = CameraManager(self.scene_manager.scene)
        self.video_overlay = VideoOverlay(self.scene_manager.scene)
        
        # Create default camera
        self.camera_manager.add_camera("main", "perspective")
        
        # Canvas and renderer (initialized on show)
        self._canvas: Optional[WgpuCanvas] = None
        self._renderer: Optional[gfx.WgpuRenderer] = None
        
        # Animation state
        self._playing = False
        self._fps = 30.0
    
    def add_track(
        self,
        track_id: str,
        poses: np.ndarray,
        edges: Optional[List[Tuple[int, int]]] = None,
        polygons: Optional[List[Dict[str, Any]]] = None,
        color: Optional[str] = None,
        keypoint_size: float = 5.0,
    ) -> None:
        """Add a new track to the visualization.
        
        Args:
            track_id: Unique identifier for this track.
            poses: Array of shape (n_frames, n_keypoints, 3).
            edges: List of (start_idx, end_idx) tuples for skeleton.
            polygons: List of polygon definitions.
            color: Optional custom color for this track.
            keypoint_size: Size of keypoint markers.
            
        Raises:
            ValueError: If track_id already exists.
        """
        if track_id in self.tracks:
            raise ValueError(f"Track '{track_id}' already exists")
        
        # Create pose sequence
        sequence = PoseSequence(poses)
        
        # Create track
        track = Track(track_id, sequence, edges=edges, polygons=polygons)
        
        # Set visualization properties
        if color:
            track.color = color
        track.keypoint_size = keypoint_size
        
        self.tracks[track_id] = track
        
        # Add to renderers
        self.pose_renderer.add_track(track)
        if polygons:
            self.polygon_renderer.add_track_polygons(
                track_id, polygons, track.color
            )
    
    def add_camera(
        self,
        name: str,
        extrinsics: np.ndarray,
        intrinsics: Optional[np.ndarray] = None,
        video_path: Optional[str] = None,
        fov: float = 60.0,
        aspect: float = 16/9,
        show_frustum: bool = True,
        show_video_plane: bool = True,
    ) -> None:
        """Add a camera to the scene.
        
        Args:
            name: Unique camera name.
            extrinsics: 4x4 transformation matrix.
            intrinsics: Optional 3x3 intrinsic matrix.
            video_path: Optional path to video file.
            fov: Field of view in degrees.
            aspect: Aspect ratio.
            show_frustum: Whether to show camera frustum.
            show_video_plane: Whether to show video on near plane.
            
        Raises:
            ValueError: If camera name already exists.
        """
        if name in self.cameras:
            raise ValueError(f"Camera '{name}' already exists")
        
        # Create camera object
        camera = Camera(
            name=name,
            extrinsics=extrinsics,
            intrinsics=intrinsics,
            resolution=(int(1920 * aspect), 1920),
            fov=fov
        )
        
        self.cameras[name] = camera
        
        # Add visualization camera to scene
        viz_camera = self.scene_manager.add_camera(
            name=f"viz_{name}",
            position=camera.position,
            look_at_target=camera.position + camera.forward,
            fov=fov
        )
    
    def set_frame(self, frame_idx: int) -> None:
        """Set the current frame.
        
        Args:
            frame_idx: Frame index to display.
        """
        self._current_frame = frame_idx
        
        # Update all tracks
        for track_id, track in self.tracks.items():
            # Update pose renderer
            self.pose_renderer.update_frame(track_id, frame_idx)
            
            # Update polygon renderer if track has polygons
            if track.polygons:
                pose_frame = track.pose_sequence.get_frame(frame_idx)
                if pose_frame is not None:
                    self.polygon_renderer.update_track_polygons(
                        track_id, pose_frame.keypoints
                    )
        
        # Update video overlays
        for overlay_id in self.video_overlay.overlays:
            self.video_overlay.update_frame(overlay_id, frame_idx)
    
    def get_total_frames(self) -> int:
        """Get total number of frames across all tracks.
        
        Returns:
            Maximum number of frames in any track.
        """
        if not self.tracks:
            return 0
        return max(track.n_frames for track in self.tracks.values())
    
    def add_video_overlay(
        self,
        overlay_id: str,
        video_path: str,
        camera_name: Optional[str] = None,
        opacity: float = 0.8
    ) -> None:
        """Add a video overlay to the visualization.
        
        Args:
            overlay_id: Unique identifier for the overlay.
            video_path: Path to video file.
            camera_name: Camera to associate with (None for active).
            opacity: Overlay opacity (0-1).
        """
        if camera_name is None:
            camera_name = self.camera_manager.active_camera_name or "main"
        
        self.video_overlay.add_video_overlay(
            overlay_id,
            video_path,
            camera_name,
            position=(0, 0, -10),
            opacity=opacity
        )
    
    def add_image_overlay(
        self,
        overlay_id: str,
        image_path: str,
        camera_name: Optional[str] = None,
        opacity: float = 0.8
    ) -> None:
        """Add an image overlay to the visualization.
        
        Args:
            overlay_id: Unique identifier for the overlay.
            image_path: Path to image file.
            camera_name: Camera to associate with (None for active).
            opacity: Overlay opacity (0-1).
        """
        if camera_name is None:
            camera_name = self.camera_manager.active_camera_name or "main"
        
        self.video_overlay.add_image_overlay(
            overlay_id,
            image_path,
            camera_name,
            opacity=opacity
        )
    
    def set_camera_view(self, view_name: str, animate: bool = True):
        """Set camera to a predefined view.
        
        Args:
            view_name: Name of the view ("front", "side", "top", etc).
            animate: Whether to animate the transition.
        """
        self.camera_manager.apply_view(view_name, animate=animate)
    
    def add_camera_view(self, name: str):
        """Save current camera position as a named view.
        
        Args:
            name: Name for the saved view.
        """
        self.camera_manager.save_view(name)
    
    def add_floor(
        self,
        floor_id: str = "main_floor",
        size: Tuple[float, float] = (20, 20),
        position: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#404040",
        show_grid: bool = True
    ):
        """Add a floor to the environment.
        
        Args:
            floor_id: Unique identifier for the floor.
            size: Floor size (width, depth).
            position: Floor position.
            color: Floor color.
            show_grid: Whether to show grid lines.
        """
        self.environment_renderer.add_floor(
            floor_id, size, position, color, 
            grid_visible=show_grid
        )
    
    def add_wall(
        self,
        wall_id: str,
        size: Tuple[float, float] = (10, 5),
        position: Tuple[float, float, float] = (0, 5, 2.5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#505050"
    ):
        """Add a wall to the environment.
        
        Args:
            wall_id: Unique identifier for the wall.
            size: Wall size (width, height).
            position: Wall position.
            rotation: Wall rotation in radians.
            color: Wall color.
        """
        self.environment_renderer.add_wall(
            wall_id, size, position, rotation, color
        )
    
    def add_box(
        self,
        box_id: str,
        size: Tuple[float, float, float] = (1, 1, 1),
        position: Tuple[float, float, float] = (0, 0, 0.5),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        color: str = "#606060"
    ):
        """Add a box to the environment.
        
        Args:
            box_id: Unique identifier for the box.
            size: Box dimensions (width, depth, height).
            position: Box position.
            rotation: Box rotation in radians.
            color: Box color.
        """
        self.environment_renderer.add_box(
            box_id, size, position, rotation, color
        )
    
    def create_room(
        self,
        size: Tuple[float, float, float] = (10, 10, 3),
        floor_color: str = "#404040",
        wall_color: str = "#505050"
    ):
        """Create a simple room environment.
        
        Args:
            size: Room dimensions (width, depth, height).
            floor_color: Floor color.
            wall_color: Wall color.
        """
        self.environment_renderer.create_room(
            size, floor_color, wall_color, add_ceiling=False
        )
    
    def show(self) -> None:
        """Display the visualization window."""
        # Create canvas
        self._canvas = WgpuCanvas(
            size=(1280, 720),
            title="Vibing-Viz",
            max_fps=60
        )
        
        # Create renderer
        self._renderer = gfx.WgpuRenderer(self._canvas)
        
        # Add grid if enabled
        if self.config.show_grid:
            grid = self.scene_manager.create_grid(size=20, divisions=20)
            self.scene_manager.add_object("grid", grid)
        
        # Add axes helper
        axes = self.scene_manager.create_axes_helper(size=2)
        self.scene_manager.add_object("axes", axes)
        
        # Set initial frame
        self.set_frame(0)
        
        # Fit camera to scene
        self.scene_manager.fit_camera_to_scene()
        
        # Setup controls
        self._setup_controls()
        
        # Start render loop
        self._canvas.request_draw(self._render_frame)
        
        # Run the app
        WgpuCanvas.run()
    
    def _setup_controls(self):
        """Setup interactive controls."""
        # Add orbit controller to default camera
        camera = self.scene_manager.active_camera
        controller = gfx.OrbitController(camera)
        controller.add_default_event_handlers(self._renderer)
        
        # Add keyboard controls
        @self._canvas.add_event_handler("key_down")
        def on_key(event):
            if event.key == " ":  # Space - play/pause
                self._playing = not self._playing
            elif event.key == "ArrowLeft":  # Previous frame
                self.set_frame(max(0, self._current_frame - 1))
                self._canvas.request_draw()
            elif event.key == "ArrowRight":  # Next frame
                max_frame = self.get_total_frames() - 1
                self.set_frame(min(max_frame, self._current_frame + 1))
                self._canvas.request_draw()
            elif event.key == "Home":  # First frame
                self.set_frame(0)
                self._canvas.request_draw()
            elif event.key == "End":  # Last frame
                self.set_frame(self.get_total_frames() - 1)
                self._canvas.request_draw()
    
    def _render_frame(self):
        """Render a single frame."""
        # Clear with background color
        self._renderer.clear_color = self.scene_manager.background_color
        
        # Render scene
        self._renderer.render(
            self.scene_manager.scene,
            self.scene_manager.active_camera
        )
        
        # Handle animation
        if self._playing:
            # Advance frame
            next_frame = (self._current_frame + 1) % self.get_total_frames()
            self.set_frame(next_frame)
            
            # Request next frame
            self._canvas.request_draw()
        
        return self._renderer
    
    def export_video(
        self,
        output_path: str,
        start_frame: int = 0,
        end_frame: Optional[int] = None,
        resolution: Tuple[int, int] = (1920, 1080),
        fps: int = 30,
        camera_trajectory: Optional[Dict[int, Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> bool:
        """Export visualization to video.
        
        Args:
            output_path: Path to save video file.
            start_frame: Starting frame index.
            end_frame: Ending frame index (None for last frame).
            resolution: Video resolution (width, height).
            fps: Frames per second.
            camera_trajectory: Optional camera movement keyframes.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            True if export completed successfully.
        """
        from vibing_viz.io.video_exporter import VideoExporter
        
        # Validate frames
        if end_frame is None:
            end_frame = self.get_total_frames() - 1
        
        if start_frame < 0 or end_frame >= self.get_total_frames():
            raise ValueError("Invalid frame range")
        
        # Create temporary canvas and renderer for export
        from wgpu.gui.offscreen import WgpuCanvas as OffscreenCanvas
        canvas = OffscreenCanvas(size=resolution)
        renderer = gfx.WgpuRenderer(canvas)
        
        # Get active camera
        camera = self.camera_manager.get_active_camera()
        if camera is None:
            camera = self.scene_manager.active_camera
        
        # Create exporter
        exporter = VideoExporter(renderer, self.scene_manager.scene, camera)
        exporter.set_resolution(*resolution)
        exporter.set_fps(fps)
        
        # Export video
        try:
            success = exporter.export(
                output_path=output_path,
                frame_callback=self.set_frame,
                start_frame=start_frame,
                end_frame=end_frame,
                camera_trajectory=camera_trajectory,
                progress_callback=progress_callback
            )
            return success
        finally:
            canvas.close()
    
    def export_image_sequence(
        self,
        output_dir: str,
        start_frame: int = 0,
        end_frame: Optional[int] = None,
        resolution: Tuple[int, int] = (1920, 1080),
        image_format: str = "png",
        camera_trajectory: Optional[Dict[int, Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> bool:
        """Export visualization as image sequence.
        
        Args:
            output_dir: Directory to save images.
            start_frame: Starting frame index.
            end_frame: Ending frame index (None for last frame).
            resolution: Image resolution (width, height).
            image_format: Image format (png, jpg, etc).
            camera_trajectory: Optional camera movement keyframes.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            True if export completed successfully.
        """
        from vibing_viz.io.video_exporter import VideoExporter
        
        # Validate frames
        if end_frame is None:
            end_frame = self.get_total_frames() - 1
        
        if start_frame < 0 or end_frame >= self.get_total_frames():
            raise ValueError("Invalid frame range")
        
        # Create temporary canvas and renderer
        from wgpu.gui.offscreen import WgpuCanvas as OffscreenCanvas
        canvas = OffscreenCanvas(size=resolution)
        renderer = gfx.WgpuRenderer(canvas)
        
        # Get active camera
        camera = self.camera_manager.get_active_camera()
        if camera is None:
            camera = self.scene_manager.active_camera
        
        # Create exporter
        exporter = VideoExporter(renderer, self.scene_manager.scene, camera)
        exporter.set_resolution(*resolution)
        
        # Export images
        try:
            success = exporter.export_image_sequence(
                output_dir=output_dir,
                frame_callback=self.set_frame,
                start_frame=start_frame,
                end_frame=end_frame,
                image_format=image_format,
                camera_trajectory=camera_trajectory,
                progress_callback=progress_callback
            )
            return success
        finally:
            canvas.close()