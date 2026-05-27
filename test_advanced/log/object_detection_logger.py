import csv
import time
from pathlib import Path


class object_logger:
    def __init__(self, filepath="object_detection_time_log.csv"):
        self.filepath = Path(filepath)
        self._file = open(self.filepath, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow([
            "timestamp", "frame_id", "loop_ms", "fps", "tracking_ms", "enhancement_ms",
        ])
        self._file.flush()

    def log(self, 
            timestamp, frame_id, loop_ms, fps, tracking_ms, enhancement_ms = 0
            ):
        self._writer.writerow([
            timestamp, frame_id, round(loop_ms, 3), round(fps, 2), round(tracking_ms, 3), round(enhancement_ms, 3)
        ])
        self._file.flush()

    def close(self):
        self._file.close()