"""Video export functionality."""

from typing import Optional, Callable, Tuple, Any, Dict
import numpy as np
from pathlib import Path
import pygfx as gfx

try:
    import imageio as iio
    from imageio_ffmpeg import get_ffmpeg_exe
except ImportError:
    try:
        import imageio.v3 as iio
    except ImportError:
        import imageio.v2 as iio
    get_ffmpeg_exe = None


class VideoExporter:
    """Exports visualization to video files.
    
    This class handles rendering frames and encoding them to video
    using imageio and ffmpeg.
    """
    
    def __init__(
        self,
        renderer: gfx.WgpuRenderer,
        scene: gfx.Scene,
        camera: gfx.Camera
    ):
        """Initialize video exporter.
        
        Args:
            renderer: PyGFX renderer.
            scene: Scene to render.
            camera: Camera to render from.
        """
        self.renderer = renderer
        self.scene = scene
        self.camera = camera
        
        # Export settings
        self.resolution = (1920, 1080)
        self.fps = 30
        self.codec = "h264"
        self.quality = 8  # 0-10, higher is better
        
        # Progress tracking
        self._progress_callback: Optional[Callable[[float], None]] = None
        self._cancelled = False
    
    def export(
        self,
        output_path: str,
        frame_callback: Callable[[int], None],
        start_frame: int = 0,
        end_frame: int = 100,
        camera_trajectory: Optional[Dict[int, Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Export visualization to video.
        
        Args:
            output_path: Path to save video file.
            frame_callback: Function to call before rendering each frame.
            start_frame: Starting frame index.
            end_frame: Ending frame index (inclusive).
            camera_trajectory: Optional dict mapping frame indices to camera params.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            True if export completed successfully.
        """
        self._progress_callback = progress_callback
        self._cancelled = False
        
        # Validate output path
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check ffmpeg availability
        if get_ffmpeg_exe:
            try:
                ffmpeg_path = get_ffmpeg_exe()
                print(f"Using ffmpeg: {ffmpeg_path}")
            except Exception as e:
                print(f"Warning: ffmpeg not found: {e}")
                print("Video export may be limited to certain formats")
        
        # Calculate total frames
        total_frames = end_frame - start_frame + 1
        
        # Create temporary canvas for offscreen rendering
        canvas = self._create_offscreen_canvas()
        
        # Create video writer
        try:
            # For imageio v3, use different API
            writer = iio.get_writer(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                quality=self.quality,
                pixelformat="yuv420p"
            )
            
            with writer:
                for i, frame_idx in enumerate(range(start_frame, end_frame + 1)):
                    if self._cancelled:
                        print("Export cancelled by user")
                        return False
                    
                    # Update progress
                    progress = i / total_frames
                    if self._progress_callback:
                        self._progress_callback(progress)
                    
                    # Apply camera trajectory if provided
                    if camera_trajectory and frame_idx in camera_trajectory:
                        self._apply_camera_params(camera_trajectory[frame_idx])
                    
                    # Update frame
                    frame_callback(frame_idx)
                    
                    # Render frame
                    frame_data = self._render_frame(canvas)
                    
                    # Write to video
                    writer.append_data(frame_data)
                
                # Final progress update
                if self._progress_callback:
                    self._progress_callback(1.0)
                
                print(f"Video exported successfully: {output_path}")
                return True
                
        except Exception as e:
            print(f"Error exporting video: {e}")
            return False
        finally:
            # Cleanup
            canvas.close()
    
    def export_image_sequence(
        self,
        output_dir: str,
        frame_callback: Callable[[int], None],
        start_frame: int = 0,
        end_frame: int = 100,
        image_format: str = "png",
        camera_trajectory: Optional[Dict[int, Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Export visualization as image sequence.
        
        Args:
            output_dir: Directory to save images.
            frame_callback: Function to call before rendering each frame.
            start_frame: Starting frame index.
            end_frame: Ending frame index (inclusive).
            image_format: Image format (png, jpg, etc).
            camera_trajectory: Optional camera trajectory.
            progress_callback: Optional progress callback.
            
        Returns:
            True if export completed successfully.
        """
        self._progress_callback = progress_callback
        self._cancelled = False
        
        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculate total frames
        total_frames = end_frame - start_frame + 1
        
        # Create temporary canvas
        canvas = self._create_offscreen_canvas()
        
        try:
            for i, frame_idx in enumerate(range(start_frame, end_frame + 1)):
                if self._cancelled:
                    print("Export cancelled by user")
                    return False
                
                # Update progress
                progress = i / total_frames
                if self._progress_callback:
                    self._progress_callback(progress)
                
                # Apply camera trajectory if provided
                if camera_trajectory and frame_idx in camera_trajectory:
                    self._apply_camera_params(camera_trajectory[frame_idx])
                
                # Update frame
                frame_callback(frame_idx)
                
                # Render frame
                frame_data = self._render_frame(canvas)
                
                # Save image
                image_path = output_dir / f"frame_{frame_idx:06d}.{image_format}"
                iio.imwrite(str(image_path), frame_data)
            
            # Final progress update
            if self._progress_callback:
                self._progress_callback(1.0)
            
            print(f"Image sequence exported to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Error exporting image sequence: {e}")
            return False
        finally:
            # Cleanup
            canvas.close()
    
    def cancel(self):
        """Cancel ongoing export."""
        self._cancelled = True
    
    def set_resolution(self, width: int, height: int):
        """Set export resolution.
        
        Args:
            width: Width in pixels.
            height: Height in pixels.
        """
        self.resolution = (width, height)
    
    def set_fps(self, fps: int):
        """Set export frame rate.
        
        Args:
            fps: Frames per second.
        """
        self.fps = fps
    
    def set_codec(self, codec: str):
        """Set video codec.
        
        Args:
            codec: Codec name (h264, h265, vp9, etc).
        """
        self.codec = codec
    
    def set_quality(self, quality: int):
        """Set export quality.
        
        Args:
            quality: Quality level (0-10).
        """
        self.quality = max(0, min(10, quality))
    
    def _create_offscreen_canvas(self):
        """Create offscreen canvas for rendering.
        
        Returns:
            Offscreen canvas.
        """
        from wgpu.gui.offscreen import WgpuCanvas as OffscreenCanvas
        
        canvas = OffscreenCanvas(size=self.resolution)
        
        # Update renderer
        self.renderer = gfx.WgpuRenderer(canvas)
        
        # Update camera aspect ratio
        if hasattr(self.camera, 'aspect'):
            self.camera.aspect = self.resolution[0] / self.resolution[1]
        
        return canvas
    
    def _render_frame(self, canvas) -> np.ndarray:
        """Render a single frame.
        
        Args:
            canvas: Canvas to render to.
            
        Returns:
            Frame data as numpy array.
        """
        # Clear and render
        self.renderer.render(self.scene, self.camera)
        
        # Get frame buffer
        frame = self.renderer.snapshot()
        
        # Ensure it's a numpy array
        if not isinstance(frame, np.ndarray):
            frame = np.asarray(frame)
        
        # Check dimensions
        if frame.ndim == 2:
            # Grayscale, convert to RGB
            frame = np.stack([frame, frame, frame], axis=-1)
        elif frame.ndim == 3 and frame.shape[2] == 4:
            # RGBA, convert to RGB
            frame = frame[:, :, :3]
        elif frame.ndim == 3 and frame.shape[2] == 3:
            # Already RGB
            pass
        else:
            raise ValueError(f"Unexpected frame shape: {frame.shape}")
        
        # Ensure uint8
        if frame.dtype != np.uint8:
            if frame.max() <= 1.0:
                frame = (frame * 255).astype(np.uint8)
            else:
                frame = frame.astype(np.uint8)
        
        return frame
    
    def _apply_camera_params(self, params: Dict[str, Any]):
        """Apply camera parameters.
        
        Args:
            params: Dictionary with camera parameters.
        """
        if "position" in params:
            self.camera.local.position = np.array(params["position"])
        
        if "target" in params:
            # Look at target
            target = np.array(params["target"])
            position = self.camera.local.position
            
            # Calculate forward vector
            forward = target - position
            forward = forward / np.linalg.norm(forward)
            
            # Calculate right vector
            up = params.get("up", [0, 0, 1])
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
            self.camera.local.matrix = rotation_matrix
            self.camera.local.position = position
        
        if "fov" in params and hasattr(self.camera, 'fov'):
            self.camera.fov = params["fov"]


def create_camera_trajectory(
    keyframes: Dict[int, Dict[str, Any]],
    total_frames: int,
    interpolation: str = "linear"
) -> Dict[int, Dict[str, Any]]:
    """Create interpolated camera trajectory from keyframes.
    
    Args:
        keyframes: Dictionary mapping frame indices to camera params.
        total_frames: Total number of frames.
        interpolation: Interpolation method ("linear", "smooth").
        
    Returns:
        Complete trajectory with interpolated values.
    """
    if not keyframes:
        return {}
    
    # Sort keyframes
    sorted_frames = sorted(keyframes.keys())
    
    # Initialize trajectory
    trajectory = {}
    
    # Interpolate between keyframes
    for i in range(total_frames):
        # Find surrounding keyframes
        prev_frame = None
        next_frame = None
        
        for kf in sorted_frames:
            if kf <= i:
                prev_frame = kf
            if kf >= i and next_frame is None:
                next_frame = kf
        
        # Handle edge cases
        if prev_frame is None:
            trajectory[i] = keyframes[sorted_frames[0]].copy()
        elif next_frame is None:
            trajectory[i] = keyframes[sorted_frames[-1]].copy()
        elif prev_frame == next_frame:
            trajectory[i] = keyframes[prev_frame].copy()
        else:
            # Interpolate
            t = (i - prev_frame) / (next_frame - prev_frame)
            
            if interpolation == "smooth":
                # Smooth interpolation
                t = t * t * (3.0 - 2.0 * t)
            
            prev_params = keyframes[prev_frame]
            next_params = keyframes[next_frame]
            
            interp_params = {}
            
            # Interpolate position
            if "position" in prev_params and "position" in next_params:
                pos1 = np.array(prev_params["position"])
                pos2 = np.array(next_params["position"])
                interp_params["position"] = (1 - t) * pos1 + t * pos2
            
            # Interpolate target
            if "target" in prev_params and "target" in next_params:
                target1 = np.array(prev_params["target"])
                target2 = np.array(next_params["target"])
                interp_params["target"] = (1 - t) * target1 + t * target2
            
            # Interpolate FOV
            if "fov" in prev_params and "fov" in next_params:
                fov1 = prev_params["fov"]
                fov2 = next_params["fov"]
                interp_params["fov"] = (1 - t) * fov1 + t * fov2
            
            # Copy other parameters
            for key in ["up"]:
                if key in prev_params:
                    interp_params[key] = prev_params[key]
            
            trajectory[i] = interp_params
    
    return trajectory