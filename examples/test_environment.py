"""Test environment rendering components."""

import numpy as np
import pygfx as gfx
from vibing_viz.visualization.renderers.environment_renderer import (
    EnvironmentRenderer, Floor, Wall, Box
)


def test_environment_objects():
    """Test environment object creation."""
    print("Testing Environment Objects...")
    
    # Test Floor
    floor = Floor(
        "test_floor",
        size=(10, 10),
        position=(0, 0, 0),
        color="#404040"
    )
    assert floor.object_type == "floor"
    assert floor.size == (10, 10)
    print("✓ Floor object creation works")
    
    # Test Wall
    wall = Wall(
        "test_wall",
        size=(5, 3),
        position=(0, 5, 1.5),
        color="#505050"
    )
    assert wall.object_type == "wall"
    assert wall.size == (5, 3)
    print("✓ Wall object creation works")
    
    # Test Box
    box = Box(
        "test_box",
        size=(1, 1, 1),
        position=(0, 0, 0.5),
        color="#606060"
    )
    assert box.object_type == "box"
    assert box.size == (1, 1, 1)
    print("✓ Box object creation works")


def test_environment_renderer():
    """Test environment renderer functionality."""
    print("\nTesting Environment Renderer...")
    
    # Create scene
    scene = gfx.Scene()
    
    # Create renderer
    renderer = EnvironmentRenderer(scene)
    
    # Test adding floor
    floor = renderer.add_floor(
        "main_floor",
        size=(20, 20),
        grid_divisions=10
    )
    assert "main_floor" in renderer.objects
    assert floor.mesh is not None
    print("✓ Floor rendering works")
    
    # Test adding wall
    wall = renderer.add_wall(
        "test_wall",
        size=(10, 5),
        position=(0, 10, 2.5)
    )
    assert "test_wall" in renderer.objects
    assert wall.mesh is not None
    print("✓ Wall rendering works")
    
    # Test adding box
    box = renderer.add_box(
        "test_box",
        size=(2, 2, 2),
        position=(5, 5, 1)
    )
    assert "test_box" in renderer.objects
    assert box.mesh is not None
    print("✓ Box rendering works")
    
    # Test visibility control
    renderer.set_object_visible("test_box", False)
    assert not renderer.object_groups["test_box"].visible
    renderer.set_object_visible("test_box", True)
    assert renderer.object_groups["test_box"].visible
    print("✓ Visibility control works")
    
    # Test opacity control
    renderer.set_object_opacity("test_wall", 0.5)
    assert renderer.objects["test_wall"].opacity == 0.5
    print("✓ Opacity control works")
    
    # Test color control
    renderer.set_object_color("test_box", "#ff0000")
    assert renderer.objects["test_box"].color == "#ff0000"
    print("✓ Color control works")
    
    # Test object removal
    renderer.remove_object("test_box")
    assert "test_box" not in renderer.objects
    assert "test_box" not in renderer.object_groups
    print("✓ Object removal works")
    
    # Test room creation
    renderer.clear()
    renderer.create_room(size=(10, 10, 3))
    assert "room_floor" in renderer.objects
    assert "room_wall_back" in renderer.objects
    assert "room_wall_left" in renderer.objects
    print("✓ Room creation works")


def test_custom_mesh():
    """Test custom mesh functionality."""
    print("\nTesting Custom Mesh...")
    
    # Create scene and renderer
    scene = gfx.Scene()
    renderer = EnvironmentRenderer(scene)
    
    # Create a simple pyramid
    vertices = np.array([
        [0, 0, 2],      # Top
        [-1, -1, 0],    # Base corners
        [1, -1, 0],
        [1, 1, 0],
        [-1, 1, 0]
    ], dtype=np.float32)
    
    faces = np.array([
        [0, 1, 2],  # Front
        [0, 2, 3],  # Right
        [0, 3, 4],  # Back
        [0, 4, 1],  # Left
        [1, 3, 2],  # Base 1
        [1, 4, 3]   # Base 2
    ], dtype=np.uint32)
    
    # Add custom mesh
    obj = renderer.add_custom_mesh(
        "pyramid",
        vertices,
        faces,
        position=(0, 0, 0),
        color="#ffd700"
    )
    
    assert "pyramid" in renderer.objects
    assert obj.mesh is not None
    print("✓ Custom mesh creation works")


def test_grid_creation():
    """Test grid line creation."""
    print("\nTesting Grid Creation...")
    
    # Create scene and renderer
    scene = gfx.Scene()
    renderer = EnvironmentRenderer(scene)
    
    # Create grid
    grid = renderer._create_grid((10, 10), 10, "#ffffff")
    
    # Check that grid contains lines
    line_count = 0
    for child in grid.children:
        if isinstance(child, gfx.Line):
            line_count += 1
    
    # Should have 11 lines in each direction (divisions + 1)
    assert line_count == 22
    print("✓ Grid creation works")


if __name__ == "__main__":
    print("Environment Rendering Tests")
    print("===========================")
    
    test_environment_objects()
    test_environment_renderer()
    test_custom_mesh()
    test_grid_creation()
    
    print("\nAll environment tests passed! ✓")