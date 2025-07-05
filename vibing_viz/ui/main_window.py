"""Main application window."""

from typing import Optional, Dict
from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QMenuBar, QMenu, QAction,
    QToolBar, QStatusBar, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon

from vibing_viz.ui.widgets.viewport_widget import ViewportWidget
from vibing_viz.ui.widgets.timeline_widget import TimelineWidget
from vibing_viz.ui.panels.scene_panel import ScenePanel
from vibing_viz.ui.panels.properties_panel import PropertiesPanel
from vibing_viz.ui.panels.tracks_panel import TracksPanel
from vibing_viz.visualization.visualizer import Visualizer


class VibingVizMainWindow(QMainWindow):
    """Main application window for Vibing-Viz.
    
    This window provides the main UI with dockable panels,
    timeline, and 3D viewport.
    """
    
    # Signals
    frame_changed = pyqtSignal(int)
    
    def __init__(self, visualizer: Optional[Visualizer] = None):
        """Initialize main window.
        
        Args:
            visualizer: Optional visualizer instance to use.
        """
        super().__init__()
        
        # Set up visualizer
        self.visualizer = visualizer or Visualizer()
        
        # Window properties
        self.setWindowTitle("Vibing-Viz")
        self.setGeometry(100, 100, 1600, 900)
        
        # Settings for persistent layout
        self.settings = QSettings("VibingViz", "MainWindow")
        
        # Apply dark theme
        self._apply_theme()
        
        # Create UI elements
        self._create_widgets()
        self._create_menus()
        self._create_toolbars()
        self._create_dock_widgets()
        self._create_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Restore layout
        self._restore_layout()
        
        # Initialize viewport
        self._setup_viewport()
    
    def _apply_theme(self):
        """Apply dark theme styling."""
        dark_style = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QDockWidget {
            color: #ffffff;
            background-color: #383838;
            border: 1px solid #555555;
        }
        QDockWidget::title {
            background-color: #404040;
            padding: 5px;
            border-bottom: 2px solid #555555;
        }
        QMenuBar {
            background-color: #383838;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #555555;
        }
        QMenu {
            background-color: #383838;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #555555;
        }
        QToolBar {
            background-color: #383838;
            border: none;
            spacing: 3px;
        }
        QStatusBar {
            background-color: #383838;
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_style)
    
    def _create_widgets(self):
        """Create main widgets."""
        # Central viewport
        self.viewport = ViewportWidget()
        self.setCentralWidget(self.viewport)
        
        # Timeline
        self.timeline = TimelineWidget()
        
        # Panels
        self.scene_panel = ScenePanel()
        self.properties_panel = PropertiesPanel()
        self.tracks_panel = TracksPanel()
    
    def _create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        self.action_open = QAction("&Open...", self)
        self.action_open.setShortcut(QKeySequence.Open)
        file_menu.addAction(self.action_open)
        
        self.action_save = QAction("&Save", self)
        self.action_save.setShortcut(QKeySequence.Save)
        file_menu.addAction(self.action_save)
        
        file_menu.addSeparator()
        
        self.action_export_video = QAction("Export &Video...", self)
        self.action_export_video.setShortcut("Ctrl+E")
        file_menu.addAction(self.action_export_video)
        
        self.action_export_data = QAction("Export &Data...", self)
        file_menu.addAction(self.action_export_data)
        
        file_menu.addSeparator()
        
        self.action_quit = QAction("&Quit", self)
        self.action_quit.setShortcut(QKeySequence.Quit)
        file_menu.addAction(self.action_quit)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        self.action_undo = QAction("&Undo", self)
        self.action_undo.setShortcut(QKeySequence.Undo)
        self.action_undo.setEnabled(False)
        edit_menu.addAction(self.action_undo)
        
        self.action_redo = QAction("&Redo", self)
        self.action_redo.setShortcut(QKeySequence.Redo)
        self.action_redo.setEnabled(False)
        edit_menu.addAction(self.action_redo)
        
        edit_menu.addSeparator()
        
        self.action_preferences = QAction("&Preferences...", self)
        self.action_preferences.setShortcut("Ctrl+,")
        edit_menu.addAction(self.action_preferences)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        self.action_reset_camera = QAction("&Reset Camera", self)
        self.action_reset_camera.setShortcut("R")
        view_menu.addAction(self.action_reset_camera)
        
        self.action_fit_to_scene = QAction("&Fit to Scene", self)
        self.action_fit_to_scene.setShortcut("F")
        view_menu.addAction(self.action_fit_to_scene)
        
        view_menu.addSeparator()
        
        self.action_show_grid = QAction("Show &Grid", self)
        self.action_show_grid.setCheckable(True)
        self.action_show_grid.setChecked(True)
        view_menu.addAction(self.action_show_grid)
        
        self.action_show_axes = QAction("Show &Axes", self)
        self.action_show_axes.setCheckable(True)
        self.action_show_axes.setChecked(True)
        view_menu.addAction(self.action_show_axes)
        
        # Window menu
        window_menu = menubar.addMenu("&Window")
        
        self.action_reset_layout = QAction("&Reset Layout", self)
        window_menu.addAction(self.action_reset_layout)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        self.action_about = QAction("&About", self)
        help_menu.addAction(self.action_about)
        
        self.action_docs = QAction("&Documentation", self)
        self.action_docs.setShortcut("F1")
        help_menu.addAction(self.action_docs)
    
    def _create_toolbars(self):
        """Create toolbars."""
        # Main toolbar
        main_toolbar = QToolBar("Main")
        main_toolbar.setMovable(False)
        self.addToolBar(main_toolbar)
        
        # Playback controls
        self.action_first_frame = QAction("⏮", self)
        self.action_first_frame.setToolTip("First Frame (Home)")
        main_toolbar.addAction(self.action_first_frame)
        
        self.action_prev_frame = QAction("⏪", self)
        self.action_prev_frame.setToolTip("Previous Frame (Left)")
        main_toolbar.addAction(self.action_prev_frame)
        
        self.action_play_pause = QAction("▶", self)
        self.action_play_pause.setToolTip("Play/Pause (Space)")
        self.action_play_pause.setCheckable(True)
        main_toolbar.addAction(self.action_play_pause)
        
        self.action_next_frame = QAction("⏩", self)
        self.action_next_frame.setToolTip("Next Frame (Right)")
        main_toolbar.addAction(self.action_next_frame)
        
        self.action_last_frame = QAction("⏭", self)
        self.action_last_frame.setToolTip("Last Frame (End)")
        main_toolbar.addAction(self.action_last_frame)
        
        main_toolbar.addSeparator()
        
        # View controls
        self.action_camera_orbit = QAction("🔄", self)
        self.action_camera_orbit.setToolTip("Orbit Camera")
        self.action_camera_orbit.setCheckable(True)
        self.action_camera_orbit.setChecked(True)
        main_toolbar.addAction(self.action_camera_orbit)
        
        main_toolbar.addSeparator()
        
        # Camera view buttons
        self.action_view_front = QAction("Front", self)
        self.action_view_front.setToolTip("Front View")
        main_toolbar.addAction(self.action_view_front)
        
        self.action_view_side = QAction("Side", self)
        self.action_view_side.setToolTip("Side View")
        main_toolbar.addAction(self.action_view_side)
        
        self.action_view_top = QAction("Top", self)
        self.action_view_top.setToolTip("Top View")
        main_toolbar.addAction(self.action_view_top)
    
    def _create_dock_widgets(self):
        """Create dockable panels."""
        # Scene panel (left)
        scene_dock = QDockWidget("Scene", self)
        scene_dock.setWidget(self.scene_panel)
        scene_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, scene_dock)
        
        # Properties panel (right)
        properties_dock = QDockWidget("Properties", self)
        properties_dock.setWidget(self.properties_panel)
        properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, properties_dock)
        
        # Tracks panel (right, tabbed with properties)
        tracks_dock = QDockWidget("Tracks", self)
        tracks_dock.setWidget(self.tracks_panel)
        tracks_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, tracks_dock)
        self.tabifyDockWidget(properties_dock, tracks_dock)
        
        # Timeline (bottom)
        timeline_dock = QDockWidget("Timeline", self)
        timeline_dock.setWidget(self.timeline)
        timeline_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, timeline_dock)
        
        # Store dock widgets
        self.dock_widgets = {
            "scene": scene_dock,
            "properties": properties_dock,
            "tracks": tracks_dock,
            "timeline": timeline_dock
        }
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Show initial message
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # File menu
        self.action_quit.triggered.connect(self.close)
        self.action_open.triggered.connect(self._on_open)
        self.action_save.triggered.connect(self._on_save)
        self.action_export_video.triggered.connect(self._on_export_video)
        self.action_export_data.triggered.connect(self._on_export_data)
        
        # View menu
        self.action_reset_camera.triggered.connect(self._on_reset_camera)
        self.action_fit_to_scene.triggered.connect(self._on_fit_to_scene)
        self.action_show_grid.toggled.connect(self._on_toggle_grid)
        self.action_show_axes.toggled.connect(self._on_toggle_axes)
        
        # Window menu
        self.action_reset_layout.triggered.connect(self._reset_layout)
        
        # Help menu
        self.action_about.triggered.connect(self._on_about)
        
        # Playback controls
        self.action_first_frame.triggered.connect(self._on_first_frame)
        self.action_prev_frame.triggered.connect(self._on_prev_frame)
        self.action_play_pause.toggled.connect(self._on_play_pause)
        self.action_next_frame.triggered.connect(self._on_next_frame)
        self.action_last_frame.triggered.connect(self._on_last_frame)
        
        # Timeline signals
        self.timeline.frame_changed.connect(self._on_frame_changed)
        
        # Viewport signals
        self.viewport.frame_rendered.connect(self._on_fps_update)
        
        # Camera view controls
        self.action_view_front.triggered.connect(lambda: self._on_camera_view("front"))
        self.action_view_side.triggered.connect(lambda: self._on_camera_view("side"))
        self.action_view_top.triggered.connect(lambda: self._on_camera_view("top"))
    
    def _setup_viewport(self):
        """Initialize viewport with visualizer."""
        # Set scene and camera
        self.viewport.set_scene(self.visualizer.scene_manager.scene)
        # Use camera manager's active camera
        active_camera = self.visualizer.camera_manager.get_active_camera()
        if active_camera:
            self.viewport.set_camera(active_camera)
        else:
            # Fallback to scene manager camera
            self.viewport.set_camera(self.visualizer.scene_manager.active_camera)
        
        # Set up controller
        self.viewport.set_controller("orbit")
        
        # Set background
        self.viewport.set_background_color(
            self.visualizer.scene_manager.background_color
        )
    
    def _restore_layout(self):
        """Restore window layout from settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _reset_layout(self):
        """Reset to default layout."""
        # Reset dock positions
        for name, dock in self.dock_widgets.items():
            dock.setVisible(True)
            dock.setFloating(False)
        
        # Re-arrange docks
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widgets["scene"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widgets["properties"])
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widgets["tracks"])
        self.tabifyDockWidget(
            self.dock_widgets["properties"],
            self.dock_widgets["tracks"]
        )
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_widgets["timeline"])
    
    # Slot implementations
    def _on_open(self):
        """Handle open file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Pose Data",
            "",
            "NumPy Files (*.npy *.npz);;All Files (*.*)"
        )
        if filename:
            # TODO: Implement file loading
            self.status_bar.showMessage(f"Opened: {filename}")
    
    def _on_save(self):
        """Handle save file."""
        # TODO: Implement saving
        self.status_bar.showMessage("Save not implemented yet")
    
    def _on_export_video(self):
        """Handle export video."""
        from PyQt5.QtWidgets import QProgressDialog
        from PyQt5.QtCore import QTimer
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video",
            "",
            "MP4 Files (*.mp4);;AVI Files (*.avi);;All Files (*.*)"
        )
        if filename:
            # Create progress dialog
            progress = QProgressDialog("Exporting video...", "Cancel", 0, 100, self)
            progress.setWindowTitle("Export Progress")
            progress.setAutoClose(True)
            progress.setMinimumDuration(0)
            
            # Progress callback
            def update_progress(value):
                progress.setValue(int(value * 100))
                QApplication.processEvents()
                return not progress.wasCanceled()
            
            # Export video
            try:
                success = self.visualizer.export_video(
                    output_path=filename,
                    start_frame=0,
                    end_frame=None,
                    resolution=(1920, 1080),
                    fps=30,
                    progress_callback=update_progress
                )
                
                if success:
                    self.status_bar.showMessage(f"Video exported: {filename}")
                    QMessageBox.information(self, "Export Complete", f"Video saved to:\n{filename}")
                else:
                    self.status_bar.showMessage("Export cancelled")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export video:\n{str(e)}")
                self.status_bar.showMessage("Export failed")
            
            finally:
                progress.close()
    
    def _on_export_data(self):
        """Handle export data."""
        # TODO: Implement data export
        self.status_bar.showMessage("Export data not implemented yet")
    
    def _on_reset_camera(self):
        """Reset camera to default position."""
        self.viewport.controller.reset() if self.viewport.controller else None
        self.viewport.request_render()
    
    def _on_fit_to_scene(self):
        """Fit camera to scene bounds."""
        self.viewport.fit_to_scene()
    
    def _on_toggle_grid(self, checked: bool):
        """Toggle grid visibility."""
        self.visualizer.config.show_grid = checked
        # TODO: Update grid visibility
        self.viewport.request_render()
    
    def _on_toggle_axes(self, checked: bool):
        """Toggle axes visibility."""
        # TODO: Update axes visibility
        self.viewport.request_render()
    
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Vibing-Viz",
            "Vibing-Viz\n\n"
            "3D Visualization for Pose Tracking Kinematics\n\n"
            "Version 0.1.0\n"
            "© 2024 Talmo Pereira"
        )
    
    def _on_first_frame(self):
        """Go to first frame."""
        self.set_frame(0)
    
    def _on_prev_frame(self):
        """Go to previous frame."""
        current = self.visualizer._current_frame
        self.set_frame(max(0, current - 1))
    
    def _on_play_pause(self, playing: bool):
        """Toggle playback."""
        if playing:
            self.action_play_pause.setText("⏸")
            self.viewport.start_animation(self._animation_callback)
        else:
            self.action_play_pause.setText("▶")
            self.viewport.stop_animation()
    
    def _on_next_frame(self):
        """Go to next frame."""
        current = self.visualizer._current_frame
        max_frame = self.visualizer.get_total_frames() - 1
        self.set_frame(min(max_frame, current + 1))
    
    def _on_last_frame(self):
        """Go to last frame."""
        self.set_frame(self.visualizer.get_total_frames() - 1)
    
    def _on_frame_changed(self, frame: int):
        """Handle frame change from timeline."""
        self.set_frame(frame)
    
    def _on_fps_update(self, fps: int):
        """Update FPS display."""
        self.status_bar.showMessage(f"FPS: {fps}")
    
    def _on_camera_view(self, view_name: str):
        """Handle camera view change.
        
        Args:
            view_name: Name of the view to apply.
        """
        self.visualizer.set_camera_view(view_name, animate=True)
        self.viewport.request_render()
    
    def _animation_callback(self):
        """Animation frame callback."""
        # Advance frame
        current = self.visualizer._current_frame
        total = self.visualizer.get_total_frames()
        
        if total > 0:
            next_frame = (current + 1) % total
            self.set_frame(next_frame)
    
    def set_frame(self, frame_idx: int):
        """Set current frame.
        
        Args:
            frame_idx: Frame index.
        """
        # Update visualizer
        self.visualizer.set_frame(frame_idx)
        
        # Update timeline
        self.timeline.set_current_frame(frame_idx)
        
        # Update status
        total = self.visualizer.get_total_frames()
        self.status_bar.showMessage(f"Frame {frame_idx + 1}/{total}")
        
        # Request render
        self.viewport.request_render()
        
        # Emit signal
        self.frame_changed.emit(frame_idx)
    
    def closeEvent(self, event):
        """Handle window close.
        
        Args:
            event: Close event.
        """
        # Save layout
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Stop animation
        self.viewport.stop_animation()
        
        event.accept()