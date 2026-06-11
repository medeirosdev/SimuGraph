from __future__ import annotations
import pytest
from simugraph.camera import Camera
from simugraph.core.node import Node

def test_camera_transforms():
    camera = Camera(screen_width=800, screen_height=600, zoom=1.0, offset_x=10.0, offset_y=20.0)
    
    # world to screen
    sx, sy = camera.world_to_screen(10.0, 20.0)
    assert sx == 0.0
    assert sy == 0.0
    
    sx, sy = camera.world_to_screen(100.0, 200.0)
    assert sx == 90.0
    assert sy == 180.0
    
    # screen to world
    wx, wy = camera.screen_to_world(90.0, 180.0)
    assert wx == 100.0
    assert wy == 200.0

def test_camera_pan():
    camera = Camera(screen_width=800, screen_height=600, zoom=2.0, offset_x=0.0, offset_y=0.0)
    
    # pan by 100 pixels in x, 50 pixels in y
    # with zoom = 2.0, this corresponds to world translation of (50, 25)
    # camera.pan shifts offset_x by -dx/zoom
    camera.pan(100, 50)
    assert camera.offset_x == -50.0
    assert camera.offset_y == -25.0

def test_camera_zoom_at():
    camera = Camera(screen_width=800, screen_height=600, zoom=1.0, offset_x=0.0, offset_y=0.0)
    
    # Zoom at screen point (400, 300) by factor 2.0
    # The world point corresponding to (400, 300) is (400, 300)
    # After zoom, the screen point (400, 300) should still correspond to (400, 300)
    camera.zoom_at(400.0, 300.0, 2.0)
    assert camera.zoom == 2.0
    
    wx, wy = camera.screen_to_world(400.0, 300.0)
    assert wx == 400.0
    assert wy == 300.0

def test_camera_fit_to_nodes():
    camera = Camera(screen_width=800, screen_height=600, zoom=1.0, offset_x=0.0, offset_y=0.0)
    
    n1 = Node(id="n1", x=100.0, y=100.0)
    n2 = Node(id="n2", x=500.0, y=400.0)
    
    camera.fit_to_nodes([n1, n2], padding=0)
    # The bounding box is 400x300. Screen size is 800x600.
    # The aspect ratio is exactly the same, so zoom should scale to fit.
    # zoom = min(800/400, 600/300) = 2.0
    assert camera.zoom == 2.0
    
    # Center wx, wy = (300, 250)
    # camera.offset_x = 300 - 400/2 = 100
    # camera.offset_y = 250 - 300/2 = 100
    assert camera.offset_x == 100.0
    assert camera.offset_y == 100.0
