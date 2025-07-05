"""Properties panel for object editing."""

from typing import Any, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QDoubleSpinBox, QSlider, QComboBox, QPushButton,
    QGroupBox, QScrollArea, QColorDialog, QLineEdit,
    QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class PropertiesPanel(QWidget):
    """Panel for editing object properties.
    
    This panel displays and allows editing of properties for the
    currently selected object in the scene.
    """
    
    # Signals
    property_changed = pyqtSignal(str, str, object)  # object_id, property_name, value
    
    def __init__(self, parent=None):
        """Initialize properties panel.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        # Current object
        self.current_object_id: Optional[str] = None
        self.current_object_type: Optional[str] = None
        
        # Property widgets
        self.property_widgets: Dict[str, QWidget] = {}
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        self.header_label = QLabel("No Selection")
        self.header_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                padding: 5px;
                background-color: #404040;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.header_label)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #2b2b2b;
                border: 1px solid #555555;
            }
        """)
        
        # Properties container
        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_container)
        self.properties_layout.setContentsMargins(5, 5, 5, 5)
        scroll.setWidget(self.properties_container)
        
        main_layout.addWidget(scroll)
        
        # Apply base styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply custom styling."""
        style = """
        QWidget {
            background-color: #2b2b2b;
            color: #cccccc;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #555555;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QLabel {
            color: #cccccc;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 3px;
            border-radius: 3px;
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
        QPushButton {
            background-color: #404040;
            color: #cccccc;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QCheckBox {
            color: #cccccc;
        }
        """
        self.setStyleSheet(style)
    
    def set_object(self, object_type: str, object_id: str, properties: Dict[str, Any]):
        """Set the object to display properties for.
        
        Args:
            object_type: Type of object (track, camera, etc).
            object_id: Unique object identifier.
            properties: Dictionary of property values.
        """
        self.current_object_id = object_id
        self.current_object_type = object_type
        
        # Update header
        self.header_label.setText(f"{object_type.title()}: {object_id}")
        
        # Clear existing properties
        self._clear_properties()
        
        # Create property editors based on type
        if object_type == "track":
            self._create_track_properties(properties)
        elif object_type == "camera":
            self._create_camera_properties(properties)
        elif object_type == "environment":
            self._create_environment_properties(properties)
        elif object_type == "light":
            self._create_light_properties(properties)
        
        # Add stretch at end
        self.properties_layout.addStretch()
    
    def _clear_properties(self):
        """Clear all property widgets."""
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.property_widgets.clear()
    
    def _create_track_properties(self, properties: Dict[str, Any]):
        """Create track-specific properties.
        
        Args:
            properties: Current property values.
        """
        # Basic properties
        basic_group = QGroupBox("Basic")
        basic_layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        name_edit = QLineEdit(properties.get("name", ""))
        name_edit.textChanged.connect(lambda v: self._emit_change("name", v))
        name_layout.addWidget(name_edit)
        basic_layout.addLayout(name_layout)
        self.property_widgets["name"] = name_edit
        
        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_btn = QPushButton()
        color = properties.get("color", "#ffffff")
        color_btn.setStyleSheet(f"background-color: {color};")
        color_btn.clicked.connect(lambda: self._pick_color("color", color_btn))
        color_layout.addWidget(color_btn)
        basic_layout.addLayout(color_layout)
        self.property_widgets["color"] = color_btn
        
        basic_group.setLayout(basic_layout)
        self.properties_layout.addWidget(basic_group)
        
        # Display properties
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout()
        
        # Visible
        visible_check = QCheckBox("Visible")
        visible_check.setChecked(properties.get("visible", True))
        visible_check.toggled.connect(lambda v: self._emit_change("visible", v))
        display_layout.addWidget(visible_check)
        self.property_widgets["visible"] = visible_check
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(properties.get("opacity", 1.0) * 100))
        opacity_slider.valueChanged.connect(lambda v: self._emit_change("opacity", v / 100.0))
        opacity_layout.addWidget(opacity_slider)
        opacity_label = QLabel(f"{properties.get('opacity', 1.0):.2f}")
        opacity_slider.valueChanged.connect(lambda v: opacity_label.setText(f"{v/100:.2f}"))
        opacity_layout.addWidget(opacity_label)
        display_layout.addLayout(opacity_layout)
        self.property_widgets["opacity"] = opacity_slider
        
        # Keypoint size
        kp_size_layout = QHBoxLayout()
        kp_size_layout.addWidget(QLabel("Keypoint Size:"))
        kp_size_spin = QDoubleSpinBox()
        kp_size_spin.setRange(0.1, 20.0)
        kp_size_spin.setValue(properties.get("keypoint_size", 5.0))
        kp_size_spin.setSingleStep(0.5)
        kp_size_spin.valueChanged.connect(lambda v: self._emit_change("keypoint_size", v))
        kp_size_layout.addWidget(kp_size_spin)
        display_layout.addLayout(kp_size_layout)
        self.property_widgets["keypoint_size"] = kp_size_spin
        
        display_group.setLayout(display_layout)
        self.properties_layout.addWidget(display_group)
    
    def _create_camera_properties(self, properties: Dict[str, Any]):
        """Create camera-specific properties.
        
        Args:
            properties: Current property values.
        """
        # Camera properties
        camera_group = QGroupBox("Camera")
        camera_layout = QVBoxLayout()
        
        # FOV
        fov_layout = QHBoxLayout()
        fov_layout.addWidget(QLabel("Field of View:"))
        fov_spin = QSpinBox()
        fov_spin.setRange(10, 120)
        fov_spin.setValue(properties.get("fov", 60))
        fov_spin.setSuffix("°")
        fov_spin.valueChanged.connect(lambda v: self._emit_change("fov", v))
        fov_layout.addWidget(fov_spin)
        camera_layout.addLayout(fov_layout)
        self.property_widgets["fov"] = fov_spin
        
        # Near/Far planes
        near_layout = QHBoxLayout()
        near_layout.addWidget(QLabel("Near Plane:"))
        near_spin = QDoubleSpinBox()
        near_spin.setRange(0.01, 100.0)
        near_spin.setValue(properties.get("near", 0.1))
        near_spin.valueChanged.connect(lambda v: self._emit_change("near", v))
        near_layout.addWidget(near_spin)
        camera_layout.addLayout(near_layout)
        self.property_widgets["near"] = near_spin
        
        far_layout = QHBoxLayout()
        far_layout.addWidget(QLabel("Far Plane:"))
        far_spin = QDoubleSpinBox()
        far_spin.setRange(1.0, 10000.0)
        far_spin.setValue(properties.get("far", 1000.0))
        far_spin.valueChanged.connect(lambda v: self._emit_change("far", v))
        far_layout.addWidget(far_spin)
        camera_layout.addLayout(far_layout)
        self.property_widgets["far"] = far_spin
        
        camera_group.setLayout(camera_layout)
        self.properties_layout.addWidget(camera_group)
    
    def _create_environment_properties(self, properties: Dict[str, Any]):
        """Create environment-specific properties.
        
        Args:
            properties: Current property values.
        """
        # Environment properties
        env_group = QGroupBox("Environment")
        env_layout = QVBoxLayout()
        
        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Floor", "Wall", "Box", "Custom"])
        type_combo.setCurrentText(properties.get("type", "Floor"))
        type_combo.currentTextChanged.connect(lambda v: self._emit_change("type", v))
        type_layout.addWidget(type_combo)
        env_layout.addLayout(type_layout)
        self.property_widgets["type"] = type_combo
        
        # Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        for dim, label in enumerate(["X", "Y", "Z"]):
            size_spin = QDoubleSpinBox()
            size_spin.setRange(0.1, 1000.0)
            size_spin.setValue(properties.get("size", [10, 10, 0.1])[dim])
            size_spin.valueChanged.connect(
                lambda v, d=dim: self._emit_size_change(d, v)
            )
            size_layout.addWidget(QLabel(f"{label}:"))
            size_layout.addWidget(size_spin)
            self.property_widgets[f"size_{label.lower()}"] = size_spin
        env_layout.addLayout(size_layout)
        
        env_group.setLayout(env_layout)
        self.properties_layout.addWidget(env_group)
    
    def _create_light_properties(self, properties: Dict[str, Any]):
        """Create light-specific properties.
        
        Args:
            properties: Current property values.
        """
        # Light properties
        light_group = QGroupBox("Light")
        light_layout = QVBoxLayout()
        
        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Directional", "Point", "Spot"])
        type_combo.setCurrentText(properties.get("type", "Directional"))
        type_combo.currentTextChanged.connect(lambda v: self._emit_change("type", v))
        type_layout.addWidget(type_combo)
        light_layout.addLayout(type_layout)
        self.property_widgets["type"] = type_combo
        
        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_btn = QPushButton()
        color = properties.get("color", "#ffffff")
        color_btn.setStyleSheet(f"background-color: {color};")
        color_btn.clicked.connect(lambda: self._pick_color("light_color", color_btn))
        color_layout.addWidget(color_btn)
        light_layout.addLayout(color_layout)
        self.property_widgets["light_color"] = color_btn
        
        # Intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity:"))
        intensity_spin = QDoubleSpinBox()
        intensity_spin.setRange(0.0, 10.0)
        intensity_spin.setValue(properties.get("intensity", 1.0))
        intensity_spin.setSingleStep(0.1)
        intensity_spin.valueChanged.connect(lambda v: self._emit_change("intensity", v))
        intensity_layout.addWidget(intensity_spin)
        light_layout.addLayout(intensity_layout)
        self.property_widgets["intensity"] = intensity_spin
        
        light_group.setLayout(light_layout)
        self.properties_layout.addWidget(light_group)
    
    def _pick_color(self, property_name: str, button: QPushButton):
        """Show color picker dialog.
        
        Args:
            property_name: Property to update.
            button: Button to update appearance.
        """
        current_color = button.styleSheet().split(":")[1].strip().rstrip(";")
        color = QColorDialog.getColor(QColor(current_color), self, "Choose Color")
        
        if color.isValid():
            hex_color = color.name()
            button.setStyleSheet(f"background-color: {hex_color};")
            self._emit_change(property_name, hex_color)
    
    def _emit_change(self, property_name: str, value: Any):
        """Emit property changed signal.
        
        Args:
            property_name: Name of changed property.
            value: New value.
        """
        if self.current_object_id:
            self.property_changed.emit(self.current_object_id, property_name, value)
    
    def _emit_size_change(self, dimension: int, value: float):
        """Emit size change for specific dimension.
        
        Args:
            dimension: 0=X, 1=Y, 2=Z.
            value: New size value.
        """
        # Get current size values
        size = [
            self.property_widgets.get("size_x", QDoubleSpinBox()).value(),
            self.property_widgets.get("size_y", QDoubleSpinBox()).value(),
            self.property_widgets.get("size_z", QDoubleSpinBox()).value()
        ]
        size[dimension] = value
        self._emit_change("size", size)
    
    def update_property(self, property_name: str, value: Any):
        """Update a property value in the UI.
        
        Args:
            property_name: Property to update.
            value: New value.
        """
        if property_name in self.property_widgets:
            widget = self.property_widgets[property_name]
            
            # Block signals to prevent loops
            widget.blockSignals(True)
            
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(value)
            elif isinstance(widget, QSlider):
                widget.setValue(int(value * 100) if property_name == "opacity" else int(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QComboBox):
                widget.setCurrentText(str(value))
            elif isinstance(widget, QPushButton) and "color" in property_name:
                widget.setStyleSheet(f"background-color: {value};")
            
            widget.blockSignals(False)