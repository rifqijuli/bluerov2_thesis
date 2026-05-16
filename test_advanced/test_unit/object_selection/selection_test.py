# tests/unit/test_object_selection.py
import pytest
import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from object.select_object import click_mouse_position

@pytest.fixture(autouse=True)
def reset_mouse():
    """Reset mouse position before every test."""
    click_mouse_position.reset()

# ── set_position ──────────────────────────────────────────────────────────────
def test_set_position():
    click_mouse_position.set_position(100, 200)
    assert click_mouse_position.x == 100
    assert click_mouse_position.y == 200

def test_reset_position():
    click_mouse_position.set_position(100, 200)
    click_mouse_position.reset()
    assert click_mouse_position.x == 0
    assert click_mouse_position.y == 0


# ── is_within_object ──────────────────────────────────────────────────────────
def make_object(x, y, w, h, track_id=1, obj_class="fish"):
    return {
        "x_coord": x,
        "y_coord": y,
        "width": w,
        "height": h,
        "track_id": track_id,
        "obj_class": obj_class
    }

def test_click_inside_bbox_returns_true():
    click_mouse_position.set_position(150, 150)
    obj = make_object(x=100, y=100, w=100, h=100, track_id=42)
    result = click_mouse_position.is_within_object(obj)
    assert result == True

def test_click_outside_bbox_returns_false():
    click_mouse_position.set_position(50, 50)
    obj = make_object(x=100, y=100, w=100, h=100)
    result = click_mouse_position.is_within_object(obj)
    assert result == False

def test_click_on_edge_of_bbox():
    click_mouse_position.set_position(100, 100)  # top-left corner
    obj = make_object(x=100, y=100, w=100, h=100)
    result = click_mouse_position.is_within_object(obj)
    assert result != False  # edge counts as inside

def test_click_bottom_right_edge():
    click_mouse_position.set_position(200, 200)  # bottom-right corner
    obj = make_object(x=100, y=100, w=100, h=100)
    result = click_mouse_position.is_within_object(obj)
    assert result != False

def test_click_just_outside_right_edge():
    click_mouse_position.set_position(201, 150)
    obj = make_object(x=100, y=100, w=100, h=100)
    result = click_mouse_position.is_within_object(obj)
    assert result == False

def test_correct_object_selected_when_multiple():
    click_mouse_position.set_position(150, 150)
    obj1 = make_object(x=100, y=100, w=100, h=100, track_id=1)
    obj2 = make_object(x=200, y=200, w=200, h=200, track_id=2)
    assert click_mouse_position.is_within_object(obj1) == True
    assert click_mouse_position.is_within_object(obj2) == False