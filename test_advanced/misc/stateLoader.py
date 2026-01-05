import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PATH = BASE_DIR / "program_state.yaml"

def load_state(path: str | Path = DEFAULT_PATH):
    """
    Load state from a YAML file.

    Returns:
        dict with keys: camera, vision
    """
    path = Path(path)
    with path.open("r") as f:
        data = yaml.safe_load(f)

    return data

def getProgramState(state: dict | None):
    # Safe default if file is empty or missing keys
    if not state or "state" not in state:
        return False

    curr_state = state["state"]
    return bool(curr_state.get("isBusy", False))

def setProgramState(is_busy: bool, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "state" not in data:
        data["state"] = {}
    data["state"]["isBusy"] = bool(is_busy)

    with path.open("w") as f:
        yaml.safe_dump(data, f)

def get_pitch_state(state: dict | None):
    # Safe default if file is empty or missing keys
    if not state or "state" not in state:
        return False

    curr_state = state["state"]
    return bool(curr_state.get("isPitchStateBusy", False))

def get_yaw_state(state: dict | None):
    # Safe default if file is empty or missing keys
    if not state or "state" not in state:
        return False

    curr_state = state["state"]
    return bool(curr_state.get("isYawStateBusy", False))

def set_yaw_state(is_busy: bool, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "state" not in data:
        data["state"] = {}
    data["state"]["isYawStateBusy"] = bool(is_busy)

    with path.open("w") as f:
        yaml.safe_dump(data, f)

def set_pitch_state(is_busy: bool, path: str | Path = DEFAULT_PATH):
    path = Path(path)

    if path.exists():
        with path.open("r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    if "state" not in data:
        data["state"] = {}
    data["state"]["isPitchStateBusy"] = bool(is_busy)

    with path.open("w") as f:
        yaml.safe_dump(data, f)