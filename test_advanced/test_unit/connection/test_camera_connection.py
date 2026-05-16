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
    timeout = 10  # seconds
    start = time.time()
    while not v.frame_available():
        if time.time() - start > timeout:
            pytest.skip("No frame received — is ROV connected?")
        time.sleep(0.03)
    return v

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