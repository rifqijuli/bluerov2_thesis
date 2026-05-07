# tests/unit/test_camera.py
import pytest
import numpy as np
import cv2
import time
import sys
from pathlib import Path

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from camera.rov_camera import Video 

@pytest.fixture(scope="module")
def video():
    """Start real video stream once for all tests."""
    v = Video(port=5601)
    # Wait for first frame (same as your main loop)
    timeout = 5  # seconds
    start = time.time()
    while not v.frame_available():
        if time.time() - start > timeout:
            pytest.skip("No frame received — is ROV connected?")
        time.sleep(0.03)
    return v

# --- frame_available ---
def test_frame_is_available(video):
    assert video.frame_available() == True


# --- frame() returns valid numpy array ---
def test_frame_returns_numpy_array(video):
    frame = video.frame()
    assert isinstance(frame, np.ndarray)


# --- frame has correct shape (3 channels BGR) ---
def test_frame_has_3_channels(video):
    frame = video.frame()
    assert len(frame.shape) == 3
    assert frame.shape[2] == 3   # BGR


# --- frame is not empty/black ---
def test_frame_is_not_blank(video):
    frame = video.frame()
    assert frame is not None
    assert frame.size > 0


# --- frame dtype is uint8 ---
def test_frame_dtype_uint8(video):
    frame = video.frame()
    assert frame.dtype == np.uint8


# --- frame consumed after read ---
def test_new_frame_reset_after_consume(video):
    # inject a fake new frame then consume it
    video._new_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    video.frame()
    assert video._new_frame is None


# --- resize works on real frame ---
def test_frame_resize(video):
    frame = video.frame()
    resized = cv2.resize(frame, (640, 480))
    assert resized.shape == (480, 640, 3)


# --- port config ---
def test_port_is_5601(video):
    assert video.port == 5601


def test_video_source_contains_port(video):
    assert "5601" in video.video_source

if __name__ == "__main__":
    pytest.main([__file__]) 