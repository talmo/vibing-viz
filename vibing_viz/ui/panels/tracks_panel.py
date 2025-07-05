"""Tracks panel for managing pose tracks."""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QToolButton, QMenu, QSlider, QLabel,
    QCheckBox, QSpinBox, QColorDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QBrush


class TracksPanel(QWidget):
    """Panel for managing and configuring tracks.
    
    This panel shows all loaded tracks with controls for visibility,
    opacity, playback options, and track-specific settings.
    """
    
    # Signals
    track_visibility_changed = pyqtSignal(str, bool)  # track_id, visible
    track_opacity_changed = pyqtSignal(str, float)  # track_id, opacity
    track_color_changed = pyqtSignal(str, str)  # track_id, color
    track_selected = pyqtSignal(str)  # track_id
    track_removed = pyqtSignal(str)  # track_id
    
    def __init__(self, parent=None):
        """Initialize tracks panel.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        # Track data storage
        self.tracks: Dict[str, Dict] = {}
        
        # Create UI
        self._create_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _create_ui(self):
        """Create UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Add track button
        self.btn_add = QPushButton("+")
        self.btn_add.setToolTip("Add track")
        self.btn_add.setMaximumWidth(30)
        toolbar_layout.addWidget(self.btn_add)
        
        # Remove track button
        self.btn_remove = QPushButton("-")
        self.btn_remove.setToolTip("Remove selected track")
        self.btn_remove.setMaximumWidth(30)
        self.btn_remove.setEnabled(False)
        toolbar_layout.addWidget(self.btn_remove)
        
        toolbar_layout.addStretch()
        
        # Show all checkbox
        self.chk_show_all = QCheckBox("Show All")
        self.chk_show_all.setChecked(True)
        toolbar_layout.addWidget(self.chk_show_all)
        
        layout.addLayout(toolbar_layout)
        
        # Track list
        self.track_list = QListWidget()
        self.track_list.setAlternatingRowColors(True)
        layout.addWidget(self.track_list)
        
        # Track controls group
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        
        # Opacity control
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setEnabled(False)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_label)
        controls_layout.addLayout(opacity_layout)
        
        # Playback speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 200)
        self.speed_spin.setValue(100)
        self.speed_spin.setSuffix("%")
        self.speed_spin.setEnabled(False)
        speed_layout.addWidget(self.speed_spin)
        controls_layout.addLayout(speed_layout)
        
        # Frame offset
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("Offset:"))
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(-1000, 1000)
        self.offset_spin.setValue(0)
        self.offset_spin.setSuffix(" frames")
        self.offset_spin.setEnabled(False)
        offset_layout.addWidget(self.offset_spin)
        controls_layout.addLayout(offset_layout)
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply custom styling."""
        style = """
        QWidget {
            background-color: #2b2b2b;
            color: #cccccc;
        }
        QListWidget {
            background-color: #2b2b2b;
            border: 1px solid #555555;
            outline: none;
        }
        QListWidget::item {
            padding: 5px;
            border-bottom: 1px solid #404040;
        }
        QListWidget::item:selected {
            background-color: #3d7aed;
        }
        QListWidget::item:hover {
            background-color: #404040;
        }
        QPushButton, QToolButton {
            background-color: #404040;
            color: #cccccc;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 3px;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: #555555;
        }
        QCheckBox {
            color: #cccccc;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background: #404040;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #3d7aed;
            width: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }
        QSpinBox {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 3px;
            border-radius: 3px;
        }
        QLabel {
            color: #cccccc;
        }
        """
        self.setStyleSheet(style)
    
    def _connect_signals(self):
        """Connect signals."""
        self.track_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.track_list.itemChanged.connect(self._on_item_changed)
        self.btn_add.clicked.connect(self._on_add_clicked)
        self.btn_remove.clicked.connect(self._on_remove_clicked)
        self.chk_show_all.toggled.connect(self._on_show_all_toggled)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self.speed_spin.valueChanged.connect(self._on_speed_changed)
        self.offset_spin.valueChanged.connect(self._on_offset_changed)
    
    def add_track(self, track_id: str, name: str, color: str = "#ffffff", 
                  n_frames: int = 0, n_keypoints: int = 0):
        """Add a track to the panel.
        
        Args:
            track_id: Unique track identifier.
            name: Display name.
            color: Track color (hex).
            n_frames: Number of frames.
            n_keypoints: Number of keypoints.
        """
        # Create list item
        item = QListWidgetItem()
        item.setData(Qt.UserRole, track_id)
        
        # Create custom widget
        item_widget = TrackListItem(track_id, name, color, n_frames, n_keypoints)
        item_widget.visibility_changed.connect(
            lambda v: self.track_visibility_changed.emit(track_id, v)
        )
        item_widget.color_changed.connect(
            lambda c: self.track_color_changed.emit(track_id, c)
        )
        
        # Add to list
        self.track_list.addItem(item)
        item.setSizeHint(item_widget.sizeHint())
        self.track_list.setItemWidget(item, item_widget)
        
        # Store track data
        self.tracks[track_id] = {
            "name": name,
            "color": color,
            "visible": True,
            "opacity": 1.0,
            "speed": 1.0,
            "offset": 0,
            "item": item,
            "widget": item_widget
        }
    
    def remove_track(self, track_id: str):
        """Remove a track from the panel.
        
        Args:
            track_id: Track identifier.
        """
        if track_id in self.tracks:
            item = self.tracks[track_id]["item"]
            row = self.track_list.row(item)
            self.track_list.takeItem(row)
            del self.tracks[track_id]
    
    def set_track_visibility(self, track_id: str, visible: bool):
        """Set track visibility.
        
        Args:
            track_id: Track identifier.
            visible: Whether track is visible.
        """
        if track_id in self.tracks:
            self.tracks[track_id]["visible"] = visible
            self.tracks[track_id]["widget"].set_visibility(visible)
    
    def _on_selection_changed(self):
        """Handle selection change."""
        selected = self.track_list.selectedItems()
        if selected:
            item = selected[0]
            track_id = item.data(Qt.UserRole)
            
            # Enable controls
            self.btn_remove.setEnabled(True)
            self.opacity_slider.setEnabled(True)
            self.speed_spin.setEnabled(True)
            self.offset_spin.setEnabled(True)
            
            # Update control values
            track_data = self.tracks.get(track_id, {})
            self.opacity_slider.setValue(int(track_data.get("opacity", 1.0) * 100))
            self.speed_spin.setValue(int(track_data.get("speed", 1.0) * 100))
            self.offset_spin.setValue(track_data.get("offset", 0))
            
            # Emit selection signal
            self.track_selected.emit(track_id)
        else:
            # Disable controls
            self.btn_remove.setEnabled(False)
            self.opacity_slider.setEnabled(False)
            self.speed_spin.setEnabled(False)
            self.offset_spin.setEnabled(False)
    
    def _on_item_changed(self, item: QListWidgetItem):
        """Handle item changes."""
        # Item changes are handled by the custom widget
        pass
    
    def _on_add_clicked(self):
        """Handle add button click."""
        # This would typically open a dialog to load track data
        # For now, just add a placeholder
        count = len(self.tracks)
        track_id = f"track_{count + 1}"
        self.add_track(
            track_id,
            f"Track {count + 1}",
            self._get_next_color(),
            100,  # placeholder frames
            17   # placeholder keypoints
        )
    
    def _on_remove_clicked(self):
        """Handle remove button click."""
        selected = self.track_list.selectedItems()
        if selected:
            track_id = selected[0].data(Qt.UserRole)
            self.remove_track(track_id)
            self.track_removed.emit(track_id)
    
    def _on_show_all_toggled(self, checked: bool):
        """Handle show all toggle."""
        for track_id, track_data in self.tracks.items():
            self.set_track_visibility(track_id, checked)
            self.track_visibility_changed.emit(track_id, checked)
    
    def _on_opacity_changed(self, value: int):
        """Handle opacity slider change."""
        selected = self.track_list.selectedItems()
        if selected:
            track_id = selected[0].data(Qt.UserRole)
            opacity = value / 100.0
            self.tracks[track_id]["opacity"] = opacity
            self.opacity_label.setText(f"{value}%")
            self.track_opacity_changed.emit(track_id, opacity)
    
    def _on_speed_changed(self, value: int):
        """Handle speed change."""
        selected = self.track_list.selectedItems()
        if selected:
            track_id = selected[0].data(Qt.UserRole)
            self.tracks[track_id]["speed"] = value / 100.0
    
    def _on_offset_changed(self, value: int):
        """Handle offset change."""
        selected = self.track_list.selectedItems()
        if selected:
            track_id = selected[0].data(Qt.UserRole)
            self.tracks[track_id]["offset"] = value
    
    def _get_next_color(self) -> str:
        """Get next color from palette."""
        from vibing_viz.utils.colors import ColorManager
        cm = ColorManager()
        track_id = f"temp_{len(self.tracks)}"
        return cm.get_track_color(track_id)


class TrackListItem(QWidget):
    """Custom widget for track list items."""
    
    # Signals
    visibility_changed = pyqtSignal(bool)
    color_changed = pyqtSignal(str)
    
    def __init__(self, track_id: str, name: str, color: str, 
                 n_frames: int, n_keypoints: int):
        """Initialize track list item.
        
        Args:
            track_id: Track identifier.
            name: Display name.
            color: Track color.
            n_frames: Number of frames.
            n_keypoints: Number of keypoints.
        """
        super().__init__()
        
        self.track_id = track_id
        self.color = color
        
        # Create UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Visibility checkbox
        self.visibility_check = QCheckBox()
        self.visibility_check.setChecked(True)
        self.visibility_check.toggled.connect(self.visibility_changed.emit)
        layout.addWidget(self.visibility_check)
        
        # Color button
        self.color_btn = QToolButton()
        self.color_btn.setFixedSize(20, 20)
        self._update_color_icon()
        self.color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.color_btn)
        
        # Name and info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.name_label)
        
        self.info_label = QLabel(f"{n_frames} frames, {n_keypoints} keypoints")
        self.info_label.setStyleSheet("font-size: 10px; color: #888888;")
        info_layout.addWidget(self.info_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
    
    def set_visibility(self, visible: bool):
        """Set visibility state."""
        self.visibility_check.setChecked(visible)
    
    def _update_color_icon(self):
        """Update color button icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 16, 16, 2, 2)
        painter.end()
        
        self.color_btn.setIcon(QIcon(pixmap))
    
    def _pick_color(self):
        """Show color picker."""
        color = QColorDialog.getColor(QColor(self.color), self, "Choose Track Color")
        if color.isValid():
            self.color = color.name()
            self._update_color_icon()
            self.color_changed.emit(self.color)