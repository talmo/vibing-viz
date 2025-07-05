"""Scene hierarchy panel."""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QHBoxLayout, QPushButton, QMenu, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor


class ScenePanel(QWidget):
    """Panel showing scene hierarchy and object management.
    
    This panel displays all objects in the scene (tracks, environments,
    cameras) in a tree structure with visibility controls.
    """
    
    # Signals
    visibility_changed = pyqtSignal(str, str, bool)  # category, item_id, visible
    selection_changed = pyqtSignal(str, str)  # category, item_id
    
    def __init__(self, parent=None):
        """Initialize scene panel.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        # Scene item storage
        self.scene_items: Dict[str, Dict] = {
            "tracks": {},
            "environments": {},
            "cameras": {},
            "lights": {}
        }
        
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
        
        # Add buttons
        self.btn_add = QPushButton("+")
        self.btn_add.setToolTip("Add object")
        self.btn_add.setMaximumWidth(30)
        toolbar_layout.addWidget(self.btn_add)
        
        self.btn_remove = QPushButton("-")
        self.btn_remove.setToolTip("Remove selected")
        self.btn_remove.setMaximumWidth(30)
        self.btn_remove.setEnabled(False)
        toolbar_layout.addWidget(self.btn_remove)
        
        toolbar_layout.addStretch()
        
        # Show all checkbox
        self.chk_show_all = QCheckBox("Show All")
        self.chk_show_all.setChecked(True)
        toolbar_layout.addWidget(self.chk_show_all)
        
        layout.addLayout(toolbar_layout)
        
        # Scene tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Scene Objects")
        self.tree.setRootIsDecorated(True)
        self.tree.setAlternatingRowColors(True)
        
        # Create root categories
        self.category_items = {}
        for category in ["Tracks", "Environments", "Cameras", "Lights"]:
            item = QTreeWidgetItem([category])
            item.setExpanded(True)
            self.tree.addTopLevelItem(item)
            self.category_items[category.lower()] = item
        
        layout.addWidget(self.tree)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply custom styling."""
        style = """
        QTreeWidget {
            background-color: #2b2b2b;
            color: #cccccc;
            border: 1px solid #555555;
        }
        QTreeWidget::item {
            padding: 2px;
        }
        QTreeWidget::item:selected {
            background-color: #3d7aed;
        }
        QTreeWidget::item:hover {
            background-color: #404040;
        }
        QPushButton {
            background-color: #404040;
            color: #cccccc;
            border: 1px solid #555555;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QPushButton:pressed {
            background-color: #333333;
        }
        QCheckBox {
            color: #cccccc;
        }
        """
        self.setStyleSheet(style)
    
    def _connect_signals(self):
        """Connect signals."""
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.btn_add.clicked.connect(self._on_add_clicked)
        self.btn_remove.clicked.connect(self._on_remove_clicked)
        self.chk_show_all.toggled.connect(self._on_show_all_toggled)
    
    def add_track(self, track_id: str, name: str, color: str = "#ffffff"):
        """Add a track to the scene tree.
        
        Args:
            track_id: Unique track identifier.
            name: Display name.
            color: Track color (hex).
        """
        self._add_item("tracks", track_id, name, color)
    
    def add_environment(self, env_id: str, name: str):
        """Add an environment object.
        
        Args:
            env_id: Unique environment identifier.
            name: Display name.
        """
        self._add_item("environments", env_id, name)
    
    def add_camera(self, camera_id: str, name: str):
        """Add a camera.
        
        Args:
            camera_id: Unique camera identifier.
            name: Display name.
        """
        self._add_item("cameras", camera_id, name)
    
    def add_light(self, light_id: str, name: str):
        """Add a light.
        
        Args:
            light_id: Unique light identifier.
            name: Display name.
        """
        self._add_item("lights", light_id, name)
    
    def _add_item(self, category: str, item_id: str, name: str, color: Optional[str] = None):
        """Add an item to the scene tree.
        
        Args:
            category: Category name.
            item_id: Unique identifier.
            name: Display name.
            color: Optional color.
        """
        # Create tree item
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.UserRole, item_id)
        item.setData(0, Qt.UserRole + 1, category)
        item.setCheckState(0, Qt.Checked)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        
        # Set color icon if provided
        if color:
            pixmap = self._create_color_icon(color)
            item.setIcon(0, QIcon(pixmap))
        
        # Add to tree
        parent = self.category_items[category]
        parent.addChild(item)
        
        # Store reference
        self.scene_items[category][item_id] = {
            "name": name,
            "item": item,
            "visible": True,
            "color": color
        }
    
    def remove_item(self, category: str, item_id: str):
        """Remove an item from the scene tree.
        
        Args:
            category: Category name.
            item_id: Item identifier.
        """
        if category in self.scene_items and item_id in self.scene_items[category]:
            item_data = self.scene_items[category].pop(item_id)
            parent = self.category_items[category]
            parent.removeChild(item_data["item"])
    
    def set_item_visibility(self, category: str, item_id: str, visible: bool):
        """Set item visibility.
        
        Args:
            category: Category name.
            item_id: Item identifier.
            visible: Whether item is visible.
        """
        if category in self.scene_items and item_id in self.scene_items[category]:
            item_data = self.scene_items[category][item_id]
            item_data["visible"] = visible
            item_data["item"].setCheckState(0, Qt.Checked if visible else Qt.Unchecked)
    
    def _create_color_icon(self, color: str, size: int = 16):
        """Create a colored square icon.
        
        Args:
            color: Hex color string.
            size: Icon size.
            
        Returns:
            QPixmap icon.
        """
        from PyQt5.QtGui import QPixmap, QPainter, QBrush
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, size, size, 2, 2)
        painter.end()
        
        return pixmap
    
    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item changes.
        
        Args:
            item: Changed item.
            column: Changed column.
        """
        if column == 0:  # Check state changed
            item_id = item.data(0, Qt.UserRole)
            category = item.data(0, Qt.UserRole + 1)
            
            if item_id and category:
                visible = item.checkState(0) == Qt.Checked
                self.visibility_changed.emit(category, item_id, visible)
    
    def _on_selection_changed(self):
        """Handle selection changes."""
        selected = self.tree.selectedItems()
        if selected:
            item = selected[0]
            item_id = item.data(0, Qt.UserRole)
            category = item.data(0, Qt.UserRole + 1)
            
            if item_id and category:
                self.selection_changed.emit(category, item_id)
                self.btn_remove.setEnabled(True)
            else:
                self.btn_remove.setEnabled(False)
        else:
            self.btn_remove.setEnabled(False)
    
    def _on_add_clicked(self):
        """Handle add button click."""
        # Create context menu
        menu = QMenu(self)
        menu.addAction("Add Track", lambda: self._add_placeholder("tracks"))
        menu.addAction("Add Environment", lambda: self._add_placeholder("environments"))
        menu.addAction("Add Camera", lambda: self._add_placeholder("cameras"))
        menu.addAction("Add Light", lambda: self._add_placeholder("lights"))
        
        menu.exec_(self.btn_add.mapToGlobal(self.btn_add.rect().bottomLeft()))
    
    def _on_remove_clicked(self):
        """Handle remove button click."""
        selected = self.tree.selectedItems()
        if selected:
            item = selected[0]
            item_id = item.data(0, Qt.UserRole)
            category = item.data(0, Qt.UserRole + 1)
            
            if item_id and category:
                self.remove_item(category, item_id)
    
    def _on_show_all_toggled(self, checked: bool):
        """Handle show all toggle.
        
        Args:
            checked: Whether show all is checked.
        """
        # Update all items
        for category in self.scene_items.values():
            for item_data in category.values():
                item_data["item"].setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
    
    def _add_placeholder(self, category: str):
        """Add a placeholder item.
        
        Args:
            category: Category to add to.
        """
        # Generate unique ID
        count = len(self.scene_items[category])
        item_id = f"{category[:-1]}_{count + 1}"
        name = f"New {category[:-1].title()} {count + 1}"
        
        if category == "tracks":
            # Use color manager for tracks
            from vibing_viz.utils.colors import ColorManager
            cm = ColorManager()
            color = cm.get_track_color(item_id)
            self.add_track(item_id, name, color)
        else:
            self._add_item(category, item_id, name)