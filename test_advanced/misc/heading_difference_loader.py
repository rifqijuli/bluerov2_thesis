import yaml
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

    with path.open("w") as f:
        yaml.safe_dump(data, f)

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

    with path.open("w") as f:
        yaml.safe_dump(data, f)