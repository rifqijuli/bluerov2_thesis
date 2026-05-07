import pytest
import numpy as np

import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tracking.yolo_track import coordinate

frame = np.zeros((720, 1280, 3), dtype=np.uint8)

def test_coordinate_nw():
    coord = coordinate(x_coord=320, y_coord=180, frame=frame)
    result = coord.difference_to_frame()
    assert result.x == pytest.approx(-320.0)
    assert result.y == pytest.approx(-180.0)

def test_coordinate_ne():
    coord = coordinate(x_coord=960, y_coord=180, frame=frame)
    result = coord.difference_to_frame()
    assert result.x == pytest.approx(320.0)
    assert result.y == pytest.approx(-180.0)

def test_coordinate_sw():
    coord = coordinate(x_coord=320, y_coord=540, frame=frame)
    result = coord.difference_to_frame()
    assert result.x == pytest.approx(-320.0)
    assert result.y == pytest.approx(180.0)

def test_coordinate_se():
    coord = coordinate(x_coord=960, y_coord=540, frame=frame)
    result = coord.difference_to_frame()
    assert result.x == pytest.approx(320.0)
    assert result.y == pytest.approx(180.0)

def test_coordinate_center():
    coord = coordinate(x_coord=640, y_coord=360, frame=frame)
    result = coord.difference_to_frame()
    assert result.x == pytest.approx(0.0)
    assert result.y == pytest.approx(0.0)

if __name__ == "__main__":
    pytest.main()
