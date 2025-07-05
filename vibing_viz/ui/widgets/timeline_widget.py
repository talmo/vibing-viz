"""Timeline widget for temporal navigation."""

from typing import Dict, List, Tuple, Optional
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QMouseEvent


class TimelineWidget(QWidget):
    """Timeline widget showing tracks and temporal navigation.
    
    This widget displays track data availability, current frame position,
    and allows navigation through time.
    """
    
    # Signals
    frame_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize timeline widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        # Timeline properties
        self.total_frames = 100
        self.current_frame = 0
        self.zoom_level = 1.0
        self.pan_offset = 0
        
        # Track data
        self.tracks: Dict[str, Dict] = {}
        
        # Visual properties
        self.track_height = 30
        self.ruler_height = 30
        self.margin = 10
        self.playhead_width = 2
        
        # Colors
        self.bg_color = QColor(40, 40, 40)
        self.ruler_color = QColor(60, 60, 60)
        self.grid_color = QColor(50, 50, 50)
        self.playhead_color = QColor(255, 100, 100)
        self.text_color = QColor(200, 200, 200)
        
        # Interaction
        self._dragging = False
        self._drag_start = QPoint()
        self._hover_frame = -1
        
        # Set minimum size
        self.setMinimumHeight(150)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Timeline canvas (custom painted)
        self.setAutoFillBackground(True)
        
        # Bottom controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(self.margin, 5, self.margin, 5)
        
        # Frame counter
        self.frame_label = QLabel("Frame: 0/0")
        self.frame_label.setStyleSheet("color: #cccccc;")
        controls_layout.addWidget(self.frame_label)
        
        controls_layout.addStretch()
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #cccccc;")
        controls_layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 500)  # 0.1x to 5x
        self.zoom_slider.setValue(100)  # 1x
        self.zoom_slider.setMaximumWidth(100)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        controls_layout.addWidget(self.zoom_slider)
        
        layout.addStretch()
        layout.addLayout(controls_layout)
    
    def add_track(self, track_id: str, color: str, data_ranges: List[Tuple[int, int]]):
        """Add or update a track.
        
        Args:
            track_id: Unique track identifier.
            color: Track color (hex).
            data_ranges: List of (start, end) frame ranges where data exists.
        """
        self.tracks[track_id] = {
            "color": color,
            "data_ranges": data_ranges,
            "visible": True
        }
        self.update()
    
    def remove_track(self, track_id: str):
        """Remove a track.
        
        Args:
            track_id: Track identifier.
        """
        if track_id in self.tracks:
            del self.tracks[track_id]
            self.update()
    
    def set_track_visibility(self, track_id: str, visible: bool):
        """Set track visibility.
        
        Args:
            track_id: Track identifier.
            visible: Whether track is visible.
        """
        if track_id in self.tracks:
            self.tracks[track_id]["visible"] = visible
            self.update()
    
    def set_total_frames(self, total: int):
        """Set total number of frames.
        
        Args:
            total: Total frame count.
        """
        self.total_frames = max(1, total)
        self._update_frame_label()
        self.update()
    
    def set_current_frame(self, frame: int):
        """Set current frame position.
        
        Args:
            frame: Frame index.
        """
        self.current_frame = max(0, min(frame, self.total_frames - 1))
        self._update_frame_label()
        self.update()
    
    def _update_frame_label(self):
        """Update frame counter label."""
        self.frame_label.setText(
            f"Frame: {self.current_frame + 1}/{self.total_frames}"
        )
    
    def _on_zoom_changed(self, value: int):
        """Handle zoom slider change.
        
        Args:
            value: Slider value (10-500).
        """
        self.zoom_level = value / 100.0
        self.update()
    
    def _frame_to_x(self, frame: int) -> int:
        """Convert frame index to x coordinate.
        
        Args:
            frame: Frame index.
            
        Returns:
            X coordinate.
        """
        timeline_width = self.width() - 2 * self.margin
        pixels_per_frame = (timeline_width * self.zoom_level) / self.total_frames
        return int(self.margin + frame * pixels_per_frame + self.pan_offset)
    
    def _x_to_frame(self, x: int) -> int:
        """Convert x coordinate to frame index.
        
        Args:
            x: X coordinate.
            
        Returns:
            Frame index.
        """
        timeline_width = self.width() - 2 * self.margin
        pixels_per_frame = (timeline_width * self.zoom_level) / self.total_frames
        frame = (x - self.margin - self.pan_offset) / pixels_per_frame
        return max(0, min(int(frame), self.total_frames - 1))
    
    def paintEvent(self, event):
        """Paint the timeline.
        
        Args:
            event: Paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), self.bg_color)
        
        # Calculate timeline area
        timeline_rect = QRect(
            self.margin,
            self.ruler_height,
            self.width() - 2 * self.margin,
            self.height() - self.ruler_height - 40  # Leave space for controls
        )
        
        # Draw ruler
        self._draw_ruler(painter)
        
        # Draw tracks
        y_offset = self.ruler_height + 10
        for track_id, track_data in self.tracks.items():
            if track_data["visible"]:
                self._draw_track(painter, track_data, y_offset)
                y_offset += self.track_height + 5
        
        # Draw playhead
        self._draw_playhead(painter)
        
        # Draw hover indicator
        if self._hover_frame >= 0:
            self._draw_hover(painter)
    
    def _draw_ruler(self, painter: QPainter):
        """Draw time ruler.
        
        Args:
            painter: QPainter instance.
        """
        # Ruler background
        ruler_rect = QRect(0, 0, self.width(), self.ruler_height)
        painter.fillRect(ruler_rect, self.ruler_color)
        
        # Calculate tick spacing
        timeline_width = self.width() - 2 * self.margin
        pixels_per_frame = (timeline_width * self.zoom_level) / self.total_frames
        
        # Determine tick interval
        min_tick_spacing = 50  # Minimum pixels between major ticks
        frames_per_tick = max(1, int(min_tick_spacing / pixels_per_frame))
        
        # Round to nice numbers
        if frames_per_tick > 100:
            frames_per_tick = (frames_per_tick // 100) * 100
        elif frames_per_tick > 50:
            frames_per_tick = 50
        elif frames_per_tick > 10:
            frames_per_tick = (frames_per_tick // 10) * 10
        elif frames_per_tick > 5:
            frames_per_tick = 5
        
        # Draw ticks and labels
        painter.setPen(QPen(self.text_color, 1))
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        for frame in range(0, self.total_frames, frames_per_tick):
            x = self._frame_to_x(frame)
            
            # Skip if outside visible area
            if x < 0 or x > self.width():
                continue
            
            # Major tick
            painter.drawLine(x, self.ruler_height - 10, x, self.ruler_height)
            
            # Label
            label = str(frame)
            label_rect = painter.fontMetrics().boundingRect(label)
            painter.drawText(
                x - label_rect.width() // 2,
                self.ruler_height - 12,
                label
            )
        
        # Draw minor ticks
        if frames_per_tick > 5:
            minor_interval = frames_per_tick // 5
            painter.setPen(QPen(self.grid_color, 1))
            
            for frame in range(0, self.total_frames, minor_interval):
                if frame % frames_per_tick == 0:
                    continue  # Skip major tick positions
                    
                x = self._frame_to_x(frame)
                if x < 0 or x > self.width():
                    continue
                    
                painter.drawLine(x, self.ruler_height - 5, x, self.ruler_height)
    
    def _draw_track(self, painter: QPainter, track_data: Dict, y_offset: int):
        """Draw a single track.
        
        Args:
            painter: QPainter instance.
            track_data: Track data dictionary.
            y_offset: Y position for track.
        """
        # Track background
        track_rect = QRect(
            self.margin,
            y_offset,
            self.width() - 2 * self.margin,
            self.track_height
        )
        painter.fillRect(track_rect, QColor(50, 50, 50))
        
        # Draw data ranges
        color = QColor(track_data["color"])
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        
        for start, end in track_data["data_ranges"]:
            x_start = self._frame_to_x(start)
            x_end = self._frame_to_x(end)
            
            # Clip to visible area
            x_start = max(x_start, self.margin)
            x_end = min(x_end, self.width() - self.margin)
            
            if x_end > x_start:
                data_rect = QRect(
                    x_start,
                    y_offset + 2,
                    x_end - x_start,
                    self.track_height - 4
                )
                painter.fillRect(data_rect, color)
    
    def _draw_playhead(self, painter: QPainter):
        """Draw current frame indicator.
        
        Args:
            painter: QPainter instance.
        """
        x = self._frame_to_x(self.current_frame)
        
        # Draw line
        painter.setPen(QPen(self.playhead_color, self.playhead_width))
        painter.drawLine(x, 0, x, self.height() - 40)
        
        # Draw handle at top
        handle_rect = QRect(x - 5, 0, 10, self.ruler_height)
        painter.fillRect(handle_rect, self.playhead_color)
    
    def _draw_hover(self, painter: QPainter):
        """Draw hover indicator.
        
        Args:
            painter: QPainter instance.
        """
        if self._hover_frame >= 0:
            x = self._frame_to_x(self._hover_frame)
            
            # Draw vertical line
            painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
            painter.drawLine(x, self.ruler_height, x, self.height() - 40)
            
            # Draw frame number
            painter.setPen(QPen(self.text_color, 1))
            label = f"Frame {self._hover_frame + 1}"
            label_rect = painter.fontMetrics().boundingRect(label)
            
            # Position label
            label_x = x + 5
            if label_x + label_rect.width() > self.width() - self.margin:
                label_x = x - label_rect.width() - 5
            
            painter.drawText(label_x, self.ruler_height + 20, label)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press.
        
        Args:
            event: Mouse event.
        """
        if event.button() == Qt.LeftButton:
            # Check if clicking on ruler area
            if event.y() < self.ruler_height:
                # Set current frame
                frame = self._x_to_frame(event.x())
                self.set_current_frame(frame)
                self.frame_changed.emit(frame)
                self._dragging = True
                self._drag_start = event.pos()
        
        elif event.button() == Qt.MiddleButton:
            # Start panning
            self._dragging = True
            self._drag_start = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move.
        
        Args:
            event: Mouse event.
        """
        # Update hover frame
        self._hover_frame = self._x_to_frame(event.x())
        
        if self._dragging:
            if event.buttons() & Qt.LeftButton and event.y() < self.ruler_height:
                # Scrubbing
                frame = self._x_to_frame(event.x())
                self.set_current_frame(frame)
                self.frame_changed.emit(frame)
            
            elif event.buttons() & Qt.MiddleButton:
                # Panning
                delta = event.x() - self._drag_start.x()
                self.pan_offset += delta
                self._drag_start = event.pos()
        
        self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release.
        
        Args:
            event: Mouse event.
        """
        self._dragging = False
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom.
        
        Args:
            event: Wheel event.
        """
        # Get mouse position for zoom center
        mouse_frame = self._x_to_frame(event.x())
        
        # Zoom
        delta = event.angleDelta().y() / 120  # Standard wheel step
        old_zoom = self.zoom_level
        self.zoom_level *= (1.1 ** delta)
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        
        # Update zoom slider
        self.zoom_slider.setValue(int(self.zoom_level * 100))
        
        # Adjust pan to keep mouse position stable
        if old_zoom != self.zoom_level:
            old_x = self._frame_to_x(mouse_frame)
            # Recalculate with new zoom
            timeline_width = self.width() - 2 * self.margin
            pixels_per_frame = (timeline_width * self.zoom_level) / self.total_frames
            new_x = self.margin + mouse_frame * pixels_per_frame + self.pan_offset
            
            # Adjust pan offset
            self.pan_offset += old_x - new_x
        
        self.update()
    
    def leaveEvent(self, event):
        """Handle mouse leave.
        
        Args:
            event: Leave event.
        """
        self._hover_frame = -1
        self.update()