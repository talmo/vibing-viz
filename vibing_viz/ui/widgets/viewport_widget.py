"""PyGFX viewport widget for Qt integration."""

from typing import Optional, Callable
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import pygfx as gfx
from wgpu.gui.qt import WgpuCanvas


class ViewportWidget(QWidget):
    """Qt widget containing a PyGFX viewport.
    
    This widget integrates PyGFX rendering with Qt, providing
    a 3D viewport that can be embedded in Qt applications.
    """
    
    # Signals
    frame_rendered = pyqtSignal(int)  # Emitted after each frame with FPS
    
    def __init__(self, parent=None):
        """Initialize viewport widget.
        
        Args:
            parent: Parent Qt widget.
        """
        super().__init__(parent)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create PyGFX canvas
        self.canvas = WgpuCanvas(parent=self, size=(800, 600))
        self.layout.addWidget(self.canvas)
        
        # Create renderer
        self.renderer = gfx.WgpuRenderer(self.canvas)
        
        # Scene and camera (will be set externally)
        self.scene: Optional[gfx.Scene] = None
        self.camera: Optional[gfx.Camera] = None
        
        # Controllers
        self.controller: Optional[gfx.Controller] = None
        
        # Animation
        self._animation_callback: Optional[Callable] = None
        self._is_animating = False
        
        # Setup render timer
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self._render_frame)
        self.render_timer.setInterval(16)  # ~60 FPS
        
        # FPS tracking
        self._frame_count = 0
        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(1000)  # Update every second
        
        # Mouse tracking for controllers
        self.setMouseTracking(True)
        
        # Background color
        self._background_color = "#1a1a1a"
    
    def set_scene(self, scene: gfx.Scene):
        """Set the scene to render.
        
        Args:
            scene: PyGFX scene object.
        """
        self.scene = scene
        self.request_render()
    
    def set_camera(self, camera: gfx.Camera):
        """Set the camera for rendering.
        
        Args:
            camera: PyGFX camera object.
        """
        self.camera = camera
        self.request_render()
    
    def set_controller(self, controller_type: str = "orbit"):
        """Set up camera controller.
        
        Args:
            controller_type: "orbit", "panzoom", or "fly".
        """
        if self.camera is None:
            return
        
        # Remove old controller
        if self.controller is not None:
            # Controller cleanup if needed
            pass
        
        # Create new controller
        if controller_type == "orbit":
            self.controller = gfx.OrbitController(self.camera)
        elif controller_type == "panzoom":
            self.controller = gfx.PanZoomController(self.camera)
        elif controller_type == "fly":
            self.controller = gfx.FlyController(self.camera)
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")
        
        # Connect events
        if self.controller:
            self.controller.register_events(self.renderer)
    
    def set_background_color(self, color: str):
        """Set viewport background color.
        
        Args:
            color: Hex color string.
        """
        self._background_color = color
        self.request_render()
    
    def start_animation(self, callback: Optional[Callable] = None):
        """Start animation loop.
        
        Args:
            callback: Optional function to call before each frame.
        """
        self._animation_callback = callback
        self._is_animating = True
        self.render_timer.start()
    
    def stop_animation(self):
        """Stop animation loop."""
        self._is_animating = False
        self.render_timer.stop()
    
    def request_render(self):
        """Request a single frame render."""
        if not self._is_animating:
            self._render_frame()
    
    def _render_frame(self):
        """Render a single frame."""
        if self.scene is None or self.camera is None:
            return
        
        # Call animation callback if provided
        if self._animation_callback:
            self._animation_callback()
        
        # Set background color
        self.renderer.clear_color = self._background_color
        
        # Render
        self.renderer.render(self.scene, self.camera)
        
        # Update frame count
        self._frame_count += 1
        
        # Request next frame if animating
        if self._is_animating:
            self.canvas.request_draw()
    
    def _update_fps(self):
        """Update FPS counter."""
        fps = self._frame_count
        self._frame_count = 0
        self.frame_rendered.emit(fps)
    
    def capture_screenshot(self) -> bytes:
        """Capture viewport screenshot.
        
        Returns:
            PNG image data as bytes.
        """
        # Render current frame
        self._render_frame()
        
        # Get frame buffer
        return self.renderer.snapshot()
    
    def resizeEvent(self, event):
        """Handle widget resize.
        
        Args:
            event: Qt resize event.
        """
        super().resizeEvent(event)
        
        # Update canvas size
        if self.canvas:
            size = event.size()
            self.canvas.set_logical_size(size.width(), size.height())
            
            # Update camera aspect ratio if perspective
            if self.camera and hasattr(self.camera, 'aspect'):
                self.camera.aspect = size.width() / size.height()
            
            self.request_render()
    
    def fit_to_scene(self, padding: float = 1.2):
        """Adjust camera to fit entire scene.
        
        Args:
            padding: Extra space factor around scene.
        """
        if self.scene is None or self.camera is None:
            return
        
        # This would call scene bounds calculation
        # For now, just trigger a render
        self.request_render()
    
    # Qt event handlers for mouse/keyboard input
    def mousePressEvent(self, event):
        """Handle mouse press."""
        super().mousePressEvent(event)
        # Controller will handle via canvas events
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        super().mouseMoveEvent(event)
    
    def wheelEvent(self, event):
        """Handle mouse wheel."""
        super().wheelEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press."""
        super().keyPressEvent(event)
        
        # Custom key handlers
        if event.key() == Qt.Key_F:
            # Fit to scene
            self.fit_to_scene()
        elif event.key() == Qt.Key_R:
            # Reset camera
            if self.controller and hasattr(self.controller, 'reset'):
                self.controller.reset()
                self.request_render()