import yaml
from pathlib import Path

def load_specs(path: str | Path = "specification.yaml"):
    """
    Load camera and vision specs from a YAML file.

    Returns:
        dict with keys: camera, vision
    """
    path = Path(path)
    with path.open("r") as f:
        data = yaml.safe_load(f)

    return data

def get_camera_fov(specs):
    """Return (h_fov_deg, v_fov_deg) from loaded specs dict."""
    cam = specs["camera"]
    return cam["fov_horizontal_deg"], cam["fov_vertical_deg"]

def get_vision_resolution(specs):
    """Return (width, height) from loaded specs dict."""
    vis = specs["vision"]
    return vis["input_width"], vis["input_height"]
