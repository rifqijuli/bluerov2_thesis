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

def getProgramState(state):
    currState = state["state"]
    return currState["isBusy"]

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