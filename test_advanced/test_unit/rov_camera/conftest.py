# test_unit/rov_camera/conftest.py
import pytest
import time

_camera_module_count = {"n": 0}

@pytest.fixture(scope="module", autouse=True)
def gstreamer_inter_module_delay():
    print(f"\n[conftest] module #{_camera_module_count['n']} starting")
    if _camera_module_count["n"] > 0:
        print(f"[conftest] sleeping 3s before next module...")
        time.sleep(3.0)
    _camera_module_count["n"] += 1
    yield