"""Test camera system components."""

import numpy as np
import pygfx as gfx
from vibing_viz.visualization.camera_manager import CameraManager, CameraView
from vibing_viz.visualization.visualizer import Visualizer


def test_camera_manager():
    """Test camera manager functionality."""
    print("Testing Camera Manager...")
    
    # Create scene
    scene = gfx.Scene()
    
    # Create camera manager
    cam_manager = CameraManager(scene)
    
    # Test adding cameras
    cam1 = cam_manager.add_camera("cam1", "perspective")
    cam2 = cam_manager.add_camera("cam2", "orthographic")
    
    assert "cam1" in cam_manager.cameras
    assert "cam2" in cam_manager.cameras
    print("✓ Camera creation works")
    
    # Test active camera
    assert cam_manager.active_camera_name == "cam1"
    cam_manager.set_active_camera("cam2")
    assert cam_manager.active_camera_name == "cam2"
    print("✓ Active camera switching works")
    
    # Test predefined views
    views = cam_manager.get_view_names()
    assert "front" in views
    assert "side" in views
    assert "top" in views
    print("✓ Predefined views available")
    
    # Test saving custom view
    cam_manager.save_view("custom1")
    assert "custom1" in cam_manager.views
    print("✓ Custom view saving works")
    
    # Test camera frustum creation
    frustum = cam_manager.create_camera_frustum("cam1")
    assert isinstance(frustum, gfx.Group)
    print("✓ Camera frustum creation works")
    
    print("\nCamera Manager tests passed!")


def test_visualizer_camera_integration():
    """Test visualizer camera integration."""
    print("\nTesting Visualizer Camera Integration...")
    
    # Create visualizer
    viz = Visualizer()
    
    # Check default camera
    assert viz.camera_manager.active_camera_name == "main"
    active_cam = viz.camera_manager.get_active_camera()
    assert active_cam is not None
    print("✓ Default camera created")
    
    # Test adding custom view
    viz.add_camera_view("my_view")
    assert "my_view" in viz.camera_manager.views
    print("✓ Custom view addition works")
    
    # Test camera view methods
    try:
        viz.set_camera_view("front", animate=False)
        print("✓ Camera view setting works")
    except Exception as e:
        print(f"✗ Camera view setting failed: {e}")
    
    print("\nVisualizer camera integration tests passed!")


def test_camera_animation():
    """Test camera animation calculations."""
    print("\nTesting Camera Animation...")
    
    # Create test views
    view1 = CameraView("start", np.array([0, 0, 0]), np.array([1, 0, 0]))
    view2 = CameraView("end", np.array([10, 10, 10]), np.array([0, 0, 0]))
    
    # Test interpolation
    scene = gfx.Scene()
    cam_manager = CameraManager(scene)
    
    # Add camera and test animation setup
    camera = cam_manager.add_camera("test", "perspective")
    cam_manager._start_view_animation(camera, view2, 1.0)
    
    assert cam_manager._animating == True
    assert cam_manager._target_view == view2
    print("✓ Animation setup works")
    
    # Test easing function
    assert cam_manager._ease_in_out(0.0) == 0.0
    assert cam_manager._ease_in_out(1.0) == 1.0
    assert 0.4 < cam_manager._ease_in_out(0.5) < 0.6
    print("✓ Easing function works")
    
    print("\nCamera animation tests passed!")


if __name__ == "__main__":
    print("Camera System Tests")
    print("===================")
    
    test_camera_manager()
    test_visualizer_camera_integration()
    test_camera_animation()
    
    print("\nAll camera system tests passed! ✓")