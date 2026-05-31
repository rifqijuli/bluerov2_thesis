import tempfile

import yaml
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PATH = BASE_DIR / "heading_difference.yaml"

def load_difference(path: str | Path = DEFAULT_PATH):
    path = Path(path)
    with path.open("r") as f:
        data = yaml.safe_load(f)

    return data

def get_yaw_difference(file):
    if file is None or "yaw" not in file or file["yaw"] is None:
        print("get_yaw_difference: invalid data, returning defaults")
        return 0.0, 0.0  # pixel_diff, degree_diff defaults
    
    difference = file["yaw"]
    return difference["pixel_difference"], difference["degree_difference"]

def get_pitch_difference(file):
    if file is None or "pitch" not in file or file["pitch"] is None:
        print("get_pitch_difference: invalid data, returning defaults")
        return 0.0, 0.0  # pixel_diff, degree_diff defaults
    
    difference = file["pitch"]
    return difference["pixel_difference"], difference["degree_difference"]

def get_closeness_difference(file):
    if file is None or "closeness" not in file or file["closeness"] is None:
        print("get_closeness_difference: invalid data, returning defaults")
        return 0.0
    
    difference = file["closeness"]
    return difference["pixel_difference"]

def get_filled_area_difference(file):
    if file is None or "filled_area" not in file or file["filled_area"] is None:
        print("get_filled_area_difference: invalid data, returning defaults")
        return 0.0  # filled area difference default
    
    difference = file["filled_area"]
    return difference["area_difference"]

def set_yaw_difference(pixel_difference: float = 0.0, degree_difference: float = 0.0, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "yaw" not in data:
        data["yaw"] = {}
    data["yaw"]["pixel_difference"] = float(pixel_difference)
    data["yaw"]["degree_difference"] = float(degree_difference)

    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, suffix='.tmp') as tmp:
        yaml.safe_dump(data, tmp)
        tmp_path = tmp.name
    os.replace(tmp_path, path)

def set_pitch_difference(pixel_difference: float = 0.0, degree_difference: float = 0.0, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "pitch" not in data:
        data["pitch"] = {}
    data["pitch"]["pixel_difference"] = float(pixel_difference)
    data["pitch"]["degree_difference"] = float(degree_difference)

    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, suffix='.tmp') as tmp:
        yaml.safe_dump(data, tmp)
        tmp_path = tmp.name
    os.replace(tmp_path, path)

def set_closeness_difference(pixel_difference: float = 0.0, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "closeness" not in data:
        data["closeness"] = {}
    data["closeness"]["pixel_difference"] = float(pixel_difference)

    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, suffix='.tmp') as tmp:
        yaml.safe_dump(data, tmp)
        tmp_path = tmp.name
    os.replace(tmp_path, path)

def set_filled_area_difference(area_difference: float = 0.0, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "filled_area" not in data:
        data["filled_area"] = {}
    data["filled_area"]["area_difference"] = float(area_difference)

    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False, suffix='.tmp') as tmp:
        yaml.safe_dump(data, tmp)
        tmp_path = tmp.name
    os.replace(tmp_path, path)