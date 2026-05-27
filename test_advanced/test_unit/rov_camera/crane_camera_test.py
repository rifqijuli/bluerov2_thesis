import pytest
import numpy as np
import cv2
import time
import sys
from pathlib import Path

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Always points to test_advanced/, regardless of where you run from
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from camera.rov_camera import Video 

@pytest.fixture(scope="module")
def video():
    """Start real video stream once for all tests."""
    try:
        v = Video(port=5601)
    except Exception as e:
        print(f"\n[front_camera] Video() failed: {type(e).__name__}: {e}")
        pytest.skip("No frame received — is PORT ROV connected?")

    timeout = 10
    start = time.time()
    while not v.frame_available():
        if time.time() - start > timeout:
            pytest.skip("Timeout — is ROV connected?")
        time.sleep(0.03)
    yield v

    # In both test files
    v.video_pipe.set_state(Gst.State.NULL)
    v.video_pipe = None
    
def get_fresh_frame(video, timeout=5):
    """Wait for a new frame and return it."""
    start = time.time()
    while time.time() - start < timeout:
        if video.frame_available():
            return video.frame()
        time.sleep(0.03)
    return None
    
# --- frame_available ---
def test_frame_is_available(video):
    assert video.frame_available() == True


# --- frame() returns valid numpy array ---
def test_frame_returns_numpy_array(video):
    frame = get_fresh_frame(video)
    assert isinstance(frame, np.ndarray)


# --- frame has correct shape (3 channels BGR) ---
def test_frame_has_3_channels(video):
    frame = get_fresh_frame(video)
    assert len(frame.shape) == 3
    assert frame.shape[2] == 3   # BGR


# --- frame is not empty/black ---
def test_frame_is_not_blank(video):
    frame = get_fresh_frame(video)
    assert frame is not None
    assert frame.size > 0


# --- frame dtype is uint8 ---
def test_frame_dtype_uint8(video):
    frame = get_fresh_frame(video)
    assert frame.dtype == np.uint8


# --- frame consumed after read ---
def test_new_frame_reset_after_consume(video):
    # inject a fake new frame then consume it
    video._new_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    video.frame()
    assert video._new_frame is None


# --- resize works on real frame ---
def test_frame_resize(video):
    frame = get_fresh_frame(video)
    resized = cv2.resize(frame, (640, 480))
    assert resized.shape == (480, 640, 3)


# --- port config ---
def test_port_is_5601(video):
    assert video.port == 5601


def test_video_source_contains_port(video):
    assert "5601" in video.video_source

if __name__ == "__main__":
    pytest.main([__file__]) 

